// Cart-specific JavaScript functionality (jQuery-enhanced)

$(function () {
  const EXPRESS_DELIVERY_COST = 1000.0;
  const SCHEDULED_DELIVERY_COST = 300.0;

  let cartData = window.initialCartData || [];
  let deliveryCost = window.deliveryCost || EXPRESS_DELIVERY_COST;
  const TAX_RATE = 0.15;

  const $cartList = $("#cart-list");
  const $emptyCartMessage = $("#empty-cart-message");
  const $cartPageActions = $("#cart-page-actions");
  const $itemCountSpan = $("#item-count");
  const $subtotalSpan = $("#subtotal");
  const $deliveryCostSpan = $("#delivery-cost");
  const $taxCostSpan = $("#tax-cost");
  const $totalCostSpan = $("#total-cost");
  const $toast = $("#toast");
  const $toastMessage = $("#toast-message");
  const $deliveryOptions = $('input[name="delivery"]');
  const $scheduleDateSpan = $("#schedule-delivery-date");

  // Initialize scheduled delivery info text with a date one week from now
  if ($scheduleDateSpan.length) {
    const date = new Date();
    date.setDate(date.getDate() + 7);
    const options = {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
    };
    $scheduleDateSpan.text(date.toLocaleDateString("en-US", options));
  }

  // Update delivery cost when user switches between express and scheduled delivery
  if ($deliveryOptions.length) {
    $deliveryOptions.on("change", function () {
      const value = $(this).val();

      if (value === "express") {
        deliveryCost = EXPRESS_DELIVERY_COST;
      } else if (value === "schedule") {
        deliveryCost = SCHEDULED_DELIVERY_COST;
      }

      updateOrderSummary();
    });
  }

  // Render cart items
  renderCart();

  function renderCart() {
    if (!$cartList.length) return;

    $cartList.empty();
    const $cartPage = $("#cart-page");

    if (cartData.length === 0) {
      if ($cartPage.length) $cartPage.addClass("empty-state");
      $("#order-summary").hide();
      if ($cartPageActions.length) $cartPageActions.hide();
      $emptyCartMessage.show();
      $(".cart-items-section").hide();
    } else {
      if ($cartPage.length) $cartPage.removeClass("empty-state");
      $("#order-summary").show();
      $emptyCartMessage.hide();
      $(".cart-items-section").show();

      cartData.forEach((item, index) => {
        const itemCard = createCartItemHTML(item, index);
        $cartList.append(itemCard);
      });
    }

    updateOrderSummary();
  }

  function createCartItemHTML(item, index) {
    const li = document.createElement("li");
    li.className = "cart-item-card";
    li.dataset.index = index;

    const qty = item.quantity || 1;
    const subtotal = (item.price * qty).toFixed(2);

    // Handle image URL - the backend already provides the full URL via image.url
    let imageUrl = item.image || "/static/images/placeholder.png";

    // If image doesn't start with / or http, prepend /static/
    if (imageUrl && !imageUrl.startsWith("/") && !imageUrl.startsWith("http")) {
      imageUrl = `/static/${imageUrl}`;
    }

    // Build custom cake details HTML if it's a custom cake
    let customDetailsHTML = "";
    if (item.is_custom) {
      customDetailsHTML = `
                <div class="custom-cake-details">
                    <div class="custom-details-grid">
                        ${item.flavour ? `<div class="detail-item"><strong>Flavour:</strong> ${item.flavour}</div>` : ""}
                        ${item.size ? `<div class="detail-item"><strong>Size:</strong> ${item.size}</div>` : ""}
                        ${item.filling ? `<div class="detail-item"><strong>Filling:</strong> ${item.filling}</div>` : ""}
                        ${item.frosting ? `<div class="detail-item"><strong>Frosting:</strong> ${item.frosting}</div>` : ""}
                        ${item.decoration ? `<div class="detail-item"><strong>Decoration:</strong> ${item.decoration}</div>` : ""}
                        ${item.layers && item.layers > 1 ? `<div class="detail-item"><strong>Layers:</strong> ${item.layers}</div>` : ""}
                        ${item.cake_message ? `<div class="detail-item detail-message"><strong>Message:</strong> "${item.cake_message}"</div>` : ""}
                        ${item.pickup_date ? `<div class="detail-item detail-date"><strong>Pickup Date:</strong> ${formatDate(item.pickup_date)}</div>` : ""}
                    </div>
                </div>
            `;
    }

    li.innerHTML = `
            ${
              item.is_custom
                ? ""
                : `
            <div class="item-image-container">
                <img src="${imageUrl}" alt="${item.name}" class="item-image">
            </div>
            `
            }
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
                <span class="item-subtotal">Rs ${subtotal}</span>
            </div>
            <button class="remove-item"><i class="fas fa-times"></i></button>
        `;

    return li;
  }

  function updateOrderSummary() {
    const subtotal = cartData.reduce(
      (total, item) => total + item.price * (item.quantity || 1),
      0,
    );
    const itemCount = cartData.reduce(
      (total, item) => total + (item.quantity || 1),
      0,
    );
    const tax = subtotal * TAX_RATE;
    const total = subtotal + deliveryCost + tax;

    // Update cart page summary elements (if they exist)
    if ($itemCountSpan.length) $itemCountSpan.text(itemCount);
    if ($subtotalSpan.length) $subtotalSpan.text(`Rs ${subtotal.toFixed(2)}`);
    if ($deliveryCostSpan.length)
      $deliveryCostSpan.text(`Rs ${deliveryCost.toFixed(2)}`);
    if ($taxCostSpan.length) $taxCostSpan.text(`Rs ${tax.toFixed(2)}`);
    if ($totalCostSpan.length) $totalCostSpan.text(`Rs ${total.toFixed(2)}`);

    // Update payment page summary elements (if they exist)
    if (window.paymentItemCountSpan)
      window.paymentItemCountSpan.textContent = itemCount;
    if (window.paymentSubtotalSpan)
      window.paymentSubtotalSpan.textContent = `Rs ${subtotal.toFixed(2)}`;
    if (window.paymentDeliveryCostSpan)
      window.paymentDeliveryCostSpan.textContent = `Rs ${deliveryCost.toFixed(2)}`;
    if (window.paymentTaxCostSpan)
      window.paymentTaxCostSpan.textContent = `Rs ${tax.toFixed(2)}`;
    if (window.paymentTotalCostSpan)
      window.paymentTotalCostSpan.textContent = `Rs ${total.toFixed(2)}`;
  }

  function formatDate(dateString) {
    if (!dateString) return "";
    const date = new Date(dateString);
    const options = {
      weekday: "short",
      year: "numeric",
      month: "short",
      day: "numeric",
    };
    return date.toLocaleDateString("en-US", options);
  }

  function showToast(message) {
    if (!$toast.length || !$toastMessage.length) return;
    $toastMessage.text(message);
    $toast.addClass("show");
    setTimeout(() => $toast.removeClass("show"), 3000);
  }

  // --- EVENT LISTENERS ---
  if ($cartList.length) {
    $cartList.on(
      "click",
      ".cart-item-card .qty-plus, .cart-item-card .qty-minus, .cart-item-card .remove-item, .cart-item-card .remove-item i",
      function (event) {
        const $target = $(event.target);
        const $itemCard = $target.closest(".cart-item-card");
        if (!$itemCard.length) return;

        const itemIndex = parseInt($itemCard.data("index"), 10);
        const item = cartData[itemIndex];
        if (!item) return;

        if ($target.hasClass("qty-plus")) {
          const newQuantity = (item.quantity || 1) + 1;
          updateQuantityInBackend(itemIndex, newQuantity);
        } else if ($target.hasClass("qty-minus")) {
          if ((item.quantity || 1) > 1) {
            const newQuantity = (item.quantity || 1) - 1;
            updateQuantityInBackend(itemIndex, newQuantity);
          }
        } else if ($target.closest(".remove-item").length) {
          // Redirect to Django backend to remove item
          window.location.href = `/cart/remove/${itemIndex}/`;
        }
      },
    );
  }

  // Function to update quantity in backend via AJAX (jQuery)
  function updateQuantityInBackend(index, quantity) {
    $.ajax({
      url: "/cart/update/",
      method: "POST",
      contentType: "application/json",
      dataType: "json",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      data: JSON.stringify({
        index: index,
        quantity: quantity,
      }),
      success: function (data) {
        if (data.success) {
          // Update local cart data
          cartData[index].quantity = quantity;
          renderCart();

          // Update cart count in navbar
          const $cartCountElement = $("#cart-count");
          if ($cartCountElement.length) {
            $cartCountElement.text(data.cart_count);
            if (data.cart_count === 0) {
              $cartCountElement.addClass("hidden");
            } else {
              $cartCountElement.removeClass("hidden");
            }
          }
        } else {
          showToast("Failed to update quantity");
        }
      },
      error: function () {
        showToast("Error updating quantity");
      },
    });
  }

  // Helper function to get CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
