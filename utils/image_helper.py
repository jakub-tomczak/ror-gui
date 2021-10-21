from math import floor
import tkinter as tk
from tkinter import ttk
import logging
from typing import Callable
import PIL.Image
import PIL.ImageTk
from utils.ScrollableFrame import ScrollableFrame

from utils.Severity import Severity

class ImageDisplay(ttk.Frame):
    # for rescaling purposes
    IMAGE_WIDTH=250
    IMAGE_HEIGHT=600
    CLICK_TO_COPY_LABEL = '(click to copy)'

    def __init__(self, logger: Callable[[str, Severity], None], window_object: tk.Tk, root: tk.Tk, image_path: str, image_name: str):
        ttk.Frame.__init__(self, master=root)
        self.__logger = logger
        self.__window_object: tk.Tk = window_object
        self.__image_path: str = image_path
        self.__image: PIL.ImageTk.PhotoImage = None
        self.__image_name = image_name
        self.__scroll_bar: ScrollableFrame = ScrollableFrame(self, ImageDisplay.IMAGE_WIDTH+30)
        # print(image_name, 'created scrollbar', id(self.__scroll_bar))
        self.__display_image()

    @property
    def image_name(self) -> str:
        return self.__image_name

    def __copy_text_to_clipboard(self, event):
        # get field value from event, but remove line copy text label and return at end
        to_strip_end = -(len(ImageDisplay.CLICK_TO_COPY_LABEL)+1)
        to_strip_start = 6
        field_value = event.widget.cget("text")[to_strip_start:to_strip_end]
        self.__window_object.clipboard_clear()  # clear clipboard contents
        self.__window_object.clipboard_append(field_value)  # append new value to clipbaord
        self.__logger(f'Copied "{field_value}" to clipboard')


    def __display_image(self):
        im = PIL.Image.open(self.__image_path)
        self.__image = PIL.ImageTk.PhotoImage(im)
        
        width = self.__image.width()
        height = self.__image.height()

        # resize so all images have the same width
        rescaling_coeff = ImageDisplay.IMAGE_WIDTH / width # if width > height else ImageDisplay.IMAGE_HEIGHT / height
        target_width = width * rescaling_coeff
        target_height = height * rescaling_coeff
        logging.debug(f'rescaling coeff {rescaling_coeff}, oryginal: {width}x{height}, res {width/height}, resized: {target_width}x{target_height}, res {target_width/target_height}')
        
        # recreate image
        new_image = im.resize((floor(target_width), floor(target_height)))
        self.__image = PIL.ImageTk.PhotoImage(new_image)
        
        # add image name and path above the image
        ttk.Label(self, text=f'Name: {self.__image_name}', font=("Arial", 14)).pack(anchor=tk.NW, fill=tk.X)
        image_path_label = ttk.Label(self, text=f'Path: {self.__image_path} (click to copy)', font=("Arial", 10))
        image_path_label.pack(anchor=tk.NW, fill=tk.X)
        image_path_label.bind("<Button-1>", self.__copy_text_to_clipboard)
        # pack scrollbar after labels to have labels above canvas
        self.__scroll_bar.pack(side='top', fill=tk.BOTH, expand=1)

        cv = tk.Canvas(master=self.__scroll_bar.frame, width=target_width + 20, height=target_height + 100)
        cv.pack(anchor='center', side='top', fill=tk.BOTH, expand=1)
        cv.create_image(0, 0, image=self.__image, anchor='nw')


    def change_image(self, image_path: str):
        self.__image_path = image_path
        self.__display_image()
