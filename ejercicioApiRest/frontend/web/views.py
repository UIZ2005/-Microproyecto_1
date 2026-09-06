import os

from flask import Flask, render_template
from flask_cors import CORS
from flask_consulate import Consul

app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

# Ruta para renderizar el template index.html
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para renderizar el template users.html
@app.route('/users')
def users():
    return render_template('users.html')

@app.route('/editUser/<string:id>')
def edit_user(id):
    print("id recibido",id)
    return render_template('editUser.html', id=id)

# Ruta para renderizar el template producto.html
@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/orders')
def orders():
    return render_template('Ordenes.html')

@app.route('/editProduct/<string:id>')
def edit_product(id):
    print("id recibido",id)
    return render_template('editProducts.html', id=id)

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
    name='frontend',
    address=os.getenv('SERVICE_ADDRESS', 'frontend'),
    interval='10s',
    tags=['frontend', 'web'],
    port=int(os.getenv('PORT', '5001')),
    httpcheck=f"http://frontend:{os.getenv('PORT', '5001')}/healthcheck"
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', '5001')))
