// EcoImpact Home Script
(function () {
  const turistas = document.getElementById('turistas');
  const gasto = document.getElementById('gasto');
  const dias = document.getElementById('dias');
  const turistasValue = document.getElementById('turistasValue');
  const gastoValue = document.getElementById('gastoValue');
  const diasValue = document.getElementById('diasValue');
  const cidadesWrap = document.getElementById('cidades');
  const totalEl = document.getElementById('total');
  const aggDiaEl = document.getElementById('aggDia');
  const cidadesSelEl = document.getElementById('cidadesSel');
  const resetBtn = document.getElementById('reset');
  const simBtn = document.getElementById('simular');
  const ctx = document.getElementById('chart');

  const formatBRL = (v) => v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 });
  const formatInt = (v) => v.toLocaleString('pt-BR');

  let chart;

  function selectedCities() {
    return Array.from(cidadesWrap.querySelectorAll('.chip.selected')).map(ch => ({
      name: ch.dataset.name,
      mult: parseFloat(ch.dataset.multiplier)
    }));
  }

  function fatorCidades() {
    const sel = selectedCities();
    if (sel.length === 0) return 1;
    const media = sel.reduce((acc, c) => acc + c.mult, 0) / sel.length;
    return media;
  }

  function calc() {
    const n = parseInt(turistas.value, 10);
    const g = parseFloat(gasto.value);
    const d = parseInt(dias.value, 10);
    const f = fatorCidades();
    const aggDia = n * g * f;
    const total = aggDia * d;
    return { n, g, d, f, aggDia, total };
  }

  function updateLabels() {
    turistasValue.textContent = formatInt(parseInt(turistas.value, 10));
    gastoValue.textContent = formatInt(parseInt(gasto.value, 10));
    diasValue.textContent = dias.value;
    const selNames = selectedCities().map(c => c.name);
    cidadesSelEl.textContent = selNames.length ? selNames.join(', ') : '—';
  }

  function renderChartSeries(result) {
    const { d, aggDia } = result;
    const labels = Array.from({ length: d }, (_, i) => `Dia ${i + 1}`);
    const data = Array.from({ length: d }, () => Math.round(aggDia));

    const color = 'rgba(29, 209, 161, 0.9)';
    const bg = 'rgba(29, 209, 161, 0.15)';

    if (!chart) {
      chart = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Gasto agregado por dia',
            data,
            borderColor: color,
            backgroundColor: bg,
            fill: true,
            tension: 0.25,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { labels: { color: '#dfe9f0' } },
            tooltip: {
              callbacks: {
                label: (ctx) => formatBRL(ctx.parsed.y)
              }
            }
          },
          scales: {
            x: {
              ticks: { color: '#9fb3c8' },
              grid: { color: 'rgba(255,255,255,0.06)' }
            },
            y: {
              ticks: {
                color: '#9fb3c8',
                callback: (v) => 'R$ ' + Number(v).toLocaleString('pt-BR')
              },
              grid: { color: 'rgba(255,255,255,0.06)' }
            }
          }
        }
      });
    } else {
      chart.data.labels = labels;
      chart.data.datasets[0].data = data;
      chart.update();
    }
  }

  function render() {
    const result = calc();
    totalEl.textContent = formatBRL(result.total);
    aggDiaEl.textContent = formatBRL(result.aggDia);
    renderChartSeries(result);
  }

  // Events
  [turistas, gasto, dias].forEach(inp => inp.addEventListener('input', () => {
    updateLabels();
    render();
  }));

  cidadesWrap.addEventListener('click', (e) => {
    const b = e.target.closest('.chip');
    if (!b) return;
    b.classList.toggle('selected');
    updateLabels();
    render();
  });

  resetBtn.addEventListener('click', () => {
    turistas.value = 50000;
    gasto.value = 350;
    dias.value = 5;
    Array.from(cidadesWrap.querySelectorAll('.chip')).forEach((c, i) => {
      c.classList.toggle('selected', i === 0);
    });
    updateLabels();
    render();
  });

  simBtn.addEventListener('click', () => {
    // just a subtle focus/scroll behavior
    document.querySelector('.results').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });

  // initial
  updateLabels();
  render();
})();
