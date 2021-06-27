import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QApplication

import jsonlines
import os.path as osp

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
ps = PorterStemmer()

class ImageViewer(QWidget):

    def __init__(self, annt_path, out_file='./annt_checked.jsonl'):
        QWidget.__init__(self)
        self.setup_ui()
        self.annt_path = annt_path
        self.out_file = out_file
        self.reader = jsonlines.open(osp.join(annt_path, 'annt.jsonl'))
        
    def setup_ui(self):
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap('./frontpage.jpg').scaledToHeight(420))

        self.main_layout = QVBoxLayout(self)  # adding widgets to layot
        self.main_layout.addWidget(self.image_label)
        self.button = QPushButton("Matched")
        self.button.clicked.connect(self.matched)
        self.button_mismatched = QPushButton("Mismatched")
        self.button_mismatched.clicked.connect(self.mismatched)

        #self.text = QLabel("Dear Annotator, <font color='red'>WELCOME!</font><br>Example: The man is sleepling on the chair")
        self.text = QLabel("Dear Annotator, <font color='red'>WELCOME!</font><br>Example: Young people are riding through the steel forest.")
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.text)
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.button_mismatched)

        self.setLayout(self.main_layout)  # set layot
        self.cnt = 0

    @staticmethod
    def format_text(obj):
        sent = obj['text']
        words_ori = word_tokenize(sent)
        words = [ps.stem(i) for i in words_ori]

        arguments = obj['frame_info']['args']
        arg_idx = [words.index(ps.stem(arg)) for arg in arguments.values()]

        vb = obj['frame_info']['verb']
        verb_idx = words.index(ps.stem(vb))

        log_str = ""
        log_str += f"VERB: <font color='red'>{vb}</font><br>"
        log_str += f"ARGS: "
        for k,v in arguments.items():
            log_str += f"{k}: <font color='blue'>{v}</font> "
        log_str += "<br>"

        log_str += "TEXT: "
        for i, word in enumerate(words_ori):
            if i == verb_idx:
                log_str += f"<font color='red'>{word}</font> "
            elif i in arg_idx:
                log_str += f"<font color='blue'>{word}</font> "
            else:
                log_str += f"{word} "
        return log_str

    def annotate(self, idx, value, d_info):
        # append new annotation to csv file
        with jsonlines.open(self.out_file, mode='a') as writer:
            d_info.update({"matched": value})
            writer.write(d_info)

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
                self.annotate(self.cnt, True, obj)
            self.cnt += 1
        except:
            self.reader.close()
            self.text.setText("End of file, please close the windows")
            
    @QtCore.pyqtSlot()
    def mismatched(self):
        # try:
            obj = self.reader.read()
            image_file = obj['image_file']
            self.text.setText(self.format_text(obj))
            self.text.setAlignment(QtCore.Qt.AlignLeft)
            self.image_label.setPixmap(QPixmap(osp.join(self.annt_path, image_file)).scaledToHeight(420))
            self.image_label.setAlignment(QtCore.Qt.AlignCenter)
            if self.cnt != 0:
                self.annotate(self.cnt, False, obj)
            self.cnt += 1
        # except:
        #     self.reader.close()
        #     self.text.setText("End of file, please close the windows")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer('./annt_v1')
    viewer.show()
    app.exec_()