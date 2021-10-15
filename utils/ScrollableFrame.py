import tkinter as tk
from tkinter import ttk


class ScrollableFrame(tk.Frame):
    def __init__(self, root: tk.Tk, canvas_width: float = -1):
        tk.Frame.__init__(self, root)
        if canvas_width < 0:
            self.canvas = tk.Canvas(self, bd=0, highlightthickness=0)
        else:
            self.canvas = tk.Canvas(self, bd=0, highlightthickness=0, width=canvas_width)
        self.canvas.pack(side=tk.LEFT, fill=tk.Y)
        self.scrollbar = tk.Scrollbar(self, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand = self.scrollbar.set)
        # update scrollregion after starting 'mainloop'
        # when all widgets are in canvas
        self.canvas.bind('<Configure>', self.update_scrollregion)

        # put frame in canvas
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((10, 10), window=self.frame, anchor='nw')

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