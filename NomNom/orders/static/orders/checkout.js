// Checkout/Order-specific JavaScript functionality

document.addEventListener('DOMContentLoaded', () => {
    let cartData = window.initialCartData || [];
    let deliveryCost = window.deliveryCost || 700.00;  // Use window.deliveryCost if available, otherwise default
    const TAX_RATE = 0.15; // 15% tax for Mauritius

    const orderSummary = document.getElementById('order-summary');
    const deliveryOptions = document.getElementsByName('delivery');
    const deliveryDateInput = document.getElementById('deliveryDate');
    const datePickerGroup = document.getElementById('date-picker-group');
    const itemCountSpan = document.getElementById('item-count');
    const subtotalSpan = document.getElementById('subtotal');
    const deliveryCostSpan = document.getElementById('delivery-cost');
    const taxCostSpan = document.getElementById('tax-cost');
    const totalCostSpan = document.getElementById('total-cost');

    
    // Payment page summary elements (for checkout)
    window.paymentItemCountSpan = document.getElementById('payment-item-count');
    window.paymentSubtotalSpan = document.getElementById('payment-subtotal');
    window.paymentDeliveryCostSpan = document.getElementById('payment-delivery-cost');
    window.paymentTaxCostSpan = document.getElementById('payment-tax-cost');
    window.paymentTotalCostSpan = document.getElementById('payment-total-cost');

    const pages = document.querySelectorAll('.page-section');
    const progressSteps = document.querySelectorAll('.progress-step');
    const progressTrack = document.getElementById('progress-track');

    updateOrderSummary();
    });
    // Checkout.js should not handle page navigation if cart.js is also loaded
    // Let cart.js handle the page navigation; checkout.js just enhances functionality

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

    deliveryOptions.forEach(option => {
        option.addEventListener('change', (event) => {
            if (event.target.value === 'express') {
                deliveryCost = 700.00;
                if(datePickerGroup) datePickerGroup.classList.remove('show');
            } else if (event.target.value === 'schedule') {
                deliveryCost = 300.00;
                if(datePickerGroup) datePickerGroup.classList.add('show');
                // Set minimum date to 2 days from today
                const minDate = new Date();
                minDate.setDate(minDate.getDate() + 2);
                const minDateStr = minDate.toISOString().split('T')[0];
                if(deliveryDateInput) deliveryDateInput.min = minDateStr;
                if(deliveryDateInput) deliveryDateInput.disabled = false;
            } else {
                // Default
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                if(deliveryDateInput) deliveryDateInput.min = tomorrow.toISOString().split('T')[0];
            }
            updateOrderSummary();
        });
    });

    // Handle date selection
    if(deliveryDateInput) {
        deliveryDateInput.addEventListener('change', (event) => {
            const selectedDate = new Date(event.target.value);
            const minDate = new Date();
            minDate.setDate(minDate.getDate() + 2);
            minDate.setHours(0, 0, 0, 0);

            if (selectedDate < minDate) {
                showToast('Please select a delivery date at least 2 days from today');
                document.getElementById('date-error').style.display = 'none';
                return;
            }
            // Clear error if valid
            document.getElementById('date-error').style.display = 'none';
        });

        // Initialize date picker min date
        const minDate = new Date();
        minDate.setDate(minDate.getDate() + 2);
        const minDateStr = minDate.toISOString().split('T')[0];
        deliveryDateInput.min = minDateStr;
        deliveryDateInput.disabled = true; // Disabled by default until schedule is selected
    }

    // Page Navigation Listeners
    const toInfoBtn = document.getElementById('to-info-btn');
    if (toInfoBtn) {
        toInfoBtn.addEventListener('click', () => {
            if (cartData.length > 0) {
                // Validate date if scheduled
                const scheduleRadio = document.getElementById('schedule');
                if (scheduleRadio && scheduleRadio.checked) {
                    if (!deliveryDateInput.value) {
                        showToast('Please select a delivery date before proceeding.');
                        document.getElementById('date-error').textContent = 'Please select a delivery date.';
                        document.getElementById('date-error').style.display = 'block';
                        return;
                    }
                }
                showPage('info-page', 2);
            } else {
                showToast("Your cart is empty!");
            }
        });
    }

    const backToCartBtn = document.getElementById('back-to-cart-btn');
    if (backToCartBtn) {
        backToCartBtn.addEventListener('click', () => {
            showPage('cart-page', 1);
        });
    }

    // --- VALIDATION FUNCTIONS ---
    const validators = {
        email: (value) => /^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(value) ? '' : 'Please enter a valid email address.',
        phone: (value) => /^5\d{7}$/.test(value.replace(/\s/g, '')) ? '' : 'Phone number must start with 5 and have exactly 8 digits.',
        name: (value) => /^[A-Za-z\s]+$/.test(value) ? '' : 'Name must contain only letters.',
        address: (value) => value.trim() ? '' : 'Street address is required.',
        city: (value) => {
            if (!window.cityList) return ''; // Will validate after JSON loads
            return window.cityList.map(c => c.toLowerCase()).includes(value.toLowerCase())
                ? '' 
                : 'Please select a valid city.';
        },

        zip: (value) => /^\d{5}$/.test(value) ? '' : 'Postal code must be exactly 5 digits.',
        cardNumber: (value) => /^\d{16}$/.test(value.replace(/\s/g, '')) ? '' : 'Card number must be exactly 16 digits.',
        expiry: (value) => {
            if (!/^\d{2}\/\d{2}$/.test(value)) return 'Invalid format (MM/YY).';
            const [month, year] = value.split('/').map(Number);
            const now = new Date();
            const currentYear = now.getFullYear() % 100;
            const currentMonth = now.getMonth() + 1;
            if (month < 1 || month > 12) return 'Invalid month.';
            if (year < currentYear || (year === currentYear && month < currentMonth)) return 'Expiry date cannot be in the past.';
            return '';
        },
        cvv: (value) => /^\d{3}$/.test(value) ? '' : 'CVV must be exactly 3 digits.'
    };

    function validateField(fieldId, validatorName) {
        const input = document.getElementById(fieldId);
        const errorEl = document.getElementById(`${fieldId}-error`);
        if (!input || !errorEl) return false;

        const errorMessage = validators[validatorName](input.value);
        if (errorMessage) {
            errorEl.textContent = errorMessage;
            errorEl.style.display = 'block';
            return false;
        } else {
            errorEl.style.display = 'none';
            return true;
        }
    }

    // --- REAL-TIME VALIDATION LISTENERS ---
    ['email', 'phone', 'firstName', 'lastName', 'address', 'city', 'zip', 'nameOnCard'].forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;

        let validator = id;
        if (id === 'firstName' || id === 'lastName' || id === 'nameOnCard') validator = 'name';

        el.addEventListener('input', () => {
            // For phone, allow typing but validate on input
            if (id === 'phone') {
                el.value = el.value.replace(/[^0-9]/g, '');
            }
            // Check validity to clear error, but don't show new error
            const errorEl = document.getElementById(`${id}-error`);
            const errorMessage = validators[validator](el.value);
            if (!errorMessage) {
                errorEl.style.display = 'none';
            }
        });

        el.addEventListener('blur', () => {
            validateField(id, validator);
        });
    });

    const toPaymentBtn = document.getElementById('to-payment-btn');
    if (toPaymentBtn) {
        toPaymentBtn.addEventListener('click', () => {
            const contactValid = validateField('email', 'email') & validateField('phone', 'phone');
            const addressValid = validateField('firstName', 'name') &
                validateField('lastName', 'name') &
                validateField('address', 'address') &
                validateField('city', 'city') &
                validateField('zip', 'zip');

            if (contactValid && addressValid) {
                showPage('payment-page', 3);
            } else {
                showToast('Please fill in all required fields correctly.');
            }
        });
    }

    const backToInfoBtn = document.getElementById('back-to-info-btn');
    if (backToInfoBtn) {
        backToInfoBtn.addEventListener('click', () => {
            showPage('info-page', 2);
        });
    }

    function showToast(message) {
        const toast = document.getElementById('toast');
        const toastMessage = document.getElementById('toast-message');
        if(toast && toastMessage) {
            toastMessage.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }
    }

    // --- CART ITEM MANIPULATION (Quantity updates, removal) ---
    const cartList = document.getElementById('cart-list');
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
                    renderCart(); // Re-render the cart with updated data

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

    // Function to render cart items (for when cart items are shown on checkout page)
    function renderCart() {
        const cartList = document.getElementById('cart-list');
        if (!cartList) return; // Only render if cart list exists on this page

        cartList.innerHTML = '';
        const cartPage = document.getElementById('cart-page');

        if (cartData.length === 0) {
            if(cartPage) cartPage.classList.add('empty-state');
            const orderSummary = document.getElementById('order-summary');
            if(orderSummary) orderSummary.style.display = 'none';
            const emptyCartMessage = document.getElementById('empty-cart-message');
            const cartPageActions = document.getElementById('cart-page-actions');
            if(emptyCartMessage) emptyCartMessage.style.display = 'block';
            if(cartPageActions) cartPageActions.style.display = 'none';
            const cartItemsSection = document.querySelector('.cart-items-section');
            if(cartItemsSection) cartItemsSection.style.display = 'none'; // Hide header and list
        } else {
            if(cartPage) cartPage.classList.remove('empty-state');
            const orderSummary = document.getElementById('order-summary');
            if(orderSummary) orderSummary.style.display = 'block';
            const emptyCartMessage = document.getElementById('empty-cart-message');
            if(emptyCartMessage) emptyCartMessage.style.display = 'none';
            const cartItemsSection = document.querySelector('.cart-items-section');
            if(cartItemsSection) cartItemsSection.style.display = 'block'; // Show header and list

            cartData.forEach((item, index) => {
                const itemCard = createCartItemHTML(item, index);
                cartList.appendChild(itemCard);
            });
        }

        updateOrderSummary();
    }

    // Function to create cart item HTML
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

    function formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    }

    // --- CITY AUTO-FILL POSTAL CODE ---
fetch("/static/data/city_zip.json")
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        window.cityZipMap = data;

        const cityInput = document.getElementById("city");
        const zipInput = document.getElementById("zip");

        if (cityInput && zipInput) {
            // Add event listener for both input and change events to handle typing and selection from datalist
            cityInput.addEventListener("input", function () {
                const typed = this.value.trim().toLowerCase();

                // Find city that matches (case-insensitive) - use fuzzy matching
                let matchedCity = null;
                for (const city in window.cityZipMap) {
                    if (city.toLowerCase() === typed) {
                        matchedCity = city;
                        break;
                    }
                }

                if (matchedCity) {
                    zipInput.value = window.cityZipMap[matchedCity];
                    validateField("zip", "zip");
                } else {
                    // Clear zip if no exact match is found
                    zipInput.value = '';
                }
            });

            // Also handle the 'change' event for when user selects from datalist
            cityInput.addEventListener("change", function () {
                const selectedCity = this.value.trim();

                if (window.cityZipMap[selectedCity]) {
                    zipInput.value = window.cityZipMap[selectedCity];
                    validateField("zip", "zip");
                }
            });
        }
    })
    .catch(err => console.error("Failed to load city_zip.json:", err));


});
