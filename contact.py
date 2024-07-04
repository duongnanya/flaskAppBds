from flask import Blueprint, render_template, redirect, request, url_for, flash
from models import AreaRange, City, Direction, PriceRange, Province, Type, db, Contact
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from models import Contact, db
from config import Config

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        message = request.form["message"]

        # Lưu message vào database
        new_message = Contact(name=name, email=email, phone=phone, message=message)
        db.session.add(new_message)
        db.session.commit()

        # Gửi email đến gmail của bạn
        send_email(
            "Liên hệ Tìm kiếm BĐS",
            f"Tên: {name}\nEmail: {email}\nSĐT: {phone}\Tin nhắn:\n{message}",
        )

        flash("Tin nhắn của bạn đã được gửi thành công!")
        return render_template("outside/os-contact.html")
    else:

        # Lấy thông tin Code để tìm kiếm BĐS
        types = Type.query.all()
        provinces = Province.query.all()
        cities = City.query.all()
        priceRanges = PriceRange.query.all()
        areaRanges = AreaRange.query.all()
        directions = Direction.query.all()

        return render_template(
            "outside/os-contact.html",
            types=types,
            provinces=provinces,
            cities=cities,
            priceRanges=priceRanges,
            areaRanges=areaRanges,
            directions=directions,
        )


def send_email(subject, message):
    msg = MIMEMultipart()
    msg["From"] = Config.MY_EMAIL
    msg["To"] = Config.MY_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText(message, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(Config.MY_EMAIL, Config.MY_EMAIL_APP_PASSWORD)
    text = msg.as_string()
    server.sendmail(Config.MY_EMAIL, Config.MY_EMAIL, text)
    server.quit()
