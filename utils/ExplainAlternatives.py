import tkinter as tk
from tkinter import StringVar
from typing import Callable, List


class ExplainAlternatives(tk.Frame):
    def __init__(self, root: tk.Tk, explain_func: Callable, alternatives: List[str]):
        tk.Frame.__init__(self, master=root)
        self.__explanation = StringVar()
        self.label: tk.Label = None
        self.__alternatives = alternatives
        # function that takes 2 alternatives and returns string - an explanation
        # why alternatives have specific positions in the rank
        self.__explain_function = explain_func
        self.first_alternative: tk.StringVar = None
        self.second_alternative: tk.StringVar = None
        self.__make_gui()

    def __explain_alternatives(self):
        alternative_1: str = self.first_alternative.get()
        alternative_2: str = self.second_alternative.get()
        assert self.__explain_function is not None, 'Explanation function is None'
        if alternative_1 is None or alternative_1 == '':
            self.__explanation.set('Set first alternative')
        elif alternative_2 is None or alternative_2 == '':
            self.__explanation.set('Set second alternative')
        elif alternative_1 == alternative_2:
            self.__explanation.set(
                f'Pick different alternatives to get explanation, Picked only alternative {alternative_1}')
        else:
            explanation = self.__explain_function(alternative_1, alternative_2)
            print('setting explanation to', explanation)
            self.__explanation.set(explanation)

    def __make_gui(self):
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=2)
        self.columnconfigure(2, weight=4)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.rowconfigure(4, weight=8)
        explain_label = tk.Label(self, text='Explain rank position')
        explain_label.grid(row=0, column=0)
        self.first_alternative = tk.StringVar()
        self.second_alternative = tk.StringVar()

        first_alternative_drop_down = tk.OptionMenu(
            self,
            self.first_alternative,
            *self.__alternatives,
        )
        first_alternative_drop_down.grid(column=0, row=1, sticky=tk.E)

        second_alternative_drop_down = tk.OptionMenu(
            self,
            self.second_alternative,
            *self.__alternatives
        )
        second_alternative_drop_down.grid(column=2, row=1, sticky=tk.W)

        explain_label_vs = tk.Label(self, text="vs.")
        explain_label_vs.grid(column=1, row=1, sticky=tk.N)

        self.pack(anchor=tk.N, fill=tk.X, expand=1)
        button = tk.Button(master=self, text='Explain position in rank', command=lambda: self.__explain_alternatives())
        button.grid(row=2, column=0, columnspan=3)

        label = tk.Label(self, text='Explanation:')
        label.grid(row=3, column=0, columnspan=3)
        self.label = tk.Label(self, textvariable=self.__explanation)
        self.label.grid(row=4, column=0, columnspan=3)

        self.__explanation.set('No alternatives were picked')
