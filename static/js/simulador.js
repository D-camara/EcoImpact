/**
 * JavaScript para o Simulador de Impacto Econômico COP-30
 * Separado do template Django para evitar conflitos de sintaxe
 */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('simulationForm');
    
    if (!form) {
        console.warn('Formulário de simulação não encontrado');
        return;
    }

    // Função para alternar seleção de cidade
    window.toggleCity = function(cityCard) {
        const checkbox = cityCard.querySelector('input[type="checkbox"]');
        if (!checkbox) return;
        
        const isChecked = checkbox.checked;
        checkbox.checked = !isChecked;
        
        if (checkbox.checked) {
            cityCard.classList.add('selected');
        } else {
            cityCard.classList.remove('selected');
        }
        
        // Trigger change event for form validation
        checkbox.dispatchEvent(new Event('change'));
    };
    
    // Inicializar estado dos cartões baseado nos checkboxes
    const cityCards = document.querySelectorAll('.city-card');
    cityCards.forEach(card => {
        const checkbox = card.querySelector('input[type="checkbox"]');
        if (checkbox && checkbox.checked) {
            card.classList.add('selected');
        }
    });
    
    // Prevenir valores negativos nos inputs numéricos
    const inputs = form.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.value < 0) {
                this.value = Math.abs(this.value);
            }
        });
    });
    
    // Feedback visual no submit
    form.addEventListener('submit', function() {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Calculando...';
            submitBtn.disabled = true;
        }
    });
    
    // Validação adicional para cidades
    form.addEventListener('submit', function(e) {
        const checkedCities = document.querySelectorAll('input[name="cidades_selecionadas"]:checked');
        
        if (checkedCities.length === 0) {
            e.preventDefault();
            alert('Por favor, selecione pelo menos uma cidade para análise.');
            return false;
        }
    });
    
    // Inicializar gráfico se houver dados
    initializeChart();
});

/**
 * Inicializa os gráficos simplificados
 */
function initializeChart() {
    console.log('🚀 Inicializando gráficos...');
    
    // Verificar se os elementos existem
    const economicElement = document.getElementById('economicChart');
    const environmentElement = document.getElementById('environmentChart');
    
    console.log('Elementos encontrados:', {
        economicChart: economicElement ? 'OK' : 'ERRO',
        environmentChart: environmentElement ? 'OK' : 'ERRO'
    });
    
    // Buscar dados do template via window
    const impactoTotal = window.impactoTotal || 0;
    const aguaTotal = window.aguaTotal || 0;
    const lixoTotal = window.lixoTotal || 0;
    
    console.log('📊 Dados encontrados:', { impactoTotal, aguaTotal, lixoTotal });
    
    // Verificar se Chart.js está carregado
    console.log('Chart.js disponível:', typeof Chart !== 'undefined' ? 'OK' : 'ERRO');
    
    if (impactoTotal === 0 && aguaTotal === 0 && lixoTotal === 0) {
        console.warn('⚠️ Nenhum dado disponível para gráficos');
        return;
    }
    
    if (!economicElement || !environmentElement) {
        console.error('❌ Elementos canvas não encontrados');
        return;
    }
    
    try {
        console.log('🎨 Criando gráfico econômico...');
        // Gráfico econômico (barras verticais)
        createEconomicChart(impactoTotal);
        
        console.log('🌿 Criando gráfico ambiental...');
        // Gráfico ambiental (barras horizontais)
        createEnvironmentalChart(aguaTotal, lixoTotal);
        
        console.log('✅ Gráficos inicializados com sucesso!');
        
    } catch (error) {
        console.error('❌ Erro ao criar gráficos:', error);
    }
}

/**
 * Cria gráfico econômico (barras verticais)
 */
function createEconomicChart(impactoTotal) {
    const ctx = document.getElementById('economicChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Impacto Econômico'],
            datasets: [{
                data: [impactoTotal],
                backgroundColor: ['#28a745'],
                borderColor: ['#1e7e34'],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function() {
                            return `R$ ${impactoTotal.toLocaleString('pt-BR')}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return 'R$ ' + (value / 1000000).toFixed(0) + 'M';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Cria gráfico ambiental (barras horizontais)
 */
function createEnvironmentalChart(aguaTotal, lixoTotal) {
    const ctx = document.getElementById('environmentChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Consumo de Água', 'Produção de Lixo'],
            datasets: [{
                data: [aguaTotal, lixoTotal * 1000], // Converter lixo para kg
                backgroundColor: ['#007bff', '#ffc107'],
                borderColor: ['#0056b3', '#e0a800'],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y', // Barras horizontais
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label;
                            if (label.includes('Água')) {
                                return `Água: ${aguaTotal.toLocaleString('pt-BR')} m³`;
                            } else {
                                return `Lixo: ${lixoTotal.toLocaleString('pt-BR')} toneladas`;
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000) {
                                return (value / 1000).toFixed(0) + 'k';
                            }
                            return value;
                        }
                    }
                }
            }
        }
    });
}

// Funções de gráficos removidas - usando apenas createEconomicChart e createEnvironmentalChart

/**
 * Cria o gráfico de pizza com os impactos (função mantida para compatibilidade)
 * @param {number} impactoTotal - Valor do impacto econômico
 * @param {number} aguaTotal - Volume de água consumida em m³
 * @param {number} lixoTotal - Produção de lixo em toneladas
 */
function createImpactChart(impactoTotal, aguaTotal, lixoTotal) {
    // Redirecionar para a nova implementação
    createNormalizedComparisonChart(impactoTotal, aguaTotal, lixoTotal);
}

/**
 * Atualiza o contador de cidades selecionadas (para futura funcionalidade)
 */
function updateCityCount() {
    const checkedCities = document.querySelectorAll('input[name="cidades_selecionadas"]:checked');
    const countElement = document.querySelector('.selected-count');
    
    if (countElement) {
        countElement.textContent = `${checkedCities.length} selecionada(s)`;
        countElement.style.display = checkedCities.length > 0 ? 'inline-block' : 'none';
    }
}

/**
 * Cria gráfico alternativo com valores convertidos para equivalência monetária
 */
function createMonetaryEquivalentChart(impactoTotal, aguaTotal, lixoTotal) {
    const ctx = document.getElementById('alternativeChart');
    if (!ctx || typeof Chart === 'undefined') return;
    
    // Converter água e lixo para valores monetários equivalentes aproximados
    const custoAguaM3 = 5.00; // R$ 5,00 por m³ (custo estimado tratamento)
    const custoLixoTon = 300.00; // R$ 300,00 por tonelada (custo gestão de resíduos)
    
    const valorAguaMonetario = aguaTotal * custoAguaM3;
    const valorLixoMonetario = lixoTotal * custoLixoTon;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: [
                'Impacto Econômico Direto',
                'Custo de Tratamento de Água',
                'Custo de Gestão de Resíduos'
            ],
            datasets: [{
                data: [impactoTotal, valorAguaMonetario, valorLixoMonetario],
                backgroundColor: ['#28a745', '#007bff', '#ffc107'],
                borderColor: ['#1e7e34', '#0056b3', '#e0a800'],
                borderWidth: 2,
                hoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    callbacks: {
                        label: function(context) {
                            const label = context.label;
                            const value = context.parsed;
                            
                            if (label.includes('Econômico')) {
                                return `${label}: R$ ${value.toLocaleString('pt-BR')}`;
                            } else if (label.includes('Água')) {
                                return `${label}: R$ ${value.toLocaleString('pt-BR')} (${aguaTotal.toLocaleString('pt-BR')} m³)`;
                            } else {
                                return `${label}: R$ ${value.toLocaleString('pt-BR')} (${lixoTotal.toLocaleString('pt-BR')} ton)`;
                            }
                        },
                        afterLabel: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${percentage}% do custo total`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 1000
            }
        }
    });
}

// Exportar funções para uso global se necessário
window.SimuladorApp = {
    toggleCity: window.toggleCity,
    createImpactChart,
    updateCityCount
};
