/**
 * charts.js
 * ---------
 * Gestiona las 5 gráficas con Chart.js + click handlers para cross-filtering.
 *
 * Expone: window.Charts
 */
(function () {
  'use strict';

  const charts = {};
  const gridColor = 'rgba(255,255,255,0.04)';
  const axisColor = '#6b6b80';

  /**
   * Configura defaults globales de Chart.js (tema oscuro).
   */
  function setDefaults() {
    if (!window.Chart) return;
    Chart.defaults.font.family = "'Inter Tight', sans-serif";
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#a8a8b8';
    Chart.defaults.plugins.legend.labels.color = '#a8a8b8';
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(10, 10, 20, 0.95)';
    Chart.defaults.plugins.tooltip.titleColor = '#f5f5fa';
    Chart.defaults.plugins.tooltip.bodyColor = '#a8a8b8';
    Chart.defaults.plugins.tooltip.borderColor = 'rgba(255,255,255,0.1)';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.titleFont = {
      family: "'JetBrains Mono', monospace", size: 10, weight: '600',
    };
    Chart.defaults.plugins.tooltip.bodyFont = {
      family: "'Inter Tight', sans-serif", size: 12,
    };
  }

  /**
   * Inicializa todas las gráficas (sin datos aún).
   */
  function init() {
    if (!window.Chart) {
      console.warn('Chart.js no cargado — gráficas deshabilitadas');
      return;
    }
    setDefaults();

    // 1. Tendencia mensual (línea con área)
    charts.trend = new Chart(document.getElementById('ch-trend'), {
      type: 'line',
      data: { labels: [], datasets: [{
        label: 'Ingresos',
        data: [],
        borderColor: '#ff3358',
        borderWidth: 2.5,
        pointBackgroundColor: '#ff3358',
        pointBorderColor: '#0a0a14',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 8,
        tension: 0.35,
        fill: true,
        backgroundColor: ctx => {
          const { ctx: c, chartArea } = ctx.chart;
          if (!chartArea) return 'rgba(255,51,88,0.1)';
          return Utils.makeVerticalGradient(c, chartArea, 'rgba(255,51,88,0.35)', 'rgba(255,51,88,0)');
        },
      }]},
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { intersect: false, mode: 'index' },
        onClick: (e, els) => {
          if (els && els.length) {
            const mes = charts.trend.data.labels[els[0].index];
            AppState.toggleCrossFilter('mes', mes);
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: items => '📅 ' + items[0].label,
              label: ctx => '💰 Ingresos: ' + Utils.fmtMXN(ctx.parsed.y),
              afterBody: () => ['', '↪ Click para filtrar todo el dashboard'],
            },
          },
        },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: axisColor, maxRotation: 0, autoSkipPadding: 20 } },
          y: { grid: { color: gridColor }, ticks: { color: axisColor, callback: v => Utils.fmtMXN(v) } },
        },
      },
    });

    // 2. Ranking de modelos (barras horizontales)
    charts.modelos = new Chart(document.getElementById('ch-modelos'), {
      type: 'bar',
      data: { labels: [], datasets: [{
        label: 'Ingreso',
        data: [],
        backgroundColor: ctx => {
          const { ctx: c, chartArea } = ctx.chart;
          if (!chartArea) return '#ff3358';
          const g = c.createLinearGradient(chartArea.left, 0, chartArea.right, 0);
          g.addColorStop(0, '#ff3358');
          g.addColorStop(1, '#ffa552');
          return g;
        },
        hoverBackgroundColor: '#ff6b9d',
        borderRadius: 6,
        borderSkipped: false,
      }]},
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        onClick: (e, els) => {
          if (els && els.length) {
            const modelo = charts.modelos.data.labels[els[0].index];
            AppState.toggleCrossFilter('modelo', modelo);
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: items => '👟 ' + items[0].label,
              label: ctx => '💰 ' + Utils.fmtMXN(ctx.parsed.x),
              afterBody: () => ['', '↪ Click para filtrar'],
            },
          },
        },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: axisColor, callback: v => Utils.fmtMXN(v) } },
          y: { grid: { display: false }, ticks: { color: axisColor } },
        },
      },
    });

    // 3. Penetración regional (barras verticales por estado)
    charts.estados = new Chart(document.getElementById('ch-estados'), {
      type: 'bar',
      data: { labels: [], datasets: [{
        label: 'Unidades',
        data: [],
        backgroundColor: ctx => {
          const { ctx: c, chartArea } = ctx.chart;
          if (!chartArea) return '#4dd0e1';
          const g = c.createLinearGradient(0, chartArea.bottom, 0, chartArea.top);
          g.addColorStop(0, '#4dd0e1');
          g.addColorStop(1, '#a78bfa');
          return g;
        },
        hoverBackgroundColor: '#ffa552',
        borderRadius: 6,
        borderSkipped: false,
      }]},
      options: {
        responsive: true, maintainAspectRatio: false,
        onClick: (e, els) => {
          if (els && els.length) {
            const estado = charts.estados.data.labels[els[0].index];
            AppState.toggleCrossFilter('estado', estado);
          }
        },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: items => '🗺️ ' + items[0].label,
              label: ctx => '📦 ' + Utils.fmtNum(ctx.parsed.y) + ' unidades',
              afterBody: () => ['', '↪ Click para filtrar'],
            },
          },
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: axisColor, maxRotation: 45, minRotation: 45 } },
          y: { grid: { color: gridColor }, ticks: { color: axisColor, callback: v => Utils.fmtNum(v) } },
        },
      },
    });

    // 4. Demanda por talla (histograma 2-color)
    charts.tallas = new Chart(document.getElementById('ch-tallas'), {
      type: 'bar',
      data: { labels: [], datasets: [{
        label: 'Unidades',
        data: [],
        backgroundColor: [],
        borderRadius: 4,
      }]},
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: items => '👣 Talla ' + items[0].label,
              label: ctx => '📦 ' + Utils.fmtNum(ctx.parsed.y) + ' unidades',
            },
          },
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: axisColor } },
          y: { grid: { color: gridColor }, ticks: { color: axisColor, callback: v => Utils.fmtNum(v) } },
        },
      },
    });

    // 5. Sentimiento mensual
    charts.sentiment = new Chart(document.getElementById('ch-sentiment'), {
      type: 'line',
      data: { labels: [], datasets: [{
        label: 'Calificación',
        data: [],
        borderColor: '#ffa552',
        borderWidth: 2.5,
        pointBackgroundColor: '#ffa552',
        pointBorderColor: '#0a0a14',
        pointBorderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 7,
        tension: 0.4,
        fill: true,
        backgroundColor: ctx => {
          const { ctx: c, chartArea } = ctx.chart;
          if (!chartArea) return 'rgba(255,165,82,0.1)';
          return Utils.makeVerticalGradient(c, chartArea, 'rgba(255,165,82,0.35)', 'rgba(255,165,82,0)');
        },
      }]},
      options: {
        responsive: true, maintainAspectRatio: false,
        interaction: { intersect: false, mode: 'index' },
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              title: items => '📅 ' + items[0].label,
              label: ctx => '⭐ ' + ctx.parsed.y.toFixed(2) + ' / 5',
            },
          },
        },
        scales: {
          x: { grid: { color: gridColor }, ticks: { color: axisColor, maxRotation: 0, autoSkipPadding: 20 } },
          y: { min: 1, max: 5, grid: { color: gridColor }, ticks: { color: axisColor, stepSize: 1 } },
        },
      },
    });
  }

  /**
   * Refresca todas las gráficas con datos filtrados.
   * Llamado por main.js cuando el estado cambia.
   */
  function update(ventas, resenas) {
    if (!charts.trend) return; // Chart.js no cargó
    const scale = AppState.state.meta.scale_v;

    // Tendencia
    const byMonth = {};
    ventas.forEach(x => {
      const ym = x.fecha.slice(0, 7);
      byMonth[ym] = (byMonth[ym] || 0) + x.ingreso * scale;
    });
    const months = Object.keys(byMonth).sort();
    charts.trend.data.labels = months;
    charts.trend.data.datasets[0].data = months.map(m => byMonth[m]);
    charts.trend.update();

    // Top modelos
    const byModelo = {};
    ventas.forEach(x => { byModelo[x.modelo] = (byModelo[x.modelo] || 0) + x.ingreso * scale; });
    const sortedM = Object.entries(byModelo).sort((a, b) => b[1] - a[1]).slice(0, 12);
    charts.modelos.data.labels = sortedM.map(x => x[0]);
    charts.modelos.data.datasets[0].data = sortedM.map(x => x[1]);
    charts.modelos.update();

    // Estados
    const byEstado = {};
    ventas.forEach(x => { byEstado[x.estado] = (byEstado[x.estado] || 0) + x.cantidad * scale; });
    const sortedE = Object.entries(byEstado).sort((a, b) => b[1] - a[1]);
    charts.estados.data.labels = sortedE.map(x => x[0]);
    charts.estados.data.datasets[0].data = sortedE.map(x => x[1]);
    charts.estados.update();

    // Tallas (con colores por segmento)
    const byTalla = {};
    ventas.forEach(x => { byTalla[x.talla] = (byTalla[x.talla] || 0) + x.cantidad * scale; });
    const tallas = Object.keys(byTalla).map(Number).sort((a, b) => a - b);
    charts.tallas.data.labels = tallas;
    charts.tallas.data.datasets[0].data = tallas.map(t => byTalla[t]);
    charts.tallas.data.datasets[0].backgroundColor = tallas.map(t => t <= 21 ? '#4dd0e1' : '#ff6b9d');
    charts.tallas.update();

    // Sentimiento
    const byMonthRes = {};
    resenas.forEach(x => {
      const ym = x.fecha.slice(0, 7);
      if (!byMonthRes[ym]) byMonthRes[ym] = { sum: 0, n: 0 };
      byMonthRes[ym].sum += x.calificacion;
      byMonthRes[ym].n += 1;
    });
    const monthsR = Object.keys(byMonthRes).sort();
    charts.sentiment.data.labels = monthsR;
    charts.sentiment.data.datasets[0].data = monthsR.map(m => byMonthRes[m].sum / byMonthRes[m].n);
    charts.sentiment.update();
  }

  window.Charts = { init, update };
})();
