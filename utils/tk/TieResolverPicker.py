from tkinter import StringVar, ttk
import tkinter as tk
from typing import Callable, Dict
from ror.AbstractTieResolver import AbstractTieResolver


class TieResolverPicker(ttk.Frame):
    def __init__(
        self,
        root: ttk.Frame,
        tie_resolvers: Dict[str, AbstractTieResolver],
        initial_resolver_name: str,
        on_resolver_changed: Callable[[str], None] = None
    ) -> None:
        super().__init__(master = root)
        self.__picker: ttk.Combobox = None
        self.__tie_resolvers = tie_resolvers
        self.__on_resolver_changed = on_resolver_changed
        self.__initial_resolver = initial_resolver_name
        assert initial_resolver_name in tie_resolvers,\
            'Initial resolver name is not valid - it does not exist in tie_resolvers list.'
        self.__picked_resolver = StringVar()
        self.__resolver_description = StringVar()
        self.__description_text_widget: tk.Text = None
        self.__picked_resolver.trace('w', lambda *_: self.__on_picker_changed())
        self.__init_gui()

    def __init_gui(self):
        ttk.Label(self, text='Pick tie resolver', font=('Arial', 15)).\
            pack(anchor=tk.NW, fill=tk.X, expand=1)
        ttk.Label(
            self,
            text='Resolver is used to separate alternatives that were put at same position in the final rank. With resolver there will be no ties in the final rank.', 
            foreground='grey40'
        ).pack(anchor=tk.NW, fill=tk.X, expand=1)
        self.__picker = ttk.Combobox(self, textvariable=self.__picked_resolver, state='readonly')
        self.__update_tie_resolvers()
        self.__picker.pack(anchor=tk.NW, fill=tk.X, expand=1)
        ttk.Label(self, text='Resolver description').pack(anchor=tk.NW, fill=tk.X, expand=1)
        description_frame = ttk.Frame(self)
        description_frame.pack(anchor=tk.NW, fill=tk.X, expand=1)
        # uncomment to use text widget instead of label
        # self.__description_text_widget = tk.Text(description_frame, height=5, width=100)
        # scroll_bar = tk.Scrollbar(description_frame)
        # scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        # scroll_bar.configure(command=self.__description_text_widget.yview)
        # self.__description_text_widget.configure(yscrollcommand=scroll_bar.set)
        # self.__description_text_widget.pack(side=tk.LEFT)
        # self.__description_text_widget.configure(state='disabled')

        ttk.Label(self, textvariable=self.__resolver_description).\
            pack(anchor=tk.NW, fill=tk.X, expand=1)
        self.__picked_resolver.set(self.__initial_resolver)

    def __update_tie_resolvers(self):
        self.__picker['values'] = [resolver.name for resolver in self.__tie_resolvers.values()]

    def __on_picker_changed(self):
        # uncomment to use text widget instead of label
        # self.__description_text_widget.configure(state='normal')
        # self.__description_text_widget.delete(1.0, tk.END)
        # self.__description_text_widget.insert(1.0, desc)
        # self.__description_text_widget.configure(state='disabled')

        desc = self.__tie_resolvers[self.tie_resolver_name].help()
        self.__resolver_description.set(desc)
        if self.__on_resolver_changed is not None:
            self.__on_resolver_changed(self.__picked_resolver.get())

    @property
    def tie_resolver_name(self) -> str:
        return self.__picker.get()