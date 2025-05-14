import io
import sqlite3

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap

from PIL import Image, ImageDraw, ImageFont

from watch_one_template import watch_one_template
from add_functions import dict_factory

from dialogs import SaveOneDialog


class WatchOne(QWidget):
    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        f = io.StringIO(watch_one_template)
        uic.loadUi(f, self)

        self.con = sqlite3.connect("./files/db.sqlite")
        self.cur = self.con.cursor()
        self.heads = self.cur.execute("""PRAGMA table_info("Data")""").fetchall()
        self.heads = [i[1] for i in self.heads]

        self.wids.addItems(self.heads)
        self.wids.currentTextChanged.connect(self.find_variants)
        self.watch_btn.clicked.connect(self.find_variants)
        self.lineEdit.textChanged.connect(self.find_variants)
        self.result.itemClicked.connect(self.change_example)

        self.save_one_btn.clicked.connect(self.save_one)

        self.sample_pixmap = QPixmap('./samples/base_s.jpg')
        image = Image.open('./samples/current_sample.png')
        self.sample = QLabel(self)
        self.sample.resize(572, 809)
        self.sample.move(600, 100)
        self.sample.setPixmap(self.sample_pixmap)
        self.selected_object = None
        self.is_selected = False

    def find_variants(self):
        self.result.clear()
        self.con.row_factory = dict_factory
        self.vars = self.con.cursor().execute(f"""SELECT * FROM Data 
        WHERE [{self.wids.currentText()}] LIKE '%{self.lineEdit.text()}%'""").fetchall()

        for elem in self.vars:
            self.result.addItem(' '.join(elem.values()))

    def change_example(self):
        elem = self.vars[self.result.currentRow()]
        sample_image = Image.open("./samples/current_sample.png")
        sample_drawer = ImageDraw.Draw(sample_image)
        for lb in self.mainwindow.lbs:
            q_f = lb.fontInfo()
            font = ImageFont.truetype(f"{q_f.family().split()[0].lower()}.ttf", q_f.pixelSize())
            sample_drawer.text((lb.pos().x() - self.mainwindow.sample.pos().x(),
                                lb.pos().y() - self.mainwindow.sample.pos().y()), lb.text(), font=font,
                               fill='black')
        image = sample_image.copy()
        drawer = ImageDraw.Draw(image)
        for w in self.mainwindow.wids:
            q_f = w.fontInfo()
            font = ImageFont.truetype(f"{q_f.family().split()[0].lower()}.ttf", q_f.pixelSize())
            drawer.text((w.pos().x() - self.mainwindow.sample.pos().x(),
                         w.pos().y() - self.mainwindow.sample.pos().y()),
                        f"{elem[w.text()]}", font=font, fill='black')
        image.save('./pictures/current_example.jpg')
        self.sample_pixmap = QPixmap('./pictures/current_example.jpg')
        self.sample.setPixmap(self.sample_pixmap)

    def save_one(self):
        self.save_one_dialog = SaveOneDialog()
        self.save_one_dialog.show()
