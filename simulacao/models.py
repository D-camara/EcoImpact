"""Modelos de domínio (scaffolding).

Implemente os campos que desejarem manter. Estrutura básica pronta.
"""

from __future__ import annotations

from django.db import models
from django.core.validators import EmailValidator, MinValueValidator, MaxValueValidator
from decimal import Decimal


class Cidade(models.Model):
    # Tamanhos realistas
    nome = models.CharField(max_length=120, unique=True)
    estado = models.CharField(max_length=50, default='PA')
    pais = models.CharField(max_length=50, default='Brasil')
    populacao = models.PositiveIntegerField()
    pib_per_capita = models.DecimalField(max_digits=12, decimal_places=2)
    area_km2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Campos específicos para COP 30 e sustentabilidade
    indice_sustentabilidade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Índice de sustentabilidade da cidade (0-100)"
    )
    emissao_co2_per_capita = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Emissão de CO2 per capita (toneladas/ano)"
    )
    cobertura_vegetal_pct = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentual de cobertura vegetal da cidade"
    )
    transporte_publico_sustentavel = models.BooleanField(
        default=False,
        help_text="Possui transporte público sustentável"
    )
    energia_renovavel_pct = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Percentual de energia renovável utilizada"
    )
    
    class Meta:
        ordering = ["nome"]
        verbose_name_plural = "Cidades"

    def __str__(self) -> str:
        return f"{self.nome} - {self.estado}"


class Turista(models.Model):
    nome = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, validators=[EmailValidator()])
    telefone = models.CharField(max_length=20, blank=True)
    idade = models.PositiveIntegerField(null=True, blank=True)
    cidade_origem = models.ForeignKey(
        Cidade, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="turistas_origem"
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    # Campos específicos para sustentabilidade e COP 30
    interesse_sustentabilidade = models.CharField(
        max_length=20,
        choices=[
            ('baixo', 'Baixo'),
            ('medio', 'Médio'),
            ('alto', 'Alto'),
        ],
        default='medio',
        help_text="Nível de interesse em turismo sustentável"
    )
    preferencia_transporte = models.CharField(
        max_length=30,
        choices=[
            ('publico', 'Transporte Público'),
            ('bicicleta', 'Bicicleta'),
            ('caminhada', 'Caminhada'),
            ('carro_eletrico', 'Carro Elétrico'),
            ('carro_hibrido', 'Carro Híbrido'),
            ('carro_combustivel', 'Carro a Combustível'),
        ],
        default='publico'
    )
    participante_cop30 = models.BooleanField(
        default=False,
        help_text="Está participando da COP 30"
    )
    
    class Meta:
        ordering = ["nome"]
        
    def __str__(self) -> str:
        return f"{self.nome} ({self.email})"


class Simulacao(models.Model):
    turista = models.ForeignKey(
        Turista, 
        on_delete=models.CASCADE, 
        related_name="simulacoes",
        null=True,
        blank=True
    )
    cidade = models.ForeignKey(
        Cidade, 
        on_delete=models.CASCADE, 
        related_name="simulacoes"
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_viagem = models.DateField(null=True, blank=True)
    duracao_dias = models.PositiveIntegerField(default=1)
    orcamento = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    parametros = models.JSONField(default=dict, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pendente', 'Pendente'),
            ('processando', 'Processando'),
            ('concluida', 'Concluída'),
            ('erro', 'Erro'),
        ],
        default='pendente',
        db_index=True
    )
    
    # Campo cenario com choices
    cenario = models.CharField(
        max_length=20,
        choices=[
            ('conservador', 'Conservador'),
            ('realista', 'Realista'),
            ('otimista', 'Otimista'),
        ],
        default='realista',
        help_text="Cenário de simulação"
    )

    # Campos estruturados principais da simulação econômica
    numero_turistas = models.PositiveIntegerField(default=1, help_text="Quantidade de turistas no cenário")
    gasto_medio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Gasto médio por turista por dia (R$)")
    
    # Campos específicos para impacto ambiental e COP 30
    tipo_hospedagem = models.CharField(
        max_length=30,
        choices=[
            ('hotel_sustentavel', 'Hotel Sustentável'),
            ('hotel_convencional', 'Hotel Convencional'),
            ('pousada_local', 'Pousada Local'),
            ('hostel', 'Hostel'),
            ('casa_local', 'Casa de Família Local'),
        ],
        null=True,
        blank=True
    )
    meio_transporte_principal = models.CharField(
        max_length=30,
        choices=[
            ('aviao', 'Avião'),
            ('onibus', 'Ônibus'),
            ('carro', 'Carro'),
            ('trem', 'Trem'),
            ('barco', 'Barco'),
        ],
        null=True,
        blank=True
    )
    atividades_sustentaveis = models.BooleanField(
        default=True,
        help_text="Prioriza atividades sustentáveis"
    )
    compensacao_carbono = models.BooleanField(
        default=False,
        help_text="Deseja compensar emissões de carbono"
    )
    
    class Meta:
        ordering = ["-data_criacao"]
        verbose_name = "Simulação"
        verbose_name_plural = "Simulações"

    def __str__(self) -> str:
        turista_nome = self.turista.nome if self.turista else "Anônimo"
        return f"Simulação {self.id} - {turista_nome} para {self.cidade.nome}"
    
    def save(self, *args, **kwargs):
        # Converter valores monetários para Decimal
        if self.orcamento is not None:
            self.orcamento = Decimal(str(self.orcamento))

        # Popular campos estruturados a partir de parametros (backfill transicional)
        if self.parametros:
            p = self.parametros
            # número de turistas
            if 'numero_turistas' in p and (not self.numero_turistas or self.numero_turistas == 1):
                try:
                    self.numero_turistas = int(p['numero_turistas'])
                except (ValueError, TypeError):
                    pass
            # gasto médio
            if 'gasto_medio' in p and self.gasto_medio is None:
                try:
                    self.gasto_medio = Decimal(str(p['gasto_medio']))
                except (ValueError, TypeError):
                    pass
            # cenário
            if 'cenario' in p and self.cenario == 'realista':
                c = str(p['cenario']).lower()
                if c in ['conservador', 'realista', 'otimista']:
                    self.cenario = c

        super().save(*args, **kwargs)


class Relatorio(models.Model):
    simulacao = models.OneToOneField(
        Simulacao, 
        on_delete=models.CASCADE, 
        related_name="relatorio"
    )
    resultado = models.JSONField(default=dict)
    impacto_ambiental = models.TextField(blank=True)
    recomendacoes = models.TextField(blank=True)
    pontuacao_sustentabilidade = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Pontuação de sustentabilidade (0-100)"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    # Campos específicos para COP 30 e métricas ambientais
    emissao_co2_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Emissão total de CO2 da viagem (kg)"
    )
    emissao_co2_transporte = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Emissão de CO2 do transporte (kg)"
    )
    emissao_co2_hospedagem = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Emissão de CO2 da hospedagem (kg)"
    )
    economia_local_impacto = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Impacto na economia local (R$)"
    )
    alternativas_sustentaveis = models.TextField(
        blank=True,
        help_text="Sugestões de alternativas mais sustentáveis"
    )
    metas_cop30_alinhamento = models.TextField(
        blank=True,
        help_text="Como a viagem se alinha com as metas da COP 30"
    )
    
    class Meta:
        verbose_name = "Relatório"
        verbose_name_plural = "Relatórios"
        ordering = ["-criado_em"]
    
    def save(self, *args, **kwargs):
        # Converter valores para Decimal antes de salvar
        decimal_fields = ['pontuacao_sustentabilidade', 'emissao_co2_total', 
                         'emissao_co2_transporte', 'emissao_co2_hospedagem', 
                         'economia_local_impacto']
        
        for field_name in decimal_fields:
            value = getattr(self, field_name)
            if value is not None:
                setattr(self, field_name, Decimal(str(value)))
        
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Relatório da Simulação {self.simulacao.id}"
