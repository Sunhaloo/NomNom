function updateCartCount(count) {
    const cartBadge = document.getElementById("cart-count");
    if (!cartBadge) return;

    cartBadge.textContent = count;

    if (count <= 0) {
        cartBadge.classList.add("hidden");
    } else {
        cartBadge.classList.remove("hidden");
        cartBadge.classList.add("bump");

        setTimeout(() => cartBadge.classList.remove("bump"), 300);
    }
}

function showCartLoginPrompt(e) {
    e.preventDefault();
    showLoginPrompt("You must login to access your cart.");
}
