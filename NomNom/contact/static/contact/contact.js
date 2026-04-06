// Contact page toast handling

document.addEventListener('DOMContentLoaded', () => {
  const toast = document.getElementById('toast');
  const toastMessage = document.getElementById('toast-message');

  function showToast(message, tags) {
    if (!toast || !toastMessage) return;

    toastMessage.textContent = message;

    // Reset variant classes
    toast.classList.remove('toast-success', 'toast-error', 'toast-info');

    const level = (tags || '').toLowerCase();

    if (level.includes('success')) {
      toast.classList.add('toast-success');
    } else if (level.includes('error') || level.includes('danger')) {
      toast.classList.add('toast-error');
    } else {
      toast.classList.add('toast-info');
    }

    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
  }

  // Read Django messages from hidden container and show them as toasts
  const container = document.getElementById('django-messages');
  if (container) {
    const msgs = container.querySelectorAll('.django-message');
    msgs.forEach((el) => {
      const tags = el.dataset.tags || '';
      const text = (el.textContent || '').trim();
      if (text) {
        showToast(text, tags);
      }
    });
  }
});
