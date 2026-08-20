from flask import Blueprint, render_template, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
import os
import time
import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database.db")


auth = Blueprint("auth", __name__)

# مدة صلاحية كود الـ 2FA بالثواني (5 دقائق)
CODE_EXPIRY_SECONDS = 300
# أقصى عدد محاولات خاطئة لكود الـ 2FA
MAX_CODE_ATTEMPTS = 5
# مدة صلاحية رابط استعادة كلمة المرور بالثواني (15 دقيقة)
RESET_TOKEN_EXPIRY_SECONDS = 900


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return "Passwords do not match"

        hashed_password = generate_password_hash(password)

        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO users
                (fullname, username, email, password)
                VALUES (?, ?, ?, ?)
                """,
                (fullname, username, email, hashed_password)
            )
            db.commit()
        except sqlite3.IntegrityError:
            db.close()
            return "Email or Username already exists"

        db.close()
        return render_template("success.html")

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        db.close()

        if user and check_password_hash(user[4], password):
            code = random.randint(100000, 999999)

            session["pending_2fa_code"] = str(code)
            session["pending_user_id"] = user[0]
            session["pending_username"] = user[1]
            # وقت إصدار الكود لاستخدامه بحساب الصلاحية
            session["pending_2fa_time"] = time.time()
            # عداد المحاولات الخاطئة
            session["pending_2fa_attempts"] = 0

            print("-----------------------------")
            print("Your 2FA Code:", code)
            print("-----------------------------")

            return redirect(url_for("auth.verify_code"))
        else:
            return "Invalid Email or Password"

    return render_template("login.html")


@auth.route("/verify-code", methods=["GET", "POST"])
def verify_code():
    if "pending_2fa_code" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        # التحقق من انتهاء صلاحية الكود
        issued_at = session.get("pending_2fa_time", 0)
        if time.time() - issued_at > CODE_EXPIRY_SECONDS:
            session.pop("pending_2fa_code", None)
            session.pop("pending_user_id", None)
            session.pop("pending_username", None)
            session.pop("pending_2fa_time", None)
            session.pop("pending_2fa_attempts", None)
            return "Code expired, please login again"

        # التحقق من عدد المحاولات
        attempts = session.get("pending_2fa_attempts", 0)
        if attempts >= MAX_CODE_ATTEMPTS:
            session.pop("pending_2fa_code", None)
            session.pop("pending_user_id", None)
            session.pop("pending_username", None)
            session.pop("pending_2fa_time", None)
            session.pop("pending_2fa_attempts", None)
            return "Too many failed attempts, please login again"

        code = request.form["code"]

        # مطابقة الكود المدخل مع الكود المؤقت
        if code == session.get("pending_2fa_code"):

            # ✅ تفعيل الجلسة الدائمة الآن بعد النجاح في الـ 2FA
            session["user_id"] = session["pending_user_id"]
            session["user"] = session["pending_username"]

            # تنظيف الجلسة من البيانات المؤقتة
            session.pop("pending_2fa_code", None)
            session.pop("pending_user_id", None)
            session.pop("pending_username", None)
            session.pop("pending_2fa_time", None)
            session.pop("pending_2fa_attempts", None)

            return redirect(url_for("auth.dashboard"))

        # محاولة خاطئة: زيادة العداد
        session["pending_2fa_attempts"] = attempts + 1
        return "Invalid Code"

    return render_template("verify_code.html")


@auth.route("/dashboard")
def dashboard():
    # منع الدخول التلقائي لحين التأكد من وجود الجلسة الدائمة (المفعّلة بعد الـ 2FA)
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template("dashboard.html", username=session["user"])


@auth.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute("SELECT fullname, username, email FROM users WHERE id = ?", (session["user_id"],))
    user = cursor.fetchone()
    db.close()

    return render_template("profile.html", user=user)


@auth.route("/logout")
def logout():
    session.clear()  # تنظيف كافة بيانات الجلسة عند الخروج
    return redirect(url_for("auth.login"))

@app.route("/")
def home():
    return redirect("/login")


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]

        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user:
            # 🔒 إنشاء رمز عشوائي غير قابل للتخمين بدل تفعيل الوصول مباشرة بالإيميل فقط
            reset_token = secrets.token_urlsafe(32)
            reset_token_expiry = time.time() + RESET_TOKEN_EXPIRY_SECONDS

            cursor.execute(
                "UPDATE users SET reset_token = ?, reset_token_expiry = ? WHERE email = ?",
                (reset_token, reset_token_expiry, email)
            )
            db.commit()
            db.close()

            # ⚠️ ملاحظة: هون المفروض يترسل reset_token فعليًا عبر إيميل المستخدم
            # (مثلاً رابط زي /reset-password/<reset_token>) بدل ما يظهر بالسيرفر.
            # حاليًا منطبعه بالكونسول كـ placeholder للتطوير فقط، بنفس نمط كود الـ 2FA.
            print("-----------------------------")
            print("Password reset token for", email, ":", reset_token)
            print("-----------------------------")

            # ما منخزن الإيميل مباشرة بالجلسة، ومنرجّع نفس الرسالة سواء الإيميل موجود أو لأ
            # حتى ما نكشف للمهاجم إذا الإيميل مسجل بالنظام أو لأ
            return "If this email exists, a reset link has been sent"

        db.close()
        # نفس الرسالة تمامًا لعدم تسريب معلومة وجود الإيميل من عدمه
        return "If this email exists, a reset link has been sent"

    return render_template("forgot_password.html")


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, email, reset_token_expiry FROM users WHERE reset_token = ?",
        (token,)
    )
    user = cursor.fetchone()

    if not user or time.time() > user[2]:
        db.close()
        return "Invalid or expired reset link"

    if request.method == "POST":
        new_password = request.form["password"]
        confirm_password = request.form.get("confirm_password", new_password)

        if new_password != confirm_password:
            db.close()
            return "Passwords do not match"

        # 🔒 تشفير كلمة المرور الجديدة أيضاً عند استعادتها
        hashed_password = generate_password_hash(new_password)

        cursor.execute(
            "UPDATE users SET password = ?, reset_token = NULL, reset_token_expiry = NULL WHERE id = ?",
            (hashed_password, user[0])
        )
        db.commit()
        db.close()

        return redirect(url_for("auth.login"))

    db.close()
    return render_template("reset_password.html", token=token)
