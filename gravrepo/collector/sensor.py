# -*- coding: utf-8 -*-
import logging
from typing import Union

from flask import Blueprint, request, jsonify, abort
from flask.views import MethodView

from ..models import db, Configuration, Sensor
from ..auth import api_key_guard

_log = logging.getLogger(__name__)


def get_sensor(name: str) -> Union[Sensor, None]:
    return db.session.query(Sensor).filter_by(sensor_name=name).first()


class SensorView(MethodView):
    @api_key_guard(read=True)
    def get(self, stype: str, name: str):
        sensor = get_sensor(name.upper())
        if sensor is not None:
            resp = {
                "Exists": True,
                "SensorID": sensor.sensor_id
            }
            if sensor.config is not None:
                resp["ConfigID"] = sensor.config_id
                resp["ConfigHash"] = sensor.config.config_hash_sha256
            return jsonify(resp)

        else:
            return jsonify({"Exists": False})

    @api_key_guard(write=True)
    def put(self, stype: str, name: str):
        """Create a new sensor object with optional meter.ini config data"""
        # cfg_hash = request.args.get('cfg', None)

        sensor = get_sensor(name)
        if sensor is None:
            sensor = Sensor(sensor_name=name.upper(),
                            sensor_type=stype.upper())

        # if cfg_hash is not None:
        #     cfg_body = request.get_json()
        #     config = Configuration(config_hash_sha256=cfg_hash, **cfg_body)
        #     db.session.add(config)
        #     db.session.flush()
        #
        #     sensor = Sensor(sensor_name=name.upper(),
        #                     sensor_type=stype.upper(),
        #                     config_id=config.config_id)
        else:
            _log.info('Sensor will be updated in future here')

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
                "SensorName": sensor.sensor_name,
                "SensorID": sensor.sensor_id
            }
            return jsonify(resp)


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
config_view = ConfigurationView.as_view('config_view')

sensor_blueprint = Blueprint('sensor_ops', __name__, url_prefix='/sensor/')
sensor_blueprint.add_url_rule('/<string:stype>/<string:name>',
                              view_func=sensor_view)
sensor_blueprint.add_url_rule('/config/<string:name>',
                              view_func=config_view)
