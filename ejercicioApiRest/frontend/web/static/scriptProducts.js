function getProducts() {
fetch('http://192.168.100.3:5003/api/products', {credentials: 'include'})

.then(response => response.json())

.then(data => {

    // Handle data
    console.log(data);

    // Get table body
    var productListBody = document.querySelector('#product-list tbody');

    productListBody.innerHTML = '';

    // Loop through products and populate table rows
    data.forEach(product => {

        var row = document.createElement('tr');

        // Name
        var nameCell = document.createElement('td');
        nameCell.textContent = product.name;
        row.appendChild(nameCell);

        // Description
        var descriptionCell = document.createElement('td');
        descriptionCell.textContent = product.description;
        row.appendChild(descriptionCell);

        // Price
        var priceCell = document.createElement('td');
        priceCell.textContent = product.price;
        row.appendChild(priceCell);

        // Stock
        var stockCell = document.createElement('td');
        stockCell.textContent = product.stock;
        row.appendChild(stockCell);

        // Actions
        var actionsCell = document.createElement('td');

        // Edit link
        var editLink = document.createElement('a');
        editLink.href = `/editProduct/${product.id}`;
        editLink.textContent = 'Edit';
        editLink.className = 'btn btn-primary mr-2';

        actionsCell.appendChild(editLink);

        // Delete link
        var deleteLink = document.createElement('a');
        deleteLink.href = '#';
        deleteLink.textContent = 'Delete';
        deleteLink.className = 'btn btn-danger';

        deleteLink.addEventListener('click', function() {
            deleteProduct(product.id);
        });

        actionsCell.appendChild(deleteLink);

        row.appendChild(actionsCell);

        productListBody.appendChild(row);

    });

})

.catch(error => console.error('Error:', error));


}

function createProduct() {


var data = {
    name: document.getElementById('name').value.trim(),
    description: document.getElementById('description').value.trim(),

    price: document.getElementById('price').value,

    stock: document.getElementById('stock').value

};

if (!data.name || !data.description || data.price === '' || data.stock === '') {
    alert('Todos los campos son obligatorios.');
    return;
}
if (Number(data.price) < 0 || Number(data.stock) < 0) {
    alert('El precio y el stock no pueden ser negativos.');
    return;
}

fetch('http://192.168.100.3:5003/api/products', {

    method: 'POST',

    headers: {
        'Content-Type': 'application/json',
    },
    credentials: 'include',

    body: JSON.stringify(data),

})

.then(response => {

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    return response.json();

})

.then(data => {

    // Handle success
    document.getElementById('name').value='';
    document.getElementById('description').value='';
    document.getElementById('price').value='';
    document.getElementById('stock').value='';
    alert('Producto creado exitosamente.');
    console.log(data);

})

.catch(error => {

    // Handle error
    console.error('Error:', error);

});


}

function updateProduct() {

var productId = document.getElementById('product-id').value;

var data = {
    name: document.getElementById('name').value.trim(),
    description: document.getElementById('description').value.trim(),

    price: document.getElementById('price').value,

    stock: document.getElementById('stock').value

};

if (!productId || !data.name || !data.description || data.price === '' || data.stock === '') {
    alert('Todos los campos son obligatorios.');
    return;
}
if (Number(data.price) < 0 || Number(data.stock) < 0) {
    alert('El precio y el stock no pueden ser negativos.');
    return;
}

fetch(`http://192.168.100.3:5003/api/products/${productId}`, {

    method: 'PUT',

    headers: {
        'Content-Type': 'application/json',
    },
    credentials: 'include',

    body: JSON.stringify(data),

})

.then(response => {

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    return response.json();

})

.then(data => {

    // Handle success
    console.log(data);

})

.catch(error => {

    // Handle error
    console.error('Error:', error);

});

}

function deleteProduct(productId) {

console.log('Deleting product with ID:', productId);

if (confirm('Are you sure you want to delete this product?')) {

    fetch(`http://192.168.100.3:5003/api/products/${productId}`, {

        method: 'DELETE',
        credentials: 'include',

    })

    .then(response => {

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        return response.json();

    })

    .then(data => {

        // Handle success
        console.log('Product deleted successfully:', data);

        // Reload the product list
        getProducts();

    })

    .catch(error => {

        // Handle error
        console.error('Error:', error);

    });

}
}
