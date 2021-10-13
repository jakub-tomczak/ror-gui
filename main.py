import tkinter as tk
from tkinter import ttk
from tkinter.constants import LEFT
from typing import Dict

from ror.Dataset import Dataset
from utils.Table import Table
from utils.logging import Severity
from utils.tk.ScrolledText import ScrolledText
from utils.time import get_log_time
from utils.file_handler import get_file, open_file


class RORWindow:
    def __init__(self) -> None:
        self.root: tk.Tk = tk.Tk()
        self.simulation_text = tk.StringVar()
        self.log_console: ScrolledText = None
        self.table: Table = None
        self.root_frames: Dict[str, ttk.Frame] = dict()
        self.open_default_file_button: ttk.Button = None
        self.debug: bool = False
        self.init_gui()
    
    def open_file(self, filename: str):
        try:
            dataset = open_file(filename)
            self.table.set_data(dataset)
            self.log(f'Opened file {filename}')
            self.show_information_tab(dataset, filename)
        except Exception as e:
            self.log(f"Failed to read file. Exception {e}")

    def open_file_dialog(self):
        try:
            filename = get_file()
        except Exception as e:
            self.log(f"Failed to get file. Exception {e}")
        if filename == '':
            self.log('No file selected')
        else:
            self.open_file(filename)

    def init_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        filemenu = tk.Menu(menu)
        filemenu.add_command(
            label="Open file...", command=self.open_file_dialog, accelerator="Control+O")
        save_file_menu = tk.Menu(filemenu)
        save_file_menu.add_command(
            label="Save to ror file (data with preferences)", command=lambda: print("saving ror file"))
        save_file_menu.add_command(
            label="Save lp file", command=lambda: print("saving lp file"))
        filemenu.add_cascade(label="Save...", menu=save_file_menu)
        menu.add_cascade(label="File", menu=filemenu)

        log = tk.Menu(menu)
        menu.add_cascade(label="Log", menu=log)
        log.add_command(
            label='Clear log', command=lambda: self.log_console.clear(), accelerator="F1")

    def init_gui(self):
        self.root.columnconfigure(0, weight=6)
        self.root.columnconfigure(1, weight=6)
        self.root.rowconfigure(0, weight=5)
        self.root.rowconfigure(1, weight=1)
        self.root.minsize(800, 600)
        self.root.geometry("1200x800")
        self.root.title('ROR')

        if self.debug:
            self.open_default_file_button = ttk.Button(
                text="Open buses.txt",
                master=self.root,
                command=lambda: self.open_file('/Users/jjtom/Jakub/ror/ror/problems/buses.txt')
            ).grid(column=1, row=1)

        # data frame
        data_frame = ttk.Frame(self.root, padding=2)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=9)
        data_frame.grid(column=0, row=0, sticky=(tk.NSEW))
        ttk.Label(data_frame, text='Data')\
            .grid(row=0, column=0, sticky=(tk.N, tk.W))
        self.table = Table(data_frame)
        self.table.grid(column=0, row=1, sticky=(tk.NSEW))
        self.root_frames['data'] = self.table

        # frames on the right
        # log_console
        log_console_frame = ttk.Frame(self.root, padding=2)
        log_console_columnspan = 1 if self.debug else 2
        log_console_frame.grid(column=0, row=1, columnspan=log_console_columnspan, sticky=tk.NSEW)
        log_console_frame.rowconfigure(0, weight=1)
        log_console_frame.rowconfigure(1, weight=8)
        self.root_frames['log_console'] = log_console_frame
        ttk.Label(log_console_frame, text='Log window')\
            .grid(row=0, column=0, sticky=(tk.NSEW))
        self.log_console = ScrolledText(
            log_console_frame, height=10, state=tk.DISABLED)
        # update grid for log console
        self.log_console.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)

        # by default set information box with no file opened
        self.hide_information_tab()

        # prepare menu
        self.init_menu()

    def clear_log(self):
        self.log_console.clear()

    def create_information_tab(self) -> ttk.Frame:
        if 'information' in self.root_frames:
            self.root_frames['information'].destroy()
        information_frame = ttk.Frame(self.root, padding=2)
        information_frame.rowconfigure(0, weight=1)
        information_frame.rowconfigure(1, weight=9)
        information_frame.grid(
            column=1, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.root_frames['information'] = information_frame
        information_box = ttk.Frame(information_frame, padding=2)
        information_box.grid(row=1, column=0, sticky=tk.NSEW)
        return information_box

    def show_information_tab(self, dataset: Dataset, filename: str):
        # information frame
        information_box = self.create_information_tab()
        ttk.Label(information_box, text='Information about opened file').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text='1. Filename: ').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=filename).pack(anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=f'2. Number of alternatives: {len(dataset.alternatives)}').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=f'3. Number of criteria: {len(dataset.criteria)}').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=f'4. Criteria:').pack(
            anchor=tk.N, fill=tk.X)
        for index, (criterion_name, criterion_type) in enumerate(dataset.criteria):
            type_name = 'cost' if criterion_type == Dataset.CRITERION_TYPES['cost'] else 'gain'
            ttk.Label(information_box, text=f'4.{index+1}. {criterion_name}, type: {type_name}').pack(anchor=tk.N, fill=tk.X)

        ttk.Label(information_box, text=f'Solve').pack(
            anchor=tk.S, fill=tk.X)

    def hide_information_tab(self):
        information_box = self.create_information_tab()
        ttk.Label(information_box, text='No file is opened').pack(
            anchor=tk.N, fill=tk.X)

    def log(self, message: str, severity: Severity = Severity.INFO):
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
