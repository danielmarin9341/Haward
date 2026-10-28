(() => {
  const products = JSON.parse(document.querySelector('#product-data')?.textContent || '[]');
  const categories = ['Todos', ...new Set(products.map(product => product.cat))];
  let selected = 'Todos';
  const compareIds = new Set();
  const cart = {};
  try {
    const saved = JSON.parse(localStorage.getItem('hawardCart') || '{}');
    for (const [id, quantity] of Object.entries(saved)) {
      const product = products.find(item => String(item.id) === id);
      if (product && Number.isInteger(quantity) && quantity > 0) cart[id] = Math.min(quantity, product.stock);
    }
  } catch { /* Inicia con el carrito vacío si el almacenamiento no es válido. */ }

  const money = value => '$' + Number(value).toLocaleString('es-CO');
  const esc = value => String(value).replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[char]);

  function drawCategories() {
    document.querySelector('#categories').innerHTML = categories.map(category =>
      `<button class="chip ${category === selected ? 'active' : ''}" data-category="${esc(category)}">${esc(category)}</button>`
    ).join('');
    document.querySelectorAll('.chip').forEach(button => button.addEventListener('click', () => {
      selected = button.dataset.category;
      drawCategories();
      drawProducts();
    }));
  }

  function drawProducts() {
    const query = document.querySelector('#buscar').value.toLocaleLowerCase('es');
    const list = products.filter(product =>
      (selected === 'Todos' || product.cat === selected) &&
      `${product.name} ${product.cat} ${product.spec}`.toLocaleLowerCase('es').includes(query)
    );
    document.querySelector('#resultCount').textContent = `${list.length} ${list.length === 1 ? 'producto disponible' : 'productos disponibles'}`;
    document.querySelector('#grid').innerHTML = list.length ? list.map(product => {
      const id = String(product.id);
      const quantity = cart[id] || 0;
      const isCompared = compareIds.has(id);
      const compareDisabled = !isCompared && compareIds.size >= 2;
      const image = product.image && /^https:\/\//i.test(product.image)
        ? `<img src="${esc(product.image)}" alt="${esc(product.name)}" loading="lazy" data-fallback="${esc(product.icon)}">`
        : esc(product.icon);
      return `<article class="card"><div class="product-art"><span class="badge">${product.stock > 0 ? 'EN STOCK' : 'AGOTADO'}</span>${image}</div><div class="details"><div class="category-label">${esc(product.cat)}</div><h3>${esc(product.name)}</h3><div class="spec">${esc(product.spec)}</div><div class="price-row"><div class="price">${money(product.price)}<small>Precio IVA incluido</small></div>${quantity ? `<div class="qty-control"><button class="qty-btn" data-step="-1" data-id="${id}" aria-label="Quitar uno">−</button><span>${quantity}</span><button class="qty-btn" data-step="1" data-id="${id}" aria-label="Agregar uno" ${quantity >= product.stock ? 'disabled' : ''}>+</button></div>` : `<button class="add" data-id="${id}" ${product.stock === 0 ? 'disabled' : ''}>Agregar</button>`}</div><div class="stock ${product.stock === 0 ? 'stock-empty' : ''}">● ${product.stock === 0 ? 'Agotado' : `${product.stock} unidades disponibles`}</div><button class="compare-toggle ${isCompared ? 'selected' : ''}" type="button" data-compare-id="${id}" aria-pressed="${isCompared}" ${compareDisabled ? 'disabled' : ''}>${isCompared ? 'Elegido' : 'Comparar'}</button></div></article>`;
    }).join('') : '<div class="empty">No encontramos componentes con esa búsqueda.</div>';
    document.querySelectorAll('.product-art img').forEach(image => image.addEventListener('error', () => {
      image.replaceWith(document.createTextNode(image.dataset.fallback));
    }, { once: true }));
    document.querySelectorAll('.add').forEach(button => button.addEventListener('click', () => changeQuantity(button.dataset.id, 1)));
    document.querySelectorAll('.qty-btn').forEach(button => button.addEventListener('click', () => changeQuantity(button.dataset.id, Number(button.dataset.step))));
    updateCartCount();
  }

  function changeQuantity(id, step) {
    const product = products.find(item => String(item.id) === id);
    const next = (cart[id] || 0) + step;
    if (!product || next < 0 || next > product.stock) return;
    if (next === 0) delete cart[id]; else cart[id] = next;
    localStorage.setItem('hawardCart', JSON.stringify(cart));
    drawProducts();
    if (document.querySelector('#cartDialog').open) renderCart();
    if (step > 0) {
      const toast = document.querySelector('#toast');
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 1500);
    }
  }

  function updateCartCount() {
    document.querySelector('#cartCount').textContent = Object.values(cart).reduce((sum, quantity) => sum + quantity, 0);
  }

  function updateCompareBar() {
    const count = compareIds.size;
    document.querySelector('#compareBar').hidden = count === 0;
    document.querySelector('#compareLabel').textContent = `${count} de 2 componentes seleccionados`;
    document.querySelector('#compareOpen').disabled = count !== 2;
  }

  function showComparison() {
    const selectedProducts = products.filter(product => compareIds.has(String(product.id)));
    if (selectedProducts.length !== 2) return;
    const rows = [
      ['Categoria', product => product.cat],
      ['Precio', product => money(product.price)],
      ['Especificaciones', product => product.spec || 'Sin especificaciones'],
      ['Disponibilidad', product => product.stock > 0 ? `${product.stock} unidades` : 'Agotado'],
    ];
    const header = selectedProducts.map(product => `<th>${esc(product.name)}</th>`).join('');
    const body = rows.map(([label, value]) => `<tr><th>${label}</th>${selectedProducts.map(product => `<td>${esc(value(product))}</td>`).join('')}</tr>`).join('');
    document.querySelector('#compareContent').innerHTML = `<table class="compare-table"><thead><tr><th>Caracteristica</th>${header}</tr></thead><tbody>${body}</tbody></table>`;
    document.querySelector('#compareDialog').showModal();
  }
  function renderCart() {
    const entries = Object.entries(cart).filter(([id, quantity]) => products.some(product => String(product.id) === id) && quantity > 0);
    const container = document.querySelector('#cartItems');
    if (!entries.length) {
      container.innerHTML = '<div class="cart-empty">Tu carrito está vacío.<br>Agrega componentes para verlos aquí.</div>';
      document.querySelector('#cartTotal').textContent = money(0);
      return;
    }
    container.innerHTML = entries.map(([id, quantity]) => {
      const product = products.find(item => String(item.id) === id);
      return `<article class="cart-line"><div class="cart-mark">${esc(product.icon)}</div><div class="cart-info"><strong>${esc(product.name)}</strong><small>${money(product.price)} cada uno</small><div class="cart-qty"><button type="button" data-cart-step="-1" data-id="${id}" aria-label="Quitar uno">−</button><span>${quantity}</span><button type="button" data-cart-step="1" data-id="${id}" aria-label="Agregar uno" ${quantity >= product.stock ? 'disabled' : ''}>+</button></div></div><div class="cart-price">${money(product.price * quantity)}</div></article>`;
    }).join('');
    const total = entries.reduce((sum, [id, quantity]) => sum + Number(products.find(product => String(product.id) === id).price) * quantity, 0);
    document.querySelector('#cartTotal').textContent = money(total);
  }

  window.showCart = () => { renderCart(); document.querySelector('#cartDialog').showModal(); };
  window.closeCart = () => document.querySelector('#cartDialog').close();
  document.querySelector('#buscar').addEventListener('input', drawProducts);
  document.querySelector('#grid').addEventListener('click', event => {
    const button = event.target.closest('[data-compare-id]');
    if (!button) return;
    const id = button.dataset.compareId;
    if (compareIds.has(id)) compareIds.delete(id);
    else if (compareIds.size < 2) compareIds.add(id);
    updateCompareBar();
    drawProducts();
  });
  document.querySelector('#compareOpen').addEventListener('click', showComparison);
  document.querySelector('#compareClear').addEventListener('click', () => {
    compareIds.clear();
    updateCompareBar();
    drawProducts();
  });
  document.querySelector('#compareClose').addEventListener('click', () => document.querySelector('#compareDialog').close());
  document.querySelector('#compareDialog').addEventListener('click', event => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  document.querySelector('#cartItems').addEventListener('click', event => {
    const button = event.target.closest('[data-cart-step]');
    if (button) changeQuantity(button.dataset.id, Number(button.dataset.cartStep));
  });
  document.querySelector('#cartDialog').addEventListener('click', event => {
    if (event.target === event.currentTarget) window.closeCart();
  });
  drawCategories();
  drawProducts();
  updateCompareBar();
})();