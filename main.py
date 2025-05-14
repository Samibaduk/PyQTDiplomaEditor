import io
import sys
import csv

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QFontDialog
from PyQt6.QtWidgets import QFileDialog, QLabel
from PyQt6.QtGui import QPixmap, QFont

from PIL import Image
from main_window_template import main_template

from dialogs import SaveDialog
from wacth_one_window import WatchOne

from add_functions import xlsx2csv, csv2sql


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMouseTracking(True)
        self.wids = []
        self.lbs = []

        self.sample_pixmap = QPixmap('./samples/base_s.jpg')
        image = Image.open('./samples/base_s.jpg')
        image.save('./samples/current_sample.png')
        self.sample = QLabel(self)
        self.sample.resize(572, 809)
        self.sample.move(500, 200)
        self.sample.setPixmap(self.sample_pixmap)
        self.selected_object = None
        self.is_selected = False

        self.icons_names = ['samples/icon_base_s.jpg', 'samples/icon_sample1.jpg', 'samples/icon_sample2.jpg',
                            'samples/icon_sample3.jpg', 'samples/icon_sample4.jpg', 'samples/icon_sample5.jpg']
        x = 602
        self.icons = []
        for icon in self.icons_names:
            self.icon_pixmap = QPixmap(icon)
            self.icon_sample = QLabel(self)
            self.icon_sample.resize(92, 130)
            self.icon_sample.move(x, 30)
            self.icon_sample.setPixmap(self.icon_pixmap)
            x += 102
            self.icons.append((self.icon_sample, icon.split('/')[0] + '/' + icon.split('/')[1][5:]))

        self.initUI()

    def initUI(self):
        f = io.StringIO(main_template)  # загружаем uic
        uic.loadUi(f, self)
        self.setWindowTitle('Diploma editor')
        self.file_input_button.clicked.connect(self.file_input)
        self.input_wids_button.clicked.connect(self.wid_input)
        self.create_button.setDisabled(True)
        self.create_button.clicked.connect(self.create_diplomas)
        self.import_sample.clicked.connect(self.add_sample_dialog)
        self.watch_one_button.clicked.connect(self.watch_one)
        self.label_name_btn.clicked.connect(self.add_label)
        self.add_picture_btn.clicked.connect(self.add_picture)
        self.watch_one_button.setDisabled(True)
        self.import_sample.resize(92, 130)
        self.import_sample.move(500, 30)

    def add_sample_dialog(self):
        file_sample = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')[0]
        self.add_sample(file_sample)

    def add_sample(self, name):
        image = Image.open(name)
        image.save('./samples/current_sample.png')
        self.sample_pixmap = QPixmap(name)
        self.sample.setPixmap(self.sample_pixmap)

    def file_input(self):
        try:
            fname = QFileDialog.getOpenFileName(
                self, 'Выбрать таблицу', '', 'Excel (*.xlsx *.xlsm *.xltx *.xltm)')[0]
            self.input_wids.clear()
            for w in self.wids:
                w.deleteLater()
            for lb in self.lns:
                lb.deleteLater()
            self.is_selected = False
            self.wids = []
            self.lbs = []
            self.file_name.setText(fname.split('/')[-1])
            self.file_name.adjustSize()

            xlsx2csv(fname)

            with open('./files/file.csv', encoding='utf-8', mode='r') as csv_file:
                self.data_size = 0
                data = csv.DictReader(csv_file, delimiter=';', quotechar='"')
                self.input_wids.addItems(next(data).keys())
                csv2sql(data)
                for elem in enumerate(data):
                    self.data_size = elem[0]
                self.data_size += 1
            self.create_button.setEnabled(True)
            self.watch_one_button.setEnabled(True)
        except Exception:
            pass

    def wid_input(self):
        self.wid = QLabel(self)
        self.wid.setText(self.input_wids.currentText())
        self.wid.move(200, 200)

        font, ok = QFontDialog.getFont(QFont("Times New Roman", 26))
        if ok:
            self.wid.setFont(font)
            self.wid.adjustSize()

        self.wid.show()
        self.wids.append(self.wid)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            for elem in self.wids:
                x = elem.pos().x()
                y = elem.pos().y()
                if x <= event.pos().x() <= x + elem.width() and y <= event.pos().y() <= y + elem.width():
                    self.selected_object = elem
                    self.is_selected = True
                    return

            for elem in self.lbs:
                x = elem.pos().x()
                y = elem.pos().y()
                if x <= event.pos().x() <= x + elem.width() and y <= event.pos().y() <= y + elem.width():
                    self.selected_object = elem
                    self.is_selected = True
                    return

            for icon in self.icons:
                elem = icon[0]
                x = elem.pos().x()
                y = elem.pos().y()
                if x <= event.pos().x() <= x + elem.width() and y <= event.pos().y() <= y + elem.width():
                    self.add_sample(icon[1])
                    return

    def mouseMoveEvent(self, event):
        if self.is_selected:
            self.selected_object.move(event.pos().x(), event.pos().y())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            if self.is_selected:
                self.selected_object.deleteLater()
                if self.selected_object in self.wids:
                    self.wids.remove(self.selected_object)
                if self.selected_object in self.lbs:
                    self.lbs.remove(self.selected_object)
                self.is_selected = False

        if event.key() == Qt.Key.Key_F:
            if self.is_selected:
                font, ok = QFontDialog.getFont(self.selected_object.font())
                if ok:
                    self.selected_object.setFont(font)
                    self.selected_object.adjustSize()
        return

    def create_diplomas(self):
        self.save_dialog = SaveDialog(self)
        self.save_dialog.show()

    def watch_one(self):
        self.watch_one_w = WatchOne(self)
        self.watch_one_w.show()

    def add_label(self):
        self.lb = QLabel(self)
        self.lb.setText(self.label_name.text())
        self.lb.move(200, 200)

        font, ok = QFontDialog.getFont(QFont("Times New Roman", 26))
        if ok:
            self.lb.setFont(font)
            self.lb.adjustSize()

        self.lb.show()
        self.lbs.append(self.lb)

    def add_picture(self):
        picture = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)')[0]
        picture_pixmap = QPixmap(picture)
        lb = QLabel(self)
        lb.move(200, 200)
        lb.setPixmap(picture_pixmap)
        lb.adjustSize()
        self.lbs.append(lb)
        lb.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
