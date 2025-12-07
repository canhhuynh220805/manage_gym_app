from functools import wraps
from flask import session, request, redirect, url_for
from flask_login import current_user


def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login_view', next=request.url))

            if current_user.user_role != role:
                return redirect(url_for('index'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator