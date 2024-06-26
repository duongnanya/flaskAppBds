from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, UserMixin

db = SQLAlchemy()

class Type(db.Model):
    __tablename__ = "m_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, description, created_user_id=None, update_user_id=None):
        self.name = name
        self.description = description
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class Province(db.Model):
    __tablename__ = "m_province"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, description, created_user_id=None, update_user_id=None):
        self.name = name
        self.description = description
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class City(db.Model):
    __tablename__ = "m_city"

    id = db.Column(db.Integer, primary_key=True)
    province_id = db.Column(db.Integer, db.ForeignKey("m_province.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    province = db.relationship("Province", backref="cities")

    def __init__(self, province_id, name, description, created_user_id=None, update_user_id=None):
        self.province_id = province_id
        self.name = name
        self.description = description
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class Direction(db.Model):
    __tablename__ = "m_direction"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, description, created_user_id=None, update_user_id=None):
        self.name = name
        self.description = description
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class Role(db.Model):
    __tablename__ = "m_role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, description, created_user_id=None, update_user_id=None):
        self.name = name
        self.description = description
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class Bds(db.Model):
    __tablename__ = "m_bds"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    price_from = db.Column(db.BigInteger)
    price_to = db.Column(db.BigInteger)
    area = db.Column(db.Float)
    address = db.Column(db.String(255))
    bed_room_quantity = db.Column(db.Integer)
    type_id = db.Column(db.Integer, db.ForeignKey("m_type.id"))
    province_id = db.Column(db.Integer, db.ForeignKey("m_province.id"))
    city_id = db.Column(db.Integer, db.ForeignKey("m_city.id"))
    direction_id = db.Column(db.Integer, db.ForeignKey("m_direction.id"))
    sold_flg = db.Column(db.Boolean, nullable=False, default=False)
    published_flg = db.Column(db.Boolean, nullable=False, default=False)
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    type = db.relationship("Type", backref="bds")
    province = db.relationship("Province", backref="bds")
    city = db.relationship("City", backref="bds")
    direction = db.relationship("Direction", backref="bds")
    images = db.relationship("BdsImage", backref="bds")
    users = db.relationship("User", secondary="r_user_bds", backref="bds")

    def __init__(self, title, content, price_from, price_to, area, address, bed_room_quantity, type_id, province_id, city_id, direction_id, sold_flg=False, published_flg=False, created_user_id=None, update_user_id=None):
        self.content = content
        self.title = title
        self.price_from = price_from
        self.price_to = price_to
        self.area = area
        self.address = address
        self.bed_room_quantity = bed_room_quantity
        self.type_id = type_id
        self.province_id = province_id
        self.city_id = city_id
        self.direction_id = direction_id
        self.sold_flg = sold_flg
        self.published_flg = published_flg
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class User(UserMixin, db.Model):
    __tablename__ = "m_user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("m_role.id"))
    img_id = db.Column(db.Integer, db.ForeignKey("m_img.id"))
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    role = db.relationship("Role", backref="users")
    image = db.relationship("Image", backref="user")

    def __init__(self, name, username, password, role_id, img_id, created_user_id=None, update_user_id=None):
        self.name = name
        self.username = username
        self.password = password
        self.role_id = role_id
        self.img_id = img_id
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class Image(db.Model):
    __tablename__ = "m_img"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, filename, created_user_id=None, update_user_id=None):
        self.filename = filename
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class BdsImage(db.Model):
    __tablename__ = "r_bds_img"

    id = db.Column(db.Integer, primary_key=True)
    bds_id = db.Column(db.Integer, db.ForeignKey("m_bds.id"), nullable=False)
    img_id = db.Column(db.Integer, db.ForeignKey("m_img.id"), nullable=False)
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)
    
    bds_rel = db.relationship('Bds', backref='bds_images')
    image = db.relationship('Image', backref='bds_images')

    def __init__(self, bds_id, img_id, created_user_id=None, update_user_id=None):
        self.bds_id = bds_id
        self.img_id = img_id
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class BdsUserRelation(db.Model):
    __tablename__ = "r_user_bds"

    id = db.Column(db.Integer, primary_key=True)
    bds_id = db.Column(db.Integer, db.ForeignKey("m_bds.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("m_user.id"), nullable=False)
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, bds_id, user_id, created_user_id=None, update_user_id=None):
        self.bds_id = bds_id
        self.user_id = user_id
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id

class PriceRange(db.Model):
    __tablename__ = "m_price_range"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price_from = db.Column(db.Numeric(precision=18, scale=2), nullable=False)
    price_to = db.Column(db.Numeric(precision=18, scale=2), nullable=False)
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, price_from, price_to, created_user_id=None, update_user_id=None):
        self.name = name
        self.price_from = price_from
        self.price_to = price_to
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id


class AreaRange(db.Model):
    __tablename__ = "m_area_range"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    area_from = db.Column(db.Integer, nullable=False)
    area_to = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    created_user_id = db.Column(db.Integer)
    update_date = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, area_from, area_to, created_user_id=None, update_user_id=None):
        self.name = name
        self.area_from = area_from
        self.area_to = area_to
        self.created_user_id = created_user_id
        self.update_user_id = update_user_id