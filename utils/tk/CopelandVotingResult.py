import tkinter as tk
from tkinter import ttk
from ror.CopelandVoter import CopelandVoter
from ror.RORParameters import RORParameter, RORParameters
import pandas as pd
from utils.Table import Table
from ror.Dataset import RORDataset
from ror.CopelandTieResolver import CopelandTieResolver

from utils.ScrollableFrame import ScrollableFrame

class CopelandVotingResult(ttk.Frame):
    def __init__(self, root: ttk.Frame, voter: CopelandVoter, dataset: RORDataset, parameters: RORParameters) -> None:
        ttk.Frame.__init__(self, root)
        self.__voter: CopelandVoter = voter
        self.__dataset: RORDataset = dataset
        self.__parameters: RORParameters = parameters
        self.__init_gui()

    def __init_gui(self):
        ttk.Label(self, text='Copeland voting results', font=('Arial', 18))\
            .pack(anchor=tk.NW, fill=tk.X)
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(anchor=tk.NW, expand=1, fill=tk.BOTH)
        frame = self.scroll.frame
        ttk.Label(frame, text='Alternative vs alternative votes', font=('Arial', 16))\
            .pack(anchor=tk.NW, padx=5, pady=5, fill=tk.X, expand=1)
        columns = [*self.__dataset.alternatives]
        columns.insert(0, 'id')
        display_precision = self.__parameters.get_parameter(RORParameter.PRECISION)
        voting_matrix = pd.DataFrame(
            data=self.__voter.voting_matrix,
            index=self.__dataset.alternatives,
            columns=self.__dataset.alternatives,
        )
        table_with_data = Table(frame)
        table_with_data.pack(anchor=tk.NW, expand=1, fill=tk.BOTH, pady=5, padx=5)
        table_with_data.set_pandas_data(voting_matrix, headers=columns, display_precision=display_precision)

        legend='''Voting rule:
If alternatives are equal in rank then both get 0.5 vote
Better alternative in rank gets 1 vote
Worst alternative gets nothing
No vote for same alternative
        '''
        ttk.Label(frame, text=legend, wraplength=400).pack(anchor=tk.NW, expand=1, fill=tk.X)

        ttk.Label(frame, text='Mean votes per alternative', font=('Arial', 16))\
            .pack(anchor=tk.NW, padx=5, pady=5, expand=1, fill=tk.X)
        voting_sum = sorted(
            self.__voter.voting_sum,
            key=lambda tuple: tuple[1],
            reverse=True
        )
        for idx, (alternative, mean_votes) in enumerate(voting_sum):
            ttk.Label(frame, text=f'\t{idx+1}. Alternative: {alternative}, voting mean: {round(mean_votes, display_precision)}')\
                .pack(anchor=tk.NW, padx=5, pady=5)

