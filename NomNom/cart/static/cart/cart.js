// Cart-specific JavaScript functionality

document.addEventListener('DOMContentLoaded', () => {
    let cartData = window.initialCartData || [];
    let deliveryCost = window.deliveryCost || 700.00;  // Use window.deliveryCost if available, otherwise default
    const TAX_RATE = 0.15; // 15% tax for Mauritius

    const cartList = document.getElementById('cart-list');
    const emptyCartMessage = document.getElementById('empty-cart-message');
    const cartPageActions = document.getElementById('cart-page-actions');
    const itemCountSpan = document.getElementById('item-count');
    const subtotalSpan = document.getElementById('subtotal');
    const deliveryCostSpan = document.getElementById('delivery-cost');
    const taxCostSpan = document.getElementById('tax-cost');
    const totalCostSpan = document.getElementById('total-cost');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    // Render cart items
    renderCart();

    function renderCart() {
        cartList.innerHTML = '';
        const cartPage = document.getElementById('cart-page');

        if (cartData.length === 0) {
            cartPage.classList.add('empty-state');
            document.getElementById('order-summary').style.display = 'none';
            if(cartPageActions) cartPageActions.style.display = 'none';
            emptyCartMessage.style.display = 'block';
            document.querySelector('.cart-items-section').style.display = 'none'; // Hide header and list
        } else {
            cartPage.classList.remove('empty-state');
            document.getElementById('order-summary').style.display = 'block';
            emptyCartMessage.style.display = 'none';
            document.querySelector('.cart-items-section').style.display = 'block'; // Show header and list

            cartData.forEach((item, index) => {
                const itemCard = createCartItemHTML(item, index);
                cartList.appendChild(itemCard);
            });
        }

        updateOrderSummary();
    }

    function createCartItemHTML(item, index) {
        const li = document.createElement('li');
        li.className = 'cart-item-card';
        li.dataset.index = index;

        const qty = item.quantity || 1;
        const subtotal = (item.price * qty).toFixed(2);

        // Handle image URL - the backend already provides the full URL via image.url
        let imageUrl = item.image || '/static/images/placeholder.png';

        // If image doesn't start with / or http, prepend /static/
        if (imageUrl && !imageUrl.startsWith('/') && !imageUrl.startsWith('http')) {
            imageUrl = `/static/${imageUrl}`;
        }

        // Build custom cake details HTML if it's a custom cake
        let customDetailsHTML = '';
        if (item.is_custom) {
            customDetailsHTML = `
                <div class="custom-cake-details">
                    <div class="custom-details-grid">
                        ${item.flavour ? `<div class="detail-item"><strong>Flavour:</strong> ${item.flavour}</div>` : ''}
                        ${item.size ? `<div class="detail-item"><strong>Size:</strong> ${item.size}</div>` : ''}
                        ${item.filling ? `<div class="detail-item"><strong>Filling:</strong> ${item.filling}</div>` : ''}
                        ${item.frosting ? `<div class="detail-item"><strong>Frosting:</strong> ${item.frosting}</div>` : ''}
                        ${item.decoration ? `<div class="detail-item"><strong>Decoration:</strong> ${item.decoration}</div>` : ''}
                        ${item.layers && item.layers > 1 ? `<div class="detail-item"><strong>Layers:</strong> ${item.layers}</div>` : ''}
                        ${item.cake_message ? `<div class="detail-item detail-message"><strong>Message:</strong> "${item.cake_message}"</div>` : ''}
                        ${item.pickup_date ? `<div class="detail-item detail-date"><strong>Pickup Date:</strong> ${formatDate(item.pickup_date)}</div>` : ''}
                    </div>
                </div>
            `;
        }

        li.innerHTML = `
            ${item.is_custom ? '' : `
            <div class="item-image-container">
                <img src="${imageUrl}" alt="${item.name}" class="item-image">
            </div>
            `}
            <div class="item-details">
                <h3>${item.name}</h3>
                <p>Rs ${item.price.toFixed(2)}</p>
                ${customDetailsHTML}
            </div>
            <div class="item-price-qty">
                <div class="qty-selector">
                    <button class="qty-minus">−</button>
                    <span>${qty}</span>
                    <button class="qty-plus">+</button>
                </div>
                <span class="item-subtotal">Rs.${subtotal}</span>
            </div>
            <button class="remove-item"><i class="fas fa-times"></i></button>
        `;

        return li;
    }

    function updateOrderSummary() {
        const subtotal = cartData.reduce((total, item) => total + (item.price * (item.quantity || 1)), 0);
        const itemCount = cartData.reduce((total, item) => total + (item.quantity || 1), 0);
        const tax = subtotal * TAX_RATE;
        const total = subtotal + deliveryCost + tax;

        // Update cart page summary elements (if they exist)
        if(itemCountSpan) itemCountSpan.textContent = itemCount;
        if(subtotalSpan) subtotalSpan.textContent = `Rs.${subtotal.toFixed(2)}`;
        if(deliveryCostSpan) deliveryCostSpan.textContent = `Rs.${deliveryCost.toFixed(2)}`;
        if(taxCostSpan) taxCostSpan.textContent = `Rs.${tax.toFixed(2)}`;
        if(totalCostSpan) totalCostSpan.textContent = `Rs.${total.toFixed(2)}`;

        // Update payment page summary elements (if they exist)
        if(window.paymentItemCountSpan) window.paymentItemCountSpan.textContent = itemCount;
        if(window.paymentSubtotalSpan) window.paymentSubtotalSpan.textContent = `Rs.${subtotal.toFixed(2)}`;
        if(window.paymentDeliveryCostSpan) window.paymentDeliveryCostSpan.textContent = `Rs.${deliveryCost.toFixed(2)}`;
        if(window.paymentTaxCostSpan) window.paymentTaxCostSpan.textContent = `Rs.${tax.toFixed(2)}`;
        if(window.paymentTotalCostSpan) window.paymentTotalCostSpan.textContent = `Rs.${total.toFixed(2)}`;
    }

    function formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }

    function showToast(message) {
        toastMessage.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    // --- EVENT LISTENERS ---
    if(cartList) {
        cartList.addEventListener('click', (event) => {
            const itemCard = event.target.closest('.cart-item-card');
            if (!itemCard) return;
            const itemIndex = parseInt(itemCard.dataset.index);
            const item = cartData[itemIndex];
            if (!item) return;

            if (event.target.classList.contains('qty-plus')) {
                const newQuantity = (item.quantity || 1) + 1;
                updateQuantityInBackend(itemIndex, newQuantity);
            } else if (event.target.classList.contains('qty-minus')) {
                if ((item.quantity || 1) > 1) {
                    const newQuantity = (item.quantity || 1) - 1;
                    updateQuantityInBackend(itemIndex, newQuantity);
                }
            } else if (event.target.classList.contains('remove-item') || event.target.parentElement.classList.contains('remove-item')) {
                // Redirect to Django backend to remove item
                window.location.href = `/cart/remove/${itemIndex}/`;
            }
        });
    }

    // Function to update quantity in backend via AJAX
    function updateQuantityInBackend(index, quantity) {
        fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                index: index,
                quantity: quantity
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update local cart data
                    cartData[index].quantity = quantity;
                    renderCart();

                    // Update cart count in navbar
                    const cartCountElement = document.getElementById('cart-count');
                    if (cartCountElement) {
                        cartCountElement.textContent = data.cart_count;
                        if (data.cart_count === 0) {
                            cartCountElement.classList.add('hidden');
                        } else {
                            cartCountElement.classList.remove('hidden');
                        }
                    }
                } else {
                    showToast('Failed to update quantity');
                }
            })
            .catch(error => {
                showToast('Error updating quantity');
            });
    }

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});