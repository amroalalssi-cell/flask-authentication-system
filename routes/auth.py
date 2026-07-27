from flask import Blueprint, render_template, request, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
auth = Blueprint("auth", __name__)

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
        
        db = sqlite3.connect("database.db")
        cursor = db.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO users
                (fullname, username, email, password)
                VALUES (?, ?, ?, ?)
                """,
                (
                    fullname,
                    username,
                    email,
                    hashed_password
                )
            )

            db.commit()

        except sqlite3.IntegrityError:

            db.close()
            return "Email or Username already exists"


        db.close()

        return "User Created Successfully"


    return render_template("register.html")

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]


        db = sqlite3.connect("database.db")
        cursor = db.cursor()


        cursor.execute(
            """
            SELECT * FROM users
            WHERE email = ?
            """,
            (email,)
        )


        user = cursor.fetchone()

        db.close()
        print(user)


        if user and check_password_hash(user[4], password):
            print("LOGIN SUCCESS")
            code = random.randint(100000, 999999)

            session["2fa_code"] = str(code)
            session["user_id"] = user[0]
            session["user"] = user[1]


            print("Your 2FA Code:", code)

            return redirect(url_for("auth.verify_code"))



    return render_template("login.html")
@auth.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    return render_template(
        "dashboard.html",
        username=session["user"]
    )


@auth.route("/logout")
def logout():

    session.pop("user", None)
    session.pop("user_id", None)

    return redirect(url_for("auth.login"))



@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form["email"]


        db = sqlite3.connect("database.db")
        cursor = db.cursor()


        cursor.execute(
            """
            SELECT * FROM users
            WHERE email = ?
            """,
            (email,)
        )


        user = cursor.fetchone()

        db.close()


        if user:

            session["reset_email"] = email

            return redirect(url_for("auth.reset_password"))


        return "Email not found"


    return render_template("forgot_password.html")


@auth.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    if "reset_email" not in session:
        return redirect(url_for("auth.login"))


    if request.method == "POST":

        new_password = request.form["password"]


        db = sqlite3.connect("database.db")
        cursor = db.cursor()


        cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE email = ?
            """,
            (
                new_password,
                session["reset_email"]
            )
        )


        db.commit()
        db.close()


        session.pop("reset_email")


        return redirect(url_for("auth.login"))


    return render_template("reset_password.html")

@auth.route("/two-factor")
def two_factor():
    return render_template("two-factor.html")



@auth.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    db = sqlite3.connect("database.db")
    cursor = db.cursor()


    cursor.execute(
        """
        SELECT fullname, username, email
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    )


    user = cursor.fetchone()

    db.close()


    return render_template(
        "profile.html",
        user=user
    )



@auth.route("/verify-code", methods=["GET", "POST"])
def verify_code():

    if request.method == "POST":

        code = request.form["code"]

        if code == session.get("2fa_code"):

            session.pop("2fa_code")

            return redirect(url_for("auth.dashboard"))

        return "Invalid Code"


    return render_template("verify_code.html")