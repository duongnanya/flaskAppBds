import os


class Config:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "duongnn")
    DB_HOST = os.getenv("DB_HOST", "localhost:5432")
    DB_NAME = "flask_app_bds"
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )
    SECRET_KEY = "duongnn_secret_key"  # Khai báo SECRET_KEY

    MY_EMAIL = "duongnanya@gmail.com"
    MY_EMAIL_APP_PASSWORD = "jfcn yjxo okfx glci"

    UPLOAD_FOLDER = "static\\uploads\\"

    # User's Role
    ROLE_ADMIN = 1
    ROLE_EDITOR = 2
    ROLE_USER = 3

    # Post's Status
    STATUS_DRAFT = 1
    STATUS_PENDING = 2
    STATUS_NEED_FIX = 3
    STATUS_OK = 4
    STATUS_PUBLISHED = 5