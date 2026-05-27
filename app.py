import json
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import builder


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(u'Jumbo Block Builder App')
        self.root.geometry('800x600')
        self.faces = []
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def show(self):
        self.put_face_panel()
        block_entry = self.put_block_entry()
        self.put_save_btn(block_entry)

        self.root.mainloop()

    def put_face_panel(self):
        panel = tk.Frame(self.root)
        panel.grid()
        self.put_face_btn(panel, 'N', 0, 1)
        self.put_face_btn(panel, 'W', 1, 0)
        self.put_face_btn(panel, 'B', 1, 1)
        self.put_face_btn(panel, 'E', 1, 2)
        self.put_face_btn(panel, 'S', 2, 1)
        self.put_face_btn(panel, 'T', 3, 1)

    def put_face_btn(self, panel, d: str, row: int, col: int):
        frame = tk.Frame(panel, width=80, height=80)
        frame.pack_propagate(False)
        frame.grid(row=row, column=col)

        btn = tk.Button(frame, text=d)
        face = {'button': btn, 'direction': d}
        self.faces.append(face)
        btn.config(command= lambda: self.open_modal(face))
        btn.pack(fill='both', expand=True)

    def open_modal(self, face):
        modal = self.__Modal(self, face)
        modal.show()

    def put_save_btn(self, block_entry):
        btn = tk.Button(self.root, text='SAVE', command= lambda: self.save(block_entry))
        btn.grid(sticky='ew')

    def save(self, block_entry):
        nbt_path = filedialog.asksaveasfilename(filetypes=[('NBT File', '*.nbt')])
        p = Path(nbt_path).relative_to(Path.cwd())
        file_name = p.stem
        inside = block_entry.get()
        inside = 'minecraft:structure_void' if inside == '' else f'minecraft:{inside}'
        model_path = f'{p.parent}\\{file_name}.json'
        face_arr = [{'texture': f['paint'][1], 'direction': f['direction']} for f in self.faces]
        builder.mk_jumbo_model(face_arr, model_path, inside)
        builder.model2nbt(model_path)

        self.root.destroy()
        App().show()

    def put_block_entry(self):
        panel = tk.Frame(self.root)
        panel.grid()
        label = tk.Label(panel, text='INSIDE BLOCK', font=('Arial', 12))
        label.grid(row=0, column=0)
        entry = tk.Entry(panel, width=30)
        entry.grid(row=1, column=0)
        return entry

    class __Modal:
        def __init__(self, parent: App, face: dict):
            self.__faces = parent.faces
            self.__face = face
            self.__color_set = {
                'red', 'blue', 'green', 'yellow', 'orange', 'purple'
            }
            self.__palette = []

            for f in parent.faces:
                if 'paint' not in f.keys():
                    continue
                paint = f['paint']
                self.__color_set.discard(paint[0])
                if paint not in self.__palette:
                    self.__palette.append(paint)

            self.__root = parent.root
            self.__modal = tk.Toplevel(self.__root)
            self.__modal.geometry('800x600')
            self.__modal.grid_columnconfigure(0, weight=1)
            self.__modal.grab_set()
            self.__modal.focus_set()

        def show(self):
            self.put_option_panel()
            self.put_template_panel()

        def put_option_panel(self):
            panel = tk.Frame(self.__modal)
            panel.grid_columnconfigure(0, weight=1)
            panel.grid(sticky='ew')

            label = tk.Label(panel, text='PALETTE', font=('Arial', 12))
            label.grid()

            for i in range(len(self.__palette)):
                paint = self.__palette[i]
                self.put_option(panel, paint, i)

            if len(self.__palette) < 6:
                self.put_option(panel, ('white', 'select new texture'), 6, True)

        def put_option(self, panel, paint: tuple[str, str], row: int, new: bool = False):
            outer = tk.Frame(panel, width=800)
            label = tk.Label(outer, text=paint[1], font=('Arial', 12))
            label.grid(row=row, column=1)
            outer.grid(sticky='ew')

            frame = tk.Frame(outer, width=30, height=30)
            frame.pack_propagate(False)
            frame.grid(row=row, column=0)
            btn = tk.Button(frame, bg=paint[0])

            if new:
                btn.config(command= lambda: self.open_folder())
            else:
                btn.config(command= lambda: self.on_selected(paint))

            btn.pack(fill='both', expand=True)

        def open_folder(self):
            file_path = filedialog.askopenfilename(filetypes=[('Jumbo Texture File', '*.json')])
            color = self.__color_set.pop()
            paint = (color, file_path)
            self.on_selected(paint)

        def on_selected(self, paint: tuple[str, str]):
            self.__face['paint'] = paint

            if self.__face in self.__faces:
                self.__faces.remove(self.__face)

            self.__faces.append(self.__face)

            self.__modal.grab_release()
            btn = self.__face['button']
            btn.config(bg=paint[0])
            btn.update()
            self.__modal.destroy()

        def put_template_panel(self):
            panel = tk.Frame(self.__modal)
            panel.grid_columnconfigure(0, weight=1)
            panel.grid(sticky='ew')
            label = tk.Label(panel, text='AVAILABLE TEMPLATES', font=('Arial', 12))
            label.grid()

            tmp_dir = './input/model_templates'
            files = os.listdir(tmp_dir)
            for i in range(len(files)):
                file_name = files[i]
                template = json.load(open(f'{tmp_dir}/{file_name}', 'r', encoding='utf-8'))
                max_paint = max([f['texture'] for f in template['faces']])
                if len(self.__palette) >= max_paint + 1:
                    self.put_template_btn(panel, file_name, template, i)

        def put_template_btn(self, panel, file_name: str, template, row: int):
            button = tk.Button(panel, text=file_name, command= lambda: self.apply_template(template))
            button.grid(sticky='ew', row=row)

        def apply_template(self, template):
            faces = template['faces']
            for i in range(len(faces)):
                f = faces[i]
                tx_i = f['texture']
                paint = self.__palette[tx_i]
                self.__faces[i]['paint'] = paint
                self.__faces[i]['direction'] = f['direction']

                btn = self.__faces[i]['button']
                btn.config(bg=paint[0])
                btn.update()

            self.__modal.destroy()
