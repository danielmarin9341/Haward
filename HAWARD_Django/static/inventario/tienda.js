(() => {
  const products = JSON.parse(document.querySelector('#product-data')?.textContent || '[]');
  const compareIds = new Set();
  const cart = {};

  try {
    const saved = JSON.parse(localStorage.getItem('hawardCart') || '{}');
    for (const [id, quantity] of Object.entries(saved)) {
      const product = products.find(item => String(item.id) === id);
      if (product && Number.isInteger(quantity) && quantity > 0) {
        cart[id] = Math.min(quantity, product.stock);
      }
    }
  } catch { /* Carrito vacío por defecto si hay error */ }

  const money = value => '$' + Number(value).toLocaleString('es-CO');
  const esc = value => String(value).replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);

  // Referencias a los elementos de control
  const categorySelect = document.getElementById('filter-category');
  const brandSelect = document.getElementById('filter-brand');
  const searchInput = document.getElementById('buscar');
  const grid = document.getElementById('grid');
  const resultCount = document.getElementById('resultCount');

  // Función principal para renderizar las tarjetas de productos
  function renderProducts(items) {
    if (!grid) return;

    if (items.length === 0) {
      grid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--muted);">No se encontraron componentes con estos filtros.</div>';
      if (resultCount) resultCount.textContent = '0 productos disponibles';
      return;
    }

    if (resultCount) {
      resultCount.textContent = `${items.length} ${items.length === 1 ? 'producto disponible' : 'productos disponibles'}`;
    }

    grid.innerHTML = items.map(product => {
      console.log("Producto:", product.name, "Imagen cruda:", product.image, product.imagen, product.image_url);
      const isCompared = compareIds.has(String(product.id));
      const inCartQty = cart[product.id] || 0;

      // Renderizado seguro de imagen local vs texto/icono
      // Detecta automáticamente cualquier nombre común para la imagen en Django
      // Obtenemos la ruta que envíe Django (revisando los nombres más comunes)
      let rawImage = product.image || product.imagen || product.image_url || product.img || product.foto;

      // Si existe una ruta y no empieza con http o /media/, le agregamos el prefijo /media/ de Django
      let imageUrl = '';
      if (rawImage && rawImage.trim() !== '') {
        imageUrl = rawImage.startsWith('http') || rawImage.startsWith('/media/') ? rawImage : '/media/' + rawImage;
      }

      let imageHtml = '';
      if (imageUrl) {
        imageHtml = `<div class="product-art"><img src="${esc(imageUrl)}" alt="${esc(product.name)}" style="width:100%; height:100%; object-fit:cover;"><span class="badge">${esc(product.cat)}</span></div>`;
      } else {
        imageHtml = `<div class="product-art"><span>${esc(product.icon || 'HW')}</span><span class="badge">${esc(product.cat)}</span></div>`;
      }
      return `
        <article class="card">
          ${imageHtml}
          <div class="details">
            <span class="product-brand" style="font-size: 11px; color: var(--cyan); letter-spacing: 0.1em; text-transform: uppercase;">${esc(product.icon || '')}</span>
            <h3 style="margin: 6px 0 8px 0; font-size: 16px; color: #fff;">${esc(product.name)}</h3>
            <p style="font-size: 13px; color: var(--muted); margin-bottom: 12px; line-height: 1.4;">${esc(product.spec || '')}</p>
            <div style="font-size: 18px; font-weight: 800; color: #fff; margin-bottom: 12px;">${money(product.price)}</div>
            
            <div style="display: flex; gap: 8px; margin-top: auto;">
              <button type="button" class="compare-btn ${isCompared ? 'active' : ''}" data-compare-id="${product.id}" style="flex: 1; padding: 8px; background: ${isCompared ? 'var(--cyan)' : 'transparent'}; color: ${isCompared ? '#000' : '#fff'}; border: 1px solid var(--line); border-radius: 6px; cursor: pointer; font-size: 12px;">
                ${isCompared ? '✓ Comparando' : 'Comparar'}
              </button>
              <button type="button" class="buy-btn" data-cart-step="1" data-id="${product.id}" style="flex: 1; padding: 8px; background: var(--cyan); color: #000; border: none; border-radius: 6px; cursor: pointer; font-weight: 700; font-size: 12px;">
                Comprar (${inCartQty})
              </button>
            </div>
          </div>
        </article>
      `;
    }).join('');
  }

  // Filtrado combinado (Categoría + Marca + Buscador de texto)
  function applyFilters() {
    const selectedCategory = categorySelect ? categorySelect.value : 'all';
    const selectedBrand = brandSelect ? brandSelect.value : 'all';
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

    const filtered = products.filter(product => {
      const matchCategory = (selectedCategory === 'all') || (product.cat === selectedCategory);
      const matchBrand = (selectedBrand === 'all') || (product.icon === selectedBrand);
      const matchQuery = !query ||
          product.name.toLowerCase().includes(query) ||
          (product.spec && product.spec.toLowerCase().includes(query));

      return matchCategory && matchBrand && matchQuery;
    });

    renderProducts(filtered);
  }

  function changeQuantity(id, step) {
    const product = products.find(item => String(item.id) === id);
    const next = (cart[id] || 0) + step;
    if (!product || next < 0 || next > product.stock) return;
    if (next === 0) delete cart[id]; else cart[id] = next;
    localStorage.setItem('hawardCart', JSON.stringify(cart));
    applyFilters();
    updateCartCount();
    if (document.querySelector('#cartDialog').open) renderCart();
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
    const selectedProducts = products.filter(product => compareIds.has(String(product.id)));
    if (selectedProducts.length !== 2) return;

    const rows = [
      ['Categoría', product => product.cat],
      ['Marca', product => product.icon || 'N/A'],
      ['Precio', product => money(product.price)],
      ['Especificaciones', product => product.spec || 'Sin especificaciones'],
      ['Disponibilidad', product => product.stock > 0 ? `${product.stock} unidades` : 'Agotado'],
    ];

    const header = selectedProducts.map(product => `<th>${esc(product.name)}</th>`).join('');
    const body = rows.map(([label, value]) => `<tr><th>${label}</th>${selectedProducts.map(product => `<td>${esc(value(product))}</td>`).join('')}</tr>`).join('');

    document.querySelector('#compareContent').innerHTML = `<table class="compare-table"><thead><tr><th>Característica</th>${header}</tr></thead><tbody>${body}</tbody></table>`;
    document.querySelector('#compareDialog').showModal();
  }

  function renderCart() {
    const entries = Object.entries(cart).filter(([id, quantity]) => products.some(product => String(product.id) === id) && quantity > 0);
    const container = document.querySelector('#cartItems');
    if (!container) return;

    if (!entries.length) {
      container.innerHTML = '<div class="cart-empty">Tu carrito está vacío.<br>Agrega componentes para verlos aquí.</div>';
      document.querySelector('#cartTotal').textContent = money(0);
      return;
    }

    container.innerHTML = entries.map(([id, quantity]) => {
      const product = products.find(item => String(item.id) === id);
      return `<article class="cart-line"><div class="cart-mark">${esc(product.icon || 'HW')}</div><div class="cart-info"><strong>${esc(product.name)}</strong><small>${money(product.price)} cada uno</small><div class="cart-qty"><button type="button" data-cart-step="-1" data-id="${id}" aria-label="Quitar uno">−</button><span>${quantity}</span><button type="button" data-cart-step="1" data-id="${id}" aria-label="Agregar uno" ${quantity >= product.stock ? 'disabled' : ''}>+</button></div></div><div class="cart-price">${money(product.price * quantity)}</div></article>`;
    }).join('');

    const total = entries.reduce((sum, [id, quantity]) => sum + Number(products.find(product => String(product.id) === id).price) * quantity, 0);
    document.querySelector('#cartTotal').textContent = money(total);
  }

  // Event Listeners globales
  window.showCart = () => { renderCart(); document.querySelector('#cartDialog').showModal(); };
  window.closeCart = () => document.querySelector('#cartDialog').close();

  if (categorySelect) categorySelect.addEventListener('change', applyFilters);
  if (brandSelect) brandSelect.addEventListener('change', applyFilters);
  if (searchInput) searchInput.addEventListener('input', applyFilters);

  if (grid) {
    grid.addEventListener('click', event => {
      const compareBtn = event.target.closest('[data-compare-id]');
      if (compareBtn) {
        const id = compareBtn.dataset.compareId;
        if (compareIds.has(id)) compareIds.delete(id);
        else if (compareIds.size < 2) compareIds.add(id);
        updateCompareBar();
        applyFilters();
        return;
      }

      const cartBtn = event.target.closest('[data-cart-step]');
      if (cartBtn) {
        changeQuantity(cartBtn.dataset.id, Number(cartBtn.dataset.cartStep));
      }
    });
  }

  const compareOpen = document.querySelector('#compareOpen');
  if (compareOpen) compareOpen.addEventListener('click', showComparison);

  const compareClear = document.querySelector('#compareClear');
  if (compareClear) compareClear.addEventListener('click', () => {
    compareIds.clear();
    updateCompareBar();
    applyFilters();
  });

  const compareClose = document.querySelector('#compareClose');
  if (compareClose) compareClose.addEventListener('click', () => document.querySelector('#compareDialog').close());

  const compareDialog = document.querySelector('#compareDialog');
  if (compareDialog) {
    compareDialog.addEventListener('click', event => {
      if (event.target === event.currentTarget) event.currentTarget.close();
    });
  }

  const cartItems = document.querySelector('#cartItems');
  if (cartItems) {
    cartItems.addEventListener('click', event => {
      const button = event.target.closest('[data-cart-step]');
      if (button) changeQuantity(button.dataset.id, Number(button.dataset.cartStep));
    });
  }

  const cartDialog = document.querySelector('#cartDialog');
  if (cartDialog) {
    cartDialog.addEventListener('click', event => {
      if (event.target === event.currentTarget) window.closeCart();
    });
  }

  // Inicialización
  updateCartCount();
  updateCompareBar();
  applyFilters();
})();