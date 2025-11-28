# src/flows/menu_flow.py
from playwright.sync_api import Page


def ir_para_custo_puro(page: Page, sel: dict):
    print("🧭 Indo direto para Custo Puro pela URL...")

    custo_puro_url = "https://cliente.grupoassistme.com.br/CustoPuro"

    # Navega até a página
    page.goto(custo_puro_url, wait_until="domcontentloaded")

    # Aguarda o grid REAL (tabela do Quasar)
    page.wait_for_selector("#App > div", timeout=20000)

    print("✅ Página de Custo Puro aberta com sucesso.")
