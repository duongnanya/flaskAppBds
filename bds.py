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
from sqlalchemy import func
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from models import (
    Bds,
    BdsImage,
    BdsTypeRelation,
    BdsUserRelation,
    City,
    # Direction,
    Image,
    Province,
    Type,
    db,
    PriceRange,
    AreaRange,
)
from config import Config
from decorators import *

bds_bp = Blueprint("bds", __name__)


@bds_bp.route("/bds_list", methods=["GET", "POST"])
@login_required
def bds_list():
    if request.method == "POST":
        search_keyword = request.form.get("search_keyword")
        exact_search = request.form.get("exact_search") is not None

        query = Bds.query.filter_by(del_flg=False)

        if search_keyword:
            if exact_search:
                query = query.filter(
                    Bds.title.ilike(f"%{search_keyword}%")
                    | Bds.content.ilike(f"%{search_keyword}%")
                    | Bds.address.ilike(f"%{search_keyword}%")
                )
                bds_data = get_bds_data(query)
            else:
                bds_data = []
                sub_keywords = search_keyword.split()
                for i in range(len(sub_keywords), 0, -1):
                    for j in range(0, len(sub_keywords) - i + 1):
                        sub_keyword = " ".join(sub_keywords[j : j + i])
                        query = Bds.query.filter_by(del_flg=False).filter(
                            Bds.title.ilike(f"%{sub_keyword}%")
                            | Bds.content.ilike(f"%{sub_keyword}%")
                            | Bds.address.ilike(f"%{sub_keyword}%")
                        )
                        bds_data.extend(get_bds_data(query))

                # Lọc ra những BDS không bị trùng
                bds_data = list({bds["bds"].id: bds for bds in bds_data}.values())

                # Sắp xếp kết quả theo độ chính xác giảm dần
                bds_data = sorted(
                    bds_data,
                    key=lambda x: -len(x["bds"].title.split())
                    + -len(x["bds"].content.split())
                    + -len(x["bds"].address.split()),
                )

        else:
            bds_data = get_bds_data(query)

        return render_template(
            "bds-list.html",
            bds_data=bds_data,
            search_keyword=search_keyword,
            exact_search=exact_search,
        )
    else:
        # Xử lý logic hiển thị danh sách BĐS
        bdses = Bds.query.filter_by(del_flg=False).order_by(Bds.id.asc()).all()
        bds_data = get_bds_data(bdses)
        return render_template("bds-list.html", bds_data=bds_data)


@bds_bp.route("/bds_detail/<int:bds_id>")
@login_required
def bds_detail(bds_id):
    bds = get_bds_by_id(bds_id)

    # Tìm các ảnh thuộc về BDS hiện tại
    bds_images = (
        BdsImage.query.filter_by(bds_id=bds.id, del_flg=False).all() if bds else []
    )

    # Lấy thông tin Type
    bds_types = Type.query.join(BdsTypeRelation).\
        filter(BdsTypeRelation.bds_id == bds.id, BdsTypeRelation.del_flg == False, Type.del_flg == False).\
        all()

    # Lấy thông tin City
    bds_city = City.query.get(bds.city_id)

    # Lấy thông tin Province
    bds_province = Province.query.get(bds.province_id)

    is_favorite = (
        BdsUserRelation.query.filter_by(
            user_id=current_user.id, bds_id=bds.id, del_flg=False
        ).first()
        is not None
    )

    if (
        current_user.role_id == Config.ROLE_ADMIN
        or current_user.role_id == Config.ROLE_EDITOR
    ):
        # Hiển thị trang bds-detail.html cho admin/editor
        return render_template(
            "bds-detail.html",
            bds_images=bds_images,
            bds=bds,
            bds_types=bds_types,
            bds_city=bds_city,
            bds_province=bds_province,
            is_favorite=is_favorite,
        )
    else:
        # Hiển thị trang os-bds-detail.html cho người dùng có Role = 3
        return render_template(
            "outside/os-bds-detail.html",
            bds_images=bds_images,
            bds=bds,
            bds_types=bds_types,
            bds_city=bds_city,
            bds_province=bds_province,
            address=bds.address,
            price_from=format_currency(bds.price_from),
            price_to=format_currency(bds.price_to),
            is_favorite=is_favorite,
        )


@bds_bp.route("/bds_add_edit", methods=["GET", "POST"])
@login_required
def bds_add_edit():
    bds_id = request.args.get("bds_id")
    bds = get_bds_by_id(bds_id) if bds_id else None

    types = Type.query.all()
    provinces = Province.query.all()
    cities = City.query.filter_by(province_id=bds.province_id).all() if bds else []
    # directions = Direction.query.all()

    # Tìm các ảnh thuộc về BDS hiện tại
    bds_images = (
        BdsImage.query.filter_by(bds_id=bds.id, del_flg=False).all() if bds else []
    )

    if request.method == "POST":
        # Lấy dữ liệu từ form
        type_ids = request.form.getlist("type-id[]")
        province_id = request.form.get("province-id")
        city_id = request.form.get("city-id")
        # direction_id = request.form.get("direction-id")
        address = request.form.get("address")
        price_from = float(request.form.get("price-from"))
        price_to = float(request.form.get("price-to"))
        area = float(request.form.get("area"))
        sold_flg = True if request.form.get("sold-flg") == "1" else False
        published_flg = True if request.form.get("published-flg") == "1" else False

        if bds:
            # Cập nhật thông tin BDS
            bds.province_id = province_id
            bds.city_id = city_id
            # bds.direction_id = direction_id
            bds.address = address
            bds.price_from = price_from
            bds.price_to = price_to
            bds.area = area
            bds.sold_flg = sold_flg
            bds.published_flg = published_flg
            bds.update_user_id = current_user.id
            db.session.add(bds)
            db.session.flush()  # Lưu BDS để có ID

            # Cập nhật các mối liên kết giữa BĐS và loại BĐS
            for bds_type_relation in bds.bds_type_relations:
                bds_type_relation.del_flg = True
                db.session.add(bds_type_relation)
            db.session.commit()

            # Tạo mới các mối liên kết giữa BĐS và loại BĐS
            for type_id in type_ids:
                bds_type_relation = BdsTypeRelation(
                    bds_id=bds.id,
                    type_id=type_id,
                    create_user_id=current_user.id,
                    update_user_id=current_user.id
                )
                db.session.add(bds_type_relation)
            db.session.commit()
        else:
            # Tạo BDS mới
            new_bds = Bds(
                province_id=province_id,
                city_id=city_id,
                # direction_id=direction_id,
                address=address,
                price_from=price_from,
                price_to=price_to,
                area=area,
                sold_flg=sold_flg,
                published_flg=published_flg,
                create_user_id=current_user.id,
                update_user_id=current_user.id,
            )
            db.session.add(new_bds)
            db.session.flush()  # Lưu BDS để có ID

            # Thêm các loại BĐS mới
            for type_id in type_ids:
                bds_type_relation = BdsTypeRelation(
                    bds_id=new_bds.id,
                    type_id=type_id,
                    create_user_id=current_user.id,
                    update_user_id=current_user.id,
                )
                db.session.add(bds_type_relation)

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
                    create_user_id=current_user.id,
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
                create_user_id=current_user.id,
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

    # Trả về template bds-add-edit.html với các dữ liệu cần thiết
    return render_template(
        "bds-add-edit.html",
        bds=bds,
        bds_images=bds_images,
        types=types,
        provinces=provinces,
        cities=cities,
        # directions=directions,
    )


@bds_bp.route("/bds_delete/<int:bds_id>")
@login_required
def bds_delete(bds_id):
    bds = get_bds_by_id(bds_id)
    if bds:
        # Xóa các BdsTypeRelation liên quan đến BĐS này
        BdsTypeRelation.query.filter_by(bds_id=bds.id, del_flg=False).update({BdsTypeRelation.del_flg: True})
        
        # Xóa các ảnh liên quan trong BdsImage
        BdsImage.query.filter_by(bds_id=bds.id, del_flg=False).update({BdsImage.del_flg: True})
        
        # Xóa các liên kết trong BdsUserRelation
        BdsUserRelation.query.filter_by(bds_id=bds.id, del_flg=False).update({BdsUserRelation.del_flg: True})
        
        db.session.commit()

        # Đánh dấu BĐS là đã xóa
        bds.del_flg = True
        db.session.commit()
    return redirect(url_for("bds.bds_list"))


@bds_bp.route("/os_bds_list", methods=["GET", "POST"])
@login_required
def os_bds_list():
    if request.method == "POST":
        bds_type_ids = request.form.getlist("type-id[]")
        bds_province_id = request.form.get("province-select")
        bds_city_id = request.form.get("city-select")
        price_range_id = request.form.get("price-range-select")
        area_range_id = request.form.get("area-range-select")
        address_text = request.form.get("address-text")
        # direction_id = request.form.get("direction-select")

        query = Bds.query.filter_by(published_flg=True, del_flg=False)
        if bds_type_ids:
            bds_ids = (
                db.session.query(BdsTypeRelation.bds_id)
                .filter(BdsTypeRelation.type_id.in_(bds_type_ids))
                .filter(BdsTypeRelation.del_flg == False)
                .group_by(BdsTypeRelation.bds_id)
                .having(func.count(BdsTypeRelation.bds_id) == len(bds_type_ids))
                .all()
            )
            query = query.filter(Bds.id.in_([bds_id[0] for bds_id in bds_ids]))
        if bds_province_id:
            query = query.filter(Bds.province_id == bds_province_id)
        if bds_city_id:
            query = query.filter(Bds.city_id == bds_city_id)
        if price_range_id:
            pr = PriceRange.query.get(price_range_id)
            query = query.filter(
                Bds.price_to >= pr.price_from, Bds.price_to <= pr.price_to
            )
        if area_range_id:
            ar = AreaRange.query.get(area_range_id)
            query = query.filter(Bds.area >= ar.area_from, Bds.area <= ar.area_to)
        if address_text:
            query = query.filter(Bds.address.like(f"%{address_text}%"))
        # if direction_id:
        #     query = query.filter(Bds.direction_id == direction_id)

        bds_data = get_bds_data(query)

        types = Type.query.all()
        provinces = Province.query.all()
        if bds_province_id:
            cities = City.query.all()
        else:
            cities = []
        priceRanges = PriceRange.query.all()
        areaRanges = AreaRange.query.all()
        # directions = Direction.query.all()

        return render_template(
            "outside/os-bds-list.html",
            bds_data=bds_data,
            types=types,
            selected_type_ids=bds_type_ids,
            provinces=provinces,
            selected_province_id=bds_province_id,
            cities=cities,
            selected_city_id=bds_city_id,
            priceRanges=priceRanges,
            selected_price_range_id=price_range_id,
            areaRanges=areaRanges,
            selected_area_range_id=area_range_id,
            address=address_text,
            # directions=directions,
            # selected_direction_id=direction_id,
        )

    else:
        # Lấy danh sách BDS đã được public và chưa bị xóa
        bdses = Bds.query.filter_by(published_flg=True, del_flg=False).all()
        bds_data = get_bds_data(bdses)

        types = Type.query.all()
        provinces = Province.query.all()
        cities = City.query.all()
        priceRanges = PriceRange.query.all()
        areaRanges = AreaRange.query.all()
        # directions = Direction.query.all()

        return render_template(
            "outside/os-bds-list.html",
            bds_data=bds_data,
            types=types,
            provinces=provinces,
            cities=cities,
            priceRanges=priceRanges,
            areaRanges=areaRanges,
            # directions=directions,
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

        remaining_images_count = (
            BdsImage.query.filter_by(bds_id=bds.id, del_flg=False).count() - 1
        )

        # Lấy thông tin về các loại BĐS
        bds_types = Type.query.join(BdsTypeRelation).\
            filter(BdsTypeRelation.bds_id == bds.id, BdsTypeRelation.del_flg == False, Type.del_flg == False).\
            all()

        bds_city = City.query.get(bds.city_id)
        bds_province = Province.query.get(bds.province_id)

        is_favorite = (
            BdsUserRelation.query.filter_by(
                user_id=current_user.id, bds_id=bds.id, del_flg=False
            ).first()
            is not None
        )

        bds_data.append(
            {
                "bds": bds,
                "first_image_url": first_image_url,
                "remaining_images_count": remaining_images_count,
                "bds_types": bds_types,
                "bds_city": bds_city,
                "bds_province": bds_province,
                "address": bds.address,
                "price_from": format_currency(bds.price_from),
                "price_to": format_currency(bds.price_to),
                "is_favorite": is_favorite,
            }
        )
    return bds_data


def format_currency(value):
    if value >= 1000000000:
        return f"{value / 1000000000:.1f} tỷ"
    elif value >= 1000000:
        decimal_part = value % 1000000 / 1000000
        if decimal_part > 0:
            return f"{value / 1000000:.1f} triệu"
        else:
            return f"{value // 1000000} triệu"
    elif value >= 1000:
        decimal_part = value % 1000 / 1000
        if decimal_part > 0:
            return f"{value / 1000:.1f} nghìn"
        else:
            return f"{value // 1000} nghìn"
    else:
        return str(int(value))


# lưu/xóa yêu thích Bds
@bds_bp.route("/toggle_favorite/<int:bds_id>", methods=["POST"])
@login_required
def toggle_favorite(bds_id):
    bds_relation = BdsUserRelation.query.filter_by(
        user_id=current_user.id, bds_id=bds_id, del_flg=False
    ).first()

    if bds_relation:
        bds_relation.del_flg = True
        db.session.add(bds_relation)
        db.session.commit()
        return jsonify({"success": True, "is_favorite": False})
    else:
        new_relation = BdsUserRelation(
            user_id=current_user.id,
            bds_id=bds_id,
            create_user_id=current_user.id,
            update_user_id=current_user.id,
        )
        db.session.add(new_relation)
        db.session.commit()
        return jsonify({"success": True, "is_favorite": True})


@bds_bp.route("/check_favorite/<int:bds_id>", methods=["GET"])
@login_required
def check_favorite(bds_id):
    bds_relation = BdsUserRelation.query.filter_by(
        user_id=current_user.id, bds_id=bds_id, del_flg=False
    ).first()
    return jsonify({"is_favorite": bool(bds_relation)})
