from functools import wraps

from flask import redirect
from flask_login import current_user


def authenticated(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            temp = current_user.username
            return func(*args, **kwargs)
        except AttributeError:
            return redirect("/", 301)

    return wrapper