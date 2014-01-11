from Tkinter import *
from ttk import *
from tkFileDialog import askopenfilename
import os
import tkFont

from recogn.rec import *


DIR = remakeDir("workDir/")
DICTIONARY = makeDir(DIR + "dict/")
RESULTS = makeDir(DIR + "results/")


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

        self.button_show = Button(self, text="Recognized words", command=self.show_rec, state=DISABLED)
        self.button_show.grid(row=4, column=1, sticky=W)

        self.button_close = Button(self, text="Close", command=sys.exit, width=10)
        self.button_close.grid(row=4, column=2, sticky=E)

        self.im_filename = ''
        self.text_filename = ''

        self.label_progress = Label(self, text="Progress: ")
        self.label_progress.grid(row=3, column=1, sticky=E)

        self.progressbar = Progressbar(self, orient="horizontal", length=214, mode="determinate")
        self.progressbar.grid(row=3, column=2)

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
            # try:
            input_image = Zone(readGrayIm(self.im_filename))
            glyph_dict = makeDictionary()
            for i, glyph in enumerate(glyph_dict):
                writeGrayIm(DICTIONARY + "glyph_%s.bmp" % i, glyph.im)

            words = words_from_line(input_image)

            self.progressbar["value"] = 0
            self.progressbar["maximum"] = len(words)
            text_file = open(self.text_filename, 'w')
            val = 0
            for index, w in enumerate(words):
                rec_word = recognize_word_brute(glyph_dict, w)
                # writeGrayIm(RESULTS + "%s_word.bmp" % index, w.extract())
                writeGrayIm(RESULTS + "%s_word_rec.bmp" % index,
                            unicode_to_image(
                                get_display(arabic_reshaper.reshape(rec_word))))
                text_file.write(rec_word.encode('utf-8') + ' ')
                val += 1
                self.progressbar["value"] = val
                self.update_idletasks()
            self.progressbar.stop()

            text_file.close()

            self.button_show.config(state=ACTIVE)

            progr_name = 'notepad.exe'
            osCommandString = ' '.join([progr_name, self.text_filename])
            os.system(osCommandString)

            # except:
            #     showerror("Open Source File", "Failed to read file\n'%s'" % self.im_filename)
            return

    def show_rec(self):
        progr_name = 'explorer'
        path = os.path.abspath(RESULTS)
        osCommandString = ' '.join([progr_name, path])
        os.system(osCommandString)


if __name__ == "__main__":
    MyFrame().mainloop()