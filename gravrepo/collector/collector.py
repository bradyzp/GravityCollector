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
    """The CollectorView receives data from sensors and inserts it into the DB

    """
    @api_key_guard(write=True)
    def post(self, sid: int):
        """

        The POST handler expects a JSON payload containing a single "data" key
        mapped to a variable length list of data-line objects e.g.:

        >>> {
        >>>    "data": [
        >>>         {"gravity": 12345.0, "datetime": 512311231, ...},
        >>>         {"gravity": 12346.1, "datetime": 512314121, ...}
        >>>    ]
        >>> }

        Parameters
        ----------
        sid: int
            Sensor ID to which the data relates

        Returns
        -------
        JSON
            JSON object with "Status" key and value of FAIL or OK
            If Status is OK, object will contain a "Count" key with the number
            of records successfully parsed and inserted into the database

        """
        data = request.json
        _log.info(f'Received {request.content_length} bytes of data')
        count = 0
        for line in data['data']:
            try:
                line['datetime'] = datetime.fromtimestamp(line['datetime'])
            except (OSError, TypeError):
                _log.exception(f'Error converting timestamp: {line["datetime"]}')
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
