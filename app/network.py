from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from http import HTTPStatus
import threading
from datetime import datetime
from time import sleep

from PyQt5.QtCore import QObject
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

from base.models import Service
from base.models import Runner
from base.models import WorkPlace
from base.models import Work
from base.models import File
from base.models import State
from base.models import Command
from base.models import Verbose
from base.models import Mode
from base.models import DefaultConfig

from sqlalchemy.orm import scoped_session
import simplejson
import cgi
import os
from shutil import copyfile
from shutil import make_archive
from shutil import rmtree

from base import utils
import base64

Session = None
API_VERSION = '/api/v1'


def create_session(session_factory):
    global Session
    Session = scoped_session(session_factory)
    return Session


class QuietSimpleHTTPRequestHandler(SimpleHTTPRequestHandler):
    """
    Класс для авторизации сервисов. Данные записывает в БД.
    Далее уже будет работать клиентская сторона, а сервер просто будет обновлят данные.
    """

    def do_GET(self):

        print('got GET to {path}'.format(path=self.path))

        if 'source/js/jquery.min.js' in self.path:
            self.path = 'source/js/jquery.min.js'
            return SimpleHTTPRequestHandler.do_GET(self)

        if 'test' in self.path:
            self.path = 'test.html'
            return SimpleHTTPRequestHandler.do_GET(self)

        if 'index' in self.path:
            self.get_services()
            return

        global Session
        session = Session()
        request_ip, request_port = self.request.getpeername()

        if '{api}/runner/command'.format(api=API_VERSION) == self.path:

            runner = session.query(Runner).filter_by(ip=request_ip).first()
            if not runner:
                print('<server> Не нашел runner по ip: ', request_ip)
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                return

            # обновляем время у клиента
            runner.timestamp = datetime.now()
            session.add(runner)
            session.commit()

            self.send_response(HTTPStatus.ACCEPTED)
            self.end_headers()

            data = {'command': runner.command.name}
            self.wfile.write(simplejson.dumps(data).encode())
            return

        if '{api}/service/command'.format(api=API_VERSION) == self.path:
            service = session.query(Service).filter_by(ip=request_ip).filter_by(dir_name=self.headers.get('dir_name')).first()
            if not service:
                print('<server> Не нашел service по ip и dir_name: ', request_ip, self.headers.get('dir_name'))
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                return
            service.timestamp = datetime.now()
            session.add(service)
            session.commit()

            self.send_response(HTTPStatus.ACCEPTED)
            self.end_headers()

            data = {'command': service.command.name}
            if service.command.name == 'start':
                mode = session.query(Mode).filter_by(active=True).first()
                if not mode:
                    data['command'] = 'not_start'
                    self.wfile.write(simplejson.dumps(data).encode())
                    return

                default_config = session.query(DefaultConfig).filter_by(service_id=service.id).filter_by(mode_id=mode.id).first()
                if not default_config:
                    data['command'] = 'not_start'
                    self.wfile.write(simplejson.dumps(data).encode())
                    return
                elif default_config.active:
                    #  запись параметров запуска args, conf
                    ARG = 'arg_{index}'
                    COMF = 'comf_{index}'
                    data['mode'] = mode.name
                    rows = session.query(File).filter_by(verbose_id=default_config.verbose_id).all()
                    for row in rows:
                        key_arg = ARG.format(index=row.index+1)  # +1 т.к. указывают индексы в конфиге с 1
                        data[key_arg] = row.arg
                        key_comf = COMF.format(index=row.index+1)  # +1 т.к. в конфиге индексы с 1
                        data[key_comf] = row.name

                else:
                    data['command'] = 'not_start'

            self.wfile.write(simplejson.dumps(data).encode())
            return

        if '{api}/service/update'.format(api=API_VERSION) == self.path:
            service = session.query(Service).filter_by(ip=request_ip).filter_by(
                dir_name=self.headers.get('dir_name')).first()
            if not service:
                print('<server> Не нашел service по ip и dir_name: ', request_ip, self.headers.get('dir_name'))
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                return
            service.timestamp = datetime.now()
            session.add(service)
            session.commit()

            self.send_response(HTTPStatus.ACCEPTED)
            self.end_headers()
            print('service.defaults', service.defaults)
            tmp = "/tmp"

            if service.defaults:
                dir_archiving = os.path.join(tmp, service.name)
                if os.path.isdir(dir_archiving):
                    rmtree(dir_archiving)
                os.mkdir(dir_archiving)
                for config in service.defaults:
                    mode_path = os.path.join(dir_archiving, config.mode.name)
                    os.mkdir(mode_path)
                    for file in config.verbose.files:
                        copyfile(os.path.join(file.path, file.name), os.path.join(mode_path, file.name))
                archive_name = make_archive(service.name, "tar", root_dir=dir_archiving)
                archive_path = os.path.abspath(archive_name)
                md5sum = utils.md5(archive_path)
                data_content = open(archive_path, 'rb').read()
                encoded_content = base64.b64encode(bytes(data_content))
                data = {'md5sum': md5sum, 'data': encoded_content, 'file_name': service.name+".tar"}
            else:
                data = {'file': 'not_found'}  # признак отсутствия файлов

            self.wfile.write(simplejson.dumps(data).encode())
            return

        if '{api}/service/config'.format(api=API_VERSION) == self.path:
            service = session.query(Service).filter_by(ip=request_ip).filter_by(
                dir_name=self.headers.get('dir_name')).first()
            if not service:
                print('<server> Не нашел service по ip и dir_name: ', request_ip, self.headers.get('dir_name'))
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
                return
            service.timestamp = datetime.now()
            session.add(service)
            session.commit()

            self.send_response(HTTPStatus.ACCEPTED)
            self.end_headers()
            data = {'config': service.config}
            self.wfile.write(simplejson.dumps(data).encode())

    def get_services(self):
        global Session
        self.send_response(HTTPStatus.ACCEPTED)
        self.end_headers()

        session = Session()
        services = session.query(Service).all()

        data = dict()
        for service in services:
            data[service.dir_name] = {'id': service.id,
                                      'name': service.name,
                                      'ip': service.ip}
        self.wfile.write(simplejson.dumps(data).encode())

    def do_POST(self):
        print('got POST to {path}'.format(path=self.path))

        global Session
        session = Session()
        request_ip, request_port = self.request.getpeername()
        content_length = int(self.headers.get('Content-Length'))

        content_type, pdict = cgi.parse_header(self.headers.get('content-type'))
        data = dict()

        if content_type == 'application/json':
            post_body = self.rfile.read(content_length)
            data = simplejson.loads(post_body)
        elif content_type == 'multipart/form-data':
            # ошибка если использовать str
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            data = cgi.parse_multipart(self.rfile, pdict)

        print('post data', data)

        if '{api}/service/diag'.format(api=API_VERSION) == self.path:
            self.create_diagnostic(request_ip, data, session)
            return

        if '{api}/service'.format(api=API_VERSION) == self.path:
            self.create_service(request_ip, data, session)
            return

        if '{api}/runner'.format(api=API_VERSION) == self.path:
            self.create_runner(request_ip, data, session)
            self.change_workplace(request_ip, data, session)
            return

        return SimpleHTTPRequestHandler.do_GET(self)

    def create_service(self, request_ip, data, session):
        # проверка отсутсвия записи в БД
        machine_service = session.query(Service).filter_by(ip=request_ip).filter_by(
            dir_name=self.headers.get('dir_name')).all()

        # проверка доступа для создания записи(проверяем по workplace который передал runner, если есть, то только PUT)
        runner = session.query(Runner).filter_by(ip=request_ip).first()
        if not runner:
            # передать 401
            self.send_response(HTTPStatus.UNAUTHORIZED)
            self.end_headers()
            return

        if not runner.dirs:
            # передать 401
            self.send_response(HTTPStatus.UNAUTHORIZED)
            self.end_headers()
            return
        for place in runner.dirs:
            if place.name == data.get('name'):
                print('<server> Такое имя в workplace уже есть')
                self.send_response(HTTPStatus.CONFLICT)
                self.end_headers()
                return

        if not machine_service:
            service = Service(ip=request_ip, name=data.get('name'),
                              dir_name=self.headers.get('dir_name'))
            try:
                session.add(service)
                session.commit()
            except Exception as error:
                print('<server> {error}'.format(error=error))
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.end_headers()
                return
            self.send_response(HTTPStatus.CREATED)
            self.end_headers()
        else:
            self.send_response(HTTPStatus.CONFLICT)
            print('<server http> Повторная запись недопустима, только PUT')
            self.end_headers()

    def create_runner(self, request_ip, data, session):
        # проверка отсутсвия записи в БД
        runner = session.query(Runner).filter_by(ip=request_ip).first()
        if not runner:
            runner = Runner(ip=request_ip, name=data.get('name'))
            runner.state = session.query(State).filter_by(name='online').first()
            runner.command = session.query(Command).filter_by(name='state').first()
            try:
                session.add(runner)
                session.commit()
                self.send_response(HTTPStatus.CREATED)
                self.end_headers()
            except Exception as error:
                print('<server> {error}'.format(error=error))
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.end_headers()
                return
        else:
            self.send_response(HTTPStatus.CONFLICT)
            print('<server> Повторная запись недопустима, только PUT. runner: ', runner)
            self.end_headers()

    def change_workplace(self, request_ip, data, session):
        # создание директорий, после регистрации runner-а
        runner = session.query(Runner).filter_by(ip=request_ip).first()

        # проверка на повторение имен
        if runner:
            workplaces = runner.dirs
        else:
            # если runner уже был создан, то ничего проводить не надо.
            return

        # сравниваем, если нет в списке, то добавляем.
        client_dirs = data.get('dirs', [])
        server_dirs = [_.name for _ in workplaces]

        for place in client_dirs:
            if place not in server_dirs:
                server_dirs.append(place)
                new_workplace = WorkPlace(place)
                new_workplace.runner_id = runner.id
                session.add(new_workplace)
        session.commit()

    def create_diagnostic(self, request_ip, fields, session):
        service = session.query(Service).filter_by(ip=request_ip).filter_by(
            dir_name=self.headers.get('dir_name')).first()
        if not service:
            print('<server> Нет сервиса по id ', self.headers.get('dir_name'))
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        local_path = os.path.abspath(os.path.dirname(__file__))
        service_dir = '{name}_{ip}'.format(name=service.dir_name, ip=service.ip.split('.')[-1])
        diag_path = os.path.join(local_path, 'diag', datetime.now().isoformat(), service_dir)

        if not os.path.isdir(diag_path):
            os.makedirs(diag_path)

        for file_name, content in fields.items():
            abs_file_path = os.path.join(diag_path, file_name)
            abs_path = os.path.dirname(abs_file_path)
            # для подкаталогов в дигностике
            if not os.path.isdir(abs_path):
                os.makedirs(abs_path)

            with open(abs_file_path, 'wb') as _file:
                for line in content:
                    _file.write(line)
        self.send_response(HTTPStatus.ACCEPTED)
        self.end_headers()

    def do_PUT(self):

        print('got PUT to {path}'.format(path=self.path))
        global Session
        session = Session()

        content_length = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_length)
        data = simplejson.loads(post_body)
        request_ip, request_port = self.request.getpeername()

        print('PUT', data)

        if '{api}/service'.format(api=API_VERSION) == self.path:

            chenge_data = session.query(Service).filter_by(ip=request_ip).filter_by(
                dir_name=self.headers.get('dir_name')).first()
            if chenge_data:
                chenge_data.name = data.get('name')
                chenge_data.timestamp = datetime.now()

                try:
                    session.add(chenge_data)
                    session.commit()
                except Exception as error:
                    print(error)
                    self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                    self.end_headers()
                    return
                self.send_response(HTTPStatus.ACCEPTED)
                self.end_headers()
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                print('<server http> Нет данных для изменения')
                self.end_headers()
            return

        if '{api}/service/state'.format(api=API_VERSION) == self.path:
            service = session.query(Service).filter_by(ip=request_ip).filter_by(
                dir_name=self.headers.get('dir_name')).first()
            state = session.query(State).filter_by(name=data.get('state')).first()
            if not state:
                print('<PUT> Ошибка статуса')
            else:
                # TODO: посик команды через БД, для последующего редатирования в графике(статус - команда)
                if data.get('state') == 'launched':
                    service.command = session.query(Command).filter_by(name='config').first()

                if data.get('state') == 'started':
                    service.command = session.query(Command).filter_by(name='wait').first()

                if data.get('state') == 'not_started':
                    print('<network> Ошибка запуска сервиса. error = ', data.get('error'))

                if data.get('state') == 'stopped':
                    service.command = session.query(Command).filter_by(name='wait').first()

                if data.get('state') == 'not_stopped':
                    print('<network> Ошибка остановки сервиса. error = ', data.get('error'))

                if data.get('state') == 'error_work':
                    print('<network> Ошибка остановки сервиса. error = ', data.get('error'))

                if data.get('state') == 'ready_diag':
                    service.command = session.query(Command).filter_by(name='diag').first()

                if data.get('state') == 'error_diag':
                    service.command = session.query(Command).filter_by(name='wait').first()

                if data.get('state') == 'sended_diag':
                    service.command = session.query(Command).filter_by(name='wait').first()

                if data.get('state') == 'sended_config':
                    service.command = session.query(Command).filter_by(name='wait').first()

                if data.get('state') == 'error_config':
                    service.command = session.query(Command).filter_by(name='wait').first()

                if data.get('state') == 'error_update':
                    service.command = session.query(Command).filter_by(name='stop').first()

                if data.get('state') == 'not_updated':
                    # повторяем обновление, до error. Клиент сам решит, когда прекратить попытки обновления.
                    service.command = session.query(Command).filter_by(name='update').first()

                if data.get('state') == 'updated':
                    service.command = session.query(Command).filter_by(name='wait').first()

                service.set_state(state)
                session.add(service)
                session.commit()

        if '{api}/service/config'.format(api=API_VERSION) == self.path:
            service = session.query(Service).filter_by(ip=request_ip).filter_by(
                dir_name=self.headers.get('dir_name')).first()

            service.config = data.get('config')

            try:
                session.add(service)
                session.commit()
            except Exception as error:
                print(error)
                self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
                self.end_headers()
                return
            self.send_response(HTTPStatus.ACCEPTED)
            self.end_headers()
            return

        if '{api}/runner/state'.format(api=API_VERSION) == self.path:
            runner = session.query(Runner).filter_by(ip=request_ip).first()
            if runner:

                if data.get('state') == 'launched':
                    runner.command = session.query(Command).filter_by(name='dirs').first()

                if data.get('state') == 'send_dirs':
                    runner.command = session.query(Command).filter_by(name='start').first()

                if data.get('state') == 'started':
                    runner.command = session.query(Command).filter_by(name='wait').first()

                if data.get('state') == 'not_started':
                    runner.command = session.query(Command).filter_by(name='wait').first()
                    # TODO: отобразить оператору ошибку запуска сервисов
                    print('<server> Ошибка Runner {ip}. {data}'.format(ip=runner.ip,
                                                                           data=data.get('error')))

                if data.get('state') == 'stopped':
                    runner.command = session.query(Command).filter_by(name='wait').first()

                if data.get('state') == 'not_stopped':
                    runner.command = session.query(Command).filter_by(name='wait').first()
                    # TODO: отобразить оператору ошибку остановки сервисов
                    print('<server> Ошибка Runner {ip}. {data}'.format(ip=runner.ip,
                                                                           data=data.get('error')))
                session.add(runner)
                session.commit()

        if '{api}/runner/dirs'.format(api=API_VERSION) == self.path:
            runner = session.query(Runner).filter_by(ip=request_ip).first()
            # TODO допилить обновление dirs
            if runner:
                pass

        if '{api}/runner'.format(api=API_VERSION) == self.path:
            print(data)
            runner = session.query(Runner).filter_by(ip=request_ip).first()
            if runner:
                runner.name = data.get('name')
                runner.timestamp = datetime.now()
                runner.state = session.query(State).filter_by(name='state').first()
                session.add(runner)
                session.commit()
                self.change_workplace(request_ip, data, session)
                self.send_response(HTTPStatus.ACCEPTED)
                self.end_headers()
            else:
                print('<server> Нет runner в БД: {host}'.format(host=request_ip))
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
            return

        return SimpleHTTPRequestHandler.do_GET(self)

    def log_message(self, *args):
        pass


class ThreadedHTTPServer(QObject):

    def __init__(self, host, port, request_handler=SimpleHTTPRequestHandler):
        super(ThreadedHTTPServer, self).__init__()
        HTTPServer.allow_reuse_address = True
        self.server = HTTPServer((host, port), request_handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        global Session
        self.session = Session()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()

    def restart(self):
        print('<server> restart')
        runners = self.session.query(Runner).all()
        for runner in runners:
            runner.command = self.session.query(Command).filter_by(name='restart').first()
            self.session.add(runner)
        self.session.commit()

    def poweroff(self):
        print('<server> poweroff')
        runners = self.session.query(Runner).all()
        for runner in runners:
            runner.command = self.session.query(Command).filter_by(name='poweroff').first()
            self.session.add(runner)
        self.session.commit()


class UpdaterModel(QThread):
    """
    Класс проверяет изменения данных в БД, при изменении отправляет сигнал.
    """
    session = None
    update = pyqtSignal(Service)
    create = pyqtSignal(Service)
    delete = pyqtSignal(Service)
    time = datetime.now()
    dirs = dict()
    stop = False

    def __init__(self):
        super(UpdaterModel, self).__init__()

    def control_dirs(self, model):
        # проверяем, существует ли модель, если нет, то добавляем в память

        if model.ip not in self.dirs:
            self.dirs.update({model.ip: [model.dir_name]})
            print('<UpdaterModel> create', self.dirs)
            return False

        if model.dir_name not in self.dirs.get(model.ip):
            self.dirs.get(model.ip).append(model.dir_name)
            print('<UpdaterModel> append', self.dirs)
            return False
        return True

    def control_delete(self):
        for ip in self.dirs:
            for _dir in self.dirs.get(ip):
                service = self.session.query(Service).filter_by(dir_name=_dir).first()
                if not service:
                    self.dirs.get(ip).remove(_dir)
                    self.delete.emit(Service(ip=ip, name=None, dir_name=_dir))

    def control_models(self):
        models = self.session.query(Service).all()
        for model in models:
            # распределение по IP адресам
            if self.control_dirs(model):
                # контроль последнего изменения
                if self.time < model.timestamp:
                    self.time = model.timestamp
                    self.update.emit(model)
            else:
                # создание нового куба
                self.time = model.timestamp
                self.create.emit(model)

            # проверка на удаление
            self.control_delete()

    def run(self):
        global Session
        self.session = Session()
        while True:
            if not self.stop:
                self.control_models()
            sleep(1)

    def th_stop(self):
        self.stop = True

    def th_start(self):
        self.stop = False


class ControlStatusModel(QThread):
    """
    Класс контролирует по времени и изменяет статуы сервисов.
    """
    session = None
    change_state = pyqtSignal(Service)
    stop = False

    def __init__(self):
        super(ControlStatusModel, self).__init__()

    def run(self):
        global Session
        self.session = Session()
        while True:
            if not self.stop:
                self.control_state()
            sleep(1)

    def control_state(self):
        offline = self.session.query(State).filter_by(name='offline').first()
        # online = self.session.query(State).filter_by(name='online').first()
        services = self.session.query(Service).all()
        for service in services:
            tdelta = datetime.now()-service.timestamp
            seconds = tdelta.total_seconds()
            if seconds > 3:
                service.state = offline
            # else:
            #     service.state = online
            self.session.add(service)
            self.change_state.emit(service)
        self.session.commit()

    def th_stop(self):
        self.stop = True

    def th_start(self):
        self.stop = False


if __name__ == '__main__':
    class Model:
        ip = 'localhost'
        port = '123'
        dir_name = 'tmp'

    updater = UpdaterModel()
    updater.dirs = {'1': ['a', 'b', 'c']}
    print(updater.control_dirs(Model()))
    print(updater.control_dirs(Model()))
    print(updater.dirs)
