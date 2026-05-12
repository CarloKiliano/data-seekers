/**
 * utils.js
 * --------
 * Helpers puros (sin estado) reusados en todos los módulos.
 * Expone: window.Utils
 */
(function () {
  'use strict';

  /**
   * Formato monetario MXN con sufijo (B/M/K).
   * @param {number} v
   * @returns {string} ej: "$3.26B", "$1.5M", "$2,500"
   */
  function fmtMXN(v) {
    if (v >= 1e9) return '$' + (v / 1e9).toFixed(2) + 'B';
    if (v >= 1e6) return '$' + (v / 1e6).toFixed(1) + 'M';
    if (v >= 1e3) return '$' + (v / 1e3).toFixed(1) + 'K';
    return '$' + Math.round(v).toLocaleString('en-US');
  }

  /**
   * Formato numérico genérico con sufijo.
   * @param {number} v
   * @returns {string} ej: "2.79M", "150.0K", "1,234"
   */
  function fmtNum(v) {
    if (v >= 1e6) return (v / 1e6).toFixed(2) + 'M';
    if (v >= 1e3) return (v / 1e3).toFixed(1) + 'K';
    return Math.round(v).toLocaleString('en-US');
  }

  /**
   * Crea un gradiente lineal vertical de Chart.js.
   */
  function makeVerticalGradient(ctx, area, top, bottom) {
    const g = ctx.createLinearGradient(0, area.top, 0, area.bottom);
    g.addColorStop(0, top);
    g.addColorStop(1, bottom);
    return g;
  }

  /**
   * Mapeo entre códigos cortos usados en datos y nombres oficiales
   * del GeoJSON de México (PhantomInsights).
   * Si tu GeoJSON usa otros nombres, ajusta aquí.
   */
  const ESTADO_MAP = {
    'CDMX':       'Ciudad de México',
    'EdoMex':     'México',
    'Nuevo':      'Nuevo León',
    'Quintana':   'Quintana Roo',
    'Chihuahua':  'Chihuahua',
    'Coahuila':   'Coahuila de Zaragoza',
    'Hidalgo':    'Hidalgo',
    'Michoacan':  'Michoacán de Ocampo',
    'Morelos':    'Morelos',
    'Puebla':     'Puebla',
  };
  const REV_ESTADO_MAP = Object.fromEntries(
    Object.entries(ESTADO_MAP).map(([k, v]) => [v, k])
  );

  /**
   * Devuelve el código corto (ej. "CDMX") a partir del nombre oficial
   * que viene en el GeoJSON. Tolerante a variaciones menores.
   */
  function nameToCode(name) {
    if (!name) return null;
    if (REV_ESTADO_MAP[name]) return REV_ESTADO_MAP[name];
    // Fallback: comparación case-insensitive y por prefijo
    const lc = name.toLowerCase().trim();
    for (const [oficial, code] of Object.entries(REV_ESTADO_MAP)) {
      if (oficial.toLowerCase() === lc) return code;
    }
    // Mapeo flexible para variaciones comunes del nombre
    const aliases = {
      'ciudad de méxico': 'CDMX',
      'ciudad de mexico': 'CDMX',
      'distrito federal': 'CDMX',
      'estado de méxico': 'EdoMex',
      'estado de mexico': 'EdoMex',
      'méxico': 'EdoMex',
      'mexico': 'EdoMex',
      'nuevo león': 'Nuevo',
      'nuevo leon': 'Nuevo',
      'quintana roo': 'Quintana',
      'coahuila': 'Coahuila',
      'coahuila de zaragoza': 'Coahuila',
      'michoacán': 'Michoacan',
      'michoacan': 'Michoacan',
      'michoacán de ocampo': 'Michoacan',
    };
    return aliases[lc] || null;
  }

  /**
   * Etiquetas base de la tabla (para reset del header al ordenar).
   */
  const TABLE_LABELS = {
    modelo: 'Modelo',
    unidades: 'Unidades',
    ingresos: 'Ingresos',
    ticket: 'Ticket Prom.',
    cal: 'Calificación',
  };

  /**
   * Determina la clase CSS para el pill de calificación.
   */
  function ratingClass(cal) {
    if (cal === null || cal === undefined) return '';
    if (cal >= 4) return 'rating-high';
    if (cal >= 3) return 'rating-mid';
    return 'rating-low';
  }

  // Exponer en window.Utils
  window.Utils = {
    fmtMXN,
    fmtNum,
    makeVerticalGradient,
    ESTADO_MAP,
    REV_ESTADO_MAP,
    nameToCode,
    TABLE_LABELS,
    ratingClass,
  };
})();
