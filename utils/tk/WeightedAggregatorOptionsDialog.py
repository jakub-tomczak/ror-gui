from functools import partial
import tkinter as tk
from tkinter import StringVar, Variable, ttk
from typing import Callable, List, Tuple

from ror.ror_solver import TIE_RESOLVERS
from utils.tk.CustomDialog import CustomDialog
from utils.ScrollableFrame import ScrollableFrame
from utils.tk.TieResolverPicker import TieResolverPicker

class AlphaValueWithWeight:
    def __init__(self, alpha_value: float, weight: float) -> None:
        self.alpha_value = alpha_value
        self.weight = weight
    
    def __repr__(self) -> str:
        return f'Alpha value: {self.alpha_value}, weight: {self.weight}'

WeightedAggregatorOptionsDialogResult = Tuple[List[AlphaValueWithWeight], str]

class WeightedAggregatorOptionsDialog(CustomDialog):
    def __init__(self,
        root: tk.Frame,
        header: str,
        on_submit_callback: Callable[[None], List[AlphaValueWithWeight]],
        submit_button_text: str = 'Submit',
        cancel_button_text: str = 'Cancel',
        weights: List[float] = None,
        alpha_values: List[float] = None
    ) -> None:
        assert weights is not None, 'Weights cannot be None'
        assert alpha_values is not None, 'Alpha values cannot be None'
        assert len(weights) == len(alpha_values), 'Number of alpha values must be same as the number of weights'
        self.__weights_list: List[AlphaValueWithWeight] = [
            AlphaValueWithWeight(alpha, weight)
            for alpha, weight in zip(alpha_values, weights)
        ]
        self.__weights: tk.Variable = Variable()
        self.__weights.set(self.__weights_list)
        self.__on_submit = on_submit_callback
        self.__weights_listbox: tk.Listbox = None
        self.__validation_text: tk.StringVar = StringVar()
        self.__new_weight_value: tk.StringVar = StringVar()
        self.__new_alpha_value: tk.StringVar = StringVar()
        self.list_body: ttk.Frame = None
        self.__resolver: TieResolverPicker = None
        # remove validation text when entering text
        self.__new_weight_value.trace('w', lambda *_: self.__validation_text.set(''))
        super().__init__(root, header, submit_button_text=submit_button_text, cancel_button_text=cancel_button_text)
    
    def get_data(self) -> WeightedAggregatorOptionsDialogResult:
        return (self.__weights_list, self.__resolver.tie_resolver_name)

    def _validate(self) -> bool:
        if len(self.__weights_list) < 1:
            self.__validation_text.set('Number of weights cannot be lower than 1')
            return False
        return True

    def _on_submit(self, data: List[float]):
        if self.__on_submit is not None:
            # close before calling __on_submit - while processing __on_submit dialog is still open, which looks weird
            # closing == destroying the dialog before __on_submit doesn't cause any issues
            self._close()
            self.__on_submit(data)

    def __add_weight(self):
        weight = 0.0
        alpha = 0.0
        try:
            alpha = float(self.__new_alpha_value.get())
            weight = float(self.__new_weight_value.get())
        except:
            self.__validation_text.set('Alpha value and/or weight have invalid value, they must be float values.')
            return
        if not 0.0 <= alpha <= 1.0:
            self.__validation_text.set('Alpha has invalid value, it must be a float value in range <0.0, 1.0>')
            return
        if weight < 0.0:
            self.__validation_text.set('Weight has invalid value, it must be a float value greater or equal 0')
            return
        # check whether there was already an entry with same alpha
        # if yes, update it
        replaced_value = False
        for item in self.__weights_list:
            if abs(item.alpha_value - alpha) < 1e-10:
                item.weight = weight
                replaced_value = True
                break
        self.__validation_text.set('')
        self.__new_weight_value.set('')
        self.__new_alpha_value.set('')
        if not replaced_value:
            new_item = AlphaValueWithWeight(alpha, weight)
            self.__weights_list.append(new_item)
        self.__update_weights_list()
        
    def __update_weights_list(self):
        if self.__weights_listbox is None:
            self.__weights_listbox = ScrollableFrame(self.list_body)
            self.__weights_listbox.grid(row=2, column=0, sticky=tk.NSEW)
        else:
            values_to_remove = list(self.__weights_listbox.frame.children.values())
            # remove all children from scrollbar frame = remove all items
            for item in values_to_remove:
                item.destroy()
            self.__weights_listbox.frame.update()
        # recreate all items
        for item in self.__weights_list:
            fr = ttk.Frame(self.__weights_listbox.frame)
            fr.pack(anchor=tk.N, fill=tk.X, expand=1)
            ttk.Label(fr, text=f'Alpha: {item.alpha_value}, weight: {item.weight}').\
                pack(side=tk.LEFT, fill=tk.X)
            ttk.Button(fr, text='Remove', command=partial(self.remove_weight, item))\
                .pack(side=tk.RIGHT, fill=tk.X)

    def remove_weight(self, alpha_with_widget):
        if alpha_with_widget is not None:
            self.__weights_list.remove(alpha_with_widget)
            self.__update_weights_list()


    def create_body(self, frame: tk.Frame):
        self.list_body = ttk.Frame(frame)
        self.list_body.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
        self.list_body.rowconfigure(0, weight=1)
        self.list_body.rowconfigure(1, weight=1)
        self.list_body.rowconfigure(2, weight=9)
        self.list_body.rowconfigure(3, weight=2)
        self.list_body.rowconfigure(4, weight=5)
        self.list_body.rowconfigure(5, weight=1)
        self.list_body.columnconfigure(0, weight=1)
        ttk.Label(self.list_body, text='Set options for weighted aggregator', font=('Arial', 17), foreground='black')\
            .grid(row=0, column=0, sticky=tk.EW)
        ttk.Label(self.list_body, text='Alpha weights').grid(row=1, column=0, sticky=tk.EW)
        
        self.__update_weights_list()
        
        add_weight_frame = ttk.Frame(self.list_body)
        add_weight_frame.grid(row=3, column=0, sticky=tk.NSEW)
        ttk.Label(add_weight_frame, text='Alpha value').pack(side=tk.LEFT)
        new_alpha_input = ttk.Entry(add_weight_frame, width=15, textvariable=self.__new_alpha_value)
        new_alpha_input.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Label(add_weight_frame, text='Weight').pack(side=tk.LEFT)
        new_weight_input = ttk.Entry(add_weight_frame, width=15, textvariable=self.__new_weight_value)
        new_weight_input.pack(side=tk.LEFT, fill=tk.Y)
        ttk.Button(add_weight_frame, text='Add weight', command=self.__add_weight).\
            pack(side=tk.RIGHT, fill=tk.Y)
        TieResolverPicker(self.list_body, TIE_RESOLVERS, 'NoResolver').\
            grid(row=4, column=0, sticky=tk.NSEW)
        ttk.Label(self.list_body, textvariable=self.__validation_text, foreground='red').\
            grid(row=5, column=0)

