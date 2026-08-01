import { fetchOrders, fetchCustomer } from './api.js';

export async function renderOrdersPage(root) {
  const orders = await fetchOrders();
  root.replaceChildren(...orders.map(o => {
    const div = document.createElement('div');
    div.className = 'order';
    div.dataset.id = o.orderId;
    div.dataset.customerId = o.customerId;
    div.textContent = o.status;
    return div;
  }));
  root.addEventListener('click', async (e) => {
    const id = e.target.dataset.customerId;
    if (id) showCustomer(await fetchCustomer(id));
  });
}

function showCustomer(c) {
  document.querySelector('#detail').textContent = `${c.name} (${c.grade})`;
}
