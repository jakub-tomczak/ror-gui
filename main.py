import tkinter as tk
from tkinter import ttk
from typing import Dict

from ror.Dataset import Dataset
from utils.Table import Table
from utils.tk.ScrolledText import ScrolledText
from utils.time import get_log_time
from utils.file_handler import open_file


class RORWindow:
    def __init__(self) -> None:
        self.root: tk.Tk = tk.Tk()
        self.simulation_text = tk.StringVar()
        self.log_console: ScrolledText = None
        self.table: Table = None
        self.root_frames: Dict[str, ttk.Frame] = dict()
        
        self.init_gui()

    def open_file_dialog(self):
        try:
            dataset: Dataset = open_file()
            self.table.set_data(dataset)
        except:
            self.log_console.set_text("Failed to read file.")

    def init_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        filemenu = tk.Menu(menu)
        filemenu.add_command(label="Open file...", command=self.open_file_dialog, accelerator="Control+O")
        save_file_menu = tk.Menu(filemenu)
        save_file_menu.add_command(label="Save to ror file (data with preferences)", command=lambda: print("saving ror file"))
        save_file_menu.add_command(label="Save lp file", command=lambda: print("saving lp file"))
        filemenu.add_cascade(label="Save...", menu=save_file_menu)
        menu.add_cascade(label="File", menu=filemenu)

        log = tk.Menu(menu)
        menu.add_cascade(label="Log", menu=log)
        log.add_command(label='Clear log', command=lambda : self.log_console.set_text("some text"), accelerator="F1")

    def init_gui(self):
        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=2)
        self.root.rowconfigure(0, weight=5)
        self.root.rowconfigure(1, weight=1)
        self.root.minsize(800, 600)
        self.root.geometry("1200x800")
        self.root.title('ROR')

        # data frame
        data_frame = ttk.Frame(self.root, padding=2)
        data_frame.rowconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=9)
        data_frame.grid(column=1, row=0, sticky=(tk.NSEW), ipady=2, ipadx=2)
        ttk.Label(data_frame, text='Data')\
            .grid(row=0, column=0, sticky=(tk.N, tk.W))
        self.table = Table(data_frame)
        self.table.grid(column=0, row=1, sticky=(tk.NSEW))
        self.root_frames['data'] = self.table


        # preferences frame
        preferences_frame = ttk.Frame(self.root, padding=2)
        preferences_frame.rowconfigure(0, weight=1)
        preferences_frame.rowconfigure(1, weight=9)
        preferences_frame.grid(column=0, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.root_frames['preferences'] = preferences_frame
        ttk.Label(preferences_frame, text='Preferences')\
            .grid(row=0, column=1, sticky=(tk.NW))

        # model frame
        model_frame = ttk.Frame(self.root, padding=2)
        model_frame.grid(column=2, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.root_frames['model'] = model_frame
        ttk.Label(model_frame, text='Model')\
            .grid(row=0, column=2, sticky=(tk.NW))

        # frames on the right
        # log_console
        log_console_frame = ttk.Frame(self.root, padding=2)
        log_console_frame.grid(column=0, row=1, columnspan=3, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.root_frames['log_console'] = log_console_frame
        ttk.Label(log_console_frame, text='Log window')\
            .grid(row=0, column=0, sticky=(tk.NW))
        self.log_console = ScrolledText(log_console_frame, height=10, state=tk.DISABLED)
        # update grid for log console
        self.log_console.grid(row=1, column=0, columnspan=2, sticky=(tk.N, tk.S, tk.W))

        # prepare menu
        self.init_menu()

    def clear_log(self):
        self.log_console.configure(state='normal')
        self.log_console.clear()
        self.log_console.configure(state='disabled')

    def log(self, message, severity):
        '''
        Logs message to a console with specified severity.
        '''
        if self.log_console is None:
            return
        data = f'[{get_log_time()}][{severity}]: {message}\n'
        # hack with changing state - to make log console readonly
        # set state to normal to be able to add a new text
        self.log_console.configure(state='normal')
        self.log_console.insert(tk.END, data)
        # disable adding new texts
        self.log_console.configure(state='disabled')
        # scroll to the end
        self.log_console.see('end')

    def run(self):
        self.root.mainloop()


def main():
    RORWindow().run()


if __name__ == '__main__':
    main()
