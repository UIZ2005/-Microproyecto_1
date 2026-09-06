import os
from flask import Flask
from ordenes.controllers.ordenes_controller import order_controller
from db.db import db
from flask_cors import CORS
from flask_consulate import Consul

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config.from_object('config.Config')
db.init_app(app)

app.secret_key = app.config['SECRET_KEY']
app.register_blueprint(order_controller)

# Health check
@app.route('/healthcheck')
def health_check():
    return '', 200

# Configuración de Consul para Docker
os.environ['CONSUL_HOST'] = os.getenv('CONSUL_HOST', 'consul')
os.environ['CONSUL_PORT'] = os.getenv('CONSUL_PORT', '8500')

# Inicializar la extensión
consul = Consul(app=app)
consul.register_service(
    name='orders',
    address=os.getenv('SERVICE_ADDRESS', 'orders'),
    interval='10s',
    tags=['microservice', 'orders'],
    port=int(os.getenv('PORT', '5004')),
    httpcheck=f"http://orders:{os.getenv('PORT', '5004')}/healthcheck"
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5004')))