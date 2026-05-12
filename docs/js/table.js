/**
 * table.js
 * --------
 * Tabla "Desempeño por modelo":
 *   - Sort por columna (click en header)
 *   - Cross-filter al click en fila
 *   - Pills de calificación con colores semánticos
 *
 * Expone: window.Table
 */
(function () {
  'use strict';

  function init() {
    // Sort por columna
    document.querySelectorAll('#tabla-modelo thead th').forEach(th => {
      th.addEventListener('click', () => {
        const key = th.dataset.sort;
        const S = AppState.state;
        if (S.sortBy === key) {
          S.sortDir = S.sortDir === 'asc' ? 'desc' : 'asc';
        } else {
          S.sortBy = key;
          S.sortDir = 'desc';
        }
        updateHeaderIndicators();
        AppState.notify();
      });
    });
    updateHeaderIndicators();
  }

  /**
   * Limpia indicadores ▼/▲ y los pone en la columna activa.
   */
  function updateHeaderIndicators() {
    const S = AppState.state;
    document.querySelectorAll('#tabla-modelo thead th').forEach(t => {
      t.classList.remove('sort-active');
      t.textContent = Utils.TABLE_LABELS[t.dataset.sort] || t.textContent;
    });
    const activeTh = document.querySelector(`#tabla-modelo thead th[data-sort="${S.sortBy}"]`);
    if (activeTh) {
      activeTh.classList.add('sort-active');
      activeTh.textContent = Utils.TABLE_LABELS[S.sortBy] + (S.sortDir === 'desc' ? ' ▼' : ' ▲');
    }
  }

  /**
   * Renderiza la tabla con datos filtrados.
   */
  function update(ventas, resenas) {
    const S = AppState.state;
    const scale = S.meta.scale_v;

    // Agregar ventas por modelo
    const byModelo = {};
    ventas.forEach(x => {
      if (!byModelo[x.modelo]) byModelo[x.modelo] = { unidades: 0, ingresos: 0, n: 0 };
      byModelo[x.modelo].unidades += x.cantidad;
      byModelo[x.modelo].ingresos += x.ingreso;
      byModelo[x.modelo].n += 1;
    });

    // Calificación promedio por modelo
    const califByModelo = {};
    resenas.forEach(x => {
      if (!califByModelo[x.modelo]) califByModelo[x.modelo] = { sum: 0, n: 0 };
      califByModelo[x.modelo].sum += x.calificacion;
      califByModelo[x.modelo].n += 1;
    });

    // Construir rows
    let rows = Object.entries(byModelo).map(([modelo, d]) => {
      const cal = califByModelo[modelo]
        ? califByModelo[modelo].sum / califByModelo[modelo].n
        : null;
      return {
        modelo,
        unidades: d.unidades * scale,
        ingresos: d.ingresos * scale,
        ticket: d.n ? d.ingresos / d.n : 0,
        cal,
      };
    });

    // Sort
    const dir = S.sortDir === 'asc' ? 1 : -1;
    rows.sort((a, b) => {
      const va = a[S.sortBy], vb = b[S.sortBy];
      if (va === null) return 1;
      if (vb === null) return -1;
      if (typeof va === 'string') return va.localeCompare(vb) * dir;
      return (va - vb) * dir;
    });

    const tbody = document.querySelector('#tabla-modelo tbody');
    if (!rows.length) {
      tbody.innerHTML = `
        <tr><td colspan="5" style="text-align:center; padding:32px; color:var(--text-muted)">
          Sin datos para los filtros seleccionados
        </td></tr>`;
      return;
    }

    tbody.innerHTML = rows.map(row => {
      const calClass = Utils.ratingClass(row.cal);
      const calText = row.cal === null ? '—' : row.cal.toFixed(2);
      const isActive = S.crossFilter
        && S.crossFilter.type === 'modelo'
        && S.crossFilter.value === row.modelo;
      return `
        <tr data-modelo="${row.modelo}" class="${isActive ? 'active' : ''}">
          <td class="modelo">${row.modelo}</td>
          <td class="num">${Utils.fmtNum(row.unidades)}</td>
          <td class="num">${Utils.fmtMXN(row.ingresos)}</td>
          <td class="num">$${Math.round(row.ticket).toLocaleString('en-US')}</td>
          <td class="num">${row.cal !== null
            ? `<span class="rating-pill ${calClass}">★ ${calText}</span>`
            : '—'}</td>
        </tr>`;
    }).join('');

    // Bind click → cross-filter
    tbody.querySelectorAll('tr[data-modelo]').forEach(tr => {
      tr.addEventListener('click', () => {
        AppState.toggleCrossFilter('modelo', tr.dataset.modelo);
      });
    });
  }

  window.Table = { init, update };
})();
