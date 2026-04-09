$(document).ready(function () {

    $('#place-order-btn').click(function () {

        if (!validateForm()) return;

        const data = {
            email: $('#email').val(),
            phone: $('#phone').val(),
            first_name: $('#firstName').val(),
            last_name: $('#lastName').val(),
            address: $('#address').val(),
            city: $('#city').val(),
            zip: $('#zip').val(),

            card_number: $('#cardNumber').val(),
            name_on_card: $('#nameOnCard').val(),
            expiry: $('#expiry').val(),
            cvv: $('#cvv').val()
        };

        $.ajax({
            url: '/orders/checkout/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),

            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },

            success: function (response) {
                if (response.success) {
                    window.location.href = `/orders/confirmation/${response.order_id}/`;
                } else {
                    alert(response.error || "Something went wrong");
                }
            },

            error: function () {
                alert("Server error. Please try again.");
            }
        });

    });

});

function getCookie(name) {
    let cookieValue = null;
    const cookies = document.cookie.split(';');

    cookies.forEach(cookie => {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        }
    });

    return cookieValue;
}