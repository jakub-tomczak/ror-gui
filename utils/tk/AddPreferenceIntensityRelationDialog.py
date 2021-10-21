import tkinter as tk
from tkinter import StringVar
from typing import Any, Callable, List, Tuple
import ror.Relation as relation
from ror.PreferenceRelations import PreferenceIntensityRelation
from utils.tk.CustomDialog import CustomDialog


class AddPreferenceIntensityRelationDialog(CustomDialog):
    def __init__(self,
                 master: tk.Tk,
                 alternatives: List[str],
                 on_submit_callback: Callable[[None], PreferenceIntensityRelation],
                 intensity_relations: List[PreferenceIntensityRelation]
                 ) -> None:
        self.__preference_relations: List[str] = list(
            relation.PREFERENCE_NAME_TO_RELATION.keys()
        )
        self.__alternative_1: StringVar = StringVar()
        self.__alternative_2: StringVar = StringVar()
        self.__alternative_3: StringVar = StringVar()
        self.__alternative_4: StringVar = StringVar()
        self.__chosen_relation: StringVar = StringVar()
        self.__validation_result: StringVar = StringVar()
        self.__alternatives: List[str] = alternatives
        self.__existing_intensity_relations = set(intensity_relations)
        self.__on_submit_callback = on_submit_callback
        super().__init__(
            master,
            'Add preference intensity relations',
            submit_button_text='Add'
        )

    def __create_relation(self) -> PreferenceIntensityRelation:
        return PreferenceIntensityRelation(
            self.__alternative_1.get(),
            self.__alternative_2.get(),
            self.__alternative_3.get(),
            self.__alternative_4.get(),
            relation.PREFERENCE_NAME_TO_RELATION[self.__chosen_relation.get()]
        )

    def get_data(self) -> Any:
        return self.__create_relation()

    def _validate(self) -> bool:
        alternatives_to_check = [
            (self.__alternative_1, 'first'),
            (self.__alternative_2, 'second'),
            (self.__alternative_3, 'third'),
            (self.__alternative_4, 'fourth')
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

        if self.__create_relation() in self.__existing_intensity_relations:
            self.__validation_result.set(
                'Failed to add preference relation: Relation already exists')
            return False
        return True

    def _on_cancel(self):
        pass

    def _on_submit(self, data):
        self.__validation_result.set('')
        self.__on_submit_callback(data)

    def create_body(self, frame: tk.Frame):
        frame.columnconfigure(0, weight=3)
        frame.columnconfigure(1, weight=3)
        frame.columnconfigure(2, weight=2)
        frame.columnconfigure(3, weight=3)
        frame.columnconfigure(4, weight=3)
        frame.rowconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        header = tk.Label(frame, text='Add new preference relation')
        header.grid(row=0, column=0)

        alternatives = [
            # alternative string var, alternative order number, column, sticky in grid
            (self.__alternative_1, 'first', 0, tk.E),
            (self.__alternative_2, 'second', 1, tk.E),
            (self.__alternative_3, 'third', 3, tk.W),
            (self.__alternative_4, 'fourth', 4, tk.W)
        ]
        def create_input_for_alternative(root: tk.Frame, alternative_data: Tuple[StringVar, str, int, str]):
            alternative, name, column, sticky = alternative_data
            frame = tk.Frame(root)
            frame.grid(column=column, row=1, sticky=sticky)
            tk.Label(frame, text=f'{name} alternative').pack(
                anchor=tk.W)
            tk.OptionMenu(
                frame,
                alternative,
                *self.__alternatives
            ).pack(anchor=tk.CENTER)
        
        create_input_for_alternative(frame, alternatives[0])
        create_input_for_alternative(frame, alternatives[1])

        relations_grid = tk.Frame(frame)
        relations_grid.grid(column=2, row=1, sticky=tk.N)
        tk.Label(relations_grid, text='relation').pack(anchor=tk.CENTER)
        tk.OptionMenu(
            relations_grid,
            self.__chosen_relation,
            *self.__preference_relations,
        ).pack(anchor=tk.CENTER)

        create_input_for_alternative(frame, alternatives[2])
        create_input_for_alternative(frame, alternatives[3])

        label = tk.Label(
            frame, textvariable=self.__validation_result, foreground='red')
        label.grid(row=3, column=0, columnspan=3, sticky=tk.NSEW)

        assert len(self.__alternatives) >= 4, 'Number of alternatives must not be lower than 4'
        self.__alternative_1.set(self.__alternatives[0])
        self.__alternative_2.set(self.__alternatives[1])
        self.__alternative_3.set(self.__alternatives[2])
        self.__alternative_4.set(self.__alternatives[3])

        assert len(self.__preference_relations) > 0, 'There must be at least one preference relation'
        self.__chosen_relation.set(self.__preference_relations[0])
