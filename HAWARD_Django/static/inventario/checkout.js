(() => {
  const CART_KEY = 'hawardCart';
  const products = JSON.parse(document.querySelector('#product-data')?.textContent || '[]');
  const summary = document.querySelector('#checkoutSummary');
  const form = document.querySelector('#checkoutForm');
  if (!summary || !form) return;

  const freeFrom = Number(summary.dataset.freeFrom);
  const shippingCost = Number(summary.dataset.shipping);
  const money = value => '$' + Number(value).toLocaleString('es-CO');
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);

  // Carrito guardado por la tienda, ajustado a lo que hay disponible ahora
  const cart = {};
  let adjusted = false;
  try {
    const saved = JSON.parse(localStorage.getItem(CART_KEY) || '{}');
    for (const [id, quantity] of Object.entries(saved)) {
      const product = products.find(item => String(item.id) === id);
      if (!product || product.stock <= 0 || !Number.isInteger(quantity) || quantity < 1) {
        adjusted = true;
        continue;
      }
      cart[id] = Math.min(quantity, product.stock);
      if (cart[id] !== quantity) adjusted = true;
    }
  } catch { /* carrito vacío */ }

  function persist() {
    try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch { /* ignorar */ }
    document.querySelector('#carritoInput').value = JSON.stringify(cart);
  }

  function render() {
    const entries = Object.entries(cart);
    const itemsBox = document.querySelector('#summaryItems');
    const payButton = document.querySelector('#payButton');
    const empty = document.querySelector('#emptyCart');
    const notice = document.querySelector('#summaryNotice');

    empty.hidden = entries.length > 0;
    payButton.disabled = entries.length === 0;
    notice.hidden = !adjusted;
    if (adjusted) notice.textContent = 'Ajustamos tu carrito a las unidades disponibles.';

    let subtotal = 0;
    itemsBox.innerHTML = entries.map(([id, quantity]) => {
      const product = products.find(item => String(item.id) === id);
      subtotal += product.price * quantity;
      const mark = product.imagen ? `<img src="${esc(product.imagen)}" alt="">` : esc(product.icon || 'HW');
      return `<div class="summary-line">
        <div class="cart-mark">${mark}</div>
        <div class="summary-info">
          <strong>${esc(product.name)}</strong>
          <div class="cart-qty">
            <button type="button" data-step="-1" data-id="${id}" aria-label="Quitar uno">−</button>
            <span>${quantity}</span>
            <button type="button" data-step="1" data-id="${id}" aria-label="Agregar uno" ${quantity >= product.stock ? 'disabled' : ''}>+</button>
          </div>
        </div>
        <div class="summary-price">${money(product.price * quantity)}</div>
      </div>`;
    }).join('');

    const shipping = entries.length === 0 ? 0 : (subtotal >= freeFrom ? 0 : shippingCost);
    document.querySelector('#sumSubtotal').textContent = money(subtotal);
    document.querySelector('#sumShipping').textContent = shipping === 0 && entries.length ? 'Gratis' : money(shipping);
    document.querySelector('#sumTotal').textContent = money(subtotal + shipping);
    document.querySelector('#sumHint').textContent = entries.length && subtotal < freeFrom
      ? `Te faltan ${money(freeFrom - subtotal)} para tener envío gratis.`
      : '';
    persist();
  }

  document.querySelector('#summaryItems').addEventListener('click', event => {
    const button = event.target.closest('[data-step]');
    if (!button) return;
    const id = button.dataset.id;
    const product = products.find(item => String(item.id) === id);
    const next = (cart[id] || 0) + Number(button.dataset.step);
    if (next < 0 || next > product.stock) return;
    if (next === 0) delete cart[id]; else cart[id] = next;
    adjusted = false;
    render();
  });

  form.addEventListener('submit', event => {
    persist();
    if (Object.keys(cart).length === 0) event.preventDefault();
  });

  render();
})();
