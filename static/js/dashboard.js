document.addEventListener('DOMContentLoaded', () => {
  const balanceElem = document.querySelector('#balance');
  const transactionsTable = document.querySelector('#transactions-body');

  async function loadDashboardData() {
    try {
      const [balanceResp, txResp] = await Promise.all([
        fetch('/api/balance'),
        fetch('/api/transactions')
      ]);

      if (!balanceResp.ok || !txResp.ok) throw new Error('Ошибка API');

      const balanceData = await balanceResp.json();
      const transactions = await txResp.json();

      updateBalance(balanceData.balance);
      updateTransactions(transactions);
    } catch (err) {
      console.error(err);
      showError('Не удалось загрузить данные дашборда.');
    }
  }

  function updateBalance(amount) {
    if (balanceElem) {
      balanceElem.textContent = `${amount.toFixed(2)} ₽`;
      if (amount < 0) balanceElem.classList.add('text-danger');
    }
  }

  function updateTransactions(list) {
    if (!transactionsTable) return;
    transactionsTable.innerHTML = '';

    list.forEach(tx => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${new Date(tx.date).toLocaleDateString()}</td>
        <td>${tx.type === 'credit' ? 'Пополнение' : 'Списание'}</td>
        <td>${tx.amount.toFixed(2)} ₽</td>
        <td>${tx.status}</td>
      `;
      transactionsTable.appendChild(row);
    });
  }

  function showError(msg) {
    const container = document.querySelector('main');
    const div = document.createElement('div');
    div.className = 'alert alert-error';
    div.textContent = msg;
    container.prepend(div);
    setTimeout(() => div.remove(), 4000);
  }

  loadDashboardData();
  setInterval(loadDashboardData, 30000);
});
