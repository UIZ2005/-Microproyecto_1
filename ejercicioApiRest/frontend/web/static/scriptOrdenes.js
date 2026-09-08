const ORDERS_API = 'http://192.168.100.3:5004';
const PRODUCTS_API = 'http://192.168.100.3:5003';
let productsCatalog = [];

function getProducts() {
    return fetch(`${PRODUCTS_API}/api/products`, {credentials: 'include'})
        .then(response => response.json().then(data => ({ok: response.ok, data})))
        .then(({ok, data}) => {
            if (!ok) throw new Error('No fue posible obtener los productos.');
            productsCatalog = data;
            populateProductSelects();
            return data;
        });
}

function populateProductSelects() {
    document.querySelectorAll('.product-id').forEach(select => {
        const selectedValue = select.value;
        select.innerHTML = '<option value="">Select a product</option>';
        productsCatalog.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.textContent = `${product.name} (Stock: ${product.stock})`;
            option.disabled = product.stock < 1;
            select.appendChild(option);
        });
        select.value = selectedValue;
        updateQuantityLimit(select.closest('.order-product-row'));
    });
}

function updateQuantityLimit(row) {
    if (!row) return;
    const select = row.querySelector('.product-id');
    const quantity = row.querySelector('.product-quantity');
    const product = productsCatalog.find(item => item.id === Number(select.value));
    quantity.max = product ? product.stock : '';
    quantity.title = product ? `Maximum available: ${product.stock}` : '';
}

function getProductName(productId) {
    const product = productsCatalog.find(item => item.id === productId);
    return product ? product.name : `Product ${productId}`;
}

function formatOrderItems(items) {
    return items.map(item => `${getProductName(item.product_id)} x ${item.quantity}`).join(', ');
}

function showOrderMessage(message, type) {
    const element = document.getElementById('order-message');
    element.textContent = message;
    element.className = `mt-3 alert alert-${type}`;
}

function getOrders() {
    fetch(`${ORDERS_API}/api/orders`, {credentials: 'include'})
        .then(response => response.json().then(data => ({ok: response.ok, data})))
        .then(({ok, data}) => {
            if (!ok) throw new Error(data.message || 'No fue posible obtener las órdenes.');
            const body = document.querySelector('#order-list tbody');
            body.innerHTML = '';
            data.forEach(order => {
                const row = document.createElement('tr');
                const values = [
                    order.id,
                    `${order.user_name} (${order.user_email})`,
                    order.total,
                    order.status,
                    new Date(order.created_at).toLocaleString(),
                    formatOrderItems(order.items)
                ];
                values.forEach(value => {
                    const cell = document.createElement('td');
                    cell.textContent = value;
                    row.appendChild(cell);
                });
                body.appendChild(row);
            });
        })
        .catch(error => showOrderMessage(error.message, 'danger'));
}

function getOrderById() {
    const orderId = document.getElementById('order-id').value.trim();
    if (!orderId || Number(orderId) < 1) {
        showOrderMessage('El ID de la orden es obligatorio y debe ser positivo.', 'warning');
        return;
    }

    fetch(`${ORDERS_API}/api/orders/${Number(orderId)}`, {credentials: 'include'})
        .then(response => response.json().then(data => ({ok: response.ok, data})))
        .then(({ok, data}) => {
            if (!ok) throw new Error(data.message || 'Orden no encontrada.');
            showOrderMessage(
                `Orden #${data.id}: ${data.user_name}, total ${data.total}, estado ${data.status}. Items: ${formatOrderItems(data.items)}.`,
                'info'
            );
        })
        .catch(error => showOrderMessage(error.message, 'danger'));
}

function updateRemoveButtons() {
    const rows = document.querySelectorAll('.order-product-row');
    rows.forEach(row => {
        row.querySelector('.remove-product').disabled = rows.length === 1;
    });
}

document.getElementById('add-product').addEventListener('click', function() {
    const row = document.querySelector('.order-product-row').cloneNode(true);
    row.querySelector('.product-id').value = '';
    row.querySelector('.product-quantity').value = '';
    row.querySelector('.remove-product').disabled = false;
    document.getElementById('order-products').appendChild(row);
    populateProductSelects();
    updateRemoveButtons();
});

document.getElementById('order-products').addEventListener('click', function(event) {
    if (event.target.classList.contains('remove-product')) {
        event.target.closest('.order-product-row').remove();
        updateRemoveButtons();
    }
});

document.getElementById('order-products').addEventListener('change', function(event) {
    if (event.target.classList.contains('product-id')) {
        updateQuantityLimit(event.target.closest('.order-product-row'));
    }
});

document.getElementById('add-order-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const products = Array.from(document.querySelectorAll('.order-product-row')).map(row => ({
        product_id: Number(row.querySelector('.product-id').value),
        quantity: Number(row.querySelector('.product-quantity').value)
    }));

    if (products.some(item => !Number.isInteger(item.product_id) || item.product_id < 1 ||
        !Number.isInteger(item.quantity) || item.quantity < 1)) {
        showOrderMessage('Cada producto debe seleccionarse y tener una cantidad positiva.', 'warning');
        return;
    }
    if (products.some(item => {
        const product = productsCatalog.find(current => current.id === item.product_id);
        return !product || item.quantity > product.stock;
    })) {
        showOrderMessage('La cantidad no puede superar el stock disponible.', 'warning');
        return;
    }

    fetch(`${ORDERS_API}/api/orders`, {
        method: 'POST',
        credentials: 'include',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({products})
    })
        .then(response => response.json().then(data => ({ok: response.ok, data})))
        .then(({ok, data}) => {
            if (!ok) throw new Error(data.message || 'No fue posible crear la orden.');
            showOrderMessage(data.message, 'success');
            document.getElementById('add-order-form').reset();
            document.getElementById('order-products').innerHTML = document.querySelector('.order-product-row').outerHTML;
            updateRemoveButtons();
            getProducts().then(getOrders).catch(error => showOrderMessage(error.message, 'danger'));
        })
        .catch(error => showOrderMessage(error.message, 'danger'));
});

getProducts()
    .then(getOrders)
    .catch(error => showOrderMessage(error.message, 'danger'));
