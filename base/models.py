from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.schema import Table
from sqlalchemy.orm import backref

from datetime import datetime

import os
from base.utils import md5


Base = declarative_base()

operator_in_work = Table('operator_in_work', Base.metadata,
                         Column('operator', Integer, ForeignKey('operator.id')),
                         Column('work', Integer, ForeignKey('work.id')))


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    ip = Column(String, index=True)
    name = Column(String, index=True)
    dir_name = Column(String, index=True)
    timestamp = Column(DATETIME, index=True, default=datetime.now)
    config = Column(String, index=True)
    log = Column(String, index=True)

    command_id = Column(Integer, ForeignKey('command.id'))
    state_id = Column(Integer, ForeignKey('state.id'))
    verbose_id = Column(Integer, ForeignKey('verbose.id'))

    defaults = relationship('DefaultConfig', backref='services')

    def __init__(self, ip, name, dir_name):
        self.ip = ip
        self.name = name
        self.dir_name = dir_name

    def __repr__(self):
        return "<Service({name} - {ip} - {dir})>".format(name=self.name, ip=self.ip, dir=self.dir_name)

    def set_state(self, state):
        self.state_id = state.id


class Operator(Base):
    __tablename__ = 'operator'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    dept = Column(String)  # отдел
    work_id = relationship('Work', secondary=operator_in_work, backref=backref('operator_in_work', lazy='dynamic'))

    def __init__(self, name, dept):
        self.name = name
        self.dept = dept

    def __repr__(self):
        return "<Operator> {name}".format(name=self.name)


class DefaultConfig(Base):
    __tablename__ = 'default_config'
    id = Column(Integer, primary_key=True)
    active = Column(Boolean, index=True)
    mode_id = Column(Integer, ForeignKey('mode.id'))
    verbose_id = Column(Integer, ForeignKey('verbose.id'))
    service_id = Column(Integer, ForeignKey('service.id'))

    def __repr__(self):
        return "<default_config>"


class State(Base):
    __tablename__ = 'state'
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, unique=True)
    color = Column(String, index=True)
    service_id = relationship('Service', backref='state')
    runner_id = relationship('Runner', backref='state')

    def __init__(self, name, color):
        self.name = name
        self.color = color

    def __repr__(self):
        return "<State {name} - {color}>".format(name=self.name, color=self.color)


class Command(Base):
    __tablename__ = 'command'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    runner_id = relationship('Runner', backref='command')
    service_id = relationship('Service', backref='command')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Command> {name}".format(name=self.name)


class Runner(Base):
    __tablename__ = 'runner'
    id = Column(Integer, primary_key=True)
    ip = Column(String, unique=True)
    name = Column(String)
    timestamp = Column(DATETIME, default=datetime.now)

    command_id = Column(Integer, ForeignKey('command.id'))
    state_id = Column(Integer, ForeignKey('state.id'))

    dirs = relationship("WorkPlace", backref='runner')

    def __init__(self, ip, name):
        self.ip = ip
        self.name = name

    def __repr__(self):
        return "<Runner {name} - {ip}>".format(name=self.name, ip=self.ip)


class WorkPlace(Base):
    __tablename__ = 'workplace'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    runner_id = Column(Integer, ForeignKey('runner.id'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<WorkPlace {name}>".format(name=self.name)


service_in_work = Table('service_in_work', Base.metadata,
                        Column('work', Integer, ForeignKey('work.id')),
                        Column('service', Integer, ForeignKey('service.id')))


class Work(Base):
    __tablename__ = 'work'
    id = Column(Integer, primary_key=True)
    time_stamp = Column(DATETIME, default=datetime.now)
    task = Column(Integer, unique=True)

    mode_id = Column(Integer, ForeignKey('mode.id'))

    services = relationship('Service', secondary=service_in_work, backref=backref('service_in_work', lazy='dynamic'))
    diag_files = relationship('File', backref='work')

    def __init__(self, task):
        self.task = task

    def __repr__(self):
        return "<Work - {}>".format()


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    index = Column(Integer, index=True)
    name = Column(String(32), index=True)
    path = Column(String(32), index=True)
    type = Column(String(32), index=True)
    size = Column(String(32), index=True)
    md5sum = Column(String(32), index=True)
    arg = Column(String(32), index=True)
    active = Column(Boolean, index=True)
    work_id = Column(Integer, ForeignKey('work.id'))
    verbose_id = Column(Integer, ForeignKey('verbose.id'))

    def add(self, file_name, path):
        self.name = file_name
        self.path = path
        self.type = os.path.splitext(file_name)[1]
        self.size = os.path.getsize(os.path.join(path, file_name))
        self.md5sum = md5(os.path.join(path, file_name))

    def clear(self):
        self.name = ''
        self.path = ''
        self.type = ''
        self.size = ''
        self.md5sum = ''
        self.arg = ''

    def __repr__(self):
        return "<File> {path} - {size}b".format(path=self.path, size=self.size)


class Mode(Base):
    __tablename__ = 'mode'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    active = Column(Boolean,)
    # default_id = Column(Integer, ForeignKey('default_config.id'))
    works = relationship('Work', backref='mode')
    defaults = relationship('DefaultConfig', backref='mode')

    def __init__(self, name):
        self.name = name
        self.active = False

    def __repr__(self):
        return "<Mode> {name}".format(name=self.name)


class Verbose(Base):
    __tablename__ = 'verbose'
    id = Column(Integer, primary_key=True)
    major = Column(Integer)
    minor = Column(Integer)
    patch = Column(Integer)

    defaults = relationship('DefaultConfig', backref='verbose')
    files = relationship('File', backref='verbose')
    services = relationship('Service', backref='verbose')

    def __repr__(self):
        return "<Verbose>"



