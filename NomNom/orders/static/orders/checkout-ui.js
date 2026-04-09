$(document).ready(function () {
    $('#to-payment-btn').click(function () {
        $('#info-page').removeClass('active');
        $('#payment-page').addClass('active');
    });

    $('#back-to-info-btn').click(function () {
        $('#payment-page').removeClass('active');
        $('#info-page').addClass('active');
    });

    if (window.orderData) {
        $('#payment-subtotal').text(`Rs ${window.orderData.subtotal.toFixed(2)}`);
        $('#payment-tax-cost').text(`Rs ${window.orderData.tax.toFixed(2)}`);
        $('#payment-item-count').text(window.orderData.item_count);
        $('#payment-delivery-cost').text(`Rs ${window.orderData.delivery.toFixed(2)}`);
        $('#payment-total-cost').text(`Rs ${window.orderData.total.toFixed(2)}`);
    }

});