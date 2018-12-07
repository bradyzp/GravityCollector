# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from math import floor
from typing import List
import logging

from flask import Blueprint, request, jsonify
from flask.views import MethodView

from ..models import db, Data, Sensor

_log = logging.getLogger(__name__)

DEFAULT_WINDOW = timedelta(minutes=60)
DEFAULT_DECIMATION = 10
QUERY_LIMIT = 86400


def js_timestamp(date: datetime):
    return date.timestamp() * 1000


class ResponderView(MethodView):
    def get(self, sid: int, startdate: int):
        """Respond to GET requests for gravity data

        Parameters
        ----------
        sid : int
            Sensor ID to retrieve data for
        startdate : int
            Datetime in milliseconds since UNIX Epoch, query will be filtered to
            data with timestamp greater than this.

        Returns
        -------
        json response

        """
        try:
            decimate = int(request.args['decimate'])
        except (ValueError, KeyError):
            decimate = DEFAULT_DECIMATION

        if decimate < 1:
            decimate = 1

        try:
            # Floor last date to seconds then add 1 to avoid querying duplicate
            # rows where the data timestamp is fractionally greater
            lastdt = datetime.fromtimestamp(floor(startdate / 1000) + 1)
        except (OSError, TypeError):
            _log.error('Invalid timestamp received')
            lastdt = datetime.now() - DEFAULT_WINDOW

        _log.info(f"Last data endpoint has is from {lastdt}")

        result: List[Data] = db.session.query(Data)\
            .filter(Data.sensor_id == sid)\
            .filter(Data.datetime > lastdt)\
            .order_by(Data.datetime.asc())\
            .limit(QUERY_LIMIT)
        data = []
        for i, line in enumerate(result):
            if i % decimate == 0:
                line_dict = {"gravity": float(line.gravity),
                             "datetime": js_timestamp(line.datetime)}
                data.append(line_dict)

        if not len(data):
            return jsonify({"data": [], "sensor": sid})
        else:
            data[-1]['datetime'] = js_timestamp(result[-1].datetime)
            return jsonify({"data": data, "sensor": sid})


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
            last_line: Data = db.session.query(Data) \
                .filter_by(sensor_id=sensor.sensor_id) \
                .order_by(Data.datetime.desc()) \
                .first()
            if last_line is not None:
                sdata['lastdata'] = last_line.datetime.timestamp()

            data.append(sdata)

        return jsonify(data)


responder_blueprint = Blueprint('responder_bp', __name__, url_prefix='/view/')
responder_view = ResponderView.as_view('responder_view')
sensor_list_view = SensorListView.as_view('sensor_list_view')
responder_blueprint.add_url_rule('/<int:sid>/<int:startdate>', view_func=responder_view)
responder_blueprint.add_url_rule('/list', view_func=sensor_list_view)
