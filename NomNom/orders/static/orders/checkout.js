// Checkout/Order-specific JavaScript functionality (jQuery-enhanced)

$(function () {
  let cartData = window.initialCartData || [];
  let deliveryCost = window.deliveryCost || 700.0;
  const TAX_RATE = 0.15;

  const $orderSummary = $("#order-summary");
  const $deliveryOptions = $('input[name="delivery"]');
  const $deliveryDateInput = $("#deliveryDate");
  const $datePickerGroup = $("#date-picker-group");
  const $itemCountSpan = $("#item-count");
  const $subtotalSpan = $("#subtotal");
  const $deliveryCostSpan = $("#delivery-cost");
  const $taxCostSpan = $("#tax-cost");
  const $totalCostSpan = $("#total-cost");

  // Payment page summary elements (for checkout)
  window.paymentItemCountSpan = document.getElementById("payment-item-count");
  window.paymentSubtotalSpan = document.getElementById("payment-subtotal");
  window.paymentDeliveryCostSpan = document.getElementById(
    "payment-delivery-cost",
  );
  window.paymentTaxCostSpan = document.getElementById("payment-tax-cost");
  window.paymentTotalCostSpan = document.getElementById("payment-total-cost");

  // Key for storing card details per logged-in user (client-side only)
  const username = window.currentUsername || "guest";
  const CARD_STORAGE_KEY = `nomnom_card_${username}`;

  let savedCard = null;
  try {
    const stored = localStorage.getItem(CARD_STORAGE_KEY);
    if (stored) {
      savedCard = JSON.parse(stored);
    }
  } catch (e) {
    savedCard = null;
  }

  updateOrderSummary();

  // Checkout.js should not handle page navigation if cart.js is also loaded
  // Let cart.js handle the page navigation; checkout.js just enhances functionality

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

  // Delivery option changes (used on pages that include delivery radios)
  if ($deliveryOptions.length) {
    $deliveryOptions.on("change", function () {
      const value = $(this).val();
      if (value === "express") {
        deliveryCost = 700.0;
        if ($datePickerGroup.length) $datePickerGroup.removeClass("show");
      } else if (value === "schedule") {
        deliveryCost = 300.0;
        if ($datePickerGroup.length) $datePickerGroup.addClass("show");
        const minDate = new Date();
        minDate.setDate(minDate.getDate() + 2);
        const minDateStr = minDate.toISOString().split("T")[0];
        if ($deliveryDateInput.length) {
          $deliveryDateInput.attr("min", minDateStr).prop("disabled", false);
        }
      } else {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        if ($deliveryDateInput.length) {
          $deliveryDateInput.attr("min", tomorrow.toISOString().split("T")[0]);
        }
      }
      updateOrderSummary();
    });
  }

  // Handle date selection (used on cart page when delivery date exists)
  if ($deliveryDateInput.length) {
    $deliveryDateInput.on("change", function () {
      const selectedDate = new Date($(this).val());
      const minDate = new Date();
      minDate.setDate(minDate.getDate() + 2);
      minDate.setHours(0, 0, 0, 0);

      if (selectedDate < minDate) {
        showToast("Please select a delivery date at least 2 days from today");
        $("#date-error").hide();
        return;
      }
      $("#date-error").hide();
    });

    // Initialize date picker min date
    const minDate = new Date();
    minDate.setDate(minDate.getDate() + 2);
    const minDateStr = minDate.toISOString().split("T")[0];
    $deliveryDateInput.attr("min", minDateStr).prop("disabled", true);
  }

  // Page Navigation Listeners (used on cart-page variant)
  const $toInfoBtn = $("#to-info-btn");
  if ($toInfoBtn.length) {
    $toInfoBtn.on("click", function () {
      if (cartData.length > 0) {
        const $scheduleRadio = $("#schedule");
        if ($scheduleRadio.length && $scheduleRadio.prop("checked")) {
          if (!$deliveryDateInput.val()) {
            showToast("Please select a delivery date before proceeding.");
            $("#date-error").text("Please select a delivery date.").show();
            return;
          }
        }
        showPage("info-page", 2);
      } else {
        showToast("Your cart is empty!");
      }
    });
  }

  const $backToCartBtn = $("#back-to-cart-btn");
  if ($backToCartBtn.length) {
    $backToCartBtn.on("click", function () {
      showPage("cart-page", 1);
    });
  }

  // --- VALIDATION FUNCTIONS ---
  const validators = {
    email: (value) =>
      /^[^@\s]+@[^@\s]+\.[^@\s]{2,}$/.test(value)
        ? ""
        : "Please enter a valid email address.",
    phone: (value) =>
      /^5\d{7}$/.test(value.replace(/\s/g, ""))
        ? ""
        : "Phone number must start with 5 and have exactly 8 digits.",
    name: (value) =>
      /^[A-Za-z\s]+$/.test(value) ? "" : "Name must contain only letters.",
    address: (value) => (value.trim() ? "" : "Street address is required."),
    city: (value) => {
      return value.trim() ? "" : "Please select a valid city.";
    },

    zip: (value) =>
      /^\d{5}$/.test(value) ? "" : "Postal code must be exactly 5 digits.",
    cardNumber: (value) =>
      /^\d{16}$/.test(value.replace(/\s/g, ""))
        ? ""
        : "Card number must be exactly 16 digits.",
    expiry: (value) => {
      if (!/^\d{2}\/\d{2}$/.test(value)) return "Invalid format (MM/YY).";
      const [month, year] = value.split("/").map(Number);
      const now = new Date();
      const currentYear = now.getFullYear() % 100;
      const currentMonth = now.getMonth() + 1;
      if (month < 1 || month > 12) return "Invalid month.";
      if (year < currentYear || (year === currentYear && month < currentMonth))
        return "Expiry date cannot be in the past.";
      return "";
    },
    cvv: (value) =>
      /^\d{3}$/.test(value) ? "" : "CVV must be exactly 3 digits.",
  };

  function validateField(fieldId, validatorName) {
    const $input = $("#" + fieldId);
    const $errorEl = $("#" + fieldId + "-error");
    if (!$input.length || !$errorEl.length) return false;

    const value = $input.val();
    const errorMessage = validators[validatorName](value);
    if (errorMessage) {
      $errorEl.text(errorMessage).show();
      return false;
    }
    $errorEl.hide();
    return true;
  }

  // --- REAL-TIME VALIDATION & FORMATTING LISTENERS ---
  [
    "email",
    "phone",
    "firstName",
    "lastName",
    "address",
    "city",
    "zip",
    "nameOnCard",
    "cardNumber",
  ].forEach((id) => {
    const $el = $("#" + id);
    if (!$el.length) return;

    let validator = id;
    if (id === "firstName" || id === "lastName" || id === "nameOnCard")
      validator = "name";

    $el.on("input", function () {
      let val = $(this).val();

      if (id === "phone") {
        val = val.replace(/[^0-9]/g, "");
        $(this).val(val);
      }

      if (id === "cardNumber") {
        let digits = val.replace(/\D/g, "").slice(0, 16);
        const groups = digits.match(/.{1,4}/g) || [];
        $(this).val(groups.join(" "));
        val = $(this).val();
      }

      const $errorEl = $("#" + id + "-error");
      const errorMessage = validators[validator](val);
      if (!errorMessage) {
        $errorEl.hide();
      }
    });

    $el.on("blur", function () {
      validateField(id, validator);
    });
  });

  // Populate saved card details when payment page is active
  function populateSavedCard() {
    if (!savedCard) return;

    const cardNumberInput = document.getElementById("cardNumber");
    const nameOnCardInput = document.getElementById("nameOnCard");
    const expiryInput = document.getElementById("expiry");
    const saveInfoCheckbox = document.getElementById("save-info");

    if (cardNumberInput && savedCard.cardNumber) {
      cardNumberInput.value = savedCard.cardNumber;
    }
    if (nameOnCardInput && savedCard.nameOnCard) {
      nameOnCardInput.value = savedCard.nameOnCard;
    }
    if (expiryInput && savedCard.expiry) {
      expiryInput.value = savedCard.expiry;
    }
    if (saveInfoCheckbox) {
      saveInfoCheckbox.checked = true;
    }
  }

  const $toPaymentBtn = $("#to-payment-btn");
  if ($toPaymentBtn.length) {
    $toPaymentBtn.on("click", function () {
      const contactValid =
        validateField("email", "email") & validateField("phone", "phone");
      const addressValid =
        validateField("firstName", "name") &
        validateField("lastName", "name") &
        validateField("address", "address") &
        validateField("city", "city") &
        validateField("zip", "zip");

      if (contactValid && addressValid) {
        showPage("payment-page", 3);
      } else {
        showToast("Please fill in all required fields correctly.");
      }
    });
  }

  const $backToInfoBtn = $("#back-to-info-btn");
  if ($backToInfoBtn.length) {
    $backToInfoBtn.on("click", function () {
      showPage("info-page", 2);
    });
  }

  function showToast(message) {
    const $toast = $("#toast");
    const $toastMessage = $("#toast-message");
    if ($toast.length && $toastMessage.length) {
      $toastMessage.text(message);
      $toast.addClass("show");
      setTimeout(() => $toast.removeClass("show"), 3000);
    }
  }

  // --- CART ITEM MANIPULATION (Quantity updates, removal) ---
  const $cartList = $("#cart-list");
  if ($cartList.length) {
    $cartList.on(
      "click",
      ".cart-item-card .qty-plus, .cart-item-card .qty-minus, .cart-item-card .remove-item, .cart-item-card .remove-item i",
      function () {
        const $itemCard = $(this).closest(".cart-item-card");
        if (!$itemCard.length) return;
        const itemIndex = parseInt($itemCard.data("index"), 10);
        const item = cartData[itemIndex];
        if (!item) return;

        if ($(this).hasClass("qty-plus")) {
          const newQuantity = (item.quantity || 1) + 1;
          updateQuantityInBackend(itemIndex, newQuantity);
        } else if ($(this).hasClass("qty-minus")) {
          if ((item.quantity || 1) > 1) {
            const newQuantity = (item.quantity || 1) - 1;
            updateQuantityInBackend(itemIndex, newQuantity);
          }
        } else if ($(this).closest(".remove-item").length) {
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
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
      },
      data: JSON.stringify({ index: index, quantity: quantity }),
      success: function (data) {
        if (data.success) {
          cartData[index].quantity = quantity;
          renderCart();

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

  // Function to render cart items (for when cart items are shown on checkout page)
  function renderCart() {
    const $cartListLocal = $("#cart-list");
    if (!$cartListLocal.length) return; // Only render if cart list exists on this page

    $cartListLocal.empty();
    const $cartPage = $("#cart-page");

    if (cartData.length === 0) {
      if ($cartPage.length) $cartPage.addClass("empty-state");
      if ($orderSummary.length) $orderSummary.hide();
      $("#empty-cart-message").show();
      $("#cart-page-actions").hide();
      $(".cart-items-section").hide();
    } else {
      if ($cartPage.length) $cartPage.removeClass("empty-state");
      if ($orderSummary.length) $orderSummary.show();
      $("#empty-cart-message").hide();
      $(".cart-items-section").show();

      cartData.forEach((item, index) => {
        const itemCard = createCartItemHTML(item, index);
        $cartListLocal.append(itemCard);
      });
    }

    updateOrderSummary();
  }

  // Function to create cart item HTML
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

  // --- CITY AUTO-FILL POSTAL CODE ---
  $.getJSON("/static/orders/data/city_zip.json")
    .done(function (data) {
      window.cityZipMap = data;

      const $cityInput = $("#city");
      const $zipInput = $("#zip");

      if ($cityInput.length && $zipInput.length) {
        const handleCityChange = function () {
          const typed = $(this).val().trim();
          let matchedCity = null;
          for (const city in window.cityZipMap) {
            if (city.toLowerCase() === typed.toLowerCase()) {
              matchedCity = city;
              break;
            }
          }

          if (matchedCity) {
            $zipInput.val(window.cityZipMap[matchedCity]);
            $zipInput.prop("readonly", true);
            validateField("zip", "zip");
          } else {
            $zipInput.val("");
            // Allow manual entry if there is no known mapping
            $zipInput.prop("readonly", false);
          }
        };

        $cityInput.on("input", handleCityChange);
        $cityInput.on("change", handleCityChange);

        // Auto-fill ZIP on initial load if a city is already selected
        if ($cityInput.val().trim()) {
          handleCityChange.call($cityInput);
        }
      }
    })
    .fail(function (jqXHR, textStatus) {
      console.error("Failed to load city_zip.json:", textStatus);
    });

  // Page navigation function
  function showPage(pageId, step) {
    $(".page-section").removeClass("active");

    const $targetPage = $("#" + pageId);
    if ($targetPage.length) {
      $targetPage.addClass("active");
    }

    if (pageId === "payment-page") {
      populateSavedCard();
    }

    if (window.updateProgress) {
      window.updateProgress(step);
    } else {
      const $steps = $(".progress-step");
      $steps.removeClass("active completed");
      $steps.each(function (index) {
        if (index + 1 < step) {
          $(this).addClass("completed");
        } else if (index + 1 === step) {
          $(this).addClass("active");
        }
      });
    }
  }
  window.showPage = showPage; // Make function globally accessible

  // Handle Place Order button click
  const $placeOrderBtn = $("#place-order-btn");
  if ($placeOrderBtn.length) {
    $placeOrderBtn.on("click", function () {
      const cardValid =
        validateField("cardNumber", "cardNumber") &
        validateField("nameOnCard", "name") &
        validateField("expiry", "expiry") &
        validateField("cvv", "cvv");

      if (cardValid) {
        const $saveInfoCheckbox = $("#save-info");

        if ($saveInfoCheckbox.length && $saveInfoCheckbox.prop("checked")) {
          const cardDataToSave = {
            cardNumber: $("#cardNumber").val() || "",
            nameOnCard: $("#nameOnCard").val() || "",
            expiry: $("#expiry").val() || "",
            // CVV is intentionally NOT stored
          };

          try {
            localStorage.setItem(
              CARD_STORAGE_KEY,
              JSON.stringify(cardDataToSave),
            );
          } catch (e) {
            // Ignore storage errors silently
          }
        } else {
          try {
            localStorage.removeItem(CARD_STORAGE_KEY);
          } catch (e) {
            // Ignore storage errors silently
          }
        }

        const form = document.createElement("form");
        form.method = "POST";
        form.action = window.location.href;

        const csrfToken = getCookie("csrftoken");
        if (csrfToken) {
          const csrfInput = document.createElement("input");
          csrfInput.type = "hidden";
          csrfInput.name = "csrfmiddlewaretoken";
          csrfInput.value = csrfToken;
          form.appendChild(csrfInput);
        }

        // Helper to append hidden form fields
        function addHiddenInput(formEl, name, value) {
          const input = document.createElement("input");
          input.type = "hidden";
          input.name = name;
          input.value = value;
          formEl.appendChild(input);
        }

        // Pass contact and shipping fields from the checkout UI to the backend
        const firstNameEl = document.getElementById("firstName");
        const lastNameEl = document.getElementById("lastName");
        const addressEl = document.getElementById("address");
        const cityEl = document.getElementById("city");
        const zipEl = document.getElementById("zip");
        const deliveryDateEl = document.getElementById("deliveryDate");

        if (firstNameEl)
          addHiddenInput(form, "firstName", firstNameEl.value || "");
        if (lastNameEl)
          addHiddenInput(form, "lastName", lastNameEl.value || "");
        if (addressEl) addHiddenInput(form, "address", addressEl.value || "");
        if (cityEl) addHiddenInput(form, "city", cityEl.value || "");
        if (zipEl) addHiddenInput(form, "zip", zipEl.value || "");
        if (deliveryDateEl && deliveryDateEl.value) {
          addHiddenInput(form, "deliveryDate", deliveryDateEl.value);
        }

        document.body.appendChild(form);
        form.submit();
      } else {
        showToast("Please fill in all payment fields correctly.");
      }
    });
  }
});
