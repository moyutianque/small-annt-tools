import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QApplication

import jsonlines
import os.path as osp

class ImageViewer(QWidget):

    def __init__(self, annt_path, out_csv='./annt.csv'):
        QWidget.__init__(self)
        self.setup_ui()
        self.annt_path = annt_path
        self.out_csv = out_csv
        self.reader = jsonlines.open(osp.join(annt_path, 'annt.jsonl'))
        
    def setup_ui(self):
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap('./magou.jpg').scaledToHeight(420))

        self.main_layout = QVBoxLayout(self)  # adding widgets to layot
        self.main_layout.addWidget(self.image_label)
        self.button = QPushButton("Matched")
        self.button.clicked.connect(self.matched)
        self.button_mismatched = QPushButton("Mismatched")
        self.button_mismatched.clicked.connect(self.mismatched)

        self.text = QLabel("Dear Annotator, <font color='red'>WELCOME!</font><br>Example: The man is sleepling on the chair")
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.text)
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.button_mismatched)

        self.setLayout(self.main_layout)  # set layot
        self.cnt = 0

    @staticmethod
    def format_text(obj):
        log_str = ""
        log_str += f"VERB:\t{obj['frame_info']['verb']}\n"
        log_str += f"ARGS:\t{obj['frame_info']['args']}\n"
        log_str += f"TEXT:\t{obj['text']}"
        return log_str

    def annotate(self, idx, value):
        # append new annotation to csv file
        file = open(self.out_csv,"a")
        file.write("%s,%s\n" % (idx, value))
        file.close()

    @QtCore.pyqtSlot()
    def matched(self):
        try:
            obj = self.reader.read()
            image_file = obj['image_file']
            self.text.setText(self.format_text(obj))
            self.text.setAlignment(QtCore.Qt.AlignLeft)

            self.image_label.setPixmap(QPixmap(osp.join(self.annt_path, image_file)).scaledToHeight(420))
            self.image_label.setAlignment(QtCore.Qt.AlignCenter)
            if self.cnt != 0:
                self.annotate(self.cnt, True)
            self.cnt += 1
        except:
            self.reader.close()
            self.text.setText("End of file, please close the windows")
            
    @QtCore.pyqtSlot()
    def mismatched(self):
        try:
            obj = self.reader.read()
            image_file = obj['image_file']
            self.text.setText(self.format_text(obj))
            self.text.setAlignment(QtCore.Qt.AlignLeft)
            self.image_label.setPixmap(QPixmap(osp.join(self.annt_path, image_file)).scaledToHeight(420))
            self.image_label.setAlignment(QtCore.Qt.AlignCenter)
            if self.cnt != 0:
                self.annotate(self.cnt, False)
            self.cnt += 1
        except:
            self.reader.close()
            self.text.setText("End of file, please close the windows")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer('./annt_first_try')
    viewer.show()
    app.exec_()