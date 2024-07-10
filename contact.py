from flask import Blueprint, render_template, redirect, request, url_for, flash
from flask_login import current_user
from models import AreaRange, City, Direction, PriceRange, Province, Type, db, Contact
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from models import Contact, db
from config import Config

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["GET", "POST"])
def contact():
    # Lấy thông tin Code để tìm kiếm BĐS
    types = Type.query.all()
    provinces = Province.query.all()
    cities = City.query.all()
    priceRanges = PriceRange.query.all()
    areaRanges = AreaRange.query.all()
    directions = Direction.query.all()

    if request.method == "POST":
        if 'name' in request.form:  # Check if contact form is submitted
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            subject = request.form["subject"]
            message = request.form["message"]

            # Lưu message vào database
            new_message = Contact(name=name, email=email, phone=phone, subject=subject, message=message)
            db.session.add(new_message)
            db.session.commit()

            # Gửi email đến gmail của bạn
            send_email(
                subject,  # Use the subject from the form
                f"Tên: {name}\nEmail: {email}\nSĐT: {phone}\nTin nhắn:\n{message}",
            )

            flash("Tin nhắn của bạn đã được gửi thành công!")
            return redirect(url_for("contact.contact"))  # Redirect back to the contact page
        else:  # Search form is submitted
            # Lấy thông tin từ các trường tìm kiếm
            type_ids = request.form.getlist('type-id[]')
            selected_province_id = request.form.get('province-select')
            selected_city_id = request.form.get('city-select')
            address = request.form.get('address-text')
            selected_price_range_id = request.form.get('price-range-select')
            selected_area_range_id = request.form.get('area-range-select')
            # selected_direction_id = request.form.get('direction-select')

            return render_template(
                'outside/os-contact.html',
                is_from_bds = True,
                type_ids=type_ids, 
                selected_province_id=selected_province_id, 
                selected_city_id=selected_city_id, 
                address=address, 
                selected_price_range_id=selected_price_range_id, 
                selected_area_range_id=selected_area_range_id,
                
                types=types,
                provinces=provinces,
                cities=cities,
                priceRanges=priceRanges,
                areaRanges=areaRanges,
                directions=directions,

                user=current_user  # Pass the current user to the template
            )
    else:
        # Hiển thị trang os-contact.html
        return render_template(
            "outside/os-contact.html",
            types=types,
            provinces=provinces,
            cities=cities,
            priceRanges=priceRanges,
            areaRanges=areaRanges,
            directions=directions,
            user=current_user  # Pass the current user to the template
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