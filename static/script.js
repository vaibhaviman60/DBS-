// ===================== INITIALIZATION =====================

window.addEventListener('DOMContentLoaded', () => {
  console.log('[SCRIPT] Page loaded, initializing dashboard...');
  
  // Render navigation sidebar
  renderSidebar();
  
  // Fetch and render all dashboard data
  loadKPIs();
  loadAlerts();
  loadInventory();
  
  console.log('[SCRIPT] Dashboard ready!');
});

// ===================== SIDEBAR NAV =====================

function renderSidebar() {
  const navEl = document.getElementById('app-nav');
  if (!navEl) return;
  
  const navItems = [
    { label: '📊 Dashboard', active: true },
    { label: '📦 Inventory', active: false },
    { label: '📋 Purchase Orders', active: false },
    { label: '🏭 Suppliers', active: false },
    { label: '👥 Customers', active: false },
    { label: '👨‍💼 Team', active: false },
    { label: '📈 Analytics', active: false },
  ];
  
  navEl.innerHTML = navItems.map(item => `
    <div class="side-nav-item ${item.active ? 'active' : ''}">
      ${item.label}
    </div>
  `).join('');
}

// ===================== KPI CARDS =====================

function loadKPIs() {
  console.log('[KPIs] Fetching KPI data from /api/kpis...');
  
  fetch('/api/kpis')
    .then(res => res.json())
    .then(data => {
      console.log('[KPIs] Data received:', data);
      renderKPIs(data);
    })
    .catch(err => console.error('[ERROR] Failed to load KPIs:', err));
}

function renderKPIs(data) {
  const strip = document.getElementById('kpi-strip');
  if (!strip) return;
  
  const kpis = [
    {
      label: 'Current Stock Value',
      value: '₹' + formatNumber(data.total_stock_value),
      delta: '↑ In Stock',
      deltaClass: 'green'
    },
    {
      label: 'Open POs',
      value: data.open_po_count,
      delta: 'In Transit',
      deltaClass: 'amber'
    },
    {
      label: 'Inventory Alerts',
      value: data.critical_alert_count,
      delta: `${data.low_alert_count} Low Stock`,
      deltaClass: 'red'
    },
    {
      label: 'Total Inv. Value',
      value: '₹' + formatNumber(data.total_inventory_value),
      delta: 'Replacement Cost',
      deltaClass: 'blue'
    }
  ];
  
  strip.innerHTML = kpis.map(kpi => `
    <div class="card">
      <div class="label">${kpi.label}</div>
      <div class="value">${kpi.value}</div>
      <div class="delta ${kpi.deltaClass}">${kpi.delta}</div>
    </div>
  `).join('');
  
  // Update quick stats
  document.getElementById('stat-open-pos').textContent = data.open_po_count;
  document.getElementById('stat-critical').textContent = data.critical_alert_count;
  document.getElementById('stat-inventory-value').textContent = '₹' + formatNumber(data.total_stock_value);
}

// ===================== ALERTS TABLE =====================

function loadAlerts() {
  console.log('[Alerts] Fetching alerts from /api/alerts...');
  
  fetch('/api/alerts')
    .then(res => res.json())
    .then(data => {
      console.log('[Alerts] Data received:', data);
      renderAlerts(data);
    })
    .catch(err => console.error('[ERROR] Failed to load alerts:', err));
}

function renderAlerts(alerts) {
  const tbody = document.getElementById('alerts-tbody');
  if (!tbody) return;
  
  if (!alerts || alerts.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--muted);">✓ No alerts. All stock levels healthy!</td></tr>';
    return;
  }
  
  tbody.innerHTML = alerts.slice(0, 10).map(alert => {
    // Get product name and other details
    const productName = alert.product_name || 'Unknown';
    const currentStock = alert.current_stock || 0;
    const reorderPoint = alert.reorder_point || 0;
    const status = alert.status || 'low';
    const classification = alert.classification || 'Monitor';
    const leadTime = alert.lead_time_days || 0;
    
    return `
      <tr>
        <td><strong>${productName}</strong></td>
        <td>${currentStock}</td>
        <td>${reorderPoint}</td>
        <td><span class="pill ${status}">${status.toUpperCase()}</span></td>
        <td><strong>${classification}</strong></td>
        <td>${leadTime} days</td>
      </tr>
    `;
  }).join('');
}

// ===================== INVENTORY TABLE =====================

function loadInventory() {
  console.log('[Inventory] Fetching inventory from /api/inventory...');
  
  fetch('/api/inventory')
    .then(res => res.json())
    .then(data => {
      console.log('[Inventory] Data received:', data);
      renderInventory(data);
    })
    .catch(err => console.error('[ERROR] Failed to load inventory:', err));
}

function renderInventory(items) {
  const tbody = document.getElementById('inventory-tbody');
  if (!tbody) return;
  
  if (!items || items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:var(--muted);">No inventory data.</td></tr>';
    return;
  }
  
  tbody.innerHTML = items.slice(0, 20).map(item => {
    const productName = item.product_name || 'Unknown';
    const category = item.category || '-';
    const currentStock = item.current_stock || 0;
    const unitCost = item.unit_cost || 0;
    const stockValue = (currentStock * unitCost).toFixed(2);
    const status = item.status || 'ok';
    
    return `
      <tr>
        <td><strong>${productName}</strong></td>
        <td>${category}</td>
        <td>${currentStock}</td>
        <td>₹${unitCost.toFixed(2)}</td>
        <td>₹${formatNumber(stockValue)}</td>
        <td><span class="pill ${status}">${status.toUpperCase()}</span></td>
      </tr>
    `;
  }).join('');
}

// ===================== HELPERS =====================

function formatNumber(num) {
  return parseFloat(num).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

function miniLineChart(vals, color) {
  const w = 560, h = 150;
  const max = Math.max(...vals);
  const min = Math.min(...vals);
  const pts = vals.map((v, i) => {
    const x = (i / (vals.length - 1)) * w;
    const y = h - ((v - min) / (max - min || 1)) * (h - 20) - 10;
    return x + ',' + y;
  }).join(' ');
  const area = `0,${h} ${pts} ${w},${h}`;
  return `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
    <polygon points="${area}" fill="${color}" opacity="0.12"></polygon>
    <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></polyline>
  </svg>`;
}

console.log('[SCRIPT] Script loaded and ready to fetch data from backend');
