from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID, JSONB, NUMERIC
from flask_sqlalchemy import SQLAlchemy

__all__ = ['db', 'Configuration', 'Data', 'Sensor', 'Authorization']

db = SQLAlchemy()


class Configuration(db.Model):
    """The Configuration table holds gravity sensor configuration parameters

    A single sensor may have multiple configurations
    """
    __tablename__ = "gr_configuration"

    config_id = db.Column(db.SmallInteger, primary_key=True)
    config_hash_sha256 = db.Column(db.VARCHAR(64))
    g0 = db.Column(NUMERIC(12, 6))
    grav_cal = db.Column(NUMERIC(12, 6))
    beam_gain = db.Column(NUMERIC(12, 6))
    beam_zero = db.Column(NUMERIC(12, 6))
    long_cal = db.Column(NUMERIC(12, 6))
    cross_cal = db.Column(NUMERIC(12, 6))
    long_offset = db.Column(NUMERIC(12, 6))
    cross_offset = db.Column(NUMERIC(12, 6))
    s_temp_gain = db.Column(NUMERIC(12, 6))
    s_temp_offset = db.Column(NUMERIC(12, 6))
    e_temp_gain = db.Column(NUMERIC(12, 6))
    e_temp_offset = db.Column(NUMERIC(12, 6))
    pressure_gain = db.Column(NUMERIC(12, 6))
    pressure_offset = db.Column(NUMERIC(12, 6))

    sensor = db.relationship('Sensor', back_populates='config')

    def to_dict(self, fields=None):
        data = {}
        print(f'fields is: {fields}')
        if fields is None:
            print('fields is none')
            keys = [key for key in self.__dict__.keys() if not key.startswith('_')]
        else:
            keys = [key for key in self.__dict__.keys() if key in fields]

        print(f'Keys: {keys}')
        for field in keys:
            try:
                data[field] = float(self.__dict__[field])
            except (KeyError, ValueError, TypeError):
                continue
        return data


class SensorType(db.Model):
    __tablename__ = "gr_sensor_type"
    sensor_type = db.Column(db.VARCHAR(16), primary_key=True)


class Sensor(db.Model):
    __tablename__ = "gr_sensor"

    sensor_id = db.Column(db.SmallInteger, primary_key=True)
    sensor_name = db.Column(db.String, unique=True, nullable=False)
    sensor_type = db.Column(db.String, db.ForeignKey(SensorType.sensor_type))
    config_id = db.Column(db.SmallInteger, db.ForeignKey(Configuration.config_id))
    config = db.relationship('Configuration')


class Data(db.Model):
    __tablename__ = "gr_data"

    line_id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.SmallInteger, db.ForeignKey(Sensor.sensor_id),
                          nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    gravity = db.Column(db.DECIMAL(12, 6), nullable=False)
    long_acc = db.Column(db.NUMERIC(12, 6))
    cross_acc = db.Column(db.NUMERIC(12, 6))
    beam = db.Column(db.NUMERIC(16, 8))
    s_temperature = db.Column(db.NUMERIC(10, 4))
    e_temperature = db.Column(db.NUMERIC(10, 4))
    pressure = db.Column(db.NUMERIC(10, 4))
    latitude = db.Column(db.NUMERIC(10, 4))
    longitude = db.Column(db.NUMERIC(10, 4))
    sensor = db.relationship('Sensor')

    def __repr__(self):
        return f'<Data DateTime {self.datetime} Gravity {self.gravity}>'


class Authorization(db.Model):
    __tablename__ = "gr_auth"

    api_key = db.Column(UUID, primary_key=True)
    friendly_name = db.Column(db.String)
    email = db.Column(db.String, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now())
    auth_read = db.Column(db.Boolean, default=True)
    auth_write = db.Column(db.Boolean)
    auth_enabled = db.Column(db.Boolean, default=False)
