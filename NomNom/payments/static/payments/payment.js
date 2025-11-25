// Payment-specific JavaScript functionality

document.addEventListener('DOMContentLoaded', () => {
    let cartData = window.initialCartData || [];
    let deliveryCost = 700.00;
    const TAX_RATE = 0.15; // 15% tax for Mauritius

    const deliveryDateInput = document.getElementById('deliveryDate');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    // --- VALIDATION FUNCTIONS ---
    const validators = {
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

    function showToast(message) {
        if(toast && toastMessage) {
            toastMessage.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 3000);
        }
    }

    // Format card number input
    if(document.getElementById('cardNumber')) {
        document.getElementById('cardNumber').addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            e.target.value = formattedValue;

            // Clear error if valid
            const errorEl = document.getElementById('cardNumber-error');
            const errorMessage = validators['cardNumber'](e.target.value);
            if (!errorMessage) {
                errorEl.style.display = 'none';
            }
        });

        document.getElementById('cardNumber').addEventListener('blur', () => {
            validateField('cardNumber', 'cardNumber');
        });
    }

    // Format expiry date input
    if(document.getElementById('expiry')) {
        document.getElementById('expiry').addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.slice(0, 2) + '/' + value.slice(2, 4);
            }
            e.target.value = value;

            // Clear error if valid
            const errorEl = document.getElementById('expiry-error');
            const errorMessage = validators['expiry'](e.target.value);
            if (!errorMessage) {
                errorEl.style.display = 'none';
            }
        });

        document.getElementById('expiry').addEventListener('blur', () => {
            validateField('expiry', 'expiry');
        });
    }

    // CVV Input restriction
    if(document.getElementById('cvv')) {
        document.getElementById('cvv').addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');

            // Clear error if valid
            const errorEl = document.getElementById('cvv-error');
            const errorMessage = validators['cvv'](e.target.value);
            if (!errorMessage) {
                errorEl.style.display = 'none';
            }
        });

        document.getElementById('cvv').addEventListener('blur', () => {
            validateField('cvv', 'cvv');
        });
    }

    const placeOrderBtn = document.getElementById('place-order-btn');
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', () => {
            const validCard = validateField('cardNumber', 'cardNumber');
            const validName = validateField('nameOnCard', 'name');
            const validExpiry = validateField('expiry', 'expiry');
            const validCvv = validateField('cvv', 'cvv');

            // Re-validate date just in case
            let validDate = true;
            const scheduleRadio = document.getElementById('schedule');
            if (scheduleRadio && scheduleRadio.checked && !deliveryDateInput.value) {
                validDate = false;
                showToast('Please select a delivery date.');
            }

            if (validCard && validName && validExpiry && validCvv && validDate) {
                showToast('Order placed successfully! Thank you for your purchase.');

                // Capture purchase data before clearing
                const totalCost = document.getElementById('total-cost').textContent;
                const deliveryDate = deliveryDateInput.value;
                const isScheduled = document.getElementById('schedule').checked;

                window.lastPurchaseData = {
                    items: [...cartData],
                    total: totalCost,
                    deliveryDate: deliveryDate,
                    isScheduled: isScheduled
                };

                // Simulate order placement, then redirect or update UI
                setTimeout(() => {
                    // This would normally be handled by backend
                    // For now, just show a success message or redirect
                    window.location.href = '/orders/success/';
                }, 1000);
            } else {
                showToast('Please correct the errors in the payment form.');
            }
        });
    }

    function renderPurchaseSummary(data) {
        const container = document.getElementById('purchase-details');
        let itemsHtml = '<ul class="summary-items-list">';
        data.items.forEach(item => {
            itemsHtml += `
                <li>
                    <span>${item.quantity}x ${item.name}</span>
                    <span>Rs. ${(item.price * item.quantity).toFixed(2)}</span>
                </li>
            `;
        });
        itemsHtml += '</ul>';

        let deliveryHtml = '';
        if (data.isScheduled && data.deliveryDate) {
            const date = new Date(data.deliveryDate);
            const today = new Date();
            today.setHours(0, 0, 0, 0);

            // Create a date object for the delivery date at midnight for comparison
            const deliveryDateObj = new Date(data.deliveryDate);
            deliveryDateObj.setHours(0, 0, 0, 0);

            if (deliveryDateObj < today) {
                deliveryHtml = `<p><strong>Delivered on:</strong> ${date.toLocaleDateString()}</p>`;
            } else {
                deliveryHtml = `<p><strong>Delivery:</strong> ${date.toLocaleDateString()}</p>`;
            }
        } else {
            deliveryHtml = `<p><strong>Delivery:</strong> Express (Tomorrow)</p>`;
        }

        container.innerHTML = `
            ${itemsHtml}
            <div class="summary-divider"></div>
            ${deliveryHtml}
            <p class="summary-total-line"><strong>Total Paid:</strong> ${data.total}</p>
        `;
    }
});