from aqt.utils import getOnlyText

anki_addon_name = "Chinese Vocabulary Generator"
anki_addon_version = "1.0.0"
anki_addon_author = "Mani"
anki_addon_license = "GPL 3.0 and later"

from aqt.qt import *
from aqt import mw
from anki.notes import Note

import os
import sys

folder = os.path.dirname(__file__)
libfolder = os.path.join(folder, "lib")
sys.path.insert(0, libfolder)

import requests
import sqlite3
import random
import jieba
import pinyin

import logging
jieba.setLogLevel(logging.ERROR)

from gtts import gTTS
from cedict import pinyinize
from hanziconv import HanziConv
from googletrans import Translator
from playsound import playsound


optionsChecked = {'ch_sim': True, 'ch_trad': True, 'ch_pin': True, 'ch_mean': True, 'ch_aud': True, 'ch_sen': True,
                  'ch_hw': True}

class Window(QDialog):
    def __init__(self):
        QDialog.__init__(self, None, Qt.Window)
        mw.setupDialogGC(self)
        self.setWindowTitle(anki_addon_name)
        layout = QVBoxLayout()

        topLayout = QFormLayout()

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

        self.ch_sen_trad_cb = QCheckBox("Sentence Traditional")
        self.ch_sen_trad_cb.setChecked(True)
        optionsLayout.addWidget(self.ch_sen_trad_cb)

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

        if self.ch_sen_trad_cb.isChecked():
            optionsChecked['ch_sen_trad'] = True
        else:
            optionsChecked['ch_sen_trad'] = False

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

        self.deck_template = dialog.templatesComboBox.currentText()

        dname = getOnlyText("Enter Deck Name")
        self.did = mw.col.decks.id(dname)
        mw.deckBrowser.refresh()

        self.setWindowTitle(anki_addon_name)
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

            ch_aud_add_button = QPushButton("Add/Change")
            ch_aud_add_button.clicked.connect(self.get_audio_ch_sim)

            ch_aud_play_button = QPushButton("Play")
            ch_aud_play_button.clicked.connect(self.ch_sim_audio_play)

            ch_aud_buttons_gl.addWidget(ch_aud_add_button)
            ch_aud_buttons_gl.addWidget(ch_aud_play_button)

            ch_aud_box_gl.addLayout(ch_aud_grouplayout)
            ch_aud_box_gl.addLayout(ch_aud_buttons_gl)

            ch_aud_groupbox.setLayout(ch_aud_box_gl)
            scrolllayout.addWidget(ch_aud_groupbox)


        # Sentence
        if optionsChecked['ch_sen']:
            # Change Button | All Sentence Button
            ch_sen_box_gl = QVBoxLayout()

            ch_sen_groupbox = QGroupBox("Sentence")
            ch_sen_grouplayout = QHBoxLayout()
            self.ch_sen_group_text_edit = QTextEdit()
            ch_sen_grouplayout.addWidget(self.ch_sen_group_text_edit)

            ch_sen_buttons_gl = QHBoxLayout()

            ch_sen_add_button = QPushButton("Add")
            ch_sen_add_button.clicked.connect(self.get_ch_sen_add)

            ch_sen_all_button = QPushButton("All Sentences")
            ch_sen_all_button.clicked.connect(self.get_ch_sen_all)

            ch_sen_buttons_gl.addWidget(ch_sen_add_button)
            ch_sen_buttons_gl.addWidget(ch_sen_all_button)

            ch_sen_box_gl.addLayout(ch_sen_grouplayout)
            ch_sen_box_gl.addLayout(ch_sen_buttons_gl)

            ch_sen_groupbox.setLayout(ch_sen_box_gl)
            scrolllayout.addWidget(ch_sen_groupbox)


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

    def get_audio_ch_sim(self):
        ch_sim = self.ch_sim_group_text_edit.toPlainText().strip()
        rand_file_name = str(random.randrange(1 << 30, 1 << 31)) + "-" + str(random.randrange(1 << 15, 1 << 16))
        if ch_sim != "":
            self.audio_file = "cvg-" + rand_file_name + ".mp3"
            ch_audio = "[sound:" + self.audio_file + "]"
            self.ch_aud_group_text_edit.setText(ch_audio)
            tts = gTTS(ch_sim, lang="zh-cn")
            tts.save(self.audio_file)

    def ch_sim_audio_play(self):
        ch_aud = self.ch_aud_group_text_edit.toPlainText().strip()
        ch_aud = ch_aud.replace("[sound:", "")
        ch_aud = ch_aud.replace("]", "")
        if os.path.exists(ch_aud):
            playsound(ch_aud)

    def get_ch_sen_add(self):
        ch_sim = self.ch_sim_group_text_edit.toPlainText().strip()
        if ch_sim != "":
            self.get_sentence(ch_sim)

    def get_ch_sen_all(self):
        print("all sen")

    def cvg_add_notes(self):
        print("Added")

        model_name = "cvg-test"
        model = mw.col.models.byName(model_name)

        if not model:
            models = mw.col.models

            model = models.new(model_name)

            fld = models.newField("Front")
            models.addField(model, fld)

            fld = models.newField("Back")
            models.addField(model, fld)

            template = models.newTemplate(self.deck_template)
            template['qfmt'] = "<div>{{Front}}</div>"
            template['afmt'] = "<div>{{Back}}</div>"
            template['css'] = ".card{}"
            models.addTemplate(model, template)
            models.add(model)

        model['did'] = self.did

        mw.col.decks.select(self.did)

        note = Note(mw.col, model)
        note["Front"] = "Hello"
        note["Back"] = "World"

        mw.col.addNote(note)

        mw.deckBrowser.refresh()

    def cvg_clear_notes(self):
        print("Cleared")

    def get_sentence(self, char):
        con = sqlite3.connect(folder+"/data.db")
        cur = con.cursor()

        sql = "Select sentence from data where sentence like " + "'%" + char + "%'"

        cur.execute(sql)
        sent = cur.fetchall()

        r1 = random.choice(sent)
        s1 = HanziConv.toSimplified(r1[0])
        trad1 = HanziConv.toTraditional(s1)

        seg_list = jieba.cut(s1, cut_all=False)
        p1 = pinyin.get(" ".join(seg_list))

        ch_sen = self.ch_sen_group_text_edit.toPlainText().strip()
        if ch_sen != "":
            ch_sen += "\n\n"

        if optionsChecked['ch_sen']:
            ch_sen += s1 + "\n"

        if optionsChecked['ch_sen_trad']:
            ch_sen += trad1 + "\n"

        if optionsChecked['ch_sen_pin']:
            ch_sen += p1 + "\n"

        if optionsChecked['ch_sen_tra']:
            translator = Translator()
            t1 = translator.translate(s1, src='zh-cn', dest="en")
            ch_sen += t1.text + "\n"

        if optionsChecked['ch_sen_audio']:
            if s1 != "":
                rand_file_name = str(random.randrange(1 << 30, 1 << 31)) + "-" + str(random.randrange(1 << 15, 1 << 16))
                audio_file = "cvg-sen-" + rand_file_name + ".mp3"
                tts = gTTS(s1, lang="zh-cn")
                tts.save(audio_file)
                ch_sen += audio_file + "\n"

        ch_sen += "\n"

        self.ch_sen_group_text_edit.setText(ch_sen)


