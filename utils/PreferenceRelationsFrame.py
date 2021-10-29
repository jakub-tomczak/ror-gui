import tkinter as tk
from tkinter import ttk
from ror.Dataset import RORDataset
import ror.Relation as relation
from ror.PreferenceRelations import PreferenceRelation
from utils.ScrollableFrame import ScrollableFrame

from functools import partial
from utils.Severity import Severity

from utils.tk.AddPreferenceRelationDialog import AddPreferenceRelationDialog
from utils.type_aliases import LoggerFunc


class PreferenceRelationsFrame(ttk.Frame):
    def __init__(self, root: tk.Tk, dataset: RORDataset, editable: bool, logger: LoggerFunc) -> None:
        super().__init__(master=root)
        self.__ror_dataset: RORDataset = dataset
        # if true then user can add preference relations
        self.__editable: bool = editable
        self.__logger = logger

        self.__init_gui()

    def __init_gui(self):
        self.rowconfigure(0, weight=1)
        self.rowconfigure(0, weight=9)
        if self.__editable:
            # add one button at the bottom for adding relations
            self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        label = ttk.Label(self, text='Preference relations')
        label.grid(row=0, column=0, sticky=tk.NSEW)

        self.__update_relations()

        if self.__editable:
            button = ttk.Button(
                self,
                text='Add preference relation',
                command=lambda: self.__add_relation()
            )
            button.grid(row=2, column=0, sticky=tk.NSEW)

    def __update_relations(self):
        frame = ScrollableFrame(self)
        for index, preference_relation in enumerate(self.__ror_dataset.preferenceRelations):
            preference_type_label = None
            if preference_relation.relation == relation.PREFERENCE:
                preference_type_label = 'is preferred to alternative'
            elif preference_relation.relation == relation.WEAK_PREFERENCE:
                preference_type_label = 'is weakly preffered over alternative'
            elif preference_relation.relation == relation.INDIFFERENCE:
                preference_type_label = 'is indifferent to alternative'
            if preference_type_label is None:
                ttk.Label(
                    frame.frame,
                    text=f'{index+1}. INVALID PREFERENCE: {preference_relation.relation}'
                ).pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
            else:
                label = '{} {} {}'.format(
                    preference_relation.alternative_1,
                    preference_type_label,
                    preference_relation.alternative_2
                )
                inside_frame = ttk.Frame(frame.frame)
                inside_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
                inside_frame.rowconfigure(0, weight=1)
                inside_frame.columnconfigure(0, weight=9)
                inside_frame.columnconfigure(1, weight=1)
                label = ttk.Label(
                    inside_frame,
                    text=f'{index+1}. {label}',
                    wraplength=150,
                    justify="left"
                ).grid(column=0, row=0, sticky=tk.W)
                if self.__editable:
                    ttk.Button(
                        inside_frame,
                        text='Remove',
                        command=partial(self.remove_relation, preference_relation)
                    ).grid(column=1, row=0)
        frame.grid(row=1, column=0, sticky=tk.NSEW)

    def __add_relation(self):
        if len(self.__ror_dataset.alternatives) < 4:
            # there must be at least 4 alternatives to creates preference intensity
            self.__logger('There must be at least 4 alternatives to creates preference intensity', Severity.ERROR)
        else:
            AddPreferenceRelationDialog(
                self,
                self.__ror_dataset.alternatives,
                self.__on_added_relation,
                self.__ror_dataset.preferenceRelations
            )

    def __on_added_relation(self, new_relation: PreferenceRelation):
        if new_relation is not None:
            self.__ror_dataset.add_preference_relation(new_relation)
            self.__logger(f'Added preference relation {new_relation}', Severity.SUCCESS)
            self.__update_relations()

    def remove_relation(self, relation: PreferenceRelation):
        self.__ror_dataset.remove_preference_relation(relation)
        self.__update_relations()
