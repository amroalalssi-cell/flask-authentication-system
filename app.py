import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
from flask import Flask
from routes.auth import auth


app = Flask(__name__)

app.secret_key = "my_secret_key"


app.register_blueprint(auth)


if __name__ == "__main__":
    app.run(debug=True)