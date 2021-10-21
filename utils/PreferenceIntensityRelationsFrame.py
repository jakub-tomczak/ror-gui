import tkinter as tk
from tkinter import ttk
from ror.Dataset import RORDataset
import ror.Relation as relation
from ror.PreferenceRelations import PreferenceIntensityRelation
from utils.ScrollableFrame import ScrollableFrame

from functools import partial

from utils.tk.AddPreferenceIntensityRelationDialog import AddPreferenceIntensityRelationDialog
from utils.type_aliases import LoggerFunc


class PreferenceIntensityRelationsFrame(tk.Frame):
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
        label = tk.Label(self, text='Preference intensity relations')
        label.grid(row=0, column=0, sticky=tk.NSEW)

        self.__update_relations()

        if self.__editable:
            button = tk.Button(
                self,
                text='Add preference intensity relation',
                command=lambda: self.__add_relation()
            )
            button.grid(row=2, column=0, sticky=tk.NSEW)

    def __update_relations(self):
        frame = ScrollableFrame(self)
        for index, intensity_relation in enumerate(self.__ror_dataset.intensityRelations):
            relation_name = None
            if intensity_relation.relation == relation.PREFERENCE:
                relation_name = 'preferred'
            elif intensity_relation.relation == relation.WEAK_PREFERENCE:
                relation_name = 'weakly preferred'
            elif intensity_relation.relation == relation.INDIFFERENCE:
                relation_name = 'indifferent'

            if relation_name is None:
                ttk.Label(
                    frame.frame,
                    text=f'{index+1}. INVALID PREFERENCE: {intensity_relation.relation}'
                ).pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
            else:
                label = '{} is {} to {} stronger than {} is {} to {}'.format(
                    intensity_relation.alternative_1,
                    relation_name,
                    intensity_relation.alternative_2,
                    intensity_relation.alternative_3,
                    relation_name,
                    intensity_relation.alternative_4
                )
                inside_frame = tk.Frame(frame.frame)
                inside_frame.pack(anchor=tk.NW, fill=tk.BOTH, expand=1)
                inside_frame.rowconfigure(0, weight=1)
                inside_frame.columnconfigure(0, weight=9)
                inside_frame.columnconfigure(1, weight=1)
                label = tk.Label(
                    inside_frame,
                    text=f'{index+1}. {label}',
                    wraplength=200,
                    justify="left",
                    bg="white",
                    foreground="black"
                ).grid(column=0, row=0, sticky=tk.W)
                if self.__editable:
                    tk.Button(
                        inside_frame,
                        text='Remove',
                        command=partial(self.remove_relation,
                                        intensity_relation)
                    ).grid(column=1, row=0)
        frame.grid(row=1, column=0, sticky=tk.NSEW)

    def __add_relation(self):
        if len(self.__ror_dataset.alternatives) < 4:
            # there must be at least 4 alternatives to creates preference intensity
            self.__logger('There must be at least 4 alternatives to creates preference intensity')
        else:
            AddPreferenceIntensityRelationDialog(
                self,
                self.__ror_dataset.alternatives,
                self.__on_added_relation,
                self.__ror_dataset.intensityRelations
            )

    def __on_added_relation(self, new_relation: PreferenceIntensityRelation):
        if new_relation is not None:
            self.__ror_dataset.add_intensity_relation(new_relation)
            self.__update_relations()

    def remove_relation(self, relation: PreferenceIntensityRelation):
        self.__ror_dataset.remove_intensity_relation(relation)
        self.__update_relations()
