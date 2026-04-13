// Profile page: map Django messages to a simple success toast

document.addEventListener("DOMContentLoaded", () => {
  const toast = document.getElementById("profile-toast");
  const toastMessage = document.getElementById("profile-toast-message");
  const closeBtn = document.querySelector(".profile-toast-close");

  function showToast(message) {
    if (!toast || !toastMessage) return;

    toastMessage.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
      toast.classList.remove("show");
    }, 3000);
  }

  if (closeBtn && toast) {
    closeBtn.addEventListener("click", () => {
      toast.classList.remove("show");
    });
  }

  const container = document.getElementById("django-messages");
  if (!container) return;

  const messages = container.querySelectorAll(".django-message");
  messages.forEach((el) => {
    const tags = (el.dataset.tags || "").toLowerCase();
    const text = (el.textContent || "").trim();

    if (!text) return;

    if (tags.includes("success")) {
      showToast(text);
    }
  });
});
