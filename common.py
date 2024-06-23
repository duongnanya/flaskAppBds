from flask import Blueprint, jsonify, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from models import db, Province, City
import pandas as pd
import logging
from datetime import datetime, timedelta
import json
from sqlalchemy import and_, exists
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
            created_user_id=current_user.id,
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
            created_user_id=current_user.id,
            update_user_id=current_user.id,
        )
        db.session.add(new_city)
    db.session.commit()

    return render_template("import-province-city.html", success=True)
