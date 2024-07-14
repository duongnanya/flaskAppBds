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

    # MY_EMAIL = "duongnanya@gmail.com"
    # MY_EMAIL_APP_PASSWORD = "jfcn yjxo okfx glci"
    
    MY_EMAIL = "mecland.vn@gmail.com"
    MY_EMAIL_APP_PASSWORD = "qftz tfsy iiyw dovq"

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

    # Message
    MSG_LOGIN_REQUIRED = "Bạn cần đăng nhập để truy cập trang này."
    MSG_FUNC_NOT_AVAILABLE_TO_AE = "Không khả dụng với Admin/Editor."

    # BdsView Count
    MIN_TIME_DIFF = 3
      
    # Số BDS lấy ra và cho hiện ở mục Top xem BDS 
    TOP_CNT = 4
    # Số BDS ở mỗi phân trang
    PER_PAGE = 10