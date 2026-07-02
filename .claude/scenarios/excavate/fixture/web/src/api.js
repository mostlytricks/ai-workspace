// Thin API client. Dev server proxies /api -> order-api (see order-api port).
export async function fetchOrders() {
  const res = await fetch('/api/orders');
  return res.json();
}

export async function fetchCustomer(id) {
  const res = await fetch(`/api/customers/${id}`);
  return res.json();
}

export async function fetchGhostStats() {
  const res = await fetch('/api/ghost/stats');
  return res.json();
}
