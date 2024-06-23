from functools import wraps
from flask import abort
from flask_login import current_user, login_required
from config import Config


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user is not None or current_user.is_authenticated:
            if current_user.role_id != Config.ROLE_ADMIN:
                abort(403)  # Hoặc redirect đến trang 403
        return func(*args, **kwargs)

    return decorated_view


def admin_editor_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if current_user is not None or current_user.is_authenticated:
            if (
                current_user.role_id != Config.ROLE_ADMIN
                and current_user.role_id != Config.ROLE_EDITOR
            ):
                abort(403)  # Hoặc redirect đến trang 403
        return func(*args, **kwargs)

    return decorated_view


def format_currency(value):
    if value >= 1000000000:
        return f"{value / 1000000000:.1f} tỷ"
    elif value >= 1000000:
        return f"{value / 1000000:.1f} triệu"
    elif value >= 1000:
        return f"{value / 1000:.1f} nghìn"
    else:
        return str(value)