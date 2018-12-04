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
        # data['datetime'] = datetime.fromtimestamp(data['datetime'])
        data['datetime'] = datetime.now()
        line = Data(sensor_id=sid, **data)
        db.session.add(line)

        try:
            db.session.commit()
        except DataError:
            _log.exception("Exception comitting line")
            return jsonify({"Status": "FAIL"})
        else:

            return jsonify({"Status": 'OK', "LineID": line.line_id})


collector_blueprint = Blueprint('collector_bp', __name__, url_prefix='/collect/')

collector_view = CollectorView.as_view('collector_view')
collector_blueprint.add_url_rule('/<int:sid>', view_func=collector_view)
