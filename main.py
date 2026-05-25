# This is a sample Python script.
import json
import numpy as np
import tkinter as tk

import nbtlib
from nbtlib import Compound, List, String, Int

from converter import Converter

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    #mk_jumbo_model('oak_log',
    #               ['oak_log_top', 'oak_log', 'oak_log', 'oak_log_top', 'oak_log', 'oak_log'],
    #               [0, 1, 2, 3, 4, 5])
    root = tk.Tk()
    root.title(u"Software Title")
    root.geometry("800x600")

    place_face(root, 'N', 0, 1)
    place_face(root, 'W', 1, 0)
    place_face(root, 'B', 1, 1)
    place_face(root, 'E', 1, 2)
    place_face(root, 'S', 2, 1)
    place_face(root, 'T', 3, 1)

    root.mainloop()

def place_face(root, d: str, row: int, col: int):
    frame = tk.Frame(root, width=60, height=60)
    frame.pack_propagate(False)
    frame.grid(row=row, column=col)
    button = tk.Button(frame, text=d)
    button.bind("<Button-1>", lambda e: open_modal(root))
    button.pack(fill='both', expand=True)

def open_modal(root):
    modal = tk.Toplevel(root)
    modal.title("モーダル")
    modal.geometry("300x200")

    modal.grab_set()
    modal.focus_set()

    root.wait_window(modal)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()