# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy.exc import DataError

from ..auth import api_key_guard
from ..models import db, Data

_log = logging.getLogger(__name__)


class CollectorView(MethodView):
    @api_key_guard(write=True)
    def post(self, sid: int):
        data = request.json
        _log.info(f'Received {request.content_length} bytes of data')
        count = 0
        for line in data['data']:
            # data['datetime'] = datetime.fromtimestamp(data['datetime'])
            line['datetime'] = datetime.now()
            payload = Data(sensor_id=sid, **line)
            db.session.add(payload)
            count += 1

        try:
            db.session.commit()
        except DataError:
            _log.exception("Exception committing line")
            return jsonify({"Status": "FAIL"})
        else:
            return jsonify({'Status': 'OK', 'Count': count})


collector_blueprint = Blueprint('collector_bp', __name__, url_prefix='/collect/')

collector_view = CollectorView.as_view('collector_view')
collector_blueprint.add_url_rule('/<int:sid>', view_func=collector_view)
