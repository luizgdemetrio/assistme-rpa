# src/app.py
import os
from dotenv import load_dotenv, find_dotenv
import typer

from src.browser import get_playwright_context
from src.flows.login_flow import do_login
from src.flows.service_flow import selecionar_servico_assistencia
from src.flows.download_nf_flow import processar_downloads

app = typer.Typer(help="CLI do Assist Me RPA")


# -------------------------------------------------------------------------
# LOGIN
# -------------------------------------------------------------------------
@app.command("login")
def login_cmd(
    headless: bool = typer.Option(False, help="Roda em headless"),
    base_url: str = typer.Option(None, help="URL da tela de login (sobrepõe .env)"),
):
    env_path = find_dotenv(filename=".env", usecwd=True)
    print(f"Usando .env: {env_path}")
    load_dotenv(env_path, override=True)

    base = base_url or os.getenv("ASSISTME_BASE_URL")
    user = os.getenv("ASSISTME_USER")
    pwd = os.getenv("ASSISTME_PASS")

    missing = []
    if not base:
        missing.append("ASSISTME_BASE_URL")
    if not user:
        missing.append("ASSISTME_USER")
    if not pwd:
        missing.append("ASSISTME_PASS")

    if missing:
        typer.secho(
            "Variáveis ausentes: " + ", ".join(missing),
            fg=typer.colors.RED,
        )
        raise typer.Exit(2)

    p, browser, context = get_playwright_context(headless=headless)
    try:
        page = context.new_page()
        do_login(page, base_url=base)
        typer.echo("✅ Login concluído.")
    finally:
        context.close()
        browser.close()
        p.stop()


# -------------------------------------------------------------------------
# RUN (principal)
# -------------------------------------------------------------------------
@app.command("run")
def run_cmd(
    protocolo: str = typer.Argument(..., help="Ex.: CP25-20693"),
    headless: bool = typer.Option(False, help="Roda em headless"),
):
    from src.utils.config import load_config
    from src.flows.menu_flow import ir_para_custo_puro
    from src.flows.protocolo_flow import abrir_visualizar_do_protocolo

    env_path = find_dotenv(filename=".env", usecwd=True)
    load_dotenv(env_path, override=True)

    base = os.getenv("ASSISTME_BASE_URL")
    if not base:
        typer.secho("ASSISTME_BASE_URL ausente no .env", fg=typer.colors.RED)
        raise typer.Exit(2)

    cfg = load_config()
    sel = cfg["seletores"]

    p, browser, context = get_playwright_context(headless=headless)

    try:
        page = context.new_page()
        do_login(page, base_url=base)
        selecionar_servico_assistencia(page)
        ir_para_custo_puro(page, sel)
        abrir_visualizar_do_protocolo(page, protocolo, sel)

        typer.echo(f"🔍 Visualizar aberto para {protocolo}. Iniciando downloads...")

        # ⬇️ AQUI! baixar NFs ANTES de fechar contexto
        processar_downloads(page, protocolo)

        typer.echo("🏁 Processo finalizado com sucesso.")

    finally:
        context.close()
        browser.close()
        p.stop()


# -------------------------------------------------------------------------
# DOCTOR
# -------------------------------------------------------------------------
@app.command("doctor")
def doctor_cmd():
    import importlib
    import shutil
    import sys

    ok = True

    def chk(name):
        nonlocal ok
        try:
            importlib.import_module(name)
            print(f"✅ {name}")
        except Exception as e:
            ok = False
            print(f"❌ {name}: {e}")

    print("Checando módulos:")
    for m in ["playwright", "dotenv", "yaml"]:
        chk(m)

    print("Checando msedge channel:")
    edge = shutil.which("msedge")
    print("✅ msedge no PATH" if edge else "⚠️ msedge não encontrado")

    sys.exit(0 if ok else 1)


# -------------------------------------------------------------------------
# ENTRYPOINT
# -------------------------------------------------------------------------
if __name__ == "__main__":
    app()
