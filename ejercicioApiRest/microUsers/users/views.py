import os
from flask import Flask, render_template
from users.controllers.user_controller import user_controller
from db.db import db
from flask_cors import CORS
from flask_consulate import Consul

app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = app.config['SECRET_KEY']
CORS(app, supports_credentials=True)
db.init_app(app)

# Registrando el blueprint del controlador de usuarios
app.register_blueprint(user_controller)

# Health check
@app.route('/healthcheck')
def health_check():
    return '', 200

os.environ['CONSUL_HOST'] = os.getenv('CONSUL_HOST', 'consul')
os.environ['CONSUL_PORT'] = os.getenv('CONSUL_PORT', '8500')

consul = Consul(app=app)

consul.register_service(
    name='users',
    address=os.getenv('SERVICE_ADDRESS', 'users'),
    interval='10s',
    tags=['microservice', 'users'],
    port=int(os.getenv('PORT', '5002')),
    httpcheck=f"http://users:{os.getenv('PORT', '5002')}/healthcheck"
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5002')))