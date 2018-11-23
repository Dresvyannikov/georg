from PyQt5.QtCore import pyqtSlot, QStringListModel
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import QAbstractListModel
from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtProperty

from PyQt5.QtGui import QColor

from base.models import Mode
from base.models import Service
from base.models import Command
from base.models import Operator

import configparser
import os

# цвета фона вкладки
OFFLINE_COLOR = QColor("gray")
ERROR_COLOR = QColor("red")
NORMAL_COLOR = QColor("#96b77b")


class DataCube(object):
    def __init__(self, dir_name, ip, label='text', color_state=ERROR_COLOR, active=True):
        self._label = label
        self._color_state = color_state
        self._active = active
        if active:
            self._color_fone = NORMAL_COLOR
        else:
            self._color_fone = OFFLINE_COLOR
        self._dir_name = dir_name
        self._ip = ip
        self._config = ''
        self.files = {}
        self.rows = 0

    def get_config_parse(self):
        config = configparser.ConfigParser()
        config.read_string(self._config)
        return config

    def set_config(self, config_str):
        self._config = config_str

        config_parse = self.get_config_parse()
        try:
            command = config_parse.get('app', 'start_command')
        except:
            command = ''
        self.rows = int((len(command.split(' '))-1) / 2)

    def config(self):
        return self._config

    def label(self):
        return self._label

    def color_state(self):
        return self._color_state

    def color_fone(self):
        return self._color_fone

    def checked(self):
        return self._active

    def dir_name(self):
        return self._dir_name

    def ip(self):
        return self._ip

    def set_active(self, flag):
        self._active = flag
        if flag:
            self._color_fone = NORMAL_COLOR
        else:
            self._color_fone = OFFLINE_COLOR


class ListDataCube(QAbstractListModel):
    LabelRole = Qt.UserRole + 1
    ColorStateRole = Qt.UserRole + 2
    ColorFoneRole = Qt.UserRole + 3
    CheckedRole = Qt.UserRole + 4
    ConfigRole = Qt.UserRole + 5

    _roles = {LabelRole: b"label",
              ColorStateRole: b"color_state",
              ColorFoneRole: b"color_fone",
              CheckedRole: b"checked",
              ConfigRole: b"config",}
    session = None
    list_data_config = {}

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)

        self._datas = []

    def rowCount(self, parent=QModelIndex()):
        return len(self._datas)

    def addData(self, data):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._datas.append(data)
        self.endInsertRows()

    def data(self, index, role=Qt.DisplayRole):
        try:
            data = self._datas[index.row()]
        except IndexError:
            return QVariant()

        if role == self.LabelRole:
            return data.label()

        if role == self.ColorStateRole:
            return data.color_state()

        if role == self.ColorFoneRole:
            return data.color_fone()

        if role == self.CheckedRole:
            return data.checked()

        if role == self.ConfigRole:
            return data.config()

        return QVariant()

    @pyqtSlot(int, bool)
    def change_active(self, index=None, state=None):
        # сигнал для модели о изменении данных
        self.beginResetModel()
        data = self._datas[index]
        data.set_active(state)
        # сигнал окончания изменения данных
        self.endResetModel()

    def roleNames(self):
        return self._roles

    @pyqtSlot(int, str)
    def set_command(self, index, com):
        cube = self._datas[index]
        service = self.session.query(Service).filter_by(ip=cube.ip()).filter_by(dir_name=cube.dir_name()).first()
        service.command = self.session.query(Command).filter_by(name=com).first()
        print('<set_command>', service.command)
        self.session.add(service)
        self.session.commit()

    @pyqtSlot(Service)
    def create_data(self, service):
        cube = DataCube(label=service.name, color_state=NORMAL_COLOR, active=True, dir_name=service.dir_name,
                        ip=service.ip)
        cube.set_config(service.config)
        # сигнал для модели о изменении данных
        self.beginResetModel()
        self.addData(cube)
        # сигнал окончания изменения данных
        self.endResetModel()

    @pyqtSlot(Service)
    def change_data(self, service):
        # сигнал для модели о изменении данных
        self.beginResetModel()
        for i in range(len(self._datas)):
            if self._datas[i].dir_name() == service.dir_name:
                self._datas[i]._label = service.name
                self._datas[i]._ip = service.ip
                self._datas[i]._color_state = service.state.color
                self._datas[i].set_config(service.config)

        # сигнал окончания изменения данных
        self.endResetModel()
        self.resetInternalData()

    @pyqtSlot(Service)
    def delete_data(self, service):
        print('delete _data', service)

        for _dir in self._datas:
            if _dir.dir_name() == service.dir_name and _dir.ip() == service.ip:
                self.beginResetModel()
                self._datas.remove(_dir)
                # сигнал окончания изменения данных
                self.endResetModel()
                self.resetInternalData()

    @pyqtSlot(str)
    def save_configs(self, config_text):
        print(config_text)
        # str_config = self._datas[1]._config
        # import configparser
        # config = configparser.ConfigParser()
        # config.read_string(str_config)

    @pyqtSlot(int, str, result='QVariant')
    def get_data(self, index, mode_name):

        pattern_row = {'arg': 'arg', 'comf': 'file'}
        service = self.session.query(Service).filter_by(id=index).first()
        # TODO: если одинаковые имена, то?
        mode = self.session.query(Mode).filter_by(name=mode_name).first()

        if not service:
            print('<foo> Ошибка поиска сервиса! Проблемы с индексами!!', index)
            return

        configs = service.defaults
        default_config = None
        for config in configs:
            if config.mode == mode:
                default_config = config

        if not default_config:
            # сгенерируем просто пустой массив с кол-вом строк из строки запуска в конфиге сервиса
            data = list()
            for i in range(self._datas[index-1].rows):
                pattern = pattern_row.copy()
                pattern['index'] = i
                data.append(pattern)

        else:
            files = default_config.verbose.files
            data = []
            for i in range(self._datas[index-1].rows):
                add = False
                pattern = pattern_row.copy()
                for file in files:
                    if file.index == i:
                        pattern['index'] = i
                        pattern['comf'] = file.path
                        pattern['arg'] = file.arg
                        data.append(pattern)
                        add = True
                if not add:
                    pattern['index'] = i
                    data.append(pattern)
        return data

    def set_data_config(self, index_tab, mode_name, data):
        print(index_tab, mode_name, data)


class MainWindow(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialise the value of the properties.
        self._name = 'georg'
        self.server = None
        self.session = None
        self.connection_thread = None
        self.updater_thread = None
        # for work
        self._mode = ''
        self._user = ''

    @pyqtProperty('QString')
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, mode):
        self._mode = mode

    @pyqtProperty('QString', constant=True)
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @pyqtProperty('QString')
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        self._user = user

    @pyqtSlot()
    def start_all(self):
        # информацию берем ил локальной БД (кол-во квадратов запускать и т.д.)
        print('RUN ALL', self._mode, self._user)

    @pyqtSlot()
    def auto_start(self):
        # отправить всем из списка
        # запрос, сколько квадратов запускать и т.д.
        print('AUTO START')

    @pyqtSlot()
    def poweroff(self):
        self.server.poweroff()
        os.system("/sbin/shutdown -t now")

    @pyqtSlot()
    def restart(self):
        self.server.restart()
        os.system("/sbin/shutdown -r now")

    @pyqtSlot()
    def connection_thread_stop(self):
        self.connection_thread.th_stop()
        self.updater_thread.th_stop()

    @pyqtSlot()
    def connection_thread_start(self):
        self.connection_thread.th_start()
        self.updater_thread.th_start()


class ListDataMode(QAbstractListModel):
    session = None
    text = 'text'

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.items = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def addData(self, data):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append(data)
        self.endInsertRows()

    def data(self, index, role=Qt.DisplayRole):
        try:
            key = self.roleNames()[role]
            return self.items[index.row()][key.decode('utf-8')]
        except IndexError:
            return QVariant()

    def roleNames(self):
        return {Qt.UserRole + 1: b"text",
                Qt.UserRole + 2: b"myother"}

    def update_data(self):
        # очистка моделей и заполнение заного из таблицы БД
        self.items = []
        _modes = self.session.query(Mode).all()
        [self.addData({self.text: mode.name}) for mode in _modes]

    @pyqtSlot(int, str)
    def change_mode(self, index, text):
        aft_name = self.items[index][self.text]
        self.beginResetModel()
        self.items[index][self.text] = text
        self.endResetModel()

    @pyqtSlot(str)
    def add_mode(self, text):
        self.beginResetModel()
        self.addData({self.text: text})
        self.endResetModel()

    @pyqtSlot()
    def save_db(self):
        modes_db = self.session.query(Mode).all()
        new_modes = []
        for i in range(len(self.items)):
            if len(modes_db) > i:
                modes_db[i].name = self.items[i].get(self.text)
            else:
                new_modes.append(Mode(name=self.items[i].get(self.text)))

        self.session.add_all(new_modes)
        self.session.commit()


class ListDataUser(QAbstractListModel):
    session = None
    text = 'text'

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.items = []

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def addData(self, data):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.items.append(data)
        self.endInsertRows()

    def data(self, index, role=Qt.DisplayRole):
        try:
            key = self.roleNames()[role]
            return self.items[index.row()][key.decode('utf-8')]
        except IndexError:
            return QVariant()

    def roleNames(self):
        return {Qt.UserRole + 1: b"text"}

    def update_data(self):
        # очистка моделей и заполнение заного из таблицы БД
        self.items = []
        _modes = self.session.query(Operator).all()
        [self.addData({self.text: mode.name}) for mode in _modes]

