import os
import sqlite3
from flask import Flask, redirect, url_for
from routes.auth import auth

app = Flask(__name__)

# 🔒 المفتاح صار يجي من environment variable بدل ما يكون مكتوب مباشرة بالكود.
# لازم تحط قيمة حقيقية بمتغير البيئة FLASK_SECRET_KEY قبل التشغيل بالإنتاج، مثلاً:
#   export FLASK_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
# القيمة الثانية بـ os.environ.get() هي fallback للتطوير المحلي فقط، لا تُستخدم بالإنتاج.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-fallback-key-change-me")

app.register_blueprint(auth)

@app.route("/")
def index():
    return redirect(url_for("auth.login"))


def init_db():
    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        reset_token TEXT,
        reset_token_expiry REAL
    )
    """)
    db.commit()
    db.close()
    print("🎉 SQLite Table Checked/Created Successfully inside Server Context!")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)