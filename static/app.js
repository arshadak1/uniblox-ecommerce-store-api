// ===== Configuration =====
const API_BASE = 'http://localhost:8000/api/v1';

// ===== Product Data =====
let products = []

// ===== Application State =====
let cart = [];

// ===== DOM Elements =====
const elements = {
    cartToggle: null,
    cartClose: null,
    cartOverlay: null,
    cartSidebar: null,
    cartBadge: null,
    cartBody: null,
    cartFooter: null,
    cartLoading: null,
    checkoutBtn: null,
    discountInput: null,
    productsGrid: null,
    messageContainer: null
};


// ===== Initialize Application =====
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    attachEventListeners();
    renderProducts();
    renderCart();
    fetchProducts();
});

async function fetchProducts() {
    try {
        const response = await fetch(`${API_BASE}/products`);
        const data = await response.json();

        if (!response.ok) {
            showMessage('error', data.detail || 'Failed to load products');
            return;
        }

        // Assuming backend returns: [{ id, name, price, description, icon }]
        products = data.products;

        renderProducts();
    } catch (error) {
        console.error('Fetch products error:', error);
        showMessage('error', 'Unable to load products. Check API connection.');
    }
}

// ===== Initialize DOM Elements =====
function initializeElements() {
    elements.cartToggle = document.getElementById('cartToggle');
    elements.cartClose = document.getElementById('cartClose');
    elements.cartOverlay = document.getElementById('cartOverlay');
    elements.cartSidebar = document.getElementById('cartSidebar');
    elements.cartBadge = document.getElementById('cartBadge');
    elements.cartBody = document.getElementById('cartBody');
    elements.cartFooter = document.getElementById('cartFooter');
    elements.cartLoading = document.getElementById('cartLoading');
    elements.checkoutBtn = document.getElementById('checkoutBtn');
    elements.discountInput = document.getElementById('discountCode');
    elements.productsGrid = document.getElementById('productsGrid');
    elements.messageContainer = document.getElementById('messageArea');
}

// ===== Attach Event Listeners =====
function attachEventListeners() {
    elements.cartToggle.addEventListener('click', openCart);
    elements.cartClose.addEventListener('click', closeCart);
    elements.cartOverlay.addEventListener('click', closeCart);
    elements.checkoutBtn.addEventListener('click', handleCheckout);

    // Close cart on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeCart();
    });
}

// ===== Cart Functions =====
function openCart() {
    elements.cartSidebar.classList.add('active');
    elements.cartOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeCart() {
    elements.cartSidebar.classList.remove('active');
    elements.cartOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

// ===== Render Products =====
function renderProducts() {
    const html = products.map(product => `
        <div class="product-card">
            <div class="product-image">${product.icon}</div>
            <div class="product-content">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-description">${product.description}</p>
                <div class="product-footer">
                    <div class="product-price">$${product.price.toFixed(2)}</div>
                    <button class="btn-add-cart" onclick="addToCart(${product.id}); event.stopPropagation();">
                        <span>Add</span>
                        <span>+</span>
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    elements.productsGrid.innerHTML = html;
}

function getLoader() {
    return '<div class="loader loader-spinner" role="status" aria-label="Loading"></div>';
}

// ===== Add to Cart =====
async function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;
    const product_data = {
        product_id: product.id,
        name: product.name,
        price: product.price,
        quantity: 1,
    }
    let loader = getLoader();
    try {
        const response = await fetch(`${API_BASE}/cart/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(product_data)
        });

        const data = await response.json();

        if (response.ok) {
            // Success
            if (!product) return;

            const existingItem = cart.find(item => item.product_id === productId);

            if (existingItem) {
                existingItem.quantity++;
            } else {
                product_data.icon = product.icon
                cart.push(product_data);
            }


            showMessage('success', `${product.name} added to cart`);
            renderCart();

            // Animate cart badge
            elements.cartBadge.style.transform = 'scale(1.3)';
            setTimeout(() => {
                elements.cartBadge.style.transform = 'scale(1)';
            }, 200);

        } else {
            // Error
            showMessage('error', data.detail || 'Add to cart failed. Please try again.');
        }
    } catch (error) {
        console.error('Add to cart error:', error);
        showMessage('error', 'Unable to connect to server.');
    } finally {
        // Hide loading
        elements.cartLoading.classList.remove('active');
        elements.checkoutBtn.disabled = false;
    }
}

// ===== Update Quantity =====
async function updateQuantity(productId, change) {
    const item = cart.find(item => item.product_id === productId);
    if (!item) return;
    item.quantity += change;

    if (item.quantity <= 0) {
        removeFromCart(productId);
        return;
    }
    try {
        const response = await fetch(`${API_BASE}/cart/update`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({product_id: productId, quantity: item.quantity})
        });

        const data = await response.json();

        if (response.ok) {
            // Success
            renderCart();
        } else {
            // Error
            showMessage('error', data.detail || 'Add to cart failed. Please try again.');
        }
    } catch (error) {
        console.error('Add to cart error:', error);
        showMessage('error', 'Unable to connect to server.');
    } finally {
        // Hide loading
        elements.cartLoading.classList.remove('active');
        elements.checkoutBtn.disabled = false;
    }
}

// ===== Remove from Cart =====
async function removeFromCart(productId) {
    renderCart();

    try {
        const response = await fetch(`${API_BASE}/cart/remove/${productId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
        });

        const data = await response.json();

        if (response.ok) {
            // Success
            const item = cart.find(item => item.product_id === productId);
            cart = cart.filter(item => item.product_id !== productId);

            if (item) {
                showMessage('success', `${item.name} removed from cart`);
            }
            renderCart();
        } else {
            // Error
            showMessage('error', data.detail || 'Checkout failed. Please try again.');
        }
    } catch (error) {
        console.error('Remove cart error:', error);
        showMessage('error', 'Unable to connect to server.');
    } finally {
        // Hide loading
        elements.cartLoading.classList.remove('active');
        elements.checkoutBtn.disabled = false;
    }
}

// ===== Render Cart =====
function renderCart() {
    const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    // Update cart badge
    elements.cartBadge.textContent = totalItems;
    elements.cartBadge.style.transition = 'transform 0.2s';

    // Update cart summary
    document.getElementById('cartSubtotal').textContent = `$${subtotal.toFixed(2)}`;
    document.getElementById('cartTotal').textContent = `$${subtotal.toFixed(2)}`;

    if (cart.length === 0) {
        // Show empty state
        elements.cartBody.innerHTML = `
            <div class="cart-empty">
                <div class="empty-icon">🛒</div>
                <p>Your cart is empty</p>
                <small>Add some products to get started</small>
            </div>
        `;
        elements.cartFooter.style.display = 'none';
    } else {
        // Show cart items
        const itemsHtml = cart.map(item => `
            <div class="cart-item">
                <div class="cart-item-image">${item.icon}</div>
                <div class="cart-item-details">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">$${(item.price * item.quantity).toFixed(2)}</div>
                    <div class="cart-item-controls">
                        <button class="qty-btn" onclick="updateQuantity(${item.product_id}, -1)">−</button>
                        <span class="qty-display">${item.quantity}</span>
                        <button class="qty-btn" onclick="updateQuantity(${item.product_id}, 1)">+</button>
                        <button class="btn-remove" onclick="removeFromCart(${item.product_id})" title="Remove">
                            ✕
                        </button>
                    </div>
                </div>
            </div>
        `).join('');

        elements.cartBody.innerHTML = itemsHtml;
        elements.cartFooter.style.display = 'block';
    }
}

// ===== Handle Checkout =====
async function handleCheckout() {
    if (cart.length === 0) {
        showMessage('error', 'Your cart is empty');
        return;
    }

    const discountCode = elements.discountInput.value.trim().toUpperCase();

    // Show loading
    elements.cartLoading.classList.add('active');
    elements.checkoutBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/checkout`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                discount_code: discountCode || null
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Success
            let message = `Order placed successfully! Total: $${data.total_amount.toFixed(2)}`;

            if (data.discount_applied) {
                message = `Order placed! You saved $${data.discount_amount.toFixed(2)}! Total: $${data.total_amount.toFixed(2)}`;
            }

            if (data.new_discount_code) {
                setTimeout(() => {
                    showMessage('success', `🎉 Congratulations! You earned a discount code: ${data.new_discount_code}`);
                }, 2000);
            }

            showMessage('success', message);

            // Clear cart
            cart = [];
            elements.discountInput.value = '';
            renderCart();
            closeCart();
        } else {
            // Error
            showMessage('error', data.detail || 'Checkout failed. Please try again.');
        }
    } catch (error) {
        console.error('Checkout error:', error);
        showMessage('error', 'Unable to connect to server. Please check if the API is running.');
    } finally {
        // Hide loading
        elements.cartLoading.classList.remove('active');
        elements.checkoutBtn.disabled = false;
    }
}

// ===== Show Message =====
function showMessage(type, text) {
    const messageId = Date.now();
    const icon = type === 'success' ? '✓' : '✕';

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <span class="message-icon">${icon}</span>
        <span>${text}</span>
    `;
    messageDiv.id = `message-${messageId}`;

    elements.messageContainer.appendChild(messageDiv);

    // Auto remove after 4 seconds
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }, 4000);
}

// ===== Utility Functions =====
function formatCurrency(amount) {
    return `$${amount.toFixed(2)}`;
}

function getCartTotal() {
    return cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
}

function getCartItemCount() {
    return cart.reduce((sum, item) => sum + item.quantity, 0);
}