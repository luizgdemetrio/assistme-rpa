from playwright.sync_api import Page
import os
import requests
from time import sleep


def extrair_lista_notas(page: Page):
    """
    Lê todas as notas dentro do popup do Custo Puro.
    Retorna lista de dicionários com infos e o botão <eye>.
    """
    itens = page.locator("label.q-item")
    total = itens.count()

    notas = []

    for i in range(total):
        item = itens.nth(i)

        prestador = item.locator(".protocolo .conteudo").inner_text().strip()
        numero_nf = item.locator(".dataCadastro .conteudo").inner_text().strip()

        # Pega a segunda ocorrência de valor
        valores = item.locator(".line .valor .conteudo")
        valor_nf = valores.nth(1).inner_text().strip()

        botao_eye = item.locator("i.far.fa-eye")

        notas.append(
            {
                "prestador": prestador,
                "numero": numero_nf,
                "valor": valor_nf,
                "eye": botao_eye,
            }
        )

    return notas


def baixar_pdf_via_iframe(url_pdf: str, destino: str):
    """
    Faz o download do PDF usando requests.
    """
    resposta = requests.get(url_pdf)

    if resposta.status_code != 200:
        raise RuntimeError(f"Erro ao baixar PDF: {url_pdf}")

    with open(destino, "wb") as f:
        f.write(resposta.content)


def fechar_nf(page: Page):
    # Fecha o modal via JS para ignorar interceptações de pointer-events
    modal_fechar = page.locator('div[role="dialog"] button:has-text("Fechar")')

    if modal_fechar.count() > 0:
        botao = modal_fechar.first
        try:
            # força clique mesmo se o overlay estiver na frente
            botao.evaluate("(el) => el.click()")
        except:
            # fallback: tenta clicar tradicionalmente
            botao.click(force=True)

    # espera o modal desaparecer
    page.wait_for_timeout(400)


def baixar_nota_fiscal(page: Page, nota: dict, pasta_destino: str):
    prestador = nota["prestador"]
    numero = nota["numero"]
    valor = nota["valor"]

    print(f"⬇️ Baixando NF {numero} - {prestador}...")

    # Abre popup da NF
    nota["eye"].click()

    # Aguarda iframe da NF
    iframe = page.locator("iframe.frame")
    iframe.wait_for(state="visible")

    # URL do PDF
    url_pdf = iframe.get_attribute("src")
    if not url_pdf:
        raise RuntimeError("Não foi possível capturar o src do iframe da NF.")

    # Nome final
    nome_final = f"{prestador} - NF {numero} - {valor}.pdf".replace("/", "-")
    destino = os.path.join(pasta_destino, nome_final)

    # Baixa PDF
    baixar_pdf_via_iframe(url_pdf, destino)
    print(f"✅ NF salva como: {nome_final}")

    # FECHAR popup da NF
    fechar_nf(page)

    # Pequeno delay para evitar conflito no próximo click
    page.wait_for_timeout(300)


def processar_downloads(page: Page, protocolo: str):
    """
    Cria a pasta destino e baixa TODAS as notas do popup de Custo Puro.
    Se já houver arquivos baixados, ignora e baixa somente as faltantes.
    """

    pasta_base = r"C:\Users\Luiz Gustavo\NEXCORP SER. TELECOMUNICAÇÕES S.A\Rodolfo Pollmann - Acionamentos PR\ASSISTME"
    pasta_destino = os.path.join(pasta_base, protocolo)

    os.makedirs(pasta_destino, exist_ok=True)

    # Lista o que já existe
    arquivos_existentes = set(os.listdir(pasta_destino))
    print(f"📁 Arquivos existentes: {len(arquivos_existentes)}\n")

    print("📄 Lendo lista de notas...")
    notas = extrair_lista_notas(page)
    print(f"Encontradas {len(notas)} notas.\n")

    for i, nota in enumerate(notas):
        # Nome final da NF
        nome_final = (
            f"{nota['prestador']} - NF {nota['numero']} - {nota['valor']}.pdf".replace(
                "/", "-"
            )
        )

        if nome_final in arquivos_existentes:
            print(f"⏭️ Pulando (já existe): {nome_final}")
            continue  # NÃO baixa de novo

        # Se não é a primeira, reabre a lista de notas
        if i > 0:
            print("🔄 Reabrindo container de notas...")
            page.wait_for_selector("text=VISUALIZAR", timeout=1500)
            page.get_by_role("button", name="VISUALIZAR").click()
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(800)

        # Baixa a nota
        baixar_nota_fiscal(page, nota, pasta_destino)

    print("\n🏁 Finalizado: todas as NFs faltantes foram baixadas!")
