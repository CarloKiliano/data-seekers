/**
 * state.js
 * --------
 * Estado central del dashboard. Patrón pub-sub simple:
 * los módulos se suscriben a `onChange` y reciben el estado actualizado.
 *
 * Expone: window.AppState
 */
(function () {
  'use strict';

  const subscribers = [];
  const state = {
    // Datos crudos (se llenan al cargar)
    ventas: [],
    resenas: [],
    estados: [],   // lista de estados disponibles
    modelos: [],   // lista de modelos disponibles
    meta: null,

    // Filtros activos
    dateFrom: null,
    dateTo: null,
    estadosSel: new Set(),   // estados seleccionados
    modelosSel: new Set(),   // modelos seleccionados
    crossFilter: null,        // {type: 'modelo'|'estado'|'mes', value: '...'}

    // UI state
    sortBy: 'ingresos',
    sortDir: 'desc',
  };

  /**
   * Inicializa el estado con los datos cargados.
   */
  function init(data) {
    state.ventas = data.ventas;
    state.resenas = data.resenas;
    state.estados = data.estados;
    state.modelos = data.modelos;
    state.meta = data.meta;
    state.dateFrom = data.meta.fecha_min;
    state.dateTo = data.meta.fecha_max;
    state.estadosSel = new Set(data.estados);
    state.modelosSel = new Set(data.modelos);
  }

  /**
   * Suscribirse a cambios. El callback recibe el estado en cada notificación.
   */
  function onChange(fn) {
    subscribers.push(fn);
  }

  /**
   * Notifica a todos los suscriptores que el estado cambió → todos hacen su refresh.
   */
  function notify() {
    subscribers.forEach(fn => {
      try { fn(state); } catch (e) { console.error('Subscriber error:', e); }
    });
  }

  /**
   * Aplica los filtros activos al dataset de ventas.
   * @returns {Array} ventas que pasan TODOS los filtros
   */
  function filteredVentas() {
    return state.ventas.filter(v => {
      if (v.fecha < state.dateFrom || v.fecha > state.dateTo) return false;
      if (!state.estadosSel.has(v.estado)) return false;
      if (!state.modelosSel.has(v.modelo)) return false;
      if (state.crossFilter) {
        const cf = state.crossFilter;
        if (cf.type === 'modelo' && v.modelo !== cf.value) return false;
        if (cf.type === 'estado' && v.estado !== cf.value) return false;
        if (cf.type === 'mes' && !v.fecha.startsWith(cf.value)) return false;
      }
      return true;
    });
  }

  /**
   * Aplica filtros al dataset de reseñas.
   * Nota: reseñas no tienen "estado", solo filtramos por fecha, modelo y crossFilter aplicable.
   */
  function filteredResenas() {
    return state.resenas.filter(r => {
      if (r.fecha < state.dateFrom || r.fecha > state.dateTo) return false;
      if (!state.modelosSel.has(r.modelo)) return false;
      if (state.crossFilter) {
        const cf = state.crossFilter;
        if (cf.type === 'modelo' && r.modelo !== cf.value) return false;
        if (cf.type === 'mes' && !r.fecha.startsWith(cf.value)) return false;
        // Si cross-filter es por estado, no afecta reseñas (no tienen columna estado)
      }
      return true;
    });
  }

  /**
   * Resetea todos los filtros a sus valores iniciales.
   */
  function reset() {
    state.dateFrom = state.meta.fecha_min;
    state.dateTo = state.meta.fecha_max;
    state.estadosSel = new Set(state.estados);
    state.modelosSel = new Set(state.modelos);
    state.crossFilter = null;
  }

  /**
   * Toggle de cross-filter: si ya está aplicado el mismo, lo quita; si no, lo aplica.
   */
  function toggleCrossFilter(type, value) {
    if (state.crossFilter && state.crossFilter.type === type && state.crossFilter.value === value) {
      state.crossFilter = null;
    } else {
      state.crossFilter = { type, value };
    }
    notify();
  }

  function clearCrossFilter() {
    state.crossFilter = null;
    notify();
  }

  window.AppState = {
    init,
    state,
    onChange,
    notify,
    filteredVentas,
    filteredResenas,
    reset,
    toggleCrossFilter,
    clearCrossFilter,
  };
})();
