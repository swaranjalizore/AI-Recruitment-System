from flask import Flask 
from config import Config
from routes.auth import auth
from routes.candidate import candidate
from routes.recruiter import recruiter
from routes.admin import admin



app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
app.config.from_object(Config)

app.register_blueprint(auth)
app.register_blueprint(candidate)
app.register_blueprint(recruiter)
app.register_blueprint(admin)


if __name__ == "__main__":
    app.run(debug=True)