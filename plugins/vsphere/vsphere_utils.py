import threading
import time


def process_cookie(cookie):
    """Split the cookie used for exporting into its component parts. return a dictionary of cookie name and value"""
    print("The cookie information is: ", cookie)
    cookie_name = cookie.split("=", 1)[0]
    cookie_value = cookie.split("=", 1)[1].split(";", 1)[0]
    cookie_path = cookie.split("=", 1)[1].split(";", 1)[1].split(
        ";", 1)[0].lstrip()
    cookie_body = " " + cookie_value + "; $" + cookie_path
    cookie_dict = dict()
    cookie_dict[cookie_name] = cookie_body
    return cookie_dict


class ProgressUpdater(threading.Thread):
    def __init__(self, vm_lease, update_time):
        super().__init__(self)
        self.vm_lease = vm_lease
        self.update_time = update_time
        self.progress_percent = 0

    def set_progress_percent(self, progress_percent):
        self.progress_percent = progress_percent

    def run(self):
        while True:
            try:
                if self.vm_lease.state == vim.HttpNfcLease.State.done:
                    return
                print("Progress of lease updating to ", self.progress_percent)
                self.vm_lease.HttpNfcLeaseProgress(self.progress_percent)
                time.sleep(self.update_time)
            except Exception as ex:
                print(ex.message)
                return
