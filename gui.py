from Tkinter import *
from ttk import *
from tkFileDialog import askopenfilename
from tkMessageBox import showerror
from ttk import Combobox, Progressbar
import os
from os import listdir
from os.path import isfile, join
import tkFont
import webbrowser

from bidi.algorithm import get_display

from recogn.rec import *
import recogn.rec as rec
from decompose.util import remakeDir, makeDir, writeGrayIm


_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_DIR = remakeDir(join(_CURRENT_DIR, "workDir/"))
_DICTIONARY = makeDir(_DIR + "dict/")
_RESULTS = makeDir(_DIR + "results/")
_RESOURCES_DIR = join(_CURRENT_DIR, "resources/")
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
        self.master.rowconfigure(11, weight=1)
        self.master.columnconfigure(5, weight=1)
        self.grid(sticky=W + E + N + S)

        font = tkFont.Font(family='Times New Romans', size=9)

        # ---------Input image and output file ----------
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

        # --------- Start, Show Results and Close buttons ----------
        self.button_start = Button(self, text="Start", command=self.process, width=10)
        self.button_start.grid(row=11, column=0, sticky=W)

        self.button_show = Button(self, text="Recognized words", command=self.show_rec, state=DISABLED)
        self.button_show.grid(row=11, column=1, sticky=E)

        self.button_close = Button(self, text="Close", command=sys.exit, width=10)
        self.button_close.grid(row=11, column=2, sticky=E)

        # ------------------- Options in Frame -----------------------

        self.label_output = Label(self, text="Options: ")
        self.label_output.grid(row=5, column=0)

        self.label_threshold = Label(self, text="Threshold: ")
        self.label_threshold.grid(row=6, column=1, sticky=W)

        self.input_threshold = Entry(self, width=15)
        self.input_threshold.delete(0, END)
        self.input_threshold.insert(0, "0.75")
        self.input_threshold.grid(row=6, column=2, sticky=W)

        self.label_threshold = Label(self, text="Font: ")
        self.label_threshold.grid(row=7, column=1, sticky=W)

        self.fontier = Fontier(_FONTS_DIR)
        self.font_combobox = Combobox(self,
                                      height=min(5, len(self.fontier.fonts_names())),
                                      values=self.fontier.fonts_names(), width=15)
        self.font_combobox.set(self.fontier.fonts_names()[0])
        self.font_combobox.grid(row=7, column=2, sticky=W)

        self.im_filename = ''
        self.text_filename = ''

        self.label_progress = Label(self, text="Progress: ")
        self.label_progress.grid(row=9, column=1, sticky=E)

        self.progressbar = Progressbar(self, orient="horizontal", length=214, mode="determinate")
        self.progressbar.grid(row=9, column=2)

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

                self.progressbar["value"] = 0
                self.progressbar["maximum"] = len(words)
                text_file = open(self.text_filename, 'w')
                for index, w in enumerate(words):
                    rec_word = recognize_word_brute(glyph_dict, w)
                    writeGrayIm(RESULTS + "%s_word_rec.bmp" % index,
                                unicode_to_image(
                                    get_display(arabic_reshaper.reshape(rec_word))))

                    text_file.write(rec_word.encode('utf-8') + ' ')
                    self.progressbar["value"] = index + 1
                    self.update_idletasks()

                text_file.close()
                self.button_show.config(state=ACTIVE)

                progr_name = 'notepad.exe'
                osCommandString = ' '.join([progr_name, self.text_filename])
                os.system(osCommandString)

            except:
                showerror("Open Source File", "Failed to read file\n'%s'" % self.im_filename)
            return

    def show_rec(self):
        webbrowser.open(_RESULTS)
        # progr_name = 'explorer'
        # path = os.path.abspath(_RESULTS)
        # osCommandString = ' '.join([progr_name, path])
        # os.system(osCommandString)


if __name__ == "__main__":
    MyFrame().mainloop()
