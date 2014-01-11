from Tkinter import *
from tkFileDialog import askopenfilename
from tkMessageBox import showerror
from ttk import Combobox
import os
from os import listdir
from os.path import isfile, join
import tkFont

import rec
from rec import *


_RESOURCES_DIR = "../resources/"
_FONTS_DIR = _RESOURCES_DIR + "fonts/"


class Fontier(object):
    def __init__(self, path):
        self.path = path

    def _file_names_in_dir(self):
        return [f for f in listdir(self.path) if isfile(join(self.path, f))]

    def fonts_names(self):
        return [fn[:-4] for fn in self._file_names_in_dir()]

    def font_files(self):
        return [join(self.path, f) for f in self._file_names_in_dir()]


class MyFrame(Frame):
    def __init__(self):
        Frame.__init__(self)
        self.master.title("Arabic text recognizer")
        self.master.rowconfigure(5, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W + E + N + S)

        font = tkFont.Font(family='Times New Romans', size=9)

        self.label_input = Label(self, text="Image: ")
        self.label_input.grid(row=1, column=0)

        self.button_open = Button(self, text="Browse", command=self.load_file, width=10)
        self.button_open.grid(row=1, column=1, sticky=W)

        self.text_input = Text(self, height=1, width=30, font=font)
        self.text_input.grid(row=1, column=2)

        self.label_output = Label(self, text="Text: ")
        self.label_output.grid(row=2, column=0)

        self.button_save = Button(self, text="Browse", command=self.save_file, width=10)
        self.button_save.grid(row=2, column=1, sticky=W)

        self.text_output = Text(self, height=1, width=30, font=font)
        self.text_output.grid(row=2, column=2)

        self.button_start = Button(self, text="Start", command=self.process, width=10)
        self.button_start.grid(row=4, column=0, sticky=W)

        self.label_done = Label(self)
        self.label_done.grid(row=4, column=1)

        self.button_close = Button(self, text="Close", command=sys.exit, width=10)
        self.button_close.grid(row=4, column=2, sticky=W)

        self.label_threshold = Label(self, text="Threshold: ")
        self.label_threshold.grid(row=3, column=0, sticky=W)

        self.input_threshold = Entry(self)
        self.input_threshold.delete(0, END)
        self.input_threshold.insert(0, "0.75")
        self.input_threshold.grid(row=3, column=1, sticky=W)

        self.label_threshold = Label(self, text="Font: ")
        self.label_threshold.grid(row=3, column=2, sticky=W)

        self.fontier = Fontier(_FONTS_DIR)
        self.font_combobox = Combobox(self,
                                      height=min(5, len(self.fontier.fonts_names())),
                                      values=self.fontier.fonts_names())
        self.font_combobox.set(self.fontier.fonts_names()[0])
        self.font_combobox.grid(row=3, column=3, sticky=W)

        self.im_filename = ''
        self.text_filename = ''

    def load_file(self):
        fname = askopenfilename(filetypes=(("Text", "*.bmp"), ("All files", "*.*")))
        if fname:
            self.im_filename = fname
            self.text_input.insert(END, fname)
            return

    def save_file(self):
        fname = askopenfilename(filetypes=(("Text", "*.txt"), ("All files", "*.*")))
        if fname:
            self.text_filename = fname
            self.text_output.insert(END, fname)
            return

    def process(self):
        if self.im_filename:
            try:
                self.label_done.config(text='In progress...')
                DIR = remakeDir("workDir/")
                DICTIONARY = makeDir(DIR + "dict/")
                RESULTS = makeDir(DIR + "results/")

                font_file = self.fontier.font_files()[self.fontier.fonts_names().index(self.font_combobox.get())]
                rec.FONT = ImageFont.truetype(font_file, SIZE)
                rec.THRESHOLD = float(self.input_threshold.get())

                input_image = Zone(readGrayIm(self.im_filename))
                glyph_dict = makeDictionary()
                for i, glyph in enumerate(glyph_dict):
                    writeGrayIm(DICTIONARY + "glyph_%s.bmp" % i, glyph.im)

                words = words_from_line(input_image)

                for index, w in enumerate(words):
                    writeGrayIm(RESULTS + "%s_word.bmp" % index, w.extract())
                    writeGrayIm(RESULTS + "%s_word_rec.bmp" % index,
                                unicode_to_image(
                                    get_display(arabic_reshaper.reshape(recognize_word_brute(glyph_dict, w)))))

                self.label_done.config(text='Done!')

                progr_name = 'notepad.exe'
                osCommandString = ' '.join([progr_name, self.text_filename])
                os.system(osCommandString)

            except ArithmeticError as e:
                print e
                showerror("Open Source File", "Failed to read file\n'%s'.\n Exception: %s" % (self.im_filename, e))
            return


if __name__ == "__main__":
    MyFrame().mainloop()
