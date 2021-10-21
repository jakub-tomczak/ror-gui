import tkinter as tk
from tkinter import ttk

class ProgressBar(tk.Frame):
    def __init__(self, root: tk.Tk):
        tk.Frame.__init__(self, master=root)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.__progress_bar: ttk.Progressbar = ttk.Progressbar(
            self,
            orient='horizontal',
            mode='determinate',
            length=400
        )
        self.__progress_bar.grid(row=0, column=0)
        self.__status_text = tk.StringVar()
        self.__progress_status = ttk.Label(self, textvariable=self.__status_text)
        self.__progress_status.grid(column=0, row=1)

    def report_progress(self, progress: int, status: str):
        self.__progress_bar['value'] = min(100, max(0, progress))
        self.__status_text.set(status)
