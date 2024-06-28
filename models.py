from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, UserMixin

db = SQLAlchemy()

class Type(db.Model):
    __tablename__ = "c_type"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, description, create_user_id=None, update_user_id=None):
        self.name = name
        self.description = description
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class Province(db.Model):
    __tablename__ = "c_province"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, description, create_user_id=None, update_user_id=None):
        self.name = name
        self.description = description
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class City(db.Model):
    __tablename__ = "c_city"

    id = db.Column(db.Integer, primary_key=True)
    province_id = db.Column(db.Integer, db.ForeignKey("c_province.id"), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    province = db.relationship("Province", backref="cities")

    def __init__(self, province_id, name, description, create_user_id=None, update_user_id=None):
        self.province_id = province_id
        self.name = name
        self.description = description
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class Direction(db.Model):
    __tablename__ = "c_direction"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, description, create_user_id=None, update_user_id=None):
        self.name = name
        self.description = description
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class Role(db.Model):
    __tablename__ = "c_role"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, description, create_user_id=None, update_user_id=None):
        self.name = name
        self.description = description
        self.create_user_id = create_user_id
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
    type_id = db.Column(db.Integer, db.ForeignKey("c_type.id"))
    province_id = db.Column(db.Integer, db.ForeignKey("c_province.id"))
    city_id = db.Column(db.Integer, db.ForeignKey("c_city.id"))
    direction_id = db.Column(db.Integer, db.ForeignKey("c_direction.id"))
    sold_flg = db.Column(db.Boolean, nullable=False, default=False)
    published_flg = db.Column(db.Boolean, nullable=False, default=False)
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    type = db.relationship("Type", backref="bds")
    province = db.relationship("Province", backref="bds")
    city = db.relationship("City", backref="bds")
    direction = db.relationship("Direction", backref="bds")
    images = db.relationship("BdsImage", backref="bds")
    users = db.relationship("User", secondary="r_bds_user", backref="bds")

    def __init__(self, title, content, price_from, price_to, area, address, bed_room_quantity, type_id, province_id, city_id, direction_id, sold_flg=False, published_flg=False, create_user_id=None, update_user_id=None):
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
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class User(UserMixin, db.Model):
    __tablename__ = "m_user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("c_role.id"))
    img_id = db.Column(db.Integer, db.ForeignKey("m_img.id"))
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    role = db.relationship("Role", backref="users")
    image = db.relationship("Image", backref="user")

    def __init__(self, name, username, password, role_id, img_id, create_user_id=None, update_user_id=None):
        self.name = name
        self.username = username
        self.password = password
        self.role_id = role_id
        self.img_id = img_id
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class Image(db.Model):
    __tablename__ = "m_img"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, filename, create_user_id=None, update_user_id=None):
        self.filename = filename
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class BdsImage(db.Model):
    __tablename__ = "r_bds_img"

    id = db.Column(db.Integer, primary_key=True)
    bds_id = db.Column(db.Integer, db.ForeignKey("m_bds.id"), nullable=False)
    img_id = db.Column(db.Integer, db.ForeignKey("m_img.id"), nullable=False)
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)
    
    bds_rel = db.relationship('Bds', backref='bds_images')
    image = db.relationship('Image', backref='bds_images')

    def __init__(self, bds_id, img_id, create_user_id=None, update_user_id=None):
        self.bds_id = bds_id
        self.img_id = img_id
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class BdsUserRelation(db.Model):
    __tablename__ = "r_bds_user"

    id = db.Column(db.Integer, primary_key=True)
    bds_id = db.Column(db.Integer, db.ForeignKey("m_bds.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("m_user.id"), nullable=False)
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, bds_id, user_id, create_user_id=None, update_user_id=None):
        self.bds_id = bds_id
        self.user_id = user_id
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class PriceRange(db.Model):
    __tablename__ = "c_price_range"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price_from = db.Column(db.Numeric(precision=18, scale=2), nullable=False)
    price_to = db.Column(db.Numeric(precision=18, scale=2), nullable=False)
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, price_from, price_to, create_user_id=None, update_user_id=None):
        self.name = name
        self.price_from = price_from
        self.price_to = price_to
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class AreaRange(db.Model):
    __tablename__ = "c_area_range"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    area_from = db.Column(db.Integer, nullable=False)
    area_to = db.Column(db.Integer, nullable=False)
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, name, area_from, area_to, create_user_id=None, update_user_id=None):
        self.name = name
        self.area_from = area_from
        self.area_to = area_to
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id

class BdsTypeRelation(db.Model):
    __tablename__ = "r_bds_type"

    id = db.Column(db.Integer, primary_key=True)
    bds_id = db.Column(db.Integer, db.ForeignKey("m_bds.id"), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey("c_type.id"), nullable=False)
    create_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp())
    create_user_id = db.Column(db.Integer, nullable=False)
    update_dt = db.Column(db.TIMESTAMP, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    update_user_id = db.Column(db.Integer, nullable=False)
    del_flg = db.Column(db.Boolean, nullable=False, default=False)

    bds = db.relationship("Bds", backref="bds_type_relations")
    type = db.relationship("Type", backref="bds_type_relations")

    def __init__(self, bds_id, type_id, create_user_id, update_user_id):
        self.bds_id = bds_id
        self.type_id = type_id
        self.create_user_id = create_user_id
        self.update_user_id = update_user_id