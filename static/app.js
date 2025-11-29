// Configuration
const API_BASE = 'http://localhost:8000/api/v1';

// Products data
const products = [
    { id: 1, name: 'Laptop', price: 999.99, description: 'High-performance laptop' },
    { id: 2, name: 'Mouse', price: 29.99, description: 'Wireless mouse' },
    { id: 3, name: 'Keyboard', price: 79.99, description: 'Mechanical keyboard' },
    { id: 4, name: 'Monitor', price: 299.99, description: '27-inch 4K monitor' },
    { id: 5, name: 'Headphones', price: 149.99, description: 'Noise-cancelling headphones' },
    { id: 6, name: 'Webcam', price: 89.99, description: 'HD webcam' }
];

// Cart state
let cart = [];

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    renderProducts();
    fetchStatistics();

    // Event listeners
    document.getElementById('checkoutBtn').addEventListener('click', handleCheckout);

    // Auto-refresh statistics every 30 seconds
    setInterval(fetchStatistics, 30000);
});

/**
 * Render products grid
 */
function renderProducts() {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <h3>${product.name}</h3>
            <p>${product.description}</p>
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <button class="btn btn-primary" onclick="addToCart(${product.id})">
                ➕ Add to Cart
            </button>
        </div>
    `).join('');
}

/**
 * Add item to cart
 * @param {number} productId - Product ID to add
 */
async function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) {
        console.error('Product not found:', productId);
        return;
    }

    const existingItem = cart.find(item => item.product_id === productId);

    if (existingItem) {
        existingItem.quantity++;
    } else {
        cart.push({
            product_id: product.id,
            name: product.name,
            price: product.price,
            quantity: 1
        });
    }
    const response = await fetch(`${API_BASE}/cart/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                product_id: product.id,
                name: product.name,
                price: product.price,
                quantity: 1
            })
        });

        const data = await response.json();

    showMessage('success', `Added ${product.name} to cart`);
    renderCart();
}

/**
 * Update item quantity in cart
 * @param {number} productId - Product ID
 * @param {number} delta - Change in quantity (+1 or -1)
 */
function updateQuantity(productId, delta) {
    const item = cart.find(item => item.product_id === productId);
    if (!item) return;

    item.quantity += delta;

    if (item.quantity <= 0) {
        removeFromCart(productId);
    } else {
        renderCart();
    }
}

/**
 * Remove item from cart
 * @param {number} productId - Product ID to remove
 */
function removeFromCart(productId) {
    const product = cart.find(item => item.product_id === productId);
    cart = cart.filter(item => item.product_id !== productId);

    if (product) {
        showMessage('success', `Removed ${product.name} from cart`);
    }

    renderCart();
}

/**
 * Render cart contents
 */
function renderCart() {
    const cartContent = document.getElementById('cartContent');
    const cartCount = document.getElementById('cartCount');
    const discountSection = document.getElementById('discountSection');
    const cartSummary = document.getElementById('cartSummary');
    const checkoutBtn = document.getElementById('checkoutBtn');

    // Calculate totals
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    // Update UI
    cartCount.textContent = totalItems;
    document.getElementById('subtotal').textContent = subtotal.toFixed(2);
    document.getElementById('total').textContent = subtotal.toFixed(2);

    if (cart.length === 0) {
        // Empty cart
        cartContent.innerHTML = '<div class="cart-empty"><p>Your cart is empty</p></div>';
        discountSection.style.display = 'none';
        cartSummary.style.display = 'none';
        checkoutBtn.style.display = 'none';
    } else {
        // Cart with items
        cartContent.innerHTML = `
            <div class="cart-items">
                ${cart.map(item => `
                    <div class="cart-item">
                        <div class="cart-item-info">
                            <h4>${item.name}</h4>
                            <div class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
                        </div>
                        <div class="cart-item-controls">
                            <div class="quantity-control">
                                <button class="quantity-btn" onclick="updateQuantity(${item.product_id}, -1)">−</button>
                                <span class="quantity-display">${item.quantity}</span>
                                <button class="quantity-btn" onclick="updateQuantity(${item.product_id}, 1)">+</button>
                            </div>
                            <button class="btn btn-danger" onclick="removeFromCart(${item.product_id})">🗑️</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        discountSection.style.display = 'block';
        cartSummary.style.display = 'block';
        checkoutBtn.style.display = 'block';
    }
}

/**
 * Handle checkout process
 */
async function handleCheckout() {
    if (cart.length === 0) {
        showMessage('error', 'Cart is empty');
        return;
    }

    const discountCode = document.getElementById('discountCode').value.trim().toUpperCase();
    const loading = document.getElementById('loading');
    const checkoutBtn = document.getElementById('checkoutBtn');

    // Show loading state
    loading.style.display = 'block';
    checkoutBtn.disabled = true;

    try {

        const response = await fetch(`${API_BASE}/checkout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                discount_code: document.getElementById("discountCode").value
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Success
            let message = `Order placed! Total: $${data.total_amount.toFixed(2)}`;

            if (data.discount_applied) {
                message += ` (Saved $${data.discount_amount.toFixed(2)})`;
            }

            if (data.new_discount_code) {
                message += `\n🎉 You earned a discount code: ${data.new_discount_code}`;
            }

            showMessage('success', message);

            // Clear cart
            cart = [];
            document.getElementById('discountCode').value = '';
            renderCart();

            // Refresh statistics
            fetchStatistics();
        } else {
            // Error from server
            showMessage('error', data.detail || 'Checkout failed');
        }
    } catch (error) {
        // Network or other error
        console.error('Checkout error:', error);
        showMessage('error', 'Failed to connect to server. Make sure the API is running on localhost:8000');
    } finally {
        // Hide loading state
        loading.style.display = 'none';
        checkoutBtn.disabled = false;
    }
}

/**
 * Fetch and display store statistics
 */
async function fetchStatistics() {
    try {
        const response = await fetch(`${API_BASE}/admin/stats`);

        if (response.ok) {
            const data = await response.json();

            // Update header stats
            document.getElementById('totalOrders').textContent = data.total_orders;
            document.getElementById('totalRevenue').textContent = data.total_purchase_amount.toFixed(2);

            // Update statistics cards
            document.getElementById('statOrders').textContent = data.total_orders;
            document.getElementById('statItems').textContent = data.total_items_purchased;
            document.getElementById('statRevenue').textContent = data.total_purchase_amount.toFixed(2);
            document.getElementById('statDiscounts').textContent = data.total_discount_amount.toFixed(2);
        }
    } catch (error) {
        console.error('Failed to fetch statistics:', error);
        // Silently fail - don't show error to user for background updates
    }
}

/**
 * Show message to user
 * @param {string} type - 'success' or 'error'
 * @param {string} text - Message text
 */
function showMessage(type, text) {
    const messageArea = document.getElementById('messageArea');
    messageArea.className = `message ${type}`;
    messageArea.textContent = text;
    messageArea.style.display = 'block';

    // Auto-hide after 5 seconds
    setTimeout(() => {
        messageArea.style.display = 'none';
    }, 5000);
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return `$${amount.toFixed(2)}`;
}

/**
 * Calculate cart total
 * @returns {number} Total cart value
 */
function calculateCartTotal() {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

/**
 * Get cart item count
 * @returns {number} Total number of items in cart
 */
function getCartItemCount() {
    return cart.reduce((sum, item) => sum + item.quantity, 0);
}