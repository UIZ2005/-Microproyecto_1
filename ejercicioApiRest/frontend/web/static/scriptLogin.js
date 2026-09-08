const USERS_API = 'http://192.168.100.3:5002';

function showLoginMessage(message, type) {
    const element = document.getElementById('login-message');
    element.textContent = message;
    element.className = `mt-3 alert alert-${type}`;
}

document.getElementById('login-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    if (!username || !password) {
        showLoginMessage('Usuario y contraseña son obligatorios.', 'warning');
        return;
    }

    try {
        const response = await fetch(`${USERS_API}/api/login`, {
            method: 'POST',
            credentials: 'include',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.message || 'No fue posible iniciar sesión.');
        }
        showLoginMessage(`Sesión iniciada como ${data.user.username}.`, 'success');
    } catch (error) {
        showLoginMessage(error.message, 'danger');
    }
});

document.getElementById('logout-button').addEventListener('click', async function() {
    const response = await fetch(`${USERS_API}/api/logout`, {
        method: 'POST',
        credentials: 'include'
    });
    const data = await response.json();
    showLoginMessage(data.message, response.ok ? 'success' : 'danger');
});