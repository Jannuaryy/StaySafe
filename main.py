from PyQt6.QtWidgets import QApplication, QWidget, QDialog, QMainWindow, QFileDialog, QDialogButtonBox
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QLayout, QLineEdit, QComboBox, QListWidget
from PyQt6.QtWidgets import QGridLayout, QFrame, QStyleFactory, QSizePolicy
from PyQt6.QtCore import Qt, QSize
import sys, os, csv
import sqlite3
from datetime import datetime
from PyQt6 import QtGui


class StaySafe_Mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Stay Safe')
        w = QWidget()
        self.setCentralWidget(w)
        main_layout = QVBoxLayout(w)
        self.statusBar().show()
        # иконка окна
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("icons/safe-mail.png"))
        self.setWindowIcon(self.icon)

        from_layout = QHBoxLayout()

        # путь
        self.fexplorer_line = QLineEdit('Выберете файл...')
        self.fexplorer_line.setDisabled(True)
        self.explorer_from = QPushButton()
        self.explorer_from.clicked.connect(self.open_explorer_from)
        from_layout.addWidget(self.fexplorer_line)
        from_layout.addWidget(self.explorer_from)

        to_layout = QHBoxLayout()

        self.texplorer_line = QLineEdit('Путь для сохранения...')
        self.texplorer_line.setDisabled(True)
        self.explorer_to = QPushButton()
        self.explorer_to.clicked.connect(self.open_explorer_to)
        to_layout.addWidget(self.texplorer_line)
        to_layout.addWidget(self.explorer_to)

        # иконка проводник
        self.icon.addPixmap(QtGui.QPixmap("icons/app.png"))
        self.explorer_from.setIcon(self.icon)
        self.explorer_to.setIcon(self.icon)

        buttons_layout = QHBoxLayout()

        # кнопки де\шифровки
        self.decryption = QPushButton('Расшифровать')
        self.decryption.clicked.connect(self.password_widget)

        self.cryption = QPushButton('Зашифровать')
        self.cryption.clicked.connect(self.password_widget)

        buttons_layout.addWidget(self.cryption)
        buttons_layout.addWidget(self.decryption)

        other_layout = QHBoxLayout()

        # настройки
        setting_button = QPushButton()
        setting_button.clicked.connect(self.open_settings)

        # иконка настроек
        self.icon.addPixmap(QtGui.QPixmap("icons/setting.png"))
        setting_button.setIcon(self.icon)

        self.log_button = QPushButton()
        self.icon.addPixmap(QtGui.QPixmap("icons/log-out.png"))
        self.log_button.setIcon(self.icon)
        self.log_button.clicked.connect(self.show_log)
        self.log_button.setIcon(self.icon)

        other_layout.addWidget(setting_button)
        other_layout.addWidget(self.log_button)

        main_layout.addLayout(from_layout)
        main_layout.addLayout(to_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(other_layout)
        other_layout.setAlignment(setting_button, Qt.AlignmentFlag.AlignLeft)
        other_layout.setAlignment(self.log_button, Qt.AlignmentFlag.AlignRight)

        self.db_con = sqlite3.connect('events.sqlite')
        self.db_con.row_factory = sqlite3.Row
        cur = self.db_con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS events(event_id INTEGER PRIMARY KEY, event_time TEXT, event_message TEXT)""")
        cur.execute("INSERT INTO events (event_time, event_message) VALUES (?, ?)", (datetime.now(), 'Запуск программы'))
        self.db_con.commit()

        self.statusBar().showMessage("Готов к работе")

    def show_log(self):
        d = QDialog(self)
        d.setModal(True)  # модальность диалога

        d.resize(500, 250)
        d.setWindowTitle('Лог событий')

        self.log = QListWidget(d)
        cur = self.db_con.cursor()
        for event in cur.execute("SELECT event_time, event_message FROM events").fetchall():
            self.log.addItem(f"{event['event_time'].split('.')[0]}: {event['event_message']}")

        l = QVBoxLayout(d)
        l.addWidget(self.log)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttonBox.button(QDialogButtonBox.StandardButton.Close).clicked.connect(d.close)
        clear_log_b = buttonBox.addButton('Очистить журнал', QDialogButtonBox.ButtonRole.ResetRole)
        clear_log_b.clicked.connect(self.clear_log)
        l.addWidget(buttonBox)

        d.show()

    def clear_log(self):
        cur = self.db_con.cursor()
        cur.execute("DELETE FROM events")
        self.db_con.commit()
        self.log.clear()

    def open_explorer_from(self):
        # путь файл
        fname = QFileDialog.getOpenFileName(self)
        self.fexplorer_line.setText(str(fname[0]) if str(fname[0]) != '' else 'Выберете файл...')

    def open_explorer_to(self):
        # путь сохранение
        fname = QFileDialog.getExistingDirectory(self)
        self.texplorer_line.setText(str(fname) if str(fname[0]) != '' else 'Путь для сохранения...')

    def password_widget(self):
        # запуск диалога пароля
        self.which_button = self.sender()
        self.password_widget = Password_dialog()
        self.password_widget.show()
        self.password_widget.accepted.connect(self.password_accepted)

    def password_accepted(self):
        self.statusBar().clearMessage()
        ecryption = False if self.which_button == self.decryption else True
        self.password = self.password_widget.write_password.text()
        self.password_widget.write_password.setText('')

        from_file = self.fexplorer_line.text()
        to_file = from_file

        # Снять-поставить расширение enc:
        if ecryption:
            to_file = f'{to_file}.enc'
        else:
            if to_file[-4:] == '.enc':
                to_file = to_file[: -4]

        # Указал ли пользователь целевую папку:
        if self.texplorer_line.isVisible():
            to_file_basename = os.path.basename(to_file)
            to_file = os.path.join(self.texplorer_line.text(), to_file_basename)

        try:
            file_to_write = to_file
            if from_file == to_file:
                file_to_write = f'{to_file}.tmp'

            self.crypt(self.password, from_file, file_to_write)

            if from_file == to_file:
                with open(file_to_write, 'rb') as file_to_write_f:
                    with open(to_file, 'wb') as to_file_f:
                        to_file_f.write(file_to_write_f.read())
                os.unlink(file_to_write)

            if from_file != to_file:
                os.unlink(from_file)

            log_message = f'Файл "{from_file}" ' + ('зашифрован' if ecryption else 'расшифрован')
            cur = self.db_con.cursor()
            cur.execute("INSERT INTO events (event_time, event_message) VALUES (?, ?)", (datetime.now(), log_message))
            self.db_con.commit()

            self.statusBar().showMessage('Файл успешно зашифрован' if ecryption else 'Файл успешно расшифрован')
        except FileNotFoundError:
            self.statusBar().showMessage('Ошибка: Не выбран файл')
        except IndexError:
            self.statusBar().showMessage('Ошибка: пустой пароль')
        except Exception:
            self.statusBar().showMessage('Непредвиденная ошибка')

    def open_settings(self):
        self.statusBar().clearMessage()
        self.settings_widget = self.settings_widget if hasattr(self, 'settings_widget') else Settings()
        self.settings_widget.show()
        self.settings_widget.accepted.connect(self.settings_accepted)

    def settings_accepted(self):
        saveType =self.settings_widget.save_change.currentIndex() # 0 - Копия, 1 - Переписать

        if saveType:
            self.texplorer_line.hide()
            self.explorer_to.hide()
        else:
            self.texplorer_line.show()
            self.explorer_to.show()

    def crypt(self, password, from_file, to_file):
        p_pos = 0
        file_to = open(to_file, 'wb')
        with open(from_file, 'rb') as file_from:
            data = file_from.read()
            for ch in data:
                ch = ch ^ ord(password[p_pos])
                file_to.write(ch.to_bytes(1, 'big'))
                p_pos += 1 if p_pos < len(password) - 1 else 0


class Password_dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setModal(True) # модальность диалога

        self.setGeometry(500, 500, 100, 50)
        self.setWindowTitle('Мастер-пароль')
        self.main_layout = QVBoxLayout(self)
        self.password_layout = QHBoxLayout()

        self.write_password = QLineEdit()
        self.visibility_password = QPushButton()
        self.write_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.visibility_password.clicked.connect(self.visibility_change)

        #
        self.icon_visible = QtGui.QIcon()
        self.icon_visible.addPixmap(QtGui.QPixmap("icons/view black.png"))

        #
        self.icon_not_visible = QtGui.QIcon()
        self.icon_not_visible.addPixmap(QtGui.QPixmap("icons/not view black.png"))

        self.visibility_password.setIcon(self.icon_not_visible)
        self.flag_visible = False

        self.password_layout.addWidget(self.write_password)
        self.password_layout.addWidget(self.visibility_password)

        self.main_layout.addWidget(QLabel('Введите мастер-пароль:'))
        self.main_layout.addLayout(self.password_layout)

        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.main_layout.addWidget(buttonBox)
        buttonBox.button(QDialogButtonBox.StandardButton.Ok).clicked.connect(self.accept)
        buttonBox.button(QDialogButtonBox.StandardButton.Cancel).clicked.connect(self.reject)

    def visibility_change(self):
        if self.flag_visible is False:
            self.visibility_password.setIcon(self.icon_not_visible)
            self.write_password.setEchoMode(QLineEdit.EchoMode.Password)
            self.flag_visible = True
        else:
            self.visibility_password.setIcon(self.icon_visible)
            self.flag_visible = False
            self.write_password.setEchoMode(QLineEdit.EchoMode.Normal)


class Settings(QDialog):
    def __init__(self):
        super().__init__()

        self.theme_confs = [{'name': 'Системная'}]
        with open('themes.csv', mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for line in csv_reader:
                self.theme_confs.append(dict(line))
        # print(self.theme_confs)

        self.setModal(True)
        self.setWindowTitle('Настройки')
        self.icon = QtGui.QIcon()
        self.icon.addPixmap(QtGui.QPixmap("icons/setting.png"))
        self.setWindowIcon(self.icon)
        self.save_changes = QPushButton('Применить')
        self.save_changes.clicked.connect(self.accept)

        buttons_names = [QLabel('Вид'), QLabel('Палитра'), QLabel('Тип сохранения'), QLabel('Язык')]

        layout = QGridLayout(self)
        changes = []
        self.type = QComboBox()
        self.type.addItems(QStyleFactory.keys())
        self.type.activated.connect(self.change_style)

        self.palette_change = QComboBox()
        self.palette_change.addItems([(theme_conf.get('name')) for theme_conf in self.theme_confs])
        self.palette_change.activated.connect(self.change_style)

        self.save_change = QComboBox()
        self.save_change.addItems(('Копия', 'Переписать'))
        self.language = QComboBox()
        self.language.addItem('В разработке')
        self.language.setDisabled(True)
        changes.append(self.type)
        changes.append(self.save_change)
        changes.append(self.language)

        layout.addWidget(QLabel('Тема'), 0, 1)
        layout.addWidget(self.type, 1, 1)
        layout.addWidget(buttons_names[0], 1, 0)

        layout.addWidget(self.palette_change, 2, 1)
        layout.addWidget(buttons_names[1], 2, 0)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line, 3, 0, 1, 2)

        layout.addWidget(self.save_change, 4, 1)
        layout.addWidget(buttons_names[2], 4, 0)
        layout.addWidget(self.language, 5, 1)
        layout.addWidget(buttons_names[3], 5, 0)

        layout.addWidget(self.save_changes, 6, 0)
        layout.setAlignment(self.save_changes, Qt.AlignmentFlag.AlignLeft)


    def change_style(self):
        QApplication.setPalette(QApplication.style().standardPalette())
        style_name = self.type.currentText().strip()
        QApplication.setStyle(QStyleFactory.create(style_name))

        palette_index = self.palette_change.currentIndex()
        if palette_index < 1:
            return

        curr_theme = self.theme_confs[palette_index]
        #print(style_name)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(*map(int, curr_theme['window_color'].split('-'))))
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(25, 25, 25))
        palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 53, 53))
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Text, Qt.GlobalColor.darkGray if style_name == 'macOS' else Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.Button, Qt.GlobalColor.darkGray)
        palette.setColor(QtGui.QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QtGui.QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(42, 130, 218))
        palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.setPalette(palette)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StaySafe_Mainwindow()
    ex.show()
    sys.exit(app.exec())
