# src/flows/login_flow.py
import os
from playwright.sync_api import Page, expect


def do_login(page: Page, base_url: str):
    page.goto(base_url, wait_until="domcontentloaded")

    # Login: rótulo é único
    page.get_by_label("Login", exact=True).fill(os.environ["ASSISTME_USER"])

    # Senha: evite colisão com "Lembrar Senha"
    # Opção A (CSS, mais à prova de mudança visual):
    page.locator('input[aria-label="Senha"][type="password"]').fill(
        os.environ["ASSISTME_PASS"]
    )
    # Opção B (placeholder, também ok):
    # page.get_by_placeholder("Digite sua senha").fill(os.environ["ASSISTME_PASS"])

    # Entrar (nome exato)
    page.get_by_role("button", name="Entrar", exact=True).click()

    # Aguarda estabilizar
    page.wait_for_load_state("networkidle")
