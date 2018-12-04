# -*- coding: utf-8 -*-

from datetime import datetime
from uuid import uuid4

from flask import Blueprint, request, make_response
from flask.views import MethodView
from sqlalchemy.exc import IntegrityError

from ..auth import auth_required
from ..models import db, Authorization


registration_blueprint = Blueprint('auth_ops', __name__, url_prefix='/auth/')


class RegistrationView(MethodView):
    @auth_required
    def post(self):
        auth = Authorization(api_key=str(uuid4()),
                             friendly_name=request.form['friendlyname'],
                             email=request.form['username'],
                             created_date=datetime.now(),
                             auth_read=True,
                             auth_write=True,
                             auth_enabled=True)
        db.session.add(auth)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return make_response('Integrity error', 409)
        return f'New authorization created, auth ID: {auth.auth_id}'

    @auth_required
    def get(self, api_key: str):
        auth: Authorization = db.session.query(Authorization).filter_by(ApiKey=api_key).first()
        if auth is not None:
            return f'Auth: {auth.api_key}, FN: {auth.friendly_name}'
        return 'No authorization found'


auth_view = RegistrationView.as_view('auth_view')

registration_blueprint.add_url_rule('/register',
                                    view_func=auth_view,
                                    methods=['POST'])
registration_blueprint.add_url_rule('/view/<string:api_key>',
                                    view_func=auth_view,
                                    methods=['GET'])
