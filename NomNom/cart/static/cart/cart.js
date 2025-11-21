document.addEventListener('DOMContentLoaded', () => {
    // --- STATE MANAGEMENT ---
    let cartData = [
        {
            id: 1,
            name: "Chocolate Fudge Cake",
            price: 450.00,
            qty: 1,
            image: "https://images.unsplash.com/photo-1578985545062-69928b1d9587?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
            customization: "Size: Medium (1kg), Toppings: Extra Chocolate Shavings",
            note: "Happy Birthday!",
            badge: "Bestseller"
        },
        {
            id: 2,
            name: "Macaron Box (12pc)",
            price: 350.00,
            qty: 2,
            image: "https://images.unsplash.com/photo-1569864358642-9d1684040f43?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80",
            customization: "Flavors: Assorted",
            note: "",
            badge: "New"
        },
        { id: 3, name: 'Strawberry Tart', price: 250.00, qty: 3, customization: '', note: 'Please pack carefully', image: 'https://images.pexels.com/photos/1998633/pexels-photo-1998633.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1', badge: 'New' }
    ];

    let deliveryCost = 0.00; // Default
    const TAX_RATE = 0.15; // 15% tax for Mauritius

    // --- DOM ELEMENT SELECTORS ---
    const cartList = document.getElementById('cart-list');
    const orderSummary = document.getElementById('order-summary');
    const emptyCartMessage = document.getElementById('empty-cart-message');
    const cartPageActions = document.getElementById('cart-page-actions');
    const itemCountSpan = document.getElementById('item-count');
    const subtotalSpan = document.getElementById('subtotal');
    const deliveryCostSpan = document.getElementById('delivery-cost');
    const taxCostSpan = document.getElementById('tax-cost');
    const totalCostSpan = document.getElementById('total-cost');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const deliveryOptions = document.getElementsByName('delivery');
    const deliveryDateInput = document.getElementById('deliveryDate');
    const datePickerGroup = document.getElementById('date-picker-group');

    // Navigation Elements
    const pages = document.querySelectorAll('.page-section');
    const progressSteps = document.querySelectorAll('.progress-step');
    const progressTrack = document.getElementById('progress-track');

    // --- INITIALIZATION ---
    renderCart();
    updateOrderSummary();

    // --- CORE FUNCTIONS ---
    function showPage(pageName, stepNumber) {
        pages.forEach(page => page.classList.remove('active'));
        document.getElementById(pageName).classList.add('active');

        // Show/hide cart-specific action buttons
        if (pageName === 'cart-page') {
            cartPageActions.style.display = 'grid';
        } else {
            cartPageActions.style.display = 'none';
        }

        progressSteps.forEach(step => step.classList.remove('active', 'completed'));
        for (let i = 0; i < stepNumber; i++) {
            const step = progressSteps[i];
            if (i < stepNumber - 1) {
                step.classList.add('completed');
            } else {
                step.classList.add('active');
            }
        }
        const trackWidth = stepNumber === 1 ? '0%' : stepNumber === 2 ? '50%' : '100%';
        progressTrack.style.width = trackWidth;
    }

    function renderCart() {
        cartList.innerHTML = '';

        if (cartData.length === 0) {
            orderSummary.style.display = 'none';
            cartPageActions.style.display = 'none';
            emptyCartMessage.style.display = 'block';
            document.querySelector('.cart-items-section h2').style.display = 'none';
        } else {
            orderSummary.style.display = 'block';
            emptyCartMessage.style.display = 'none';
            document.querySelector('.cart-items-section h2').style.display = 'block';

            cartData.forEach(item => {
                const itemCard = createCartItemHTML(item);
                cartList.appendChild(itemCard);
            });
        }

        updateOrderSummary();
    }

    function createCartItemHTML(item) {
        const li = document.createElement('li');
        li.className = 'cart-item-card';
        li.dataset.id = item.id;

        const subtotal = (item.price * item.qty).toFixed(2);
        const noteHTML = item.note ? `<p class="item-note"><i class="fas fa-gift"></i> ${item.note}</p>` : '';
        const badgeHTML = item.badge ? `<span class="item-badge">${item.badge}</span>` : '';

        li.innerHTML = `
            <div class="item-image-container">
                <img src="${item.image}" alt="${item.name}" class="item-image">
                ${badgeHTML}
            </div>
            <div class="item-details">
                <h3>${item.name}</h3>
                <p>${item.customization}</p>
                ${noteHTML}
            </div>
            <div class="item-price-qty">
                <div class="qty-selector">
                    <button class="qty-minus">−</button>
                    <span>${item.qty}</span>
                    <button class="qty-plus">+</button>
                </div>
                <span class="item-subtotal">Rs.${subtotal}</span>
            </div>
            <button class="remove-item"><i class="fas fa-times"></i></button>
        `;
        return li;
    }

    function updateOrderSummary() {
        const subtotal = cartData.reduce((total, item) => total + (item.price * item.qty), 0);
        const itemCount = cartData.reduce((total, item) => total + item.qty, 0);
        const tax = (subtotal + deliveryCost) * TAX_RATE;
        const total = subtotal + deliveryCost + tax;

        itemCountSpan.textContent = itemCount;
        subtotalSpan.textContent = `Rs.${subtotal.toFixed(2)}`;
        deliveryCostSpan.textContent = `Rs.${deliveryCost.toFixed(2)}`;
        taxCostSpan.textContent = `Rs.${tax.toFixed(2)}`;
        totalCostSpan.textContent = `Rs.${total.toFixed(2)}`;
    }

    function showToast(message) {
        toastMessage.textContent = message;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 3000);
    }

    // --- EVENT LISTENERS ---
    cartList.addEventListener('click', (event) => {
        const itemCard = event.target.closest('.cart-item-card');
        if (!itemCard) return;
        const itemId = parseInt(itemCard.dataset.id);
        const item = cartData.find(i => i.id === itemId);
        if (!item) return;

        if (event.target.classList.contains('qty-plus')) {
            item.qty++;
            renderCart();
        } else if (event.target.classList.contains('qty-minus')) {
            if (item.qty > 1) {
                item.qty--;
                renderCart();
            }
        } else if (event.target.classList.contains('remove-item') || event.target.parentElement.classList.contains('remove-item')) {
            cartData = cartData.filter(i => i.id !== itemId);
            showToast(`${item.name} removed from cart`);
            renderCart();
        }
    });

    deliveryOptions.forEach(option => {
        option.addEventListener('change', (event) => {
            if (event.target.value === 'express') {
                deliveryCost = 1000.00;
                datePickerGroup.classList.remove('show');
            } else if (event.target.value === 'schedule') {
                deliveryCost = 300.00;
                datePickerGroup.classList.add('show');
                // Set minimum date to 2 days from today
                const minDate = new Date();
                minDate.setDate(minDate.getDate() + 2);
                const minDateStr = minDate.toISOString().split('T')[0];
                deliveryDateInput.min = minDateStr;
                deliveryDateInput.disabled = false;
            } else {
                // Fallback/Default
                const tomorrow = new Date();
                tomorrow.setDate(tomorrow.getDate() + 1);
                deliveryDateInput.min = tomorrow.toISOString().split('T')[0];
            }
            updateOrderSummary();
        });
    });

    // Handle date selection
    deliveryDateInput.addEventListener('change', (event) => {
        const selectedDate = new Date(event.target.value);
        const minDate = new Date();
        minDate.setDate(minDate.getDate() + 2);
        minDate.setHours(0, 0, 0, 0);

        if (selectedDate < minDate) {
            showToast('Please select a date at least 2 days from today');
            event.target.value = '';
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

    // Page Navigation Listeners
    document.getElementById('to-info-btn').addEventListener('click', () => {
        if (cartData.length > 0) {
            // Validate date if scheduled
            const scheduleRadio = document.getElementById('schedule');
            if (scheduleRadio.checked) {
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

    document.getElementById('back-to-cart-btn').addEventListener('click', () => {
        showPage('cart-page', 1);
    });

    // --- VALIDATION FUNCTIONS ---
    const validators = {
        email: (value) => /^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(value) ? '' : 'Please enter a valid email address.',
        phone: (value) => /^5\d{7}$/.test(value.replace(/\s/g, '')) ? '' : 'Phone number must start with 5 and have exactly 8 digits.',
        name: (value) => /^[A-Za-z\s]+$/.test(value) ? '' : 'Name must contain only letters.',
        address: (value) => value.trim() ? '' : 'Street address is required.',
        city: (value) => {
            const options = Array.from(document.querySelectorAll('#city-list option')).map(opt => opt.value.toLowerCase());
            return options.includes(value.toLowerCase()) ? '' : 'Please select a valid city.';
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

    // Format card number input
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

    // Format expiry date input
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

    // CVV Input restriction
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

    // --- CITY AUTO-FILL POSTAL CODE ---
    const cityZipMap = {
        "Port Louis": "11302",
        "Curepipe": "74213",
        "Vacoas": "73411",
        "Quatre Bornes": "72101",
        "Rose Hill": "71301",
        "Beau Bassin": "71501",
        "Phoenix": "73521",
        "Grand Baie": "30510",
        "Flic en Flac": "90502",
        "Tamarin": "90901",
        "Mahebourg": "50804",
        "Goodlands": "30406",
        "Triolet": "21503",
        "Rose Belle": "51802",
        "Chemin Grenier": "60103",
        "Riviere du Rempart": "30906",
        "Lallmatie": "41803",
        "Plaine Magnien": "51603",
        "Pailles": "11202",
        "Surinam": "61203",
        "Le Hochet": "20905",
        "Montagne Blanche": "41302",
        "Grand Gaube": "30605",
        "Petit Raffray": "30703",
        "Baie du Tombeau": "20102",
        "Bambous": "90102",
        "Bambous Virieux": "50102",
        "Bananes": "50202",
        "Beau Vallon": "50302",
        "Bel Air Riviere Seche": "40102",
        "Bel Ombre": "60202",
        "Belle Vue Maurel": "30102",
        "Benares": "60302",
        "Bois Cheri": "60402",
        "Bois des Amourettes": "50402",
        "Bon Accueil": "40202",
        "Bramsthan": "40302",
        "Brisée Verdière": "40402",
        "Britannia": "60502",
        "Camp de Masque": "40502",
        "Camp de Masque Pavé": "40602",
        "Camp Diable": "60602",
        "Camp Ithier": "40702",
        "Camp Thorel": "40802",
        "Cap Malheureux": "30202",
        "Cascavelle": "90202",
        "Case Noyale": "90302",
        "Chamarel": "90402",
        "Chamouny": "60702",
        "Cluny": "50502",
        "Congomah": "20202",
        "Cottage": "30302",
        "Crève Coeur": "20302",
        "D'Epinay": "20402",
        "Dagotière": "80102",
        "Dubreuil": "70102",
        "Ecroignard": "40902",
        "Espérance Trébuchet": "30402",
        "Fond du Sac": "20502",
        "Grand Bel Air": "50602",
        "Grand Bois": "60802",
        "Grand River South East": "41002",
        "Grande Retraite": "41102",
        "Grande Riviere Noire": "90602",
        "Gros Cailloux": "90702",
        "L'Avenir": "80202",
        "L'Escalier": "60902",
        "La Flora": "61002",
        "La Gaulette": "90802",
        "La Laura-Malenga": "80302",
        "Lalmatie": "41202",
        "Laventure": "41402",
        "Le Morne": "91002",
        "Long Mountain": "20602",
        "Mare Chicose": "50902",
        "Mare d'Albert": "51002",
        "Mare La Chaux": "41502",
        "Mare Tabac": "51102",
        "Melrose": "41602",
        "Midlands": "70202",
        "Moka": "80402",
        "Montagne Longue": "20702",
        "Morcellement Saint Andre": "20802",
        "New Grove": "51202",
        "Notre Dame": "21002",
        "Nouvelle Decouverte": "80502",
        "Nouvelle France": "51302",
        "Olivia": "41702",
        "Pamplemousses": "21102",
        "Petit Bel Air": "51402",
        "Petite Riviere": "91102",
        "Piton": "30802",
        "Plaine des Papayes": "21202",
        "Plaine des Roches": "31002",
        "Pointe aux Cannoniers": "31102",
        "Pointe aux Piments": "21302",
        "Poste de Flacq": "41902",
        "Poudre d'Or": "31202",
        "Poudre d'Or Hamlet": "31302",
        "Providence": "42002",
        "Quartier Militaire": "42102",
        "Quatre Cocos": "42202",
        "Quatre Soeurs": "42302",
        "Queen Victoria": "42402",
        "Richelieu": "91202",
        "Ripailles": "80602",
        "Riviere des Anguilles": "61102",
        "Riviere des Creoles": "51702",
        "Riviere du Poste": "51502",
        "Riviere Noire": "91302",
        "Roche Terre": "31402",
        "Roches Noires": "31502",
        "Saint Aubin": "61302",
        "Saint Hubert": "51902",
        "Saint Julien d'Hotman": "42502",
        "Saint Pierre": "80702",
        "Sebastopol": "42602",
        "Souillac": "61402",
        "Terre Rouge": "21402",
        "The Vale": "31602",
        "Trois Boutiques": "52002",
        "Trou aux Biches": "21602",
        "Trou d'Eau Douce": "42702",
        "Tyack": "61502",
        "Union Park": "52102",
        "Vale": "31702",
        "Ville Bague": "21702",
        "Wooton": "70302"
    };

    document.getElementById('city').addEventListener('input', function () {
        const city = this.value;
        // Case-insensitive lookup
        const matchedCity = Object.keys(cityZipMap).find(key => key.toLowerCase() === city.toLowerCase());

        if (matchedCity) {
            document.getElementById('zip').value = cityZipMap[matchedCity];
            // Trigger validation for zip to clear any errors
            validateField('zip', 'zip');
        }
    });

    document.getElementById('to-payment-btn').addEventListener('click', () => {
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

    document.getElementById('back-to-info-btn').addEventListener('click', () => {
        showPage('info-page', 2);
    });

    document.getElementById('place-order-btn').addEventListener('click', () => {
        const validCard = validateField('cardNumber', 'cardNumber');
        const validName = validateField('nameOnCard', 'name');
        const validExpiry = validateField('expiry', 'expiry');
        const validCvv = validateField('cvv', 'cvv');

        // Re-validate date just in case
        let validDate = true;
        const scheduleRadio = document.getElementById('schedule');
        if (scheduleRadio.checked && !deliveryDateInput.value) {
            validDate = false;
            showToast('Please select a delivery date.');
        }

        if (validCard && validName && validExpiry && validCvv && validDate) {
            showToast('Order placed successfully! Thank you for your purchase.');
            setTimeout(() => {
                cartData = [];
                showPage('cart-page', 1);
                renderCart();
            }, 3000);
        } else {
            showToast('Please correct the errors in the payment form.');
        }
    });
});
