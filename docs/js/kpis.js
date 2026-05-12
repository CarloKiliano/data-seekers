/**
 * kpis.js
 * -------
 * Calcula y renderiza los 4 KPIs ejecutivos.
 *
 * Expone: window.KPIs
 */
(function () {
  'use strict';

  function update(ventas, resenas) {
    const S = AppState.state;
    const scale = S.meta.scale_v;

    const ingresoTotal = ventas.reduce((s, x) => s + x.ingreso, 0);
    const unidades = ventas.reduce((s, x) => s + x.cantidad, 0);
    const ticket = ventas.length ? ingresoTotal / ventas.length : 0;
    const calif = resenas.length
      ? resenas.reduce((s, x) => s + x.calificacion, 0) / resenas.length
      : 0;

    // Escalar al universo real (porque trabajamos con sample)
    const ingresoScaled = ingresoTotal * scale;
    const unidadesScaled = unidades * scale;

    // Render principal
    document.getElementById('kpi-ingresos').textContent = Utils.fmtMXN(ingresoScaled);
    document.getElementById('kpi-unidades').textContent = Utils.fmtNum(unidadesScaled);
    document.getElementById('kpi-ticket').textContent =
      '$' + Math.round(ticket).toLocaleString('en-US');
    document.getElementById('kpi-calif').textContent = calif
      ? calif.toFixed(2) + ' /5'
      : '—';

    // Trends (sub-textos)
    document.getElementById('kpi-ingresos-trend').textContent =
      `${ventas.length.toLocaleString('en-US')} transacciones`;

    const totalDays = (new Date(S.dateTo) - new Date(S.dateFrom)) / (1000 * 60 * 60 * 24);
    document.getElementById('kpi-unidades-trend').textContent =
      totalDays > 0 && unidadesScaled > 0
        ? `~${(unidadesScaled / totalDays).toFixed(0)} unidades/día`
        : '—';

    document.getElementById('kpi-ticket-trend').textContent = ventas.length
      ? `min $${Math.round(Math.min(...ventas.map(x => x.ingreso)))} · max $${Math.round(Math.max(...ventas.map(x => x.ingreso)))}`
      : '—';

    const calTrend = document.getElementById('kpi-calif-trend');
    if (calif >= 4) {
      calTrend.textContent = '↑ Excelente';
      calTrend.className = 'kpi-trend up';
    } else if (calif >= 3) {
      calTrend.textContent = '→ Sobre el neutro';
      calTrend.className = 'kpi-trend';
    } else if (calif > 0) {
      calTrend.textContent = '↓ Bajo el neutro';
      calTrend.className = 'kpi-trend down';
    } else {
      calTrend.textContent = '—';
      calTrend.className = 'kpi-trend';
    }
  }

  /**
   * Renderiza los metadatos del header (LIVE indicator + records).
   */
  function renderMeta() {
    const meta = AppState.state.meta;
    document.getElementById('meta-records').innerHTML =
      `<strong>${meta.total_ventas.toLocaleString('en-US')}</strong> ventas · ` +
      `<strong>${meta.total_resenas.toLocaleString('en-US')}</strong> reseñas`;
    document.getElementById('meta-range').textContent =
      `${meta.fecha_min} → ${meta.fecha_max}`;
  }

  window.KPIs = { update, renderMeta };
})();
