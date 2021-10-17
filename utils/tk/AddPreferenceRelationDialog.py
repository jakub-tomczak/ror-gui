import tkinter as tk
from tkinter import StringVar
from typing import Any, Callable, List, Tuple
import ror.Relation as relation
from ror.PreferenceRelations import PreferenceRelation
from utils.tk.CustomDialog import CustomDialog


class AddPreferenceRelationDialog(CustomDialog):
    def __init__(self,
                 master: tk.Tk,
                 alternatives: List[str],
                 on_submit_callback: Callable[[None], PreferenceRelation]
                 ) -> None:
        self.__preference_relations: List[str] = relation.PREFERENCE_NAME_TO_RELATION.keys()
        self.__alternative_1: StringVar = StringVar()
        self.__alternative_2: StringVar = StringVar()
        self.__chosen_relation: StringVar = StringVar()
        self.__validation_result: StringVar = StringVar()
        self.__alternatives: List[str] = alternatives
        self.__on_submit_callback = on_submit_callback
        super().__init__(
            master,
            'Add preference relations',
            submit_button_text='Add'
        )

    def get_data(self) -> Any:
        return PreferenceRelation(
            self.__alternative_1.get(),
            self.__alternative_2.get(),
            relation.PREFERENCE_NAME_TO_RELATION[self.__chosen_relation.get()]
        )

    def _validate(self) -> bool:
        alternatives_to_check = [
            (self.__alternative_1, 'first'),
            (self.__alternative_2, 'second')
        ]
        for alternative, name in alternatives_to_check:
            if alternative.get() == '' or alternative.get() not in self.__alternatives:
                self.__validation_result.set(
                    f'Failed to add preference relation: Invalid {name} alternative')
                return False
        alternatives_set = set([alternative.get() for alternative, _ in alternatives_to_check])
        if len(alternatives_set) != len(alternatives_to_check):
            self.__validation_result.set(
                'Failed to add preference relation: Alternatives must be different')
            return False
        if self.__chosen_relation.get() == '' or self.__chosen_relation.get() not in self.__preference_relations:
            self.__validation_result.set(
                'Failed to add preference relation: Invalid relation name')
            return False
        return True

    def _on_cancel(self):
        pass

    def _on_submit(self, data):
        self.__validation_result.set('')
        self.__on_submit_callback(data)

    def create_body(self, frame: tk.Frame):
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=2)
        frame.columnconfigure(2, weight=3)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        header = tk.Label(frame, text='Add new preference intensity relation')
        header.grid(row=0, column=0)

        alternatives = [
            # alternative string var, alternative order number, column, sticky in grid
            (self.__alternative_1, 'first', 0, tk.E),
            (self.__alternative_2, 'second', 2, tk.W)
        ]
        def create_input_for_alternative(root: tk.Frame, alternative_data: Tuple[StringVar, str, int, str]):
            alternative, name, column, sticky = alternative_data
            frame = tk.Frame(root)
            frame.grid(column=column, row=1, sticky=sticky)
            tk.Label(frame, text=f'{name} alternative').pack(
                anchor=tk.CENTER)
            tk.OptionMenu(
                frame,
                alternative,
                *self.__alternatives,
            ).pack(anchor=tk.CENTER)
        
        create_input_for_alternative(frame, alternatives[0])

        relations_grid = tk.Frame(frame)
        relations_grid.grid(column=1, row=1, sticky=tk.N)
        tk.Label(relations_grid, text='relation').pack(anchor=tk.CENTER)
        tk.OptionMenu(
            relations_grid,
            self.__chosen_relation,
            *self.__preference_relations,
        ).pack(anchor=tk.CENTER)

        create_input_for_alternative(frame, alternatives[0])

        label = tk.Label(
            frame, textvariable=self.__validation_result, foreground='red')
        label.grid(row=3, column=0, columnspan=3, sticky=tk.NSEW)
