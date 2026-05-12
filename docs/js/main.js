/**
 * main.js
 * -------
 * Entry point. Carga los datos, inicializa todos los módulos,
 * y los conecta al sistema de notificación del AppState.
 */
(function () {
  'use strict';

  /**
   * Lifecycle:
   *   1. Cargar JSON de datos
   *   2. Inicializar AppState
   *   3. Inicializar UI (filtros, charts, mapa, tabla)
   *   4. Suscribir todos los módulos a cambios de estado
   *   5. Primer render
   */
  async function start() {
    try {
      const res = await fetch('data/panam_data.json');
      if (!res.ok) throw new Error('No se pudo cargar data/panam_data.json');
      const data = await res.json();

      AppState.init(data);
      KPIs.renderMeta();

      // Inicialización de módulos

      Filters.init();
      try { Charts.init(); } catch (e) { console.warn('Charts init falló:', e); }
      Table.init();

      // Suscribir el refresh global. Cada que algo cambia, todo se actualiza.
      AppState.onChange(refresh);

      // Primer render
      refresh();
    } catch (err) {
      console.error('Error fatal al cargar dashboard:', err);
      document.body.innerHTML = `
        <div style="padding: 60px; text-align: center; font-family: system-ui; color: #f5f5fa;">
          <h1 style="color: #ff3358;">⚠️ Error al cargar el dashboard</h1>
          <p style="margin-top: 16px; opacity: 0.7;">${err.message}</p>
          <p style="margin-top: 24px; font-size: 0.85rem; opacity: 0.5;">
            Verifica que estés sirviendo el archivo desde un servidor web (no abriéndolo con file://).
            <br>
            Usa: <code style="background: #11111e; padding: 4px 8px; border-radius: 4px;">python3 -m http.server 8000</code>
          </p>
        </div>`;
    }
  }

  /**
   * Refresh global: re-calcula filtros y actualiza todos los módulos.
   */
  function refresh() {
    const ventas = AppState.filteredVentas();
    const resenas = AppState.filteredResenas();

    KPIs.update(ventas, resenas);
    Charts.update(ventas, resenas);
    Table.update(ventas, resenas);
  }

  // Arrancar cuando el DOM esté listo
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
