import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Union

from flask import abort, request

from .models import db, Authorization


_log = logging.getLogger(__name__)


class AuthorizationToken:
    """AuthorizationToken represents an in memory API Token which
    can be validated against an API key to reduce DB queries for
    repeated inserts.

    """
    def __init__(self, key: str):
        self.key: str = key
        self._auth: Authorization = _query_key(self.key)
        self._created = datetime.now()
        self._lifetime = timedelta(seconds=300)

    @property
    def read(self):
        if self._auth is not None:
            return self._auth.auth_read
        return False

    @property
    def write(self):
        if self._auth is not None:
            return self._auth.auth_write
        return False

    @property
    def enabled(self):
        if self._auth is not None:
            return self._auth.auth_enabled

    @property
    def expires(self):
        return self._created + self._lifetime

    @property
    def valid(self):
        return self.enabled and datetime.now() < self.expires


def _query_key(key: str) -> Union[None, Authorization]:
    # return Authorization.query.filter_by(api_key=key).first()
    return db.session.query(Authorization).filter_by(api_key=key).first()


def api_key_guard(read=True, write=False):
    """Guard routes based on Bearer token UUID"""
    def inner(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = request.headers.get('Authorization', None)
            if key is None:
                _log.error("API key is required to access this resource")
                return abort(403)
            else:
                key = key.split()[1]

            token = AuthorizationToken(key)

            if not token.valid:
                _log.debug("Token is invalid")

            if read and not token.read:
                _log.warning("Required Read permission not granted to this token")
                return abort(403)

            if write and not token.write:
                _log.warning("Required Write permission not granted to this token")
                return abort(403)

            _log.debug("API Key is valid")
            return f(*args, **kwargs)
        return wrapped
    return inner


def auth_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        _log.warning("Authorization not implemented yet")
        return f(*args, **kwargs)
    return wrapped
