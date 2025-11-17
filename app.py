# app.py
import flet as ft
from ir_calc import calcular_ir

def main(page: ft.Page):
    page.title = "Calculadora de IR"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.window_preferred_size = ft.Size(380, 800)
    page.padding = 15

    titulo = ft.Text("Calculadora de Imposto de Renda", size=18, weight="bold")

    salario = ft.TextField(label="Salário bruto (R$)", keyboard_type=ft.KeyboardType.NUMBER)
    dependentes = ft.TextField(label="Número de dependentes", keyboard_type=ft.KeyboardType.NUMBER)

    resultado = ft.Column()

    def calcular(e):
        try:
            s = float(salario.value.replace(",", "."))
            d = int(float(dependentes.value))
        except:
            resultado.controls = [ft.Text("Erro: Digite valores válidos.")]
            page.update()
            return

        r = calcular_ir(s, d)

        resultado.controls = [
            ft.Text(f"Salário bruto: R$ {r['salario_bruto']:.2f}"),
            ft.Text(f"Nº dependentes: {r['num_dependentes']}"),
            ft.Text(f"Desconto por dependentes: R$ {r['desconto_dependentes']:.2f}"),
            ft.Text(f"Tipo de desconto usado: {r['tipo_desconto']}"),
            ft.Text(f"Valor do desconto aplicado: R$ {r['desconto_usado']:.2f}"),
            ft.Text(f"Salário base: R$ {r['salario_base']:.2f}"),
            ft.Text(f"Alíquota IR: {r['aliquota']}%"),
            ft.Text(f"Parcela a deduzir: R$ {r['parcela_deduzir']:.2f}"),
            ft.Text(f"Imposto devido (IR): R$ {r['imposto_liquido']:.2f}"),
            ft.Text(
                f"Salário líquido: R$ {r['salario_liquido']:.2f}",
                weight="bold"
            ),
            ft.Text(f"Alíquota efetiva: {r['aliquota_efetiva']:.2f} %"),
        ]
        page.update()

    botao = ft.ElevatedButton("Calcular IR", on_click=calcular)
    page.add(titulo, salario, dependentes, botao, resultado)

ft.app(target=main)