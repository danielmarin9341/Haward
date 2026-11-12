document.addEventListener('DOMContentLoaded', () => {
  // 1. Cargar los productos inyectados por Django de forma segura
  const rawDataElement = document.getElementById('product-data');
  let products = [];

  if (rawDataElement) {
    try {
      products = JSON.parse(rawDataElement.textContent);
    } catch (e) {
      console.error("Error al parsear los datos de la tienda:", e);
    }
  }

  // Estado del carrito guardado en el navegador
  let cart = JSON.parse(localStorage.getItem('haward_cart')) || [];

  // Referencias a elementos del DOM
  const grid = document.getElementById('grid');
  const filterCategory = document.getElementById('filter-category');
  const filterBrand = document.getElementById('filter-brand');
  const searchInput = document.getElementById('buscar');
  const resultCount = document.getElementById('resultCount');
  const cartCount = document.getElementById('cartCount');
  const cartItemsContainer = document.getElementById('cartItems');
  const cartTotal = document.getElementById('cartTotal');

  // Función para formatear dinero en pesos colombianos
  function formatMoney(amount) {
    return '$' + Number(amount).toLocaleString('es-CO');
  }

  // Renderizar productos aplicando filtros de categoría, marca y búsqueda
  function renderProducts() {
    if (!grid) return;

    const selectedCat = filterCategory ? filterCategory.value : 'all';
    const selectedBrand = filterBrand ? filterBrand.value : 'all';
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

    const filtered = products.filter(p => {
      const matchCat = selectedCat === 'all' || p.cat === selectedCat;
      const matchBrand = selectedBrand === 'all' ||
          (p.icon && p.icon.toLowerCase().includes(selectedBrand.toLowerCase())) ||
          (p.name && p.name.toLowerCase().includes(selectedBrand.toLowerCase()));
      const matchSearch = !query ||
          p.name.toLowerCase().includes(query) ||
          p.cat.toLowerCase().includes(query) ||
          p.spec.toLowerCase().includes(query);
      return matchCat && matchBrand && matchSearch;
    });

    if (resultCount) {
      resultCount.textContent = `${filtered.length} componentes encontrados`;
    }

    if (filtered.length === 0) {
      grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #888;">No se encontraron componentes con los filtros seleccionados.</div>`;
      return;
    }

    grid.innerHTML = filtered.map(product => {
      const inCart = cart.find(item => item.id === product.id);
      const inCartQty = inCart ? inCart.qty : 0;
      const isOutOfStock = product.stock <= 0;

      // Lógica de precios: Normal vs Oferta
      let priceHtml = '';
      if (product.is_on_sale && product.sale_price !== null && !isNaN(product.sale_price)) {
        priceHtml = `
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span style="font-size: 13px; text-decoration: line-through; color: #888;">${formatMoney(product.price)}</span>
                        <span style="font-size: 10px; background: rgba(236, 72, 153, 0.2); color: #ec4899; border: 1px solid #ec4899; padding: 2px 6px; border-radius: 4px; font-weight: 800;">OFERTA</span>
                    </div>
                    <div style="font-size: 18px; font-weight: 900; color: #ec4899; margin-bottom: 4px;">${formatMoney(product.sale_price)}</div>
                `;
      } else {
        priceHtml = `<div style="font-size: 18px; font-weight: 900; color: #fff; margin-bottom: 4px;">${formatMoney(product.price)}</div>`;
      }

      // Imagen del producto o contenedor alternativo si no tiene
      const imgHtml = product.imagen
          ? `<img src="${product.imagen}" alt="${product.name}" style="width: 100%; height: 150px; object-fit: cover; border-radius: 8px; margin-bottom: 10px;">`
          : `<div style="width: 100%; height: 150px; background: #1a1a1a; display: flex; align-items: center; justify-content: center; border-radius: 8px; margin-bottom: 10px; color: #555; font-size: 12px; font-weight: 600;">HAWARD HARDWARE</div>`;

      return `
                <div class="product-card" style="background: #121212; border: 1px solid #222; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; justify-content: space-between; transition: border-color 0.2s;">
                    <div>
                        ${imgHtml}
                        <div style="font-size: 11px; color: #06b6d4; text-transform: uppercase; font-weight: 700; margin-bottom: 4px;">${product.cat}</div>
                        <h3 style="font-size: 16px; font-weight: 800; color: #fff; margin-bottom: 6px;">${product.name}</h3>
                        <p style="font-size: 12px; color: #aaa; margin-bottom: 12px; line-height: 1.4;">${product.spec}</p>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: ${isOutOfStock ? '#ef4444' : '#10b981'}; margin-bottom: 8px; font-weight: 600;">
                            ${isOutOfStock ? '● Agotado' : `● Stock disponible: ${product.stock}`}
                        </div>
                        ${priceHtml}
                        <div style="display: flex; gap: 8px; margin-top: 12px;">
                            <button type="button" class="buy-btn" data-id="${product.id}" 
                                style="flex: 1; padding: 10px; background: ${isOutOfStock ? '#333' : '#06b6d4'}; color: ${isOutOfStock ? '#777' : '#000'}; border: none; border-radius: 6px; cursor: ${isOutOfStock ? 'not-allowed' : 'pointer'}; font-weight: 700; font-size: 12px;" 
                                ${isOutOfStock ? 'disabled' : ''}>
                                ${isOutOfStock ? 'Agotado' : `Comprar ${inCartQty > 0 ? '(' + inCartQty + ')' : ''}`}
                            </button>
                        </div>
                    </div>
                </div>
            `;
    }).join('');

    // Escuchar clics en los botones de compra
    document.querySelectorAll('.buy-btn').forEach(btn => {
      if (!btn.disabled) {
        btn.addEventListener('click', (e) => {
          const id = Number(e.target.dataset.id);
          addToCart(id);
        });
      }
    });
  }

  function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    if (!product || product.stock <= 0) return;

    const finalPrice = product.is_on_sale && product.sale_price !== null ? product.sale_price : product.price;
    const existing = cart.find(item => item.id === productId);

    if (existing) {
      if (existing.qty < product.stock) {
        existing.qty++;
      } else {
        alert('Has alcanzado el límite de stock disponible para este producto.');
        return;
      }
    } else {
      cart.push({ id: product.id, name: product.name, price: finalPrice, qty: 1 });
    }

    saveCart();
    renderProducts();
    renderCartModal();
  }

  function saveCart() {
    localStorage.setItem('haward_cart', JSON.stringify(cart));
    updateCartCount();
  }

  function updateCartCount() {
    const totalQty = cart.reduce((sum, item) => sum + item.qty, 0);
    if (cartCount) cartCount.textContent = totalQty;
  }

  function renderCartModal() {
    if (!cartItemsContainer) return;

    if (cart.length === 0) {
      cartItemsContainer.innerHTML = `<p style="text-align: center; color: #888; padding: 20px;">Tu carrito está vacío.</p>`;
      if (cartTotal) cartTotal.textContent = formatMoney(0);
      return;
    }

    let total = 0;
    cartItemsContainer.innerHTML = cart.map(item => {
      const subtotal = item.price * item.qty;
      total += subtotal;
      return `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #222;">
                    <div>
                        <div style="font-weight: 700; color: #fff; font-size: 14px;">${item.name}</div>
                        <div style="font-size: 12px; color: #888;">${formatMoney(item.price)} x ${item.qty}</div>
                    </div>
                    <div style="font-weight: 800; color: #06b6d4;">${formatMoney(subtotal)}</div>
                </div>
            `;
    }).join('');

    if (cartTotal) cartTotal.textContent = formatMoney(total);
  }

  // Eventos de filtros en tiempo real
  if (filterCategory) filterCategory.addEventListener('change', renderProducts);
  if (filterBrand) filterBrand.addEventListener('change', renderProducts);
  if (searchInput) searchInput.addEventListener('input', renderProducts);

  // Renderizado inicial al cargar la página
  renderProducts();
  updateCartCount();
  renderCartModal();
});

// Funciones globales para abrir y cerrar el carrito desde el HTML
function showCart() {
  const dialog = document.getElementById('cartDialog');
  if (dialog) dialog.showModal();
}

function closeCart() {
  const dialog = document.getElementById('cartDialog');
  if (dialog) dialog.close();
}