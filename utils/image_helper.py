from math import floor
import tkinter as tk
import logging
import PIL.Image
import PIL.ImageTk

class ImageDisplay(tk.Frame):
    # for rescaling purposes
    IMAGE_WIDTH=300
    IMAGE_HEIGHT=700

    def __init__(self, root: tk.Tk, image_path: str, image_name: str):
        tk.Frame.__init__(self, master=root)
        self.__image_path: str = image_path
        self.__image: PIL.ImageTk.PhotoImage = None
        self.__image_name = image_name

        self.__display_image()

    def __display_image(self):
        im = PIL.Image.open(self.__image_path)
        self.__image = PIL.ImageTk.PhotoImage(im)
        
        width = self.__image.width()
        height = self.__image.height()

        rescaling_coeff = ImageDisplay.IMAGE_WIDTH / width if width > height else ImageDisplay.IMAGE_HEIGHT / height
        target_width = width * rescaling_coeff
        target_height = height * rescaling_coeff
        logging.debug(f'rescaling coeff {rescaling_coeff}, oryginal: {width}x{height}, res {width/height}, resized: {target_width}x{target_height}, res {target_width/target_height}')
        
        # recreate image
        new_image = im.resize((floor(target_width), floor(target_height)))
        self.__image = PIL.ImageTk.PhotoImage(new_image)
        
        # add image name and path above the image
        tk.Label(self, text=f'Name: {self.__image_name}', font=("Arial", 14)).pack(anchor=tk.NW, fill=tk.X)
        tk.Label(self, text=f'Path: {self.__image_path}', font=("Arial", 8)).pack(anchor=tk.NW, fill=tk.X)

        cv = tk.Canvas(master=self)
        cv.pack(side='top', fill=tk.BOTH, expand=1)
        cv.create_image(0, 0, image=self.__image, anchor='nw')


    def change_image(self, image_path: str):
        self.__image_path = image_path
        self.__display_image()
