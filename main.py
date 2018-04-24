"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""
import tkinter as tk

__version__ = '0.1'


class MigrationApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        self.switch_frame(LoginScreen)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


class LoginScreen(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        title_label = tk.Label(self, text="Oracle Cloud Infrastructure")
        login_btn = tk.Button(self, text="Login",
                              command=lambda: master.switch_frame(CompartmentScreen))
        title_label.pack(side="top", fill="x", pady=10)
        login_btn.pack()


class CompartmentScreen(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        compartment_label = tk.Label(self, text="Select Compartment")
        back_btn = tk.Button(self, text="Back",
                             command=lambda: master.switch_frame(LoginScreen))
        compartment_label.pack(side="top", fill="x", pady=10)
        back_btn.pack()


if __name__ == "__main__":
    app = MigrationApp()
    app.title("Dragonfly | OCI Migration Tool")
    app.mainloop()
