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

    def __init__(self,annt_path, dpath1, dpath2):
        QWidget.__init__(self)
        self.setup_ui()
        self.dpath1 = dpath1
        self.dpath2 = dpath2
        self.annt_path=annt_path
        self.sorted_diff_list = self.cal_diff(self.dpath1, self.dpath2)
        
    def setup_ui(self):
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap('./frontpage.jpg').scaledToHeight(420))

        self.main_layout = QVBoxLayout(self)  # adding widgets to layot
        self.main_layout.addWidget(self.image_label)

        # match button
        self.button = QPushButton("Next Sample")
        self.button.clicked.connect(self.next)

        #self.text = QLabel("Dear Annotator, <font color='red'>WELCOME!</font><br>Example: The man is sleepling on the chair")
        self.text = QLabel("Dear Annotator, <font color='red'>WELCOME!</font><br>Click next to show score difference between two annotators")
        self.text.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.text)
        self.main_layout.addWidget(self.button)

        self.setLayout(self.main_layout)  # set layot
        self.cnt = 0

    def format_text(self, obj, match_diff, match_level_1, match_level_2):
        sent = obj['text']
        words_ori = word_tokenize(sent)
        words = [ps.stem(i) for i in words_ori]

        arguments = obj['frame_info']['args']
        arg_idx = [words.index(ps.stem(arg)) for arg in arguments.values()]

        vb = obj['frame_info']['verb']
        verb_idx = words.index(ps.stem(vb))

        log_str = f"[Num: {self.cnt}] Match level diff: <b>{match_diff}</b> Annt score(User1): <b>{match_level_1}</b> Annt score(User2): <b>{match_level_2}</b><br>"
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

    def cal_diff(self, dpath1, dpath2):
        annots1 = os.listdir(dpath1)
        annots2 = os.listdir(dpath2)

        data1 = dict()
        data2 = dict()

        self.data = dict()
        with jsonlines.open(osp.join(self.annt_path, 'annt.jsonl')) as fp: 
            for i, obj in enumerate(fp):
                self.data[i] = obj

        for annt1 in annots1:
            annt_file = osp.join(dpath1, annt1)
            with jsonlines.open(annt_file) as fp:
                for obj in fp:
                    data1[obj['id']] = obj['match level']
        self.data1 = data1

        for annt2 in annots2:
            annt_file = osp.join(dpath2, annt2)
            with jsonlines.open(annt_file) as fp:
                for obj in fp:
                    data2[obj['id']] = obj['match level']
        self.data2 = data2

        assert data1.keys() == data2.keys(), f"number of ids mismatch, lack of {data1.keys()-data2.keys()} or {data2.keys()-data1.keys()}"
        data_diff = dict()
        for k, v in data1.items():
            data_diff[k] = abs(v - data2[k]) # NOTE: use absolute difference

        sorted_diff = sorted(data_diff.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_diff

    @QtCore.pyqtSlot()
    def next(self):
        if self.cnt >= len(self.sorted_diff_list):
            self.text.setText("End of file, please close the windows")
            return

        item_id, match_level = self.sorted_diff_list[self.cnt]
        
        image_file = self.data[item_id-1]['image_file']
        self.text.setText(self.format_text(self.data[item_id-1], match_level, self.data1[item_id], self.data2[item_id]))
        self.text.setAlignment(QtCore.Qt.AlignLeft)

        self.image_label.setPixmap(QPixmap(osp.join(self.annt_path, image_file)).scaledToHeight(420))
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)

        self.cnt += 1
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    #viewer = ImageViewer('./annt_v1', dpath1='./annt_v1_choice_zehao', dpath2='./annt_v1_choice_ziqin')
    viewer = ImageViewer('./annt_v2', dpath1='./annt_v2_choice_yubo', dpath2='./annt_v2_choice_mukai')
    #viewer = ImageViewer('./annt_v1', dpath1='./annotator_test', dpath2='./annotator_test')
    viewer.show()
    app.exec_()