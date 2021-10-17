import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, root: tk.Tk, canvas_width: float = -1):
        tk.Frame.__init__(self, root, width=canvas_width)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0) #, scrollregion=(0,0,500,800)
        # put frame in canvas
        self.frame = tk.Frame(self.canvas, background="grey")
        self.scrollbar = tk.Scrollbar(self, orient='vertical', command=self.__move) # self.__move
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas.create_window((0,0), window=self.frame, anchor=tk.NW)
        # update scrollregion after starting 'mainloop'
        # when all widgets are in canvas
        self.frame.bind("<Configure>", self.update_scrollregion)

    def __move(self, *args):
        # print(*args)
        # print('canvas with id', id(self.canvas))
        self.canvas.yview(*args)

    def force_scroll_update(self):
        # update canvas frame to refresh its size
        # self.frame.update()
        # update scrollregion
        pass
        # self.update_scrollregion(None)

    def update_scrollregion(self, event):
        # update scrollregion
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
