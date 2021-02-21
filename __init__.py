anki_addon_name = "Chinese Vocabulary Generator"
anki_addon_version = "1.0.0"
anki_addon_author = "Mani"
anki_addon_license = "GPL 3.0 and later"

from aqt.qt import *
from aqt import mw

import os
import sys

folder = os.path.dirname(__file__)
libfolder = os.path.join(folder, "lib")
sys.path.insert(0, libfolder)

from hanziconv import HanziConv
from cedict import pinyinize
import requests

optionsChecked = {'ch_sim': True, 'ch_trad': True, 'ch_pin': True, 'ch_mean': True, 'ch_aud': True, 'ch_sen': True,
                  'ch_hw': True}

class Window(QDialog):
    def __init__(self):
        QDialog.__init__(self, None, Qt.Window)
        mw.setupDialogGC(self)
        self.setWindowTitle(anki_addon_name)
        layout = QVBoxLayout()

        self.deck_name = "Vocabulary Generator"

        topLayout = QFormLayout()

        self.deckNameEdit = QLineEdit()
        topLayout.addRow(QLabel("Deck Name"), self.deckNameEdit)

        self.templatesComboBox = QComboBox()
        self.templatesComboBox.addItems(['Xie Hanzi', 'Pleco', 'Hanping', 'Reveal.js'])
        topLayout.addRow(QLabel("Templates"), self.templatesComboBox)

        optionsLayout = QVBoxLayout()

        # self.ch_sim_cb = QCheckBox("Simplified")
        # self.ch_sim_cb.setChecked(True)
        # optionsLayout.addWidget(self.ch_sim_cb)

        self.ch_trad_cb = QCheckBox("Traditional")
        self.ch_trad_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_trad_cb)

        self.ch_pin_cb = QCheckBox("Pinyin")
        self.ch_pin_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_pin_cb)

        self.ch_mean_cb = QCheckBox("Meaning")
        self.ch_mean_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_mean_cb)

        self.ch_aud_cb = QCheckBox("Audio")
        self.ch_aud_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_aud_cb)

        self.ch_hw_cb = QCheckBox("Hanzi Writer")
        self.ch_hw_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_hw_cb)

        self.ch_sen_cb = QCheckBox("Sentence")
        self.ch_sen_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_cb)

        self.ch_sen_pin_cb = QCheckBox("Sentence Pinyin")
        self.ch_sen_pin_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_pin_cb)

        self.ch_sen_tra_cb = QCheckBox("Sentence Translation")
        self.ch_sen_tra_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_tra_cb)

        self.ch_sen_audio_cb = QCheckBox("Sentence Audio")
        self.ch_sen_audio_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_audio_cb)


        self.btnBox = QDialogButtonBox()
        self.btnBox.setStandardButtons(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.btnBox.accepted.connect(self.show_cvg_window)
        self.btnBox.rejected.connect(self.reject)

        layout.addLayout(topLayout)
        layout.addLayout(optionsLayout)
        layout.addWidget(self.btnBox)
        self.setLayout(layout)

    def show_cvg_window(self):

        # if self.ch_sim_cb.isChecked():
        #     optionsChecked['ch_sim'] = True
        # else:
        #     optionsChecked['ch_sim'] = False

        if self.ch_trad_cb.isChecked():
            optionsChecked['ch_trad'] = True
        else:
            optionsChecked['ch_trad'] = False

        if self.ch_pin_cb.isChecked():
            optionsChecked['ch_pin'] = True
        else:
            optionsChecked['ch_pin'] = False

        if self.ch_mean_cb.isChecked():
            optionsChecked['ch_mean'] = True
        else:
            optionsChecked['ch_mean'] = False

        if self.ch_aud_cb.isChecked():
            optionsChecked['ch_aud'] = True
        else:
            optionsChecked['ch_aud'] = False

        if self.ch_sen_cb.isChecked():
            optionsChecked['ch_sen'] = True
        else:
            optionsChecked['ch_sen'] = False

        if self.ch_sen_pin_cb.isChecked():
            optionsChecked['ch_sen_pin'] = True
        else:
            optionsChecked['ch_sen_pin'] = False

        if self.ch_sen_audio_cb.isChecked():
            optionsChecked['ch_sen_audio'] = True
        else:
            optionsChecked['ch_sen_audio'] = False

        if self.ch_sen_tra_cb.isChecked():
            optionsChecked['ch_sen_tra'] = True
        else:
            optionsChecked['ch_sen_tra'] = False

        if self.ch_hw_cb.isChecked():
            optionsChecked['ch_hw'] = True
        else:
            optionsChecked['ch_hw'] = False

        if self.deckNameEdit.text().strip() != "":
            self.deck_name = self.deckNameEdit.text().strip()
            self.hide()
            cvg_w = CVG_Window()
            cvg_w.show()


dialog = Window()
def showCVGEditor():
    dialog.exec_()

options_action = QAction(anki_addon_name + "...", mw)
options_action.triggered.connect(showCVGEditor)
mw.addonManager.setConfigAction(__name__, showCVGEditor)
mw.form.menuTools.addAction(options_action)


class CVG_Window(QDialog):
    def __init__(self):
        QDialog.__init__(self, None, Qt.Window)
        mw.setupDialogGC(self)

        self.deck_name = dialog.deck_name
        self.deck_template = dialog.templatesComboBox.currentText()

        self.setWindowTitle(self.deck_name + " - " + anki_addon_name)
        self.resize(600, 720)

        scrolllayout = QVBoxLayout()

        scrollwidget = QWidget()
        scrollwidget.setLayout(scrolllayout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scrollwidget)

        # Simplified
        ch_sim_groupbox = QGroupBox("Enter Simplified")
        ch_sim_grouplayout = QVBoxLayout()
        self.ch_sim_group_text_edit = QTextEdit()
        # Enter Button
        enter_button = QPushButton("Enter")
        ch_sim_grouplayout.addWidget(self.ch_sim_group_text_edit)
        ch_sim_grouplayout.addWidget(enter_button)
        enter_button.clicked.connect(self.cvg_get_ch_data)

        ch_sim_groupbox.setLayout(ch_sim_grouplayout)
        scrolllayout.addWidget(ch_sim_groupbox)

        # Traditional
        if optionsChecked['ch_trad']:
            ch_trad_groupbox = QGroupBox("Traditional")
            ch_trad_grouplayout = QHBoxLayout()
            self.ch_trad_group_text_edit = QTextEdit()
            ch_trad_grouplayout.addWidget(self.ch_trad_group_text_edit)
            ch_trad_groupbox.setLayout(ch_trad_grouplayout)
            scrolllayout.addWidget(ch_trad_groupbox)


        # Pinyin
        if optionsChecked['ch_pin']:
            ch_pin_groupbox = QGroupBox("Pinyin")
            ch_pin_grouplayout = QHBoxLayout()
            self.ch_pin_group_text_edit = QTextEdit()
            ch_pin_grouplayout.addWidget(self.ch_pin_group_text_edit)
            ch_pin_groupbox.setLayout(ch_pin_grouplayout)
            scrolllayout.addWidget(ch_pin_groupbox)

        # Meaning
        if optionsChecked['ch_mean']:
            ch_mean_groupbox = QGroupBox("Meaning")
            ch_mean_grouplayout = QHBoxLayout()
            self.ch_mean_group_text_edit = QTextEdit()
            ch_mean_grouplayout.addWidget(self.ch_mean_group_text_edit)
            ch_mean_groupbox.setLayout(ch_mean_grouplayout)
            scrolllayout.addWidget(ch_mean_groupbox)

        # Audio
        if optionsChecked['ch_aud']:
            ch_aud_box_gl = QVBoxLayout()

            ch_aud_groupbox = QGroupBox("Audio")
            ch_aud_grouplayout = QHBoxLayout()
            self.ch_aud_group_text_edit = QTextEdit()
            ch_aud_grouplayout.addWidget(self.ch_aud_group_text_edit)

            ch_aud_buttons_gl = QHBoxLayout()
            ch_aud_play_button = QPushButton("Play")
            ch_aud_change_button = QPushButton("Change")
            ch_aud_buttons_gl.addWidget(ch_aud_play_button)
            ch_aud_buttons_gl.addWidget(ch_aud_change_button)

            ch_aud_box_gl.addLayout(ch_aud_grouplayout)
            ch_aud_box_gl.addLayout(ch_aud_buttons_gl)

            ch_aud_groupbox.setLayout(ch_aud_box_gl)
            scrolllayout.addWidget(ch_aud_groupbox)


        # Sentence
        if optionsChecked['ch_sen']:
            # Change Button | All Sentence Button
            ch_sen_box_gl = QVBoxLayout()

            ch_sen_audio_groupbox = QGroupBox("Sentence")
            ch_sen_audio_grouplayout = QHBoxLayout()
            self.ch_sen_audio_group_text_edit = QTextEdit()
            ch_sen_audio_grouplayout.addWidget(self.ch_sen_audio_group_text_edit)

            ch_sen_audio_buttons_gl = QHBoxLayout()
            ch_sen_audio_change_button = QPushButton("Change")
            ch_sen_audio_all_button = QPushButton("All Sentences")
            ch_sen_audio_buttons_gl.addWidget(ch_sen_audio_change_button)
            ch_sen_audio_buttons_gl.addWidget(ch_sen_audio_all_button)

            ch_sen_box_gl.addLayout(ch_sen_audio_grouplayout)
            ch_sen_box_gl.addLayout(ch_sen_audio_buttons_gl)

            ch_sen_audio_groupbox.setLayout(ch_sen_box_gl)
            scrolllayout.addWidget(ch_sen_audio_groupbox)

        # Sentence Pinyin
        if optionsChecked['ch_sen_pin']:
            ch_sen_pin_groupbox = QGroupBox("Sentence Pinyin")
            ch_sen_pin_grouplayout = QHBoxLayout()
            self.ch_sen_pin_group_text_edit = QTextEdit()
            ch_sen_pin_grouplayout.addWidget(self.ch_sen_pin_group_text_edit)
            ch_sen_pin_groupbox.setLayout(ch_sen_pin_grouplayout)
            scrolllayout.addWidget(ch_sen_pin_groupbox)

        # Sentence Translation
        if optionsChecked['ch_sen_tra']:
            ch_sen_tra_groupbox = QGroupBox("Sentence Translation")
            ch_sen_tra_grouplayout = QHBoxLayout()
            self.ch_sen_tra_group_text_edit = QTextEdit()
            ch_sen_tra_grouplayout.addWidget(self.ch_sen_tra_group_text_edit)
            ch_sen_tra_groupbox.setLayout(ch_sen_tra_grouplayout)
            scrolllayout.addWidget(ch_sen_tra_groupbox)

        # Sentence Audio
        if optionsChecked['ch_sen_audio']:
            ch_sen_box_gl = QVBoxLayout()

            ch_sen_audio_groupbox = QGroupBox("Sentence Audio")
            ch_sen_audio_grouplayout = QHBoxLayout()
            self.ch_sen_audio_group_text_edit = QTextEdit()
            ch_sen_audio_grouplayout.addWidget(self.ch_sen_audio_group_text_edit)

            ch_sen_audio_buttons_gl = QHBoxLayout()
            ch_sen_audio_play_button = QPushButton("Play")
            ch_sen_audio_change_button = QPushButton("Change")
            ch_sen_audio_buttons_gl.addWidget(ch_sen_audio_play_button)
            ch_sen_audio_buttons_gl.addWidget(ch_sen_audio_change_button)

            ch_sen_box_gl.addLayout(ch_sen_audio_grouplayout)
            ch_sen_box_gl.addLayout(ch_sen_audio_buttons_gl)

            ch_sen_audio_groupbox.setLayout(ch_sen_box_gl)
            scrolllayout.addWidget(ch_sen_audio_groupbox)

        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton("Add", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("Clear", QDialogButtonBox.RejectRole)

        self.buttonBox.accepted.connect(self.cvg_add_notes)
        self.buttonBox.rejected.connect(self.cvg_clear_notes)

        layout = QVBoxLayout()
        layout.addWidget(scroll)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def cvg_get_ch_data(self):
        print("Get Data")
        ch_sim = self.ch_sim_group_text_edit.toPlainText().strip()
        #ch_trad = HanziConv.toTraditional(ch_sim)

        base_url = "https://cdn.jsdelivr.net/gh/infinyte7/cedict-json/v2/"
        ch_url = base_url + ch_sim + ".json"
        r = requests.get(ch_url)

        if r.status_code == 200:
            ch_data = r.json()

            self.ch_trad_group_text_edit.setText(ch_data['traditional'])

            ch_pin = ""
            for p in ch_data['pinyin']:
                ch_pin += pinyinize(p) + ", "
            ch_pin.strip().rstrip(",")

            self.ch_pin_group_text_edit.setText(ch_pin)

            ch_mean = ""
            if len(ch_data['definitions']) > 1:
                for d in ch_data['definitions']:
                    ch_mean += d + "\n" + ch_data['definitions'][d].replace("; ", "\n").strip() + "\n\n"
            else:
                ch_mean += ch_data['definitions'][ch_data['pinyin'][0]].replace("; ", "\n").strip() + "\n\n"
            self.ch_mean_group_text_edit.setText(ch_mean)

    def cvg_add_notes(self):
        print("Added")

    def cvg_clear_notes(self):
        print("Cleared")
