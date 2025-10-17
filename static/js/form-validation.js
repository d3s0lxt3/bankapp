document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('form');

  forms.forEach(form => {
    form.addEventListener('submit', event => {
      if (!validateForm(form)) {
        event.preventDefault();
      }
    });
  });

  function validateForm(form) {
    let valid = true;
    const inputs = form.querySelectorAll('input[required], select[required]');
    inputs.forEach(input => {
      if (!input.value.trim()) {
        showError(input, 'Поле не может быть пустым');
        valid = false;
      } else if (input.type === 'email' && !isValidEmail(input.value)) {
        showError(input, 'Некорректный email');
        valid = false;
      } else if (input.name === 'amount' && parseFloat(input.value) <= 0) {
        showError(input, 'Сумма должна быть больше 0');
        valid = false;
      } else {
        clearError(input);
      }
    });
    return valid;
  }

  function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function showError(input, message) {
    clearError(input);
    const err = document.createElement('div');
    err.className = 'error-message';
    err.textContent = message;
    err.style.color = 'red';
    err.style.fontSize = '0.9rem';
    input.after(err);
    input.style.borderColor = 'red';
  }

  function clearError(input) {
    input.style.borderColor = '';
    const next = input.nextElementSibling;
    if (next && next.classList.contains('error-message')) next.remove();
  }
});
