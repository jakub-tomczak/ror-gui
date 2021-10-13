import tkinter as tk
from tkinter import ttk
from typing import Dict, Tuple

from ror.Dataset import Dataset, RORDataset
import ror.Relation as relation
from ror.data_loader import AvailableParameters
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
        self.debug: bool = True
        self.current_filename: str = None
        self.dataset: RORDataset = None
        self.parameters: Dict[AvailableParameters, float] = None
        self.init_gui()

    def open_file(self, filename: str):
        try:
            loading_result = open_file(filename)
            self.dataset = loading_result.dataset
            self.parameters = loading_result.parameters
            self.table.set_data(self.dataset)
            self.current_filename = filename
            self.log(f'Opened file {filename}')
            self.show_information_tab()
        except Exception as e:
            self.current_filename = None
            self.log(f"Failed to read file. Exception {e}")

    def open_file_dialog(self):
        try:
            filename = get_file()
        except Exception as e:
            self.current_filename = None
            self.log(f"Failed to get file. Exception {e}")
        if filename == '':
            self.current_filename = None
            self.log('No file selected')
        else:
            self.open_file(filename)

    def save_file(self):
        format = 'txt'
        if self.dataset is not None:
            splited = self.current_filename.split(f'.{format}')
            if len(splited) != 2:
                self.log('Failed to save file')
            name = splited[0]
            self.dataset.save_to_file(f'{name}.{format}')
            self.log(f'Saved dataset to {name}.{format}')
        else:
            self.log('Dataset is empty')

    def close_file(self):
        self.table.remove_data(self.dataset)
        self.dataset = None
        self.current_filename = None
        self.parameters = None
        self.hide_information_tab()

    def cancel_changes(self):
        if self.current_filename is not None:
            self.open_file(self.current_filename)
            self.log(f'Canceleed changes - reopened file {self.current_filename}')
        else:
            self.log('No file is currently opened')

    def init_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)
        filemenu = tk.Menu(menu)
        filemenu.add_command(
            label="Open file...", command=self.open_file_dialog, accelerator="Control+O")
        save_file_menu = tk.Menu(filemenu)
        save_file_menu.add_command(
            label="Save to ror file (data with preferences)", command=lambda: self.save_file())
        # save_file_menu.add_command(
        #     label="Save lp file", command=lambda: print("saving lp file"))
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
        self.root.minsize(1200, 800)
        self.root.geometry("1200x800")
        self.root.title('ROR')

        if self.debug:
            self.open_default_file_button = ttk.Button(
                text="Open buses.txt",
                master=self.root,
                command=lambda: self.open_file(
                    '/Users/jjtom/Jakub/ror/ror/problems/buses.txt')
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
        log_console_frame.grid(
            column=0, row=1, columnspan=log_console_columnspan, sticky=tk.NSEW)
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

    '''
    Returns information box that consumes 80% of the height of the information tab
    and informatino bottom box that takes 10% of the height of the information tab
    '''
    def create_information_tab(self) -> Tuple[ttk.Frame, ttk.Frame]:
        if 'information' in self.root_frames:
            self.root_frames['information'].destroy()
        information_frame = ttk.Frame(self.root, padding=2)
        information_frame.rowconfigure(0, weight=8)
        information_frame.rowconfigure(1, weight=1)
        information_frame.grid(
            column=1, row=0, sticky=(tk.N, tk.E, tk.S, tk.W))
        self.root_frames['information'] = information_frame
        information_box = ttk.Frame(information_frame, padding=2)
        information_box.grid(row=0, column=0, sticky=tk.NSEW)
        information_box_bottom = ttk.Frame(information_frame, padding=2)
        information_box_bottom.grid(row=1, column=0, sticky=tk.NSEW)
        return information_box, information_box_bottom

    def show_information_tab(self):
        if self.dataset is None:
            self.log('No dataset available')
        if self.current_filename is None or self.current_filename == '':
            self.log('Filename is invalid')
        filename = self.current_filename
        # information frame
        information_box, information_box_bottom = self.create_information_tab()
        ttk.Label(information_box, text='Information about opened file').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text='1. Filename: ').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=filename).pack(anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=f'2. Number of alternatives: {len(self.dataset.alternatives)}').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=f'3. Number of criteria: {len(self.dataset.criteria)}').pack(
            anchor=tk.N, fill=tk.X)
        ttk.Label(information_box, text=f'4. Criteria:').pack(
            anchor=tk.N, fill=tk.X)
        for index, (criterion_name, criterion_type) in enumerate(self.dataset.criteria):
            type_name = 'cost' if criterion_type == Dataset.CRITERION_TYPES['cost'] else 'gain'
            ttk.Label(
                information_box, text=f'4.{index+1}. {criterion_name}, type: {type_name}').pack(anchor=tk.N, fill=tk.X)

        tab_control = ttk.Notebook(information_box)
        preference_relations_tab = ttk.Frame(tab_control)
        intensity_relations_tab = ttk.Frame(tab_control)

        tab_control.add(preference_relations_tab, text='Preference relations')
        tab_control.add(intensity_relations_tab, text='Intensity relations')
        tab_control.pack(anchor=tk.N, fill=tk.BOTH)

        # display preference relations in the tab
        for index, preference_relation in enumerate(self.dataset.preferenceRelations):
            preference_type_label = None
            if preference_relation.relation == relation.PREFERENCE:
                preference_type_label = 'is preferred to alternative'
            elif preference_relation.relation == relation.WEAK_PREFERENCE:
                preference_type_label = 'is weakly preffered over alternative'
            elif preference_relation.relation == relation.INDIFFERENCE:
                preference_type_label = 'is indifferent to alternative'
            if preference_type_label is None:
                ttk.Label(
                    preference_relations_tab, text=f'{index+1}. INVALID PREFERENCE: {preference_relation.relation}').pack(anchor=tk.N, fill=tk.X)
            else:
                label = '{} {} {}'.format(
                    preference_relation.alternative_1,
                    preference_type_label,
                    preference_relation.alternative_2
                )
                ttk.Label(
                    preference_relations_tab, text=f'{index+1}. {label}', wraplength=250, justify="left").pack(anchor=tk.N, fill=tk.X)

        # display intensity relations in the tab
        for index, intensity_relation in enumerate(self.dataset.intensityRelations):
            relation_name = None
            if intensity_relation.relation == relation.PREFERENCE:
                relation_name = 'preferred'
            elif intensity_relation.relation == relation.WEAK_PREFERENCE:
                relation_name = 'weakly preferred'
            elif preference_relation.relation == relation.INDIFFERENCE:
                relation_name = 'indifferent'

            if preference_type_label is None:
                ttk.Label(
                    intensity_relations_tab, text=f'{index+1}. INVALID PREFERENCE: {preference_relation.relation}').pack(anchor=tk.N, fill=tk.X)
            else:
                label = '{} is {} to {} stronger than {} is {} to {}'.format(
                    intensity_relation.alternative_1,
                    relation_name,
                    intensity_relation.alternative_2,
                    intensity_relation.alternative_3,
                    relation_name,
                    intensity_relation.alternative_4
                )
                ttk.Label(
                    intensity_relations_tab, text=f'{index+1}. {label}', wraplength=250, justify="left").pack(anchor=tk.N, fill=tk.X)
        # bottom tab buttons
        information_box_bottom.columnconfigure(0, weight=1)
        information_box_bottom.columnconfigure(1, weight=1)
        information_box_bottom.columnconfigure(2, weight=1)
        information_box_bottom.columnconfigure(3, weight=1)
        information_box_bottom.rowconfigure(0, weight=1)
        ttk.Button(
                master=information_box_bottom,
                text='Solve',
                command=lambda: self.solve()
        ).grid(column=0, row=0)
        ttk.Button(
                master=information_box_bottom,
                text='Save file',
                command=lambda: self.save_file()
        ).grid(column=1, row=0)
        ttk.Button(
                master=information_box_bottom,
                text='Cancel changes',
                command=lambda: self.cancel_changes()
        ).grid(column=2, row=0)
        ttk.Button(
                master=information_box_bottom,
                text='Close file',
                command=lambda: self.close_file()
        ).grid(column=3, row=0)

    def hide_information_tab(self):
        information_box, information_box_bottom = self.create_information_tab()
        ttk.Label(information_box, text='No file is opened').pack(
            anchor=tk.N, fill=tk.X)
        # bottom tab buttons
        information_box_bottom.columnconfigure(0, weight=1)
        information_box_bottom.rowconfigure(0, weight=1)
        ttk.Button(
                master=information_box_bottom,
                text='Open file',
                command=lambda: self.open_file_dialog()
        ).grid(column=0, row=0)

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
