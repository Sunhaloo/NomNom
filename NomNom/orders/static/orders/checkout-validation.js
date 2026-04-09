function validateForm() {
    let valid = true;

    function checkField(id, message) {
        const value = $('#' + id).val().trim();
        const errorEl = $('#' + id + '-error');

        if (!value) {
            errorEl.text(message).show();
            valid = false;
        } else {
            errorEl.hide();
        }
    }

    checkField('email', 'Email is required');
    checkField('phone', 'Phone is required');
    checkField('firstName', 'First name is required');
    checkField('lastName', 'Last name is required');
    checkField('address', 'Address is required');
    checkField('city', 'City is required');
    checkField('zip', 'Postal code is required');

    checkField('cardNumber', 'Card number is required');
    checkField('nameOnCard', 'Name on card is required');
    checkField('expiry', 'Expiry date is required');
    checkField('cvv', 'CVV is required');

    if (!valid) {
        alert("Please fill in all required fields.");
    }

    return valid;
}