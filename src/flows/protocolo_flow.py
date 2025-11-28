# src/flows/protocolo_flow.py
from playwright.sync_api import Page, TimeoutError as PWTimeout
from time import sleep


def _usar_filtro(page: Page, filtro_sel: str, texto: str):
    """
    Preenche o campo de busca e aciona a filtragem.
    Funciona tanto na tela de Custo Puro quanto em outras telas.
    """

    f = page.locator(filtro_sel)

    if not f.count():
        return

    campo = f.first

    # Garante foco
    campo.click()

    # Limpa e digita
    campo.fill("")
    campo.fill(texto)

    # Enter aciona busca em todas as telas
    campo.press("Enter")

    # Espera o Quasar atualizar o grid (não usa networkidle porque não há requisição)
    page.wait_for_timeout(1200)


def abrir_visualizar_do_protocolo(page: Page, protocolo: str, sel: dict):
    """
    Procura um protocolo no grid e abre o Visualizar.
    Agora funciona perfeitamente com a tela de Custo Puro.
    """

    # Detecta se estamos no Custo Puro
    estamos_no_custo_puro = "custopuro" in page.url.lower()

    # Seleciona o campo de filtro correto
    if estamos_no_custo_puro:
        filtro_sel = 'input[placeholder*="Pesquise aqui"]'
    else:
        filtro_sel = sel.get("filtro_busca")

    # 1) Tenta filtrar
    if filtro_sel:
        try:
            _usar_filtro(page, filtro_sel, protocolo)
        except PWTimeout:
            pass  # Continua mesmo que falhe
        page.wait_for_load_state("networkidle")

    # 2) Captura as linhas do grid
    linhas = page.locator(sel["grid_linhas"])
    total = linhas.count()

    if total == 0:
        raise RuntimeError("Grid não carregou nenhuma linha. Verifique os seletores.")
    print(f"🔍 {total} linhas encontradas no grid após filtro.")

    mais = page.locator("button:has(i.fas.fa-ellipsis-v)")
    mais.first.click()
    print(f"📂 Menu 'mais' aberto para o protocolo {protocolo}.")

    btn_visualizar = sel.get("acao_visualizar")
    if not btn_visualizar:
        raise RuntimeError("Seletor para ação de Visualizar não definido.")
    page.wait_for_selector("text=VISUALIZAR", timeout=5000)
    page.get_by_role("button", name="VISUALIZAR").click()
    sleep(360)
