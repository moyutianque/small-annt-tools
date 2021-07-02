import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel, QPushButton, QApplication

import jsonlines
import os.path as osp
import os

import time

from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
ps = PorterStemmer()

class ImageViewer(QWidget):

    def __init__(self, annt_path, out_file='./annt_checked.jsonl'):
        QWidget.__init__(self)
        self.setup_ui()
        self.annt_path = annt_path

        out_root = f'{annt_path}_choice_{int(time.time())}'
        os.makedirs(out_root, exist_ok=True)
        self.out_file = osp.join(out_root, out_file)
        self.reader = jsonlines.open(osp.join(annt_path, 'annt.jsonl'))
        
    def setup_ui(self):
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap('./frontpage.jpg').scaledToHeight(420))

        self.main_layout = QVBoxLayout(self)  # adding widgets to layot
        self.main_layout.addWidget(self.image_label)

        # match button
        self.button = QPushButton("Match")
        self.button.clicked.connect(lambda: self.match_level(1))
        # mismatch button
        self.button_mismatched = QPushButton("Mismatch")
        self.button_mismatched.clicked.connect(lambda: self.match_level(4))
        
        self.text = QLabel("Dear Annotator, <font color='red'>WELCOME!</font><br>Example: Young people are riding through the steel forest.")
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.text.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse) 

        self.main_layout.addWidget(self.text)
        self.main_layout.addWidget(self.button)
        self.main_layout.addWidget(self.button_mismatched)

        self.setLayout(self.main_layout)  # set layot
        self.cnt = 0

    def format_text(self, obj, head_info="Does the trigger in caption matches the definition of the trigger?"):
        sent = obj['text']
        words_ori = word_tokenize(sent)
        words = [ps.stem(i) for i in words_ori]

        arguments = obj['frame_info']['args']
        arg_idx = [words.index(ps.stem(arg)) for arg in arguments.values()]

        vb = obj['frame_info']['verb']
        verb_idx = words.index(ps.stem(vb))

        log_str = f"[Num: {self.cnt}] <b>{head_info}</b><br>"
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

    def annotate(self, idx, value, d_info, Ainfo='txt-trigger level'):
        """ Ainfo: 'txt-trigger level' 'img-trigger level' 'txt-img level' """
        # append new annotation to csv file

        d_info.update({Ainfo: value, "id":idx})
        if Ainfo == 'txt-img level':
            with jsonlines.open(self.out_file, mode='a') as writer:
                writer.write(d_info)

    @QtCore.pyqtSlot()
    def match_level(self, match_level):
        try:
            if self.cnt != 0:
                self.annotate(self.cnt, match_level, self.pre_obj, Ainfo=self.Ainfo)
            
            if self.cnt == 0 or self.Ainfo == 'txt-img level':
                self.cnt += 1
                self.Ainfo = 'txt-trigger level'

                obj = self.reader.read()
                image_file = obj['image_file']
                self.text.setText(self.format_text(obj, head_info="Does the trigger in caption match the definition of the trigger?"))
                self.text.setAlignment(QtCore.Qt.AlignLeft)

                self.image_label.setPixmap(QPixmap(osp.join(self.annt_path, image_file)).scaledToHeight(420))
                self.image_label.setAlignment(QtCore.Qt.AlignCenter)
                self.pre_obj = obj
            elif self.Ainfo == 'txt-trigger level':
                self.text.setText(self.format_text(self.pre_obj, head_info="Does the action in image match the definition of the trigger?"))
                self.text.setAlignment(QtCore.Qt.AlignLeft)
                self.Ainfo = 'img-trigger level'
            elif self.Ainfo == 'img-trigger level':
                self.text.setText(self.format_text(self.pre_obj, head_info="Does the caption match the image content?"))
                self.text.setAlignment(QtCore.Qt.AlignLeft)
                self.Ainfo = 'txt-img level'
            else:
                raise Exception(f"Unexpected Ainfo: {self.Ainfo}")

        except:
            self.reader.close()
            self.text.setText("End of file, please close the windows")
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer('./annt_v1.2')
    viewer.show()
    app.exec_()