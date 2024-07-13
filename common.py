from flask import Blueprint, jsonify, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from models import Bds, BdsViewCount, Category, Status, db, Province, City
import pandas as pd
import logging
from datetime import datetime, timedelta
import json
from sqlalchemy import and_, exists, func
from config import Config

common_bp = Blueprint("common", __name__)


@common_bp.route("/import_province_city")
def import_province_city():
    return render_template("import-province-city.html")


@common_bp.route("/handle_imported_file", methods=["POST"])
def handle_imported_file():
    file = request.files["imported_excel"]
    df = pd.read_excel(file)

    # Insert data into Province table
    provinces = df["Tỉnh thành"].unique()
    for province in provinces:
        new_province = Province(
            name=province,
            description="",
            create_user_id=current_user.id,
            update_user_id=current_user.id,
        )
        db.session.add(new_province)
    db.session.commit()

    # Insert data into City table
    for index, row in df.iterrows():
        province = Province.query.filter_by(name=row["Tỉnh thành"]).first()
        new_city = City(
            name=row["Thành phố / Huyện"],
            description="",
            province_id=province.id,
            create_user_id=current_user.id,
            update_user_id=current_user.id,
        )
        db.session.add(new_city)
    db.session.commit()

    return render_template("import-province-city.html", success=True)


def get_categories():
    categories = Category.query.filter_by(del_flg=False).all()
    return categories


def get_statuses():
    statuses = Status.query.filter_by(del_flg=False).all()
    return statuses


def get_top_bds_24():
    now = datetime.now()
    last_24_hours = now - timedelta(hours=24)

    subquery = db.session.query(
        BdsViewCount.bds_id,
        func.sum(BdsViewCount.cnt_view_24).label('total_views')
    ).filter(
        BdsViewCount.last_view_24 >= last_24_hours
    ).group_by(
        BdsViewCount.bds_id
    ).subquery()

    top_bds = db.session.query(
        Bds
    ).join(
        subquery, Bds.id == subquery.c.bds_id
    ).order_by(
        subquery.c.total_views.desc()
    ).limit(Config.TOP_CNT).all()

    return top_bds