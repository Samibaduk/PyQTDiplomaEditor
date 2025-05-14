import io
import csv

import os.path

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtWidgets import QFileDialog, QProgressBar, QLabel

from PIL import Image, ImageDraw, ImageFont

from save_dialog_template import save_dialog_template
from save_one_template import save_one_template


class SaveDialog(QDialog):
    def __init__(self, mainwindow):
        self.data_size = mainwindow.data_size
        self.mainwindow = mainwindow
        super().__init__()
        self.setWindowTitle('Сохрнаить димпломы')
        self.initUI()

    def initUI(self):
        f = io.StringIO(save_dialog_template)
        uic.loadUi(f, self)
        self.radio_pdf.setChecked(True)
        self.accept_button_box.accepted.connect(self.create_diplomas)
        self.accept_button_box.rejected.connect(self.close_dialog)
        self.choose_folder_btn.clicked.connect(self.choose_folder)

    def create_diplomas(self):
        self.way = self.radio_folder.isChecked()
        self.directory = self.folder_name.text()
        self.f_name = self.file_name.text()
        if os.path.exists(self.directory):
            with open('./files/file.csv', encoding='utf-8', mode='r') as csv_file:
                data = csv.DictReader(csv_file, delimiter=';', quotechar='"')
                diplomas = []

                self.progress = ProgressBarDialog(self.data_size)
                self.progress.show()
                self.hide()

                sample_image = Image.open("./samples/current_sample.png")
                sample_drawer = ImageDraw.Draw(sample_image)
                for lb in self.mainwindow.lbs:
                    q_f = lb.fontInfo()
                    font = ImageFont.truetype(f"{q_f.family().split()[0].lower()}.ttf", q_f.pixelSize())
                    sample_drawer.text((lb.pos().x() - self.mainwindow.sample.pos().x(),
                                        lb.pos().y() - self.mainwindow.sample.pos().y()), lb.text(), font=font,
                                       fill='black')

                for pic in enumerate(data):
                    image = sample_image.copy()
                    drawer = ImageDraw.Draw(image)
                    elem = pic[1]
                    i = pic[0] + 1
                    self.progress.pb.setValue(self.progress.pb.value() + 1)

                    for w in self.mainwindow.wids:
                        q_f = w.fontInfo()
                        font = ImageFont.truetype(f"{q_f.family().split()[0].lower()}.ttf", q_f.pixelSize())
                        drawer.text((w.pos().x() - self.mainwindow.sample.pos().x(),
                                     w.pos().y() - self.mainwindow.sample.pos().y()),
                                    f"{elem[w.text()]}", font=font, fill='black')
                    if self.way:
                        image.save(f'{self.directory}/{self.f_name}_{i}.pdf')
                    else:
                        diplomas.append(image)
                if not self.way:
                    diplomas[0].save(f"{self.directory}/{self.f_name}.pdf", save_all=True, append_images=diplomas[1:])
                self.close()
                self.progress.close()
                self.show_info_msg('Дипломы успешно созданы.', 'Готово!', "Info")
        else:
            self.show_info_msg("Выбранной папки не существует", 'Ошибка!', "Warning")

    def close_dialog(self):
        self.close()

    def choose_folder(self):
        self.folder_name.setText(QFileDialog.getExistingDirectory())

    def show_info_msg(self, info, title, icon_name):
        dict = {"Warning": QMessageBox.Icon.Warning, "Info": QMessageBox.Icon.Information}
        msg = QMessageBox()
        msg.setIcon(dict[icon_name])
        msg.setText(info)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        retval = msg.exec()


class SaveOneDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        f = io.StringIO(save_one_template)
        uic.loadUi(f, self)
        self.setWindowTitle('Сохрнаить димпломы')
        self.accept_button_box.accepted.connect(self.create_diplomas)
        self.accept_button_box.rejected.connect(self.close_dialog)
        self.choose_folder_btn.clicked.connect(self.choose_folder)

    def create_diplomas(self):
        self.directory = self.folder_name.text()
        self.f_name = self.file_name.text()
        if os.path.exists(self.directory):
            image = Image.open('./pictures/current_example.jpg')
            image.save(f'{self.directory}/{self.f_name}.pdf')
            self.close()
            self.show_info_msg('Диплом успешно создан.', 'Готово!', "Info")
        else:
            self.show_info_msg("Выбранной папки не существует", 'Ошибка!', "Warning")

    def close_dialog(self):
        self.close()

    def choose_folder(self):
        self.folder_name.setText(QFileDialog.getExistingDirectory())

    def show_info_msg(self, info, title, icon_name):
        dict = {"Warning": QMessageBox.Icon.Warning, "Info": QMessageBox.Icon.Information}
        msg = QMessageBox()
        msg.setIcon(dict[icon_name])
        msg.setText(info)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        retval = msg.exec()


class ProgressBarDialog(QDialog):
    def __init__(self, size):
        self.size = size
        super().__init__()

        self.resize(300, 150)
        self.setWindowTitle('Загрузка')

        self.label = QLabel(self)
        self.label.setText('Пожалуйста, подождите.')
        self.label.move(20, 10)
        self.label.show()

        self.pb = QProgressBar(self)
        self.pb.setRange(0, size)
        self.pb.move(10, 100)
        self.pb.show()
