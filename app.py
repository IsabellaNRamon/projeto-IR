# app.py
import flet as ft
from ir_calc import calcular_ir

def main(page: ft.Page):
    page.title = "Calculadora de IR (mensal / anual)"
    page.window_preferred_size = ft.Size(420, 820)
    page.padding = 16
    page.vertical_alignment = ft.MainAxisAlignment.START

    titulo = ft.Text("Calculadora de Imposto de Renda", size=20, weight="bold")

    # tipo de cálculo: mensal (IRRF) ou anual (IRPF simplificado A)
    tipo_calc = ft.Dropdown(
        width=320,
        options=[
            ft.dropdown.Option("mensal", text="Mensal (IRRF - desconto na folha)"),
            ft.dropdown.Option("anual", text="Anual (IRPF - modo simplificado)")
        ],
        value="mensal"
    )

    # ano (2023, 2024, 2025)
    ano = ft.Dropdown(
        width=180,
        options=[
            ft.dropdown.Option("2023", text="2023"),
            ft.dropdown.Option("2024", text="2024"),
            ft.dropdown.Option("2025", text="2025"),
        ],
        value="2024"
    )

    # mês (1-12) — só para cálculo mensal
    meses_options = [ft.dropdown.Option(str(i), text=f"{i:02d}") for i in range(1,13)]
    mes = ft.Dropdown(width=120, options=meses_options, value="1")

    # campos de entrada
    salario_input = ft.TextField(label="Salário bruto (ou rendimento anual quando 'anual')", width=320, keyboard_type=ft.KeyboardType.NUMBER)
    dependentes_input = ft.TextField(label="Número de dependentes", width=120, value="0", keyboard_type=ft.KeyboardType.NUMBER)

    resultado_container = ft.Container(content=ft.Column(), padding=12, border=ft.border.all(1, "#A9A9A9"), border_radius=8, visible=False)

    def formatar_brl(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def atualizar_visibilidade(e=None):
        # mês só aparece se tipo == mensal
        if tipo_calc.value == "mensal":
            mes.visible = True
        else:
            mes.visible = False
        page.update()

    tipo_calc.on_change = atualizar_visibilidade
    atualizar_visibilidade()

    def calcular(e):
        # validações simples
        try:
            valor = float(salario_input.value.replace(",", "."))
            dependentes = int(float(dependentes_input.value))
            ano_sel = int(ano.value)
            mes_sel = int(mes.value)
            tipo = tipo_calc.value  # 'mensal' ou 'anual'
        except Exception:
            resultado_container.content.controls = [ft.Text("Erro: preencha valores válidos (use ponto ou vírgula para decimal).")]
            resultado_container.visible = True
            page.update()
            return

        # chama o calculador
        if tipo == "mensal":
            r = calcular_ir("mensal", valor, dependentes, ano_sel, mes_sel)
        else:
            r = calcular_ir("anual", valor, dependentes, ano_sel)

        # montar exibição
        controls = [
            ft.Text(f"Tipo: {r.get('tipo').capitalize()}"),
            ft.Text(f"Ano: {r.get('ano')}"),
        ]
        if r['tipo'] == "mensal":
            controls += [
                ft.Text(f"Mês: {r.get('mes'):02d}"),
                ft.Text(f"Salário bruto: {formatar_brl(r['salario_bruto'])}"),
                ft.Text(f"Nº dependentes: {r['num_dependentes']}"),
                ft.Text(f"Desconto por dependentes: {formatar_brl(r['desconto_dependentes'])}"),
                ft.Text(f"Tipo de desconto aplicado: {r['tipo_desconto']}"),
                ft.Text(f"Valor do desconto aplicado: {formatar_brl(r['desconto_usado'])}"),
                ft.Text(f"Salário base: {formatar_brl(r['salario_base'])}"),
                ft.Text(f"Alíquota IR: {r['aliquota']} %"),
                ft.Text(f"Parcela a deduzir: {formatar_brl(r['parcela_deduzir'])}"),
                ft.Text(f"Imposto devido (IR): {formatar_brl(r['imposto_liquido'])}"),
                ft.Text(""),
                ft.Text(f"Salário líquido: {formatar_brl(r['salario_liquido'])}", weight="bold"),
                ft.Text(f"Alíquota efetiva: {r['aliquota_efetiva']} %"),
            ]
        else:
            controls += [
                ft.Text(f"Rendimento tributável anual: {formatar_brl(r['rendimento_anual'])}"),
                ft.Text(f"Nº dependentes: {r['num_dependentes']}"),
                ft.Text(f"Desconto por dependentes (anual): {formatar_brl(r['desconto_dependentes'])}"),
                ft.Text(f"Tipo de desconto aplicado: {r['tipo_desconto']}"),
                ft.Text(f"Valor do desconto aplicado: {formatar_brl(r['desconto_usado'])}"),
                ft.Text(f"Base tributável anual: {formatar_brl(r['base_tributavel'])}"),
                ft.Text(f"Alíquota IR: {r['aliquota']} %"),
                ft.Text(f"Parcela a deduzir anual: {formatar_brl(r['parcela_deduzir'])}"),
                ft.Text(f"Imposto anual devido (IR): {formatar_brl(r['imposto_liquido'])}"),
                ft.Text(""),
                ft.Text(f"Rendimento líquido anual: {formatar_brl(r['rendimento_liquido'])}", weight="bold"),
                ft.Text(f"Alíquota efetiva: {r['aliquota_efetiva']} %"),
            ]

        resultado_container.content.controls = controls
        resultado_container.visible = True
        page.update()

    def limpar(e):
        salario_input.value = ""
        dependentes_input.value = "0"
        resultado_container.visible = False
        page.update()

    botao_calcular = ft.ElevatedButton("Calcular", on_click=calcular)
    botao_limpar = ft.ElevatedButton("Limpar", on_click=limpar)

    # layout
    page.add(
        titulo,
        ft.Row([tipo_calc, ano, mes], spacing=10),
        ft.Row([salario_input, dependentes_input], alignment=ft.MainAxisAlignment.START, spacing=20),
        ft.Row([botao_calcular, botao_limpar], spacing=12),
        ft.Text("Resultado:", weight="bold"),
        resultado_container
    )

ft.app(target=main)