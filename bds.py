import filetype
import os
from flask import (
    Blueprint,
    app,
    current_app,
    jsonify,
    render_template,
    redirect,
    request,
    url_for,
    session,
)
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from models import Bds, BdsImage, City, Direction, Image, Province, Type, db
from config import Config
from decorators import *

bds_bp = Blueprint("bds", __name__)


@bds_bp.route("/bds_list")
@login_required
def bds_list():
    # Xử lý logic hiển thị danh sách BĐS
    if current_user.role_id == Config.ROLE_ADMIN or current_user.role_id == Config.ROLE_EDITOR:
        # Hiển thị trang danh sách BĐS cho admin/editor
        bdses = Bds.query.filter_by(del_flg=False).order_by(Bds.id.asc()).all()
        bds_data = get_bds_data(bdses)
        return render_template("bds-list.html", bds_data=bds_data)
    else:
        # Hiển thị trang danh sách BĐS cho người dùng thường
        return render_template("outside/bds-list.html")


@bds_bp.route("/bds_detail/<int:bds_id>")
@login_required
def bds_detail(bds_id):
    bds = get_bds_by_id(bds_id)

    # Tìm các ảnh thuộc về BDS hiện tại
    bds_images = (
        BdsImage.query.filter_by(bds_id=bds.id, del_flg=False).all() if bds else []
    )

    # Lấy thông tin Type
    bds_type = Type.query.get(bds.type_id)

    return render_template(
        "bds-detail.html",
        bds_images=bds_images,
        bds=bds,
        bds_type=bds_type,
    )


@bds_bp.route("/bds_add_edit", methods=["GET", "POST"])
@login_required
def bds_add_edit():
    bds_id = request.args.get("bds_id")
    bds = get_bds_by_id(bds_id) if bds_id else None

    types = Type.query.all()
    provinces = Province.query.all()
    cities = City.query.filter_by(province_id=bds.province_id).all() if bds else []
    directions = Direction.query.all()

    # Tìm các ảnh thuộc về BDS hiện tại
    bds_images = (
        BdsImage.query.filter_by(bds_id=bds.id, del_flg=False).all() if bds else []
    )

    if request.method == "POST":
        # Lấy dữ liệu từ form
        type_id = request.form.get("type_id")
        province_id = request.form.get("province_id")
        city_id = request.form.get("city_id")
        direction_id = request.form.get("direction_id")
        address = request.form.get("address")
        price_from = float(request.form.get("price_from"))
        price_to = float(request.form.get("price_to"))
        area = float(request.form.get("area"))
        sold_flg = True if request.form.get("sold_flg") == "1" else False
        published_flg = True if request.form.get("published_flg") == "1" else False

        if bds:
            # Cập nhật thông tin BDS
            bds.type_id = type_id
            bds.province_id = province_id
            bds.city_id = city_id
            bds.direction_id = direction_id
            bds.address = address
            bds.price_from = price_from
            bds.price_to = price_to
            bds.area = area
            bds.sold_flg = sold_flg
            bds.published_flg = published_flg
            bds.update_user_id = current_user.id
            db.session.add(bds)
            db.session.flush()  # Lưu BDS để có ID
        else:
            # Tạo BDS mới
            new_bds = Bds(
                type_id=type_id,
                province_id=province_id,
                city_id=city_id,
                direction_id=direction_id,
                address=address,
                price_from=price_from,
                price_to=price_to,
                area=area,
                sold_flg=sold_flg,
                published_flg=published_flg,
                created_user_id=current_user.id,
                update_user_id=current_user.id,
            )
            db.session.add(new_bds)
            db.session.flush()  # Lưu BDS để có ID
            bds = new_bds

        # Xử lý ảnh
        images = request.files.getlist("input2[]")
        image_ids = []
        for image in images:
            if image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(
                    current_app.root_path, Config.UPLOAD_FOLDER, filename
                )

                # Tạo thư mục 'static/uploads' nếu chưa tồn tại
                upload_folder = os.path.join(
                    current_app.root_path, Config.UPLOAD_FOLDER
                )
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                image.save(image_path)

                img = Image(
                    filename=filename,
                    created_user_id=current_user.id,
                    update_user_id=current_user.id,
                )
                db.session.add(img)
                db.session.flush()  # Lưu ảnh để có ID
                image_ids.append(img.id)

        # Liên kết ảnh với BDS
        for img_id in image_ids:
            bdsImg = BdsImage(
                bds_id=bds.id,
                img_id=img_id,
                created_user_id=current_user.id,
                update_user_id=current_user.id,
            )
            db.session.add(bdsImg)

        # Xử lý xóa ảnh
        delete_image_ids = request.form.getlist("delete_images[]")
        if delete_image_ids:
            for image_id in delete_image_ids:
                bdsImage = BdsImage.query.get(int(image_id))
                if bdsImage:
                    # Xóa ảnh ở bảng Image
                    image = Image.query.get(bdsImage.img_id)
                    if image:
                        image.del_flg = True
                    # Đánh dấu xóa ảnh ở bảng BdsImage
                    bdsImage.del_flg = True
                    db.session.add(bdsImage)

        db.session.commit()

        return redirect(url_for("bds.bds_list"))

    return render_template(
        "bds-add-edit.html",
        bds=bds,
        bds_images=bds_images,
        types=types,
        provinces=provinces,
        cities=cities,
        directions=directions,
    )


@bds_bp.route("/bds_delete/<int:bds_id>")
@login_required
def bds_delete(bds_id):
    bds = get_bds_by_id(bds_id)
    if bds:
        bds.del_flg = True
        db.session.commit()
    return redirect("/bds_list")


@bds_bp.route("/bds_search", methods=["GET", "POST"])
@login_required
def bds_search():
    if request.method == "POST":
        search_keyword = request.form.get("search_keyword")

        query = Bds.query.filter_by(del_flg=False)

        if search_keyword:
            query = query.filter(
                Bds.address.ilike(f"%{search_keyword}%")
                | Bds.title.ilike(f"%{search_keyword}%")
                | Bds.content.ilike(f"%{search_keyword}%")
            )

        bds_data = get_bds_data(query)

        return render_template(
            "bds-list.html", bds_data=bds_data, search_keyword=search_keyword
        )


def get_bds_by_id(bds_id):
    bds = Bds.query.filter_by(id=bds_id, del_flg=False).first()
    return bds


# UPLOAD: validate_image
def validate_image(stream):
    kind = filetype.guess(stream)
    if kind is not None and kind.extension in ["jpg", "jpeg", "png", "gif", "bmp"]:
        return "." + kind.extension
    return None


@bds_bp.route("/get_cities/<int:province_id>", methods=["GET"])
def get_cities(province_id):
    cities = City.query.filter_by(province_id=province_id).all()
    return jsonify([{"id": city.id, "name": city.name} for city in cities])


def get_bds_data(query):
    bds_data = []
    for bds in query:
        first_image = BdsImage.query.filter_by(bds_id=bds.id, del_flg=False).first()
        if first_image:
            image = Image.query.filter_by(id=first_image.img_id, del_flg=False).first()
            first_image_url = url_for("static", filename=f"uploads/{image.filename}")
        else:
            first_image_url = None
        bds_type = Type.query.get(bds.type_id)
        bds_data.append(
            {
                "bds": bds,
                "first_image_url": first_image_url,
                "bds_type": bds_type,
                "price_from": format_currency(bds.price_from),
                "price_to": format_currency(bds.price_to),
            }
        )
    return bds_data
