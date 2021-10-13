from math import floor
import tkinter as tk
import logging
import PIL.Image
import PIL.ImageTk

class ImageDisplay(tk.Toplevel):
    # for rescaling purposes
    WINDOW_WIDTH=600
    WINDOW_HEIGHT=1000 

    def __init__(self, root: tk.Tk, image_path: str, image_name: str):
        tk.Toplevel.__init__(self, master=root)
        self.__image_path: str = image_path
        self.__image: PIL.ImageTk.PhotoImage = None
        self.__image_name = image_name

        self.__display_image()

    def __display_image(self):
        im = PIL.Image.open(self.__image_path)
        self.__image = PIL.ImageTk.PhotoImage(im)
        
        width = self.__image.width()
        height = self.__image.height()

        rescaling_coeff = ImageDisplay.WINDOW_WIDTH / width if width > height else ImageDisplay.WINDOW_HEIGHT / height
        target_width = width * rescaling_coeff
        target_height = height * rescaling_coeff
        logging.debug(f'rescaling coeff {rescaling_coeff}, oryginal: {width}x{height}, res {width/height}, resized: {target_width}x{target_height}, res {target_width/target_height}')
        
        # recreate image
        new_image = im.resize((floor(target_width), floor(target_height)))
        self.__image = PIL.ImageTk.PhotoImage(new_image)
        # resize window to match width
        window_width = min(ImageDisplay.WINDOW_WIDTH, floor(target_width))
        self.geometry(f'{window_width}x{ImageDisplay.WINDOW_HEIGHT}')

        # set window title
        self.title(self.__image_name)
        
        cv = tk.Canvas(master=self)
        cv.pack(side='top', fill=tk.BOTH, expand=1)
        cv.create_image(0, 0, image=self.__image, anchor='nw')

    
    def change_image(self, image_path: str):
        self.__image_path = image_path
        self.__display_image()
