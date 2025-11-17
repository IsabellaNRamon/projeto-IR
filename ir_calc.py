# ir_calc.py
from dataclasses import dataclass

DEPENDENT_DEDUCTION = 189.59
DESCONTO_SIMPLIFICADO = 528.00

# Tabela exata do material (para bater com os exemplos)
BRACKETS = [
    (0.00,     1903.98,  0.0,   0.00),
    (1903.99,  2826.65,  7.5,  142.80),
    (2826.66,  3751.05, 15.0,  354.80),
    (3751.06,  4664.68, 22.5,  636.13),
    (4664.69, float('inf'), 27.5, 869.36),
]


def round2(x):
    return round(x + 1e-9, 2)


def encontrar_faixa(salario_base):
    for minv, maxv, ali, parcela in BRACKETS:
        if minv <= salario_base <= maxv:
            return ali, parcela
    return 0, 0


def calcular_ir(salario_bruto: float, num_dependentes: int):
    salario_bruto = float(salario_bruto)
    num_dependentes = int(num_dependentes)

    # valor total de desconto por dependentes
    desconto_dependentes = num_dependentes * DEPENDENT_DEDUCTION

    # regra do material
    if desconto_dependentes > DESCONTO_SIMPLIFICADO:
        desconto_usado = desconto_dependentes
        tipo_desconto = "Desconto por Dependentes"
    else:
        desconto_usado = DESCONTO_SIMPLIFICADO
        tipo_desconto = "Desconto Simplificado"

    salario_base = salario_bruto - desconto_usado
    aliquota, parcela_deduzir = encontrar_faixa(salario_base)

    imposto_bruto = salario_base * (aliquota / 100)
    imposto_liquido = imposto_bruto - parcela_deduzir
    if imposto_liquido < 0:
        imposto_liquido = 0

    salario_liquido = salario_bruto - imposto_liquido
    aliquota_efetiva = imposto_liquido / salario_bruto if salario_bruto > 0 else 0

    return dict(
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
        aliquota_efetiva=round2(aliquota_efetiva * 100),
    )