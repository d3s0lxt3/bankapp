document.addEventListener('DOMContentLoaded', () => {
  console.log('%cBankApp initialized', 'color:#0e47a1;font-weight:bold;');

  document.body.style.opacity = 0;
  setTimeout(() => {
    document.body.style.transition = 'opacity 0.5s ease';
    document.body.style.opacity = 1;
  }, 50);

  const logoutBtn = document.querySelector('#logout-btn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
      await fetch('/logout', { method: 'POST' });
      window.location.href = '/login';
    });
  }

  const year = new Date().getFullYear();
  const yearElem = document.querySelector('#current-year');
  if (yearElem) yearElem.textContent = year;

  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = 0;
      setTimeout(() => alert.remove(), 600);
    }, 4000);
  });
});
