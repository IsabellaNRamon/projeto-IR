# ir_calc.py
"""
Cálculos de IR mensal (IRRF) e anual (IRPF - modo simplificado A).
Contém tabelas para 2023, 2024 e 2025 (mensais). Para cálculo anual, as
faixas mensais são multiplicadas por 12 (procedimento usual).
"""

from typing import Tuple, List

# valores fixos oficiais
DEPENDENT_DEDUCTION_MONTHLY = 189.59  # dedução por dependente (mensal)
# desconto simplificado mensal mudou em 2024 (ex.: 528,00 antes; 564.80 em 2024)
SIMPLIFIED_DEDUCTION_MONTHLY_BY_YEAR = {
    2023: 528.00,
    2024: 564.80,
    2025: 564.80,
}

# Tabelas mensais (faixas) - listas de (min, max, aliquota_percent, parcela_deduzir)
# Fontes: páginas de "Tabelas" da Receita Federal (valores oficiais)
# Observações:
# - 2023 teve mudança em maio/2023: de jan-abr usa tabela antiga; de mai-dez nova tabela.
# - 2024 teve mudança em fev/2024; 2025 segue tabela vigente (usada 2024/2025).
# Para facilitar, a função get_monthly_table() lida com mês/ano e retorna a lista correta.

# tabela antiga (usada até abril/2023)
TABLE_2023_JAN_APR = [
    (0.00,     1903.98,  0.0,   0.00),
    (1903.99,  2826.65,  7.5,  142.80),
    (2826.66,  3751.05, 15.0,  354.80),
    (3751.06,  4664.68, 22.5,  636.13),
    (4664.69, float('inf'), 27.5, 869.36),
]

# tabela vigente a partir de maio/2023 (e parcialmente utilizada em 2024/2025 as base mensal)
TABLE_2023_MAY_ON = [
    (0.00,     2112.00,  0.0,   0.00),
    (2112.01,  2826.65,  7.5,  158.40),
    (2826.66,  3751.05, 15.0,  370.40),
    (3751.06,  4664.68, 22.5,  651.73),
    (4664.69, float('inf'), 27.5, 884.96),
]

# tabela a partir de fev/2024 (ajuste que passou a valer em 02/2024)
TABLE_2024_FEB_ON = [
    (0.00,     2259.20,  0.0,   0.00),
    (2259.21,  2826.65,  7.5,  169.44),
    (2826.66,  3751.05, 15.0,  381.44),
    (3751.06,  4664.68, 22.5,  662.77),
    (4664.69, float('inf'), 27.5, 896.00),
]

# para 2025 assumimos a mesma tabela de 2024 (conforme publicações oficiais recentes)
TABLE_2025 = TABLE_2024_FEB_ON

def get_monthly_table(year: int, month: int) -> Tuple[List[Tuple[float,float,float,float]], float]:
    """
    Retorna (tabela_mensal, desconto_simplificado_mensal) para o ano e mês solicitados.
    A tabela é lista de tuplas (min, max, aliquota_percent, parcela_deduzir).
    """
    # default simplificado para o ano (se não estiver no dicionário, usa 528.00)
    simplificado = SIMPLIFIED_DEDUCTION_MONTHLY_BY_YEAR.get(year, 528.00)

    if year == 2023:
        if 1 <= month <= 4:
            tabela = TABLE_2023_JAN_APR
        else:
            tabela = TABLE_2023_MAY_ON
    elif year == 2024:
        # mudança em fev/2024 -> se mês == 1, ainda usaria tabela anterior (mai/2023),
        # a partir de fevereiro usa a nova tabela (TABLE_2024_FEB_ON)
        if month == 1:
            tabela = TABLE_2023_MAY_ON
        else:
            tabela = TABLE_2024_FEB_ON
    elif year == 2025:
        # usa tabela de 2024/2025 (TABLE_2025)
        tabela = TABLE_2025
    else:
        # fallback: usa tabela mais recente conhecida (2024)
        tabela = TABLE_2024_FEB_ON

    return tabela, simplificado


def round2(x):
    return round(x + 1e-9, 2)


def encontrar_faixa_na_tabela(salario_base: float, tabela: List[Tuple[float,float,float,float]]) -> Tuple[float, float]:
    """
    Retorna (aliquota_percent, parcela_deduzir) de acordo com 'tabela'.
    """
    for minv, maxv, ali, parcela in tabela:
        if minv <= salario_base <= maxv:
            return ali, parcela
    # fallback
    return 0.0, 0.0


def calcular_ir_mensal(salario_bruto: float, num_dependentes: int, year: int, month: int):
    """
    Calcula IRRF mensal para o salário bruto informado, considerando o ano e mês de vigência das tabelas.
    Segue a regra: se houver dependentes -> usa dedução por dependentes; se não -> usa desconto simplificado.
    """
    salario_bruto = float(salario_bruto)
    num_dependentes = int(num_dependentes)

    tabela, simplificado_mensal = get_monthly_table(year, month)

    desconto_dependentes = num_dependentes * DEPENDENT_DEDUCTION_MONTHLY

    # regra: se tem dependentes -> usa dependentes; se não -> usa simplificado
    if num_dependentes > 0:
        desconto_usado = desconto_dependentes
        tipo_desconto = "Desconto por Dependentes"
    else:
        desconto_usado = simplificado_mensal
        tipo_desconto = "Desconto Simplificado"

    salario_base = salario_bruto - desconto_usado
    aliquota, parcela_deduzir = encontrar_faixa_na_tabela(salario_base, tabela)

    imposto_bruto = salario_base * (aliquota / 100.0)
    imposto_liquido = imposto_bruto - parcela_deduzir
    if imposto_liquido < 0:
        imposto_liquido = 0.0

    salario_liquido = salario_bruto - imposto_liquido
    aliquota_efetiva = (imposto_liquido / salario_bruto * 100.0) if salario_bruto > 0 else 0.0

    return dict(
        tipo="mensal",
        ano=year,
        mes=month,
        salario_bruto=round2(salario_bruto),
        num_dependentes=num_dependentes,
        desconto_dependentes=round2(desconto_dependentes),
        tipo_desconto=tipo_desconto,
        desconto_usado=round2(desconto_usado),
        salario_base=round2(salario_base),
        aliquota=aliquota,
        parcela_deduzir=round2(parcela_deduzir),
        imposto_bruto=round2(imposto_bruto),
        imposto_liquido=round2(imposto_liquido),
        salario_liquido=round2(salario_liquido),
        aliquota_efetiva=round(aliquota_efetiva, 4),
    )


def calcular_ir_anual(rendimento_anual: float, num_dependentes: int, year: int):
    """
    Modo simplificado A para cálculo anual:
    - usuário informa rendimento tributável anual e número de dependentes
    - se houver dependentes, aplica dedução anual por dependente (DEPENDENT_DEDUCTION_MONTHLY * 12)
      caso contrário aplica desconto simplificado anual (SIMPLIFIED_DEDUCTION_MONTHLY_BY_YEAR[year] * 12)
    - convertemos a tabela mensal do ano para anual (multiplicando limites e parcela por 12)
    """
    rendimento_anual = float(rendimento_anual)
    num_dependentes = int(num_dependentes)

    # usamos tabela mensal adequada para o ano (tomando mês arbitrário: fevereiro ou maio não importa aqui;
    # para tabela anual usamos a tabela vigente na maior parte do ano: para 2023 usamos a tabela 'may_on' se isso fizer sentido)
    # estratégia: pegar tabela do mês 12 daquele ano (tabela vigente ao fim do ano)
    tabela_mensal, simplificado_mensal = get_monthly_table(year, 12)

    # construir tabela anual (multiplica limites e parcela por 12)
    tabela_anual = []
    for minv, maxv, ali, parcela in tabela_mensal:
        tabela_anual.append((minv * 12.0, (maxv if maxv != float('inf') else float('inf')) * 12.0, ali, parcela * 12.0))

    desconto_dependentes_anuais = num_dependentes * DEPENDENT_DEDUCTION_MONTHLY * 12.0
    simplificado_anual = simplificado_mensal * 12.0

    if num_dependentes > 0:
        desconto_usado = desconto_dependentes_anuais
        tipo_desconto = "Desconto por Dependentes (anual)"
    else:
        desconto_usado = simplificado_anual
        tipo_desconto = "Desconto Simplificado (anual)"

    base_tributavel = rendimento_anual - desconto_usado
    aliquota, parcela_deduzir = encontrar_faixa_na_tabela(base_tributavel, tabela_anual)

    imposto_bruto = base_tributavel * (aliquota / 100.0)
    imposto_liquido = imposto_bruto - parcela_deduzir
    if imposto_liquido < 0:
        imposto_liquido = 0.0

    rendimento_liquido = rendimento_anual - imposto_liquido
    aliquota_efetiva = (imposto_liquido / rendimento_anual * 100.0) if rendimento_anual > 0 else 0.0

    return dict(
        tipo="anual",
        ano=year,
        rendimento_anual=round2(rendimento_anual),
        num_dependentes=num_dependentes,
        desconto_dependentes=round2(desconto_dependentes_anuais),
        tipo_desconto=tipo_desconto,
        desconto_usado=round2(desconto_usado),
        base_tributavel=round2(base_tributavel),
        aliquota=aliquota,
        parcela_deduzir=round2(parcela_deduzir),
        imposto_bruto=round2(imposto_bruto),
        imposto_liquido=round2(imposto_liquido),
        rendimento_liquido=round2(rendimento_liquido),
        aliquota_efetiva=round(aliquota_efetiva, 4),
    )


def calcular_ir(tipo: str, valor: float, num_dependentes: int, year: int, month: int = 1):
    """
    Função wrapper para uso pela UI.
    - tipo: "mensal" ou "anual"
    - valor: para 'mensal' espera salário bruto mensal; para 'anual' espera rendimento anual tributável
    - num_dependentes: int
    - year: ano (ex: 2023)
    - month: mês (1-12) — usado apenas para 'mensal'
    """
    tipo = tipo.lower()
    if tipo == "mensal":
        return calcular_ir_mensal(valor, num_dependentes, year, month)
    elif tipo == "anual":
        return calcular_ir_anual(valor, num_dependentes, year)
    else:
        raise ValueError("tipo deve ser 'mensal' ou 'anual'")
