from flask import Flask 
from config import Config
from routes.auth import auth


app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(auth)

if __name__ == "__main__":
    app.run(debug=True)