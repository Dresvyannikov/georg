# -*- coding: utf-8 -*-
"""
Файл инициализации приложения
"""
import sys
import os
from PyQt5.QtGui import QGuiApplication

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QUrl

from PyQt5.QtQml import QQmlApplicationEngine

from app.models import ListDataCube
from app.models import MainWindow
from app.models import ListDataMode
from app.models import ListDataUser

from app.network import ThreadedHTTPServer
from app.network import QuietSimpleHTTPRequestHandler
from app.network import create_session
from app.network import UpdaterModel
from app.network import ControlStatusModel

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from base.models import Base
from base.models import State
from base.models import Command
from base.models import Mode
from base.models import Operator


def make_connection(signal, fun):
    signal.connect(fun)


sql_engine = create_engine('sqlite:///' + os.path.dirname(os.path.abspath(sys.argv[0])) + '/base/app.db?check_same_thread=False',
                           echo=False)
Base.metadata.create_all(sql_engine)
Session = session_factory = sessionmaker(bind=sql_engine)

# заполняем БД справочной информацией состояний клиента
session = Session()
create_session(session_factory)

if not session.query(State).all():
    offline_state = State(name='offline', color="gray")
    online_state = State(name='online', color="#9cdb8c")
    error_state = State(name='error', color="red")
    launched = State(name='launched', color="#9cdb8c")
    started = State(name='started', color="#9cdb8c")
    not_started = State(name='not_started', color="red")
    stopped = State(name='stopped', color="#9cdb8c")
    not_stopped = State(name='not_stopped', color="red")
    error_work = State(name='error_work', color="red")
    error_diag = State(name='error_diag', color="red")
    ready_diag = State(name='ready_diag', color="#9cdb8c")
    sended_diag = State(name='sended_diag', color="#9cdb8c")
    sended_config = State(name='sended_config', color="#9cdb8c")
    error_config = State(name='error_config', color="red")
    config_set = State(name='config_set', color="#9cdb8c")
    error_set_config = State(name='error_set_config', color="red")
    updated = State(name='updated', color='#9cdb8c')
    not_updated = State(name='not_updated', color='yellow')
    error_update = State(name='error_update', color="red")
    not_found_file = State(name='not_found_file', color="red")

    session.add_all([offline_state, online_state, error_state, launched, started, not_started, stopped, not_stopped,
                     error_work, error_diag, ready_diag, sended_diag, sended_config, error_config, config_set,
                     error_set_config, updated, not_updated,  error_update, not_found_file])
    session.commit()

if not session.query(Command).all():
    wait = Command(name='wait')
    start = Command(name='start')
    stop = Command(name='stop')
    off = Command(name='poweroff')
    restart = Command(name='restart')
    state = Command(name='state')
    dirs = Command(name='dirs')
    diag = Command(name='diag')
    config = Command(name='config')
    set_config = Command(name='set_config')
    update = Command(name='update')

    session.add_all([wait, start, stop, off, restart, state, dirs, diag, config, set_config, update])
    session.commit()

if not session.query(Operator).all():
    admin = Operator('admin', '332')
    session.add(admin)
    session.commit()


QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()
ctx = engine.rootContext()

main_window = MainWindow()
main_window.session = session
ctx.setContextProperty("main_window", main_window)

list_data_cube = ListDataCube()
list_data_cube.session = session
ctx.setContextProperty("list_data_cube", list_data_cube)
list_data_mode = ListDataMode()
list_data_mode.session = session
list_data_mode.update_data()
ctx.setContextProperty("list_data_mode", list_data_mode)

list_data_user = ListDataUser()
list_data_user.session = session
list_data_user.update_data()
ctx.setContextProperty("list_data_user", list_data_user)

engine.load(QUrl.fromLocalFile("view/main.qml"))

handler = QuietSimpleHTTPRequestHandler
with ThreadedHTTPServer("localhost", 8000, request_handler=handler) as main_window.server:
    # поток проверки БД на обновление
    updater = UpdaterModel()
    main_window.updater_thread = updater
    make_connection(updater.update, list_data_cube.change_data)
    make_connection(updater.create, list_data_cube.create_data)
    make_connection(updater.delete, list_data_cube.delete_data)
    updater.start()

    state_control = ControlStatusModel()
    main_window.connection_thread = state_control
    make_connection(state_control.change_state, list_data_cube.change_data)
    state_control.start()

    list_data_mode.set_gui_setting()

    engine.quit.connect(app.quit)
    sys.exit(app.exec_())



