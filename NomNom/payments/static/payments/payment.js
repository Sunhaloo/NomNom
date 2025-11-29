// ===============================
//   Clean Payment.js (Frontend Only)
// ===============================

document.addEventListener('DOMContentLoaded', () => {

    /* -----------------------
       TOAST NOTIFICATION
    ------------------------ */
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');

    function showToast(message) {
        if (toast && toastMessage) {
            toastMessage.textContent = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2500);
        }
    }

    /* -----------------------
       VALIDATION RULES
    ------------------------ */
    const validators = {
        cardNumber: (value) =>
            /^\d{16}$/.test(value.replace(/\s/g, ''))
                ? ''
                : 'Card number must be exactly 16 digits.',

        expiry: (value) => {
            if (!/^\d{2}\/\d{2}$/.test(value)) return 'Invalid format (MM/YY).';

            const [month, year] = value.split('/').map(Number);
            const now = new Date();
            const currentYear = now.getFullYear() % 100;
            const currentMonth = now.getMonth() + 1;

            if (month < 1 || month > 12) return 'Invalid month.';
            if (year < currentYear || (year === currentYear && month < currentMonth))
                return 'Expiry date cannot be in the past.';

            return '';
        },

        cvv: (value) =>
            /^\d{3}$/.test(value)
                ? ''
                : 'CVV must be exactly 3 digits.'
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

    /* -----------------------
       CARD NUMBER FORMATTING
    ------------------------ */
    const cardNumberEl = document.getElementById('cardNumber');
    if (cardNumberEl) {
        cardNumberEl.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            e.target.value = value.match(/.{1,4}/g)?.join(' ') || value;

            const errorEl = document.getElementById('cardNumber-error');
            if (!validators.cardNumber(e.target.value)) errorEl.style.display = 'none';
        });

        cardNumberEl.addEventListener('blur', () =>
            validateField('cardNumber', 'cardNumber')
        );
    }

    /* -----------------------
       EXPIRY FORMAT
    ------------------------ */
    const expiryEl = document.getElementById('expiry');
    if (expiryEl) {
        expiryEl.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');

            if (value.length >= 2) {
                value = value.slice(0, 2) + '/' + value.slice(2, 4);
            }

            e.target.value = value;

            const errorEl = document.getElementById('expiry-error');
            if (!validators.expiry(e.target.value)) errorEl.style.display = 'none';
        });

        expiryEl.addEventListener('blur', () =>
            validateField('expiry', 'expiry')
        );
    }

    /* -----------------------
       CVV FORMAT
    ------------------------ */
    const cvvEl = document.getElementById('cvv');
    if (cvvEl) {
        cvvEl.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/\D/g, '');

            const errorEl = document.getElementById('cvv-error');
            if (!validators.cvv(e.target.value)) errorEl.style.display = 'none';
        });

        cvvEl.addEventListener('blur', () =>
            validateField('cvv', 'cvv')
        );
    }

    /* -----------------------
       PLACE ORDER BUTTON
    ------------------------ */
    const placeOrderBtn = document.getElementById('place-order-btn');

    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', () => {
            const validCard = validateField('cardNumber', 'cardNumber');
            const validExpiry = validateField('expiry', 'expiry');
            const validCvv = validateField('cvv', 'cvv');
            const validName = document.getElementById('nameOnCard').value.trim() !== '';

            if (!validName) {
                showToast('Please enter name on card.');
            }

            if (validCard && validExpiry && validCvv && validName) {
                // SUCCESS
                showToast('Payment successful! Redirecting...');
                setTimeout(() => {
                    window.location.href = '/'; // Landing page redirect
                }, 1500);
            } else {
                // FAIL
                showToast('Please correct the errors before proceeding.');
            }
        });
    }
});
