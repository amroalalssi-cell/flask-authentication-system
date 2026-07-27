import sqlite3


db = sqlite3.connect("database.db")

cursor = db.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    fullname TEXT NOT NULL,

    username TEXT NOT NULL UNIQUE,

    email TEXT NOT NULL UNIQUE,

    password TEXT NOT NULL

)
""")


db.commit()
db.close()


print("Database created successfully")