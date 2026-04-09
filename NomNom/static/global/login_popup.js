
function showLoginPrompt(message = "You must login to add items to cart.") {
    const overlay = document.createElement("div");
    overlay.className = "login-overlay";
    const popup = document.createElement("div");
    popup.className = "login-popup";

    popup.innerHTML = `
        <div class="login-popup-inner">
            <i class="fas fa-lock popup-icon"></i>
            <h3>Login Required</h3>
            <p>${message}</p>

            <a href="/login/" class="login-btn">Click here to login</a>

            <button class="close-btn">&times;</button>
        </div>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(popup);

    function closePopup() {
        overlay.classList.remove("show");
        popup.classList.remove("show");

        setTimeout(() => {
            overlay.remove();
            popup.remove();
        }, 200);
    }

    overlay.addEventListener("click", e => {
        if (e.target === overlay) closePopup();
    });

    popup.querySelector(".close-btn").addEventListener("click", closePopup);

    requestAnimationFrame(() => {
        overlay.classList.add("show");
        popup.classList.add("show");
    });
}
