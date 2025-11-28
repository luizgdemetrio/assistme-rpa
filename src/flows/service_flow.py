# src/flows/service_flow.py
from playwright.sync_api import Page, expect


def selecionar_servico_assistencia(page: Page):
    """
    Seleciona o serviço 'Assistência' após o login.
    """
    # Garante que a tela de serviços carregou
    expect(page.get_by_text("Selecione um Serviço")).to_be_visible(timeout=30000)

    # Clica no card 'Assistência'
    # Opção 1: pelo texto visível
    page.get_by_role("heading", name="Assistência", exact=True).click()

    # Caso não funcione, fallback:
    # page.locator("h5:text('Assistência')").click()

    # Espera o redirecionamento pro sistema principal (menu lateral)
    page.wait_for_load_state("networkidle")

    # Pequena verificação
    assert (
        "financeiro" in page.content().lower() or "menu" in page.content().lower()
    ), "⚠️ Parece que o clique não entrou no sistema principal."
