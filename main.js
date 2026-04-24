// static/js/main.js
// Shared utilities for all pages

// ── ON PAGE LOAD ─────────────────────────
document.addEventListener('DOMContentLoaded', () => {

    // 1. Highlight active nav link
    const links = document.querySelectorAll('.nav-link');
    links.forEach(link => {
        if (link.getAttribute('href') === window.location.pathname) {
            link.classList.add('active');
        }
    });

    // 2. Show logged in user in navbar
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const navUser = document.getElementById('nav-user');
    if (navUser && user.name) {
        navUser.textContent = user.role === 'admin' ?
            'Admin: ' + user.name :
            'Hi, ' + user.name;
    }

    // 3. Protect dashboard pages
    // If not logged in, redirect to login
    const publicPages = ['/', '/signup'];
    if (!publicPages.includes(window.location.pathname)) {
        if (!localStorage.getItem('user')) {
            window.location.href = '/';
        }
    }

});

// ── FORMAT FUNCTIONS ─────────────────────

// Format Indian currency
// Example: formatINR(18999) → "₹18,999.00"
function formatINR(amount) {
    return '₹' + Number(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Format date nicely
// Example: formatDate("2017-12-30") → "30 Dec 2017"
function formatDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

// Shorten long text
// Example: truncate("Samsung Galaxy M34 5G Phone", 20) → "Samsung Galaxy M34 5..."
function truncate(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Get rank badge HTML
// Gold for 1st, Silver for 2nd, Bronze for 3rd
function getRankBadge(index) {
    if (index === 0) return '<span class="rank-badge gold">1</span>';
    if (index === 1) return '<span class="rank-badge silver">2</span>';
    if (index === 2) return '<span class="rank-badge bronze">3</span>';
    return `<span class="rank-badge">${index + 1}</span>`;
}

// Get status badge HTML
// Example: getStatusBadge("delivered") → green badge
function getStatusBadge(status) {
    return `<span class="badge badge-${status}">${status}</span>`;
}

// ── ALERT FUNCTION ───────────────────────

// Show alert message on any page
// Usage: showAlert('Product added!', 'success')
// Usage: showAlert('Error!', 'error')
function showAlert(msg, type) {
    const box = document.getElementById('alert-box');
    if (!box) return;
    box.textContent = msg;
    box.className = `alert alert-${type}`;
    box.style.display = 'block';
    // Auto hide after 3 seconds
    setTimeout(() => {
        box.style.display = 'none';
    }, 3000);
}

// ── LOGOUT FUNCTION ──────────────────────

// Logout and redirect to login page
async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
    } catch (e) {
        // Even if request fails, clear local storage
    }
    localStorage.removeItem('user');
    window.location.href = '/';
}

// ── API HELPER FUNCTIONS ─────────────────

// GET request helper
// Usage: const data = await apiGet('/api/products');
async function apiGet(url) {
    try {
        const res = await fetch(url);
        const data = await res.json();
        return data;
    } catch (e) {
        console.error('GET error:', url, e);
        return null;
    }
}

// POST request helper
// Usage: const result = await apiPost('/api/products', {name: 'x'});
async function apiPost(url, body) {
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        return { ok: res.ok, data };
    } catch (e) {
        console.error('POST error:', url, e);
        return { ok: false, data: { error: 'Server error' } };
    }
}

// PUT request helper
// Usage: const result = await apiPut('/api/products/1', {name: 'y'});
async function apiPut(url, body) {
    try {
        const res = await fetch(url, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });
        const data = await res.json();
        return { ok: res.ok, data };
    } catch (e) {
        console.error('PUT error:', url, e);
        return { ok: false, data: { error: 'Server error' } };
    }
}

// DELETE request helper
// Usage: const result = await apiDelete('/api/products/1');
async function apiDelete(url) {
    try {
        const res = await fetch(url, { method: 'DELETE' });
        const data = await res.json();
        return { ok: res.ok, data };
    } catch (e) {
        console.error('DELETE error:', url, e);
        return { ok: false, data: { error: 'Server error' } };
    }
}

// ── LOADING STATE ────────────────────────

// Show loading spinner in a table
// Usage: showTableLoading('products-table', 6);
function showTableLoading(tableId, colSpan) {
    const table = document.getElementById(tableId);
    if (table) {
        table.innerHTML = `
      <tr>
        <td colspan="${colSpan}" class="loading">
          Loading data...
        </td>
      </tr>`;
    }
}

// ── USER INFO ────────────────────────────

// Get current logged in user
// Usage: const user = getCurrentUser();
function getCurrentUser() {
    return JSON.parse(localStorage.getItem('user') || '{}');
}

// Check if current user is admin
// Usage: if (isAdmin()) { showAdminButtons(); }
function isAdmin() {
    const user = getCurrentUser();
    return user.role === 'admin';
}