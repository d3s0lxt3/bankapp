const API = {
  async get(endpoint) {
    const resp = await fetch(`/api/${endpoint}`);
    if (!resp.ok) throw new Error(`Ошибка при GET /api/${endpoint}`);
    return await resp.json();
  },

  async post(endpoint, data) {
    const resp = await fetch(`/api/${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!resp.ok) throw new Error(`Ошибка при POST /api/${endpoint}`);
    return await resp.json();
  }
};

document.addEventListener('DOMContentLoaded', () => {
  const transferForm = document.querySelector('#transfer-form');
  if (!transferForm) return;

  transferForm.addEventListener('submit', async e => {
    e.preventDefault();
    const amount = parseFloat(transferForm.querySelector('[name="amount"]').value);
    const target = transferForm.querySelector('[name="target"]').value;

    try {
      const res = await API.post('transfer', { amount, target });
      alert(`Перевод выполнен успешно: ${res.status}`);
      transferForm.reset();
    } catch (err) {
      console.error(err);
      alert('Ошибка перевода. Проверьте данные.');
    }
  });
});
