"""
Oracle VM Migration
=====

Application to move local images in VMDK or QCOW2 format to OCI VM

"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

__version__ = '0.1'


class MigrationApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None
        title_style = ttk.Style()
        title_style.configure("T.TLabel", font=("Helvetica", 36), bg='#333333')
        input_label_style = ttk.Style()
        input_label_style.configure("IL.TLabel", font=("Helvetica", 18), activebackground='#333333')
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
        tk.Frame.__init__(self, master, background='#ededed')

        self.title_label = ttk.Label(self, text="Oracle Cloud Infrastructure Account", style="T.TLabel")
        self.tenancy_label = ttk.Label(self, text="Tenancy OCID", style="IL.TLabel")
        self.tenancy_input = ttk.Entry(self)
        self.user_label = ttk.Label(self, text="User OCID", style="IL.TLabel")
        self.user_input = ttk.Entry(self)
        self.region_label = ttk.Label(self, text="Region", style="IL.TLabel")
        self.region_input = ttk.Entry(self)
        self.fingerprint_label = ttk.Label(self, text="Fingerprint", style="IL.TLabel")
        self.fingerprint_input = ttk.Entry(self)
        self.key_label = ttk.Label(self, text="Private Key", style="IL.TLabel")
        self.key_btn = ttk.Button(self, text="Select Private Key",
                              command=lambda: self.open_file())
        self.key_path = ""
        self.login_btn = ttk.Button(self, text="Login",
                              command=lambda: self.login(master))

        row = 2
        column = 1
        col_span = 1

        self.title_label.grid(row=row, column=column, columnspan=col_span, sticky='NW')
        self.tenancy_label.grid(row=row+1, column=column, columnspan=col_span, sticky='NW')
        self.tenancy_input.grid(row=row+2, column=column, columnspan=col_span, sticky='NSEW')
        self.user_label.grid(row=row+3, column=column, columnspan=col_span, sticky='NW')
        self.user_input.grid(row=row+4, column=column, columnspan=col_span, sticky='NSEW')
        self.region_label.grid(row=row+5, column=column, columnspan=col_span, sticky='NW')
        self.region_input.grid(row=row+6, column=column, columnspan=col_span, sticky='NSEW')
        self.fingerprint_label.grid(row=row+7, column=column, columnspan=col_span, sticky='NW')
        self.fingerprint_input.grid(row=row+8, column=column, columnspan=col_span, sticky='NSEW')
        self.key_label.grid(row=row+9, column=column, columnspan=col_span, sticky='NW')
        self.key_btn.grid(row=row+10, column=column, columnspan=col_span, sticky='NSEW')
        self.login_btn.grid(row=row+11, column=column, columnspan=col_span, sticky='NSEW')

    def open_file(self):
        filename =  filedialog.askopenfilename(initialdir = "/",title = "Select Private Key File")
        self.key_path = filename
        self.key_btn['text']=filename

    def login(self, master):
        print(self.tenancy_input.get())
        print(self.user_input.get())
        print(self.region_input.get())
        print(self.fingerprint_input.get())
        print(self.key_path)
        master.switch_frame(CompartmentScreen)


class CompartmentScreen(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        compartment_label = ttk.Label(self, text="Select Compartment")
        back_btn = ttk.Button(self, text="Back",
                             command=lambda: master.switch_frame(LoginScreen))
        compartment_label.grid(row=2, column=1, columnspan = 3)
        back_btn.grid(row=3, column=2)


if __name__ == "__main__":
    app = MigrationApp()
    app.title("Dragonfly | OCI Migration Tool")
    app.geometry('800x600')
    app.configure(background='#ededed')
    app.mainloop()
