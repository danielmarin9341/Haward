(() => {
  const products = JSON.parse(document.querySelector('#product-data')?.textContent || '[]');
  const CART_KEY = 'hawardCart';
  const compareIds = new Set();
  const cart = {};

  // Recupera el carrito guardado, ajustado al stock actual
  try {
    const saved = JSON.parse(localStorage.getItem(CART_KEY) || '{}');
    for (const [id, quantity] of Object.entries(saved)) {
      const product = products.find(item => String(item.id) === id);
      if (product && Number.isInteger(quantity) && quantity > 0 && product.stock > 0) {
        cart[id] = Math.min(quantity, product.stock);
      }
    }
  } catch { /* carrito vacío si el almacenamiento falla */ }

  const money = value => '$' + Number(value).toLocaleString('es-CO');
  // Escapa todo texto que viene de la base de datos antes de usarlo en innerHTML
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);

  const categorySelect = document.getElementById('filter-category');
  const brandSelect = document.getElementById('filter-brand');
  const searchInput = document.getElementById('buscar');
  const grid = document.getElementById('grid');
  const resultCount = document.getElementById('resultCount');

  const unitPrice = product => (product.is_on_sale && product.sale_price !== null) ? product.sale_price : product.price;

  // Llena los filtros con las categorías y marcas que existen en el catálogo
  function fillSelect(select, values) {
    if (!select) return;
    while (select.options.length > 1) select.remove(1);
    [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b, 'es')).forEach(value => {
      select.add(new Option(value, value));
    });
  }
  fillSelect(categorySelect, products.map(product => product.cat));
  fillSelect(brandSelect, products.map(product => product.brand));

  function renderProducts(items, animate) {
    if (!grid) return;
    grid.classList.toggle('animate', Boolean(animate));

    if (resultCount) {
      resultCount.textContent = `${items.length} ${items.length === 1 ? 'producto disponible' : 'productos disponibles'}`;
    }

    if (items.length === 0) {
      grid.innerHTML = '<div class="empty">No se encontraron componentes con estos filtros.</div>';
      return;
    }

    grid.innerHTML = items.map((product, index) => {
      const isCompared = compareIds.has(String(product.id));
      const quantity = cart[product.id] || 0;
      const outOfStock = product.stock <= 0;
      const onSale = product.is_on_sale && product.sale_price !== null;

      const art = product.imagen
        ? `<img src="${esc(product.imagen)}" alt="${esc(product.name)}" loading="lazy">`
        : `<span>${esc(product.icon || 'HW')}</span>`;

      const action = outOfStock
        ? '<button type="button" class="add" disabled>Agotado</button>'
        : quantity > 0
          ? `<div class="qty-control">
               <button type="button" class="qty-btn" data-cart-step="-1" data-id="${product.id}" aria-label="Quitar uno">−</button>
               <span>${quantity}</span>
               <button type="button" class="qty-btn" data-cart-step="1" data-id="${product.id}" aria-label="Agregar uno" ${quantity >= product.stock ? 'disabled' : ''}>+</button>
             </div>`
          : `<button type="button" class="add" data-cart-step="1" data-id="${product.id}">Agregar</button>`;

      return `
        <article class="card" style="--i:${Math.min(index, 12)}">
          <div class="product-art">
            ${art}
            <span class="badge">${esc(product.cat)}</span>
            ${onSale ? '<span class="badge badge-sale">OFERTA</span>' : ''}
          </div>
          <div class="details">
            <div>
              <span class="category-label">${esc(product.brand || product.cat)}</span>
              <h3>${esc(product.name)}</h3>
              <p class="spec">${esc(product.spec)}</p>
              <div class="stock ${outOfStock ? 'stock-empty' : ''}">${outOfStock ? 'Agotado' : `${product.stock} disponibles`}</div>
            </div>
            <div>
              <div class="price-row">
                <div class="price">
                  ${onSale ? `<small class="old">${money(product.price)}</small>` : ''}
                  ${money(unitPrice(product))}
                </div>
                ${action}
              </div>
              <button type="button" class="compare-toggle ${isCompared ? 'selected' : ''}" data-compare-id="${product.id}">
                ${isCompared ? '✓ En comparación' : 'Comparar'}
              </button>
            </div>
          </div>
        </article>`;
    }).join('');
  }

  // Filtros combinados: categoría + marca + texto
  function applyFilters(animate = true) {
    const category = categorySelect ? categorySelect.value : 'all';
    const brand = brandSelect ? brandSelect.value : 'all';
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

    const filtered = products.filter(product =>
      (category === 'all' || product.cat === category) &&
      (brand === 'all' || product.brand === brand) &&
      (!query ||
        product.name.toLowerCase().includes(query) ||
        product.cat.toLowerCase().includes(query) ||
        (product.brand || '').toLowerCase().includes(query) ||
        (product.spec || '').toLowerCase().includes(query))
    );
    renderProducts(filtered, animate);
  }

  function saveCart() {
    try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch { /* ignorar */ }
  }

  function changeQuantity(id, step) {
    const product = products.find(item => String(item.id) === id);
    const next = (cart[id] || 0) + step;
    if (!product || next < 0 || next > product.stock) return;
    if (next === 0) delete cart[id]; else cart[id] = next;
    saveCart();
    applyFilters(false); // sin repetir la animación de entrada
    updateCartCount();
    if (document.querySelector('#cartDialog')?.open) renderCart();
  }

  function updateCartCount() {
    const count = Object.values(cart).reduce((sum, quantity) => sum + quantity, 0);
    const countEl = document.querySelector('#cartCount');
    if (countEl) countEl.textContent = count;
  }

  function updateCompareBar() {
    const count = compareIds.size;
    const bar = document.querySelector('#compareBar');
    const label = document.querySelector('#compareLabel');
    const openBtn = document.querySelector('#compareOpen');
    if (bar) bar.hidden = count === 0;
    if (label) label.textContent = `${count} de 2 componentes seleccionados`;
    if (openBtn) openBtn.disabled = count !== 2;
  }

  function showComparison() {
    const selected = products.filter(product => compareIds.has(String(product.id)));
    if (selected.length !== 2) return;

    const rows = [
      ['Categoría', product => product.cat],
      ['Marca', product => product.brand || 'N/A'],
      ['Precio', product => money(unitPrice(product))],
      ['Especificaciones', product => product.spec || 'Sin especificaciones'],
      ['Disponibilidad', product => product.stock > 0 ? `${product.stock} unidades` : 'Agotado'],
    ];
    const header = selected.map(product => `<th>${esc(product.name)}</th>`).join('');
    const body = rows.map(([label, value]) =>
      `<tr><th>${label}</th>${selected.map(product => `<td>${esc(value(product))}</td>`).join('')}</tr>`
    ).join('');

    document.querySelector('#compareContent').innerHTML =
      `<table class="compare-table"><thead><tr><th>Característica</th>${header}</tr></thead><tbody>${body}</tbody></table>`;
    document.querySelector('#compareDialog').showModal();
  }

  function renderCart() {
    const entries = Object.entries(cart).filter(([id]) => products.some(product => String(product.id) === id));
    const container = document.querySelector('#cartItems');
    const checkoutLink = document.querySelector('#checkoutLink');
    if (!container) return;

    if (checkoutLink) checkoutLink.hidden = entries.length === 0;

    if (!entries.length) {
      container.innerHTML = '<div class="cart-empty">Tu carrito está vacío.<br>Agrega componentes para verlos aquí.</div>';
      document.querySelector('#cartTotal').textContent = money(0);
      return;
    }

    let total = 0;
    container.innerHTML = entries.map(([id, quantity]) => {
      const product = products.find(item => String(item.id) === id);
      const price = unitPrice(product);
      total += price * quantity;
      const mark = product.imagen
        ? `<img src="${esc(product.imagen)}" alt="">`
        : esc(product.icon || 'HW');
      return `<article class="cart-line">
        <div class="cart-mark">${mark}</div>
        <div class="cart-info">
          <strong>${esc(product.name)}</strong>
          <small>${money(price)} cada uno</small>
          <div class="cart-qty">
            <button type="button" data-cart-step="-1" data-id="${id}" aria-label="Quitar uno">−</button>
            <span>${quantity}</span>
            <button type="button" data-cart-step="1" data-id="${id}" aria-label="Agregar uno" ${quantity >= product.stock ? 'disabled' : ''}>+</button>
          </div>
        </div>
        <div class="cart-price">${money(price * quantity)}</div>
      </article>`;
    }).join('');
    document.querySelector('#cartTotal').textContent = money(total);
  }

  window.showCart = () => { renderCart(); document.querySelector('#cartDialog').showModal(); };
  window.closeCart = () => document.querySelector('#cartDialog').close();

  categorySelect?.addEventListener('change', () => applyFilters());
  brandSelect?.addEventListener('change', () => applyFilters());
  searchInput?.addEventListener('input', () => applyFilters());

  grid?.addEventListener('click', event => {
    const compareBtn = event.target.closest('[data-compare-id]');
    if (compareBtn) {
      const id = compareBtn.dataset.compareId;
      if (compareIds.has(id)) compareIds.delete(id);
      else if (compareIds.size < 2) compareIds.add(id);
      updateCompareBar();
      applyFilters(false);
      return;
    }
    const cartBtn = event.target.closest('[data-cart-step]');
    if (cartBtn) changeQuantity(cartBtn.dataset.id, Number(cartBtn.dataset.cartStep));
  });

  document.querySelector('#compareOpen')?.addEventListener('click', showComparison);
  document.querySelector('#compareClear')?.addEventListener('click', () => {
    compareIds.clear();
    updateCompareBar();
    applyFilters(false);
  });
  document.querySelector('#compareClose')?.addEventListener('click', () => document.querySelector('#compareDialog').close());
  document.querySelector('#compareDialog')?.addEventListener('click', event => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });

  document.querySelector('#cartItems')?.addEventListener('click', event => {
    const button = event.target.closest('[data-cart-step]');
    if (button) changeQuantity(button.dataset.id, Number(button.dataset.cartStep));
  });
  document.querySelector('#cartDialog')?.addEventListener('click', event => {
    if (event.target === event.currentTarget) window.closeCart();
  });

  saveCart(); // guarda el carrito ya ajustado al stock
  updateCartCount();
  updateCompareBar();
  applyFilters();
})();
