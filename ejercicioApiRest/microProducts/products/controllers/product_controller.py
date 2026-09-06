from flask import Blueprint, request, jsonify
from products.models.product_model import Products
from db.db import db

product_controller = Blueprint(
    'product_controller',
    __name__
)


# GET - Obtener todos los productos
@product_controller.route('/api/products', methods=['GET'])
def get_products():

    print("Listado de productos")

    products = Products.query.all()

    result = [
        {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'stock': product.stock
        }
        for product in products
    ]

    return jsonify(result)


# GET - Obtener un producto
@product_controller.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):

    print("Obteniendo producto")

    product = Products.query.get_or_404(product_id)

    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock
    })


# POST - Crear producto
@product_controller.route('/api/products', methods=['POST'])
def create_product():

    print("Creando producto")

    data = request.json

    new_product = Products(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        stock=data['stock']
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        'message': 'Product created successfully'
    }), 201


# PUT - Actualizar producto
@product_controller.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):

    print("Actualizando producto")

    product = Products.query.get_or_404(product_id)

    data = request.json

    product.name = data['name']
    product.description = data['description']
    product.price = data['price']
    product.stock = data['stock']

    db.session.commit()

    return jsonify({
        'message': 'Product updated successfully'
    })


# DELETE - Eliminar producto
@product_controller.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):

    print("Eliminando producto")

    product = Products.query.get_or_404(product_id)

    db.session.delete(product)
    db.session.commit()

    return jsonify({
        'message': 'Product deleted successfully'
    })