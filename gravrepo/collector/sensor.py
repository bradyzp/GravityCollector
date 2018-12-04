# -*- coding: utf-8 -*-
import logging
from typing import Union, List

from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, jsonify, abort
from flask.views import MethodView

from ..models import db, Configuration, Sensor, Data
from ..auth import api_key_guard

_log = logging.getLogger(__name__)


def get_sensor(name: str) -> Union[Sensor, None]:
    return db.session.query(Sensor).filter_by(sensor_name=name).first()


class SensorView(MethodView):
    @api_key_guard(write=True)
    def put(self, name):
        sensor = Sensor(sensor_name=name, sensor_type="AT1M")
        db.session.add(sensor)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return f"Duplicate value detected {e}"
        else:
            return "Added new sensor"

    @api_key_guard(read=True)
    def get(self, name: str):
        sensor = get_sensor(name.upper())
        if sensor is not None:
            resp = {
                "Valid": True,
                "SensorID": sensor.sensor_id
            }
            if sensor.config is not None:
                resp["ConfigID"] = sensor.config_id
                resp["ConfigHash"] = sensor.config.config_hash_sha256
            return jsonify(resp)

        else:
            return jsonify({"Valid": False})

    # @api_key_guard(write=True)
    def post(self, name: str):
        body = request.get_json()
        sensor_type = request.args.get('type', 'AT1M')
        cfg_hash = request.args.get('cfg', None)
        print(body)

        if cfg_hash is not None:
            config = Configuration(config_hash_sha256=cfg_hash, **body)
            db.session.add(config)
            db.session.flush()

            sensor = Sensor(sensor_name=name.upper(),
                            sensor_type=sensor_type.upper(),
                            config_id=config.config_id)
        else:
            sensor = Sensor(sensor_name=name.upper(),
                            sensor_type=sensor_type.upper())
        db.session.add(sensor)

        try:
            db.session.commit()
        except Exception as e:
            _log.exception(e)
            db.session.rollback()
            return abort(409)
        else:
            resp = {
                "Valid": True,
                "ConfigID": sensor.config_id,
                "SensorID": sensor.sensor_id
            }
            return jsonify(resp)


class SensorListView(MethodView):
    def get(self):
        cfg_fields = request.args.get('fields', None)
        if cfg_fields is not None:
            cfg_fields = cfg_fields.split(',')

        sensors: List[Sensor] = db.session.query(Sensor)
        data = []
        for sensor in sensors:
            config = sensor.config
            if config is not None:
                cfg_data = config.to_dict(cfg_fields)
            else:
                cfg_data = {}
            sdata = {"name": sensor.sensor_name,
                     "type": sensor.sensor_type,
                     "id": sensor.sensor_id,
                     "config": cfg_data
                     }
            last_line: Data = db.session.query(Data)\
                .filter_by(sensor_id=sensor.sensor_id)\
                .order_by(Data.datetime.desc())\
                .first()
            if last_line is not None:
                sdata['lastdata'] = last_line.datetime.timestamp()

            data.append(sdata)

        return jsonify(data)


class ConfigurationView(MethodView):
    @api_key_guard(read=True)
    def get(self, name):
        config = get_sensor(name).config

        return f'Config for {name} g0: {config.g0} cal: {config.GravCal}'

    @api_key_guard(write=True)
    def post(self, name):
        print("Adding new configuration for sensor: " + name)
        return 'Adding new config'


sensor_view = SensorView.as_view('sensor_view')
sensor_list_view = SensorListView.as_view('sensor_list_view')
config_view = ConfigurationView.as_view('config_view')

sensor_blueprint = Blueprint('sensor_ops', __name__, url_prefix='/sensor/')
sensor_blueprint.add_url_rule('/<string:name>',
                              view_func=sensor_view)
sensor_blueprint.add_url_rule('/config/<string:name>',
                              view_func=config_view)
sensor_blueprint.add_url_rule('/list/', view_func=sensor_list_view)
