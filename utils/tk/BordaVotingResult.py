from tkinter import ttk
import tkinter as tk
from ror.BordaTieResolver import BordaTieResolver
from ror.RORParameters import RORParameters
from ror.loader_utils import RORParameter
from utils.ScrollableFrame import ScrollableFrame
import pandas as pd

from utils.Table import Table


class BordaVotingResult(ttk.Frame):
    def __init__(self, root: ttk.Frame, tie_resolver: BordaTieResolver, ror_parameters: RORParameters):
        ttk.Frame.__init__(self, master=root)
        self.__tie_resolver: BordaTieResolver = tie_resolver
        self.__parameters: RORParameters = ror_parameters
        self.scroll: ScrollableFrame = None
        self.__init_gui()

    def __init_gui(self):
        ttk.Label(self, text='Borda voting results', font=('Arial', 18))\
            .pack(anchor=tk.NW, fill=tk.X)
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(anchor=tk.NW, expand=1, fill=tk.BOTH)
        frame = self.scroll.frame
        ttk.Label(frame, text='Votes per rank', font=('Arial', 16))\
            .pack(anchor=tk.NW, padx=5, pady=5, fill=tk.X, expand=1)
        table_with_data = Table(frame)
        table_with_data.pack(anchor=tk.NW, expand=1, fill=tk.BOTH, pady=5, padx=5)
        table_with_data.set_pandas_data(self.__tie_resolver.votes_per_rank)

        ttk.Label(frame, text='Mean votes per alternative', font=('Arial', 16))\
            .pack(anchor=tk.NW, padx=5, pady=5, expand=1, fill=tk.X)
        alternative_mean_position = [
            (alternative, mean_position)
            for alternative, mean_position
            in self.__tie_resolver.alternative_to_mean_position.items()
        ]
        sorted_alternative_mean_position = sorted(
            alternative_mean_position,
            key=lambda tuple: tuple[1],
            reverse=True
        )
        display_precision = self.__parameters.get_parameter(RORParameter.PRECISION)
        for idx, (alternative, mean_votes) in enumerate(sorted_alternative_mean_position):
            ttk.Label(frame, text=f'\t{idx+1}. Alternative: {alternative}, mean votes: {round(mean_votes, display_precision)}')\
                .pack(anchor=tk.NW, padx=5, pady=5)

