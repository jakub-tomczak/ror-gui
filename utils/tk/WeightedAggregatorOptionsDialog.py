from functools import partial
import tkinter as tk
from tkinter import IntVar, StringVar, Variable, ttk
from typing import Callable, List, Tuple
from collections import namedtuple

from ror.ror_solver import TIE_RESOLVERS
from utils.tk.AlphaValueCountSliderFrame import DEFAULT_NUMBER_OF_ALPHA_VALUES, MAX_NUMBER_OF_ALPHA_VALUES, AlphaValueCountSliderFrame
from utils.tk.CustomDialog import CustomDialog
from utils.ScrollableFrame import ScrollableFrame
from utils.tk.TieResolverPicker import TieResolverPicker
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from enum import Enum
import copy


class AlphaValueWithWeight:
    def __init__(self, alpha_value: float, weight: float) -> None:
        self.alpha_value = alpha_value
        self.weight = weight
    
    def __repr__(self) -> str:
        return f'Alpha value: {self.alpha_value}, weight: {self.weight}'

class WeightGeneratorType(Enum):
    CUSTOM = 'custom'
    TRIANGLE = 'triangle'
    NORMAL_DISTRIBUTION = 'normal distribution'

Coordinates = namedtuple('Coordinates', ['x', 'y'])

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
        matplotlib.use('TkAgg')
        assert weights is not None, 'Weights cannot be None'
        assert alpha_values is not None, 'Alpha values cannot be None'
        assert len(weights) == len(alpha_values), 'Number of alpha values must be same as the number of weights'
        self.__weights_list: List[AlphaValueWithWeight] = [
            AlphaValueWithWeight(alpha, weight)
            for alpha, weight in zip(alpha_values, weights)
        ]
        self.__initial_alpha_values_and_weights: List[AlphaValueWithWeight] = copy.deepcopy(self.__weights_list)
        self.__weights: tk.Variable = Variable()
        self.__weights.set(self.__weights_list)
        self.__on_submit = on_submit_callback
        self.__weights_scrolled_frame: tk.Listbox = None
        self.__validation_text: tk.StringVar = StringVar()
        self.__new_weight_value: tk.StringVar = StringVar()
        self.__new_alpha_value: tk.StringVar = StringVar()
        self.__number_of_alpha_values: tk.IntVar = IntVar(value=len(self.__weights_list))
        self.__number_of_alpha_values.trace('w', lambda *_: self.__update_number_of_alpha_values())
        self.list_body: ttk.Frame = None
        self.__resolver: TieResolverPicker = None
        self.__weights_type_name: tk.StringVar = StringVar()
        self.__weights_type_name.trace('w', lambda *_: self.__on_weights_generator_change())
        self.__weights_type_picker: ttk.Combobox = None
        self.__weights_types: List[str] = [item.value for item in WeightGeneratorType]
        self.__graph_object: FigureCanvasTkAgg = None
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

    def _on_submit(self, data: WeightedAggregatorOptionsDialogResult):
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
        self.__weights_list = sorted(self.__weights_list, key=lambda item: item.alpha_value)
        self.__display_weights_list()
        self.__update_graph()

    def __update_number_of_alpha_values(self):
        self.__generate_alpha_weights(self.__weights_type_name.get())
        self.__display_weights_list()
        self.__update_graph()

    def __set_alpha_values_using_scale(self, value: int):
        self.__number_of_alpha_values.set(value)
    
    def __display_alpha_value_count_slider(self, root: ttk.Frame) -> ttk.Frame:
        return AlphaValueCountSliderFrame(
            root,
            self.__set_alpha_values_using_scale,
            DEFAULT_NUMBER_OF_ALPHA_VALUES
        )

    def __generate_alpha_weights(self, method: WeightGeneratorType):
        points: int = self.__number_of_alpha_values.get()
        new_weights_list: List[AlphaValueWithWeight] = []
        get_alpha_values = lambda points: np.linspace(start=0.0, stop=1.0, num=points)
        if method == WeightGeneratorType.NORMAL_DISTRIBUTION.value:
            def get_normal_distribution_data(points: int) -> Tuple[List[float], List[float]]:
                mu, sigma = 0.5, 0.25 # mean and standard deviation
                x_values = get_alpha_values(points)
                y_values = 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (x_values - mu)**2 / (2 * sigma**2))
                return [x_values, y_values]
            alpha_values, weights = get_normal_distribution_data(points)
            new_weights_list = [
                AlphaValueWithWeight(alpha, weight)
                for alpha, weight in zip(alpha_values, weights)
            ]
        elif method == WeightGeneratorType.TRIANGLE.value:
            def interpolate(start: Coordinates, stop: Coordinates, val: float) -> float:
                return start.y + (val - start.x) / (stop.x - start.x)*(stop.y-start.y)
            alpha_values = get_alpha_values(points)
            lowest_weight = 1.0
            highest_weight = 2.0
            # for alpha values < 0.5 interpolate starting from weight = 1.0 when alpha value = 0,
            # ending on weight = 2.0 when alpha value = 0.5
            lower_than_half = partial(interpolate, Coordinates(x=0.0, y=lowest_weight), Coordinates(x=0.5, y=highest_weight))
            # for alpha values > 0.5 interpolate starting from weight = 2.0 when alpha value = 0.5,
            # ending on weight = 1.0 when alpha value = 1.0
            higher_than_half = partial(interpolate, Coordinates(x=0.5, y=highest_weight), Coordinates(x=1.0, y=lowest_weight))
            weights = []
            for alpha_value in alpha_values:
                weight = 0.0
                if alpha_value < 0.5:
                    weight = lower_than_half(alpha_value)
                elif alpha_value > 0.5:
                    weight = higher_than_half(alpha_value)
                else:
                    weight = 2.0
                weights.append(weight)
            new_weights_list = [
                AlphaValueWithWeight(alpha, weight)
                for alpha, weight in zip(alpha_values, weights)
            ]
        elif method == WeightGeneratorType.CUSTOM.value:
            new_weights_list = copy.deepcopy(self.__initial_alpha_values_and_weights)
        self.__weights_list = new_weights_list

    def __on_weights_generator_change(self):
        new_weight_generator_method = self.__weights_type_name.get()
        if new_weight_generator_method is None or new_weight_generator_method == '':
            return
        # reset the number of alpha values
        self.__number_of_alpha_values.set(DEFAULT_NUMBER_OF_ALPHA_VALUES)
        self.__generate_alpha_weights(new_weight_generator_method)
        self.__display_weights_list()
        self.__display_alpha_values_generator()
        self.__update_graph()

    def __update_graph(self) -> tk.Canvas:
        x_data: List[float] = [item.alpha_value for item in self.__weights_list]
        y_data: List[float] = [item.weight for item in self.__weights_list]
        plt.close()
        plt.cla()
        plt.clf()
        frame = ttk.Frame(self.list_body)
        frame.grid(row=6, column=0, sticky=tk.NSEW)
        # Use TkAgg in the backend of tkinter application
        fig, ax = plt.subplots(figsize=(3, 4))
        ax.bar(x_data, height=y_data, width=0.05, color='grey')
        ax.set(xlabel='Alpha value', ylabel='Weight', title='Weights to be used')
        ax.grid()
        self.__graph_object = FigureCanvasTkAgg(fig, master=frame)
        self.__graph_object.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        return frame

    def __display_weights_list(self):
        weights_frame = ttk.Frame(self.list_body)
        weights_frame.grid(row=4, column=0, sticky=tk.NSEW)
        self.__weights_scrolled_frame = ScrollableFrame(weights_frame)
        self.__weights_scrolled_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
        # create all items
        for idx, item in enumerate(self.__weights_list):
            fr = ttk.Frame(self.__weights_scrolled_frame.frame, padding=5)
            fr.pack(anchor=tk.NW, fill=tk.X, expand=1)
            ttk.Label(fr, text=f'{idx+1}. Alpha: {round(item.alpha_value, 3)}, weight: {round(item.weight, 3)}').\
                pack(side=tk.LEFT, fill=tk.X)
            if self.__weights_type_name.get() == WeightGeneratorType.CUSTOM.value:
                ttk.Button(fr, text='Remove', command=partial(self.remove_weight, item))\
                    .pack(side=tk.RIGHT, fill=tk.X)

    def __display_alpha_value_form(self, root: ttk.Frame) -> ttk.Frame:
        add_weight_frame = ttk.Frame(root)
        ttk.Label(add_weight_frame, text='Alpha value').pack(side=tk.LEFT)
        new_alpha_input = ttk.Entry(add_weight_frame, width=15, textvariable=self.__new_alpha_value)
        new_alpha_input.pack(side=tk.LEFT)
        ttk.Label(add_weight_frame, text='Weight').pack(side=tk.LEFT)
        new_weight_input = ttk.Entry(add_weight_frame, width=15, textvariable=self.__new_weight_value)
        new_weight_input.pack(side=tk.LEFT)
        ttk.Button(add_weight_frame, text='Add weight', command=self.__add_weight).\
            pack(side=tk.RIGHT)
        return add_weight_frame
    
    def __display_alpha_values_generator(self):
        fr = ttk.Frame(self.list_body)
        form: ttk.Frame = None
        if self.__weights_type_name.get() == WeightGeneratorType.CUSTOM.value:
            form = self.__display_alpha_value_form(fr)
        else:
            form = self.__display_alpha_value_count_slider(fr)
        form.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
        fr.grid(row=5, column=0, sticky=tk.NSEW)

    def remove_weight(self, alpha_with_widget):
        if alpha_with_widget is not None:
            self.__weights_list.remove(alpha_with_widget)
            self.__display_weights_list()
            self.__update_graph()

    def create_body(self, frame: tk.Frame):
        self.list_body = ttk.Frame(frame)
        self.list_body.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
        self.list_body.rowconfigure(0, weight=1)
        self.list_body.rowconfigure(1, weight=1)
        self.list_body.rowconfigure(2, weight=1)
        self.list_body.rowconfigure(3, weight=1)
        self.list_body.rowconfigure(4, weight=6)
        self.list_body.rowconfigure(5, weight=3)
        self.list_body.rowconfigure(6, weight=6)
        self.list_body.rowconfigure(7, weight=5)
        self.list_body.rowconfigure(8, weight=1)
        self.list_body.columnconfigure(0, weight=1)
        ttk.Label(self.list_body, text='Set options for weighted aggregator', font=('Arial', 17), foreground='black')\
            .grid(row=0, column=0, sticky=tk.EW)
        ttk.Label(self.list_body, text='Select alpha values and weights distribution').grid(row=1, column=0, sticky=tk.EW)
        self.__weights_type_picker = ttk.Combobox(self.list_body, textvariable=self.__weights_type_name, state='readonly')
        self.__weights_type_picker['values'] = self.__weights_types
        self.__weights_type_picker.grid(row=2, column=0, sticky=tk.NSEW)
        ttk.Label(self.list_body, text='Alpha weights').grid(row=3, column=0, sticky=tk.EW)
        
        self.__display_weights_list()
        self.__display_alpha_values_generator()
        self.__update_graph()

        self.__resolver = TieResolverPicker(self.list_body, TIE_RESOLVERS, 'NoResolver').\
            grid(row=7, column=0, sticky=tk.NSEW)
        ttk.Label(self.list_body, textvariable=self.__validation_text, foreground='red').\
            grid(row=8, column=0)
        self.__weights_type_name.set(WeightGeneratorType.CUSTOM.value)

