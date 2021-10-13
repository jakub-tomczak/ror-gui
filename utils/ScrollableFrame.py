import tkinter as tk
from tkinter import ttk


class ScrollableFrame(tk.Frame):
    def __init__(self, root: tk.Tk):
        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y)
        self.scrollbar = tk.Scrollbar(self, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill='y')
        self.canvas.configure(yscrollcommand = self.scrollbar.set)

        # update scrollregion after starting 'mainloop'
        # when all widgets are in canvas
        self.canvas.bind('<Configure>', self.update_scrollregion)

        # put frame in canvas
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0,0), window=self.frame, anchor='nw')

        self.scrollbar = ttk.Scrollbar()

    def force_scroll_update(self):
        # update canvas frame to refresh its size
        self.frame.update()
        # update scrollregion
        self.update_scrollregion(None) 

    def update_scrollregion(self, event):
        # update scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def update_frame(self):
        self.frame.update()