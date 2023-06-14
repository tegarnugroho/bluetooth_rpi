from flask import Flask
from routes import app_routes

app = Flask(__name__)
app.register_blueprint(app_routes, url_prefix='/v1')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
