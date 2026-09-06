import os
from decimal import Decimal, InvalidOperation

import requests
from flask import Blueprint, jsonify, request, session

from db.db import db
from ordenes.models.ordenes_model import Order, OrderItem

order_controller = Blueprint('order_controller', __name__)


def get_products_service():
    consul_host = os.getenv('CONSUL_HOST', 'consul')
    consul_port = os.getenv('CONSUL_PORT', '8500')

    url = f'http://{consul_host}:{consul_port}/v1/health/service/products'

    response = requests.get(url, params={'passing': 'true'}, timeout=5)
    response.raise_for_status()

    services = response.json()

    if not services:
        raise RuntimeError('No se encontró una instancia saludable de products en Consul')

    service = services[0]
    service_data = service['Service']
    address = service_data.get('Address')
    port = service_data.get('Port')

    if not address or not port:
        raise RuntimeError('Consul devolvió una dirección incompleta para products')

    return f'http://{address}:{port}'

def serialize_order(order):
    return {
        'id': order.id,
        'user_name': order.user_name,
        'user_email': order.user_email,
        'total': float(order.total),
        'status': order.status,
        'created_at': order.created_at.isoformat(),
        'items': [
            {
                'product_id': item.product_id,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price),
                'subtotal': float(item.subtotal)
            }
            for item in order.items
        ]
    }


@order_controller.route('/api/orders', methods=['GET'])
def get_all_orders():
    user_email = session.get('email')
    if not user_email:
        return jsonify({'message': 'Debe iniciar sesión para consultar sus órdenes'}), 401

    orders = Order.query.filter_by(user_email=user_email).order_by(Order.id.desc()).all()
    return jsonify([serialize_order(order) for order in orders])


@order_controller.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    user_email = session.get('email')
    if not user_email:
        return jsonify({'message': 'Debe iniciar sesión para consultar sus órdenes'}), 401

    order = Order.query.filter_by(id=order_id, user_email=user_email).first()
    if order is None:
        return jsonify({'message': 'Orden no encontrada'}), 404
    return jsonify(serialize_order(order))


@order_controller.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    user_email = session.get('email')
    if not user_email:
        return jsonify({'message': 'Debe iniciar sesión para eliminar una orden'}), 401

    order = Order.query.filter_by(id=order_id, user_email=user_email).first()
    if order is None:
        return jsonify({'message': 'Orden no encontrada'}), 404

    try:
        db.session.delete(order)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'No fue posible eliminar la orden'}), 500

    return jsonify({'message': 'Orden eliminada exitosamente'}), 200


@order_controller.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json(silent=True) or {}
    user_name = session.get('username')
    user_email = session.get('email')
    if not user_name or not user_email:
        return jsonify({'message': 'Información de usuario inválida'}), 400

    products = data.get('products')
    if not products or not isinstance(products, list):
        return jsonify({'message': 'Información de productos inválida'}), 400

    requested = {}
    for item in products:
        product_id = item.get('product_id', item.get('id')) if isinstance(item, dict) else None
        quantity = item.get('quantity') if isinstance(item, dict) else None
        if not isinstance(product_id, int) or not isinstance(quantity, int) or quantity <= 0:
            return jsonify({'message': 'Cada producto debe tener id y una cantidad positiva'}), 400
        requested[product_id] = requested.get(product_id, 0) + quantity

    product_data = []
    try:
        products_url = get_products_service()
        for product_id, quantity in requested.items():
            response = requests.get(f'{products_url}/api/products/{product_id}', timeout=5)
            if response.status_code == 404:
                return jsonify({'message': f'Producto {product_id} no encontrado'}), 404
            response.raise_for_status()
            product = response.json()
            if product.get('stock', 0) < quantity:
                return jsonify({'message': f'Inventario insuficiente para el producto {product_id}'}), 409
            price = Decimal(str(product['price']))
            product_data.append((product_id, quantity, product, price))
    except (requests.RequestException, RuntimeError, ValueError, KeyError, InvalidOperation):
        return jsonify({'message': 'No fue posible consultar el servicio de Productos'}), 502

    total = sum((quantity * price for _, quantity, _, price in product_data), Decimal('0.00'))
    updated_products = []

    try:
        products_url = get_products_service()
        for product_id, quantity, product, price in product_data:
            response = requests.put(
                f'{products_url}/api/products/{product_id}',
                json={
                    'name': product['name'],
                    'description': product.get('description'),
                    'price': product['price'],
                    'stock': product['stock'] - quantity
                },
                timeout=5
            )
            response.raise_for_status()
            updated_products.append((product_id, quantity, price))

        order = Order(
            user_name=user_name,
            user_email=user_email,
            total=total,
            status='pending'
        )
        order.items = [
            OrderItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=price,
                subtotal=quantity * price
            )
            for product_id, quantity, price in updated_products
        ]
        db.session.add(order)
        db.session.commit()
    except (requests.RequestException, RuntimeError, KeyError, ValueError, InvalidOperation):
        db.session.rollback()
        return jsonify({'message': 'No fue posible actualizar el inventario en Productos'}), 502
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'No fue posible crear la orden'}), 500

    return jsonify({'message': 'Orden creada exitosamente', 'order': serialize_order(order)}), 201
