# 1. inserção de dados dos turistas
turistas = int(input("Quantos turistas visitam a região? "))
gasto_por_dia = float(input("Quanto cada turista gasta por dia (R$)? "))
dias_estadia = int(input("Quantas dias eles ficam? "))
cidades = int(input("Quantas cidades serão visitadas? "))

# 2. Cálculos de impactos
impacto_direto = turistas * gasto_por_dia * dias_estadia
impacto_total = impacto_direto * 1.5 # O '1.5' significa que a cada 1 real gasto, gera 0,50 centavos para a economia
impacto_por_cidade = impacto_total / cidades

# 3. Resultados
print("\n=== Gasto Estimado ===")
print(f"1. Impacto Total (R$): {impacto_total:,.2f}")
print(f"2. Impacto Direto (R$): {impacto_direto:,.2f}")
print(f"3. Impacto por Cidade (R$): {impacto_por_cidade:,.2f}")