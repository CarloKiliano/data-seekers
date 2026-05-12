/**
 * filters.js
 * ----------
 * Maneja:
 *   - Inputs de fecha (rango temporal)
 *   - Multiselects de Estados y Modelos
 *   - Botón Reset
 *   - Chip de cross-filter activo
 *
 * Expone: window.Filters
 */
(function () {
  'use strict';

  /**
   * Construye un multi-select estilizado.
   * @param {object} cfg - { btnId, panelId, items, stateKey, labelSingular, labelPlural }
   * @returns {object} - { render(), updateBtnLabel() } API pública
   */
  function buildMultiSelect(cfg) {
    const btn = document.getElementById(cfg.btnId);
    const panel = document.getElementById(cfg.panelId);
    const S = AppState.state;

    function render() {
      const set = S[cfg.stateKey];
      panel.innerHTML = `
        <label class="multi-option">
          <input type="checkbox" data-all="1" ${set.size === cfg.items.length ? 'checked' : ''}>
          <span>Todos</span>
        </label>
      ` + cfg.items.map(v => `
        <label class="multi-option">
          <input type="checkbox" value="${v}" ${set.has(v) ? 'checked' : ''}>
          <span>${v}</span>
        </label>
      `).join('');
      updateBtnLabel();
    }

    function updateBtnLabel() {
      const set = S[cfg.stateKey];
      if (set.size === cfg.items.length) {
        btn.textContent = `Todos los ${cfg.labelPlural}`;
      } else if (set.size === 0) {
        btn.textContent = `Ningún ${cfg.labelSingular}`;
      } else if (set.size === 1) {
        btn.textContent = [...set][0];
      } else {
        btn.textContent = `${set.size} ${cfg.labelPlural}`;
      }
    }

    btn.addEventListener('click', e => {
      e.stopPropagation();
      // Cerrar otros paneles abiertos
      document.querySelectorAll('.multi-select-panel').forEach(p => {
        if (p !== panel) p.classList.remove('open');
      });
      panel.classList.toggle('open');
    });

    // Cerrar al click fuera
    document.addEventListener('click', e => {
      if (!panel.contains(e.target) && e.target !== btn) panel.classList.remove('open');
    });

    panel.addEventListener('change', e => {
      const target = e.target;
      const set = S[cfg.stateKey];
      if (target.dataset.all) {
        // Checkbox "Todos"
        const checked = target.checked;
        panel.querySelectorAll('input[type=checkbox]:not([data-all])').forEach(cb => cb.checked = checked);
        set.clear();
        if (checked) cfg.items.forEach(v => set.add(v));
      } else {
        if (target.checked) set.add(target.value);
        else set.delete(target.value);
        // Sincronizar "Todos"
        const allCb = panel.querySelector('input[data-all]');
        allCb.checked = set.size === cfg.items.length;
      }
      updateBtnLabel();
      AppState.notify();
    });

    return { render, updateBtnLabel };
  }

  let estadosCtrl = null;
  let modelosCtrl = null;

  /**
   * Inicializa filtros. Debe llamarse después de AppState.init().
   */
  function init() {
    const S = AppState.state;

    // Inputs de fecha
    const dateFromEl = document.getElementById('f-date-from');
    const dateToEl = document.getElementById('f-date-to');
    dateFromEl.min = S.meta.fecha_min;
    dateFromEl.max = S.meta.fecha_max;
    dateFromEl.value = S.dateFrom;
    dateToEl.min = S.meta.fecha_min;
    dateToEl.max = S.meta.fecha_max;
    dateToEl.value = S.dateTo;

    dateFromEl.addEventListener('change', e => {
      S.dateFrom = e.target.value;
      AppState.notify();
    });
    dateToEl.addEventListener('change', e => {
      S.dateTo = e.target.value;
      AppState.notify();
    });

    // Multi-selects
    estadosCtrl = buildMultiSelect({
      btnId: 'btn-estados',
      panelId: 'panel-estados',
      items: S.estados,
      stateKey: 'estadosSel',
      labelSingular: 'estado',
      labelPlural: 'estados',
    });
    modelosCtrl = buildMultiSelect({
      btnId: 'btn-modelos',
      panelId: 'panel-modelos',
      items: S.modelos,
      stateKey: 'modelosSel',
      labelSingular: 'modelo',
      labelPlural: 'modelos',
    });
    estadosCtrl.render();
    modelosCtrl.render();

    // Reset
    document.getElementById('btn-reset').addEventListener('click', () => {
      AppState.reset();
      dateFromEl.value = S.dateFrom;
      dateToEl.value = S.dateTo;
      estadosCtrl.render();
      modelosCtrl.render();
      AppState.notify();
    });

    // Chip cross-filter
    document.getElementById('active-chip-clear').addEventListener('click', () => {
      AppState.clearCrossFilter();
    });

    // Suscripción al estado: actualiza el chip cuando cambia
    AppState.onChange(updateChip);
  }

  /**
   * Actualiza la visibilidad y contenido del chip de cross-filter.
   */
  function updateChip() {
    const chip = document.getElementById('active-chip');
    const text = document.getElementById('active-chip-text');
    const cf = AppState.state.crossFilter;
    if (cf) {
      text.innerHTML = `↪ Filtrado por <strong>${cf.type}: ${cf.value}</strong> — click cualquier gráfica para cambiar`;
      chip.classList.add('show');
    } else {
      chip.classList.remove('show');
    }
  }

  window.Filters = { init };
})();
