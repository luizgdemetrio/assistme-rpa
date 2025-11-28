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


def baixar_nota_fiscal(page: Page, nota: dict, pasta_destino: str):
    """
    Clica no olho, pega o PDF dentro do iframe e salva com nome correto.
    """
    prestador = nota["prestador"]
    numero = nota["numero"]
    valor = nota["valor"]

    print(f"⬇️ Baixando NF {numero} - {prestador}...")

    # Abre popup clicando no olho
    nota["eye"].click()

    # Aguarda iframe aparecer
    iframe = page.locator("iframe.frame")
    iframe.wait_for(state="visible", timeout=5000)

    # Captura a URL do PDF
    url_pdf = iframe.get_attribute("src")

    if not url_pdf:
        raise RuntimeError("Não foi possível capturar o src do iframe da NF.")

    # Define nome final
    nome_final = f"{prestador} - NF {numero} - {valor}.pdf".replace("/", "-")
    destino = os.path.join(pasta_destino, nome_final)

    # Baixa PDF via HTTP direto
    baixar_pdf_via_iframe(url_pdf, destino)

    print(f"✅ NF salva como: {nome_final}")

    # Fecha o popup — o botão geralmente é o X ou “Fechar”
    page.get_by_role("button", name="Fechar").click(timeout=3000)
    sleep(0.5)


def processar_downloads(page: Page, protocolo: str):
    """
    Cria a pasta destino e baixa TODAS as notas do popup de Custo Puro.
    """

    pasta_base = r"C:\Users\Luiz Gustavo\NEXCORP SER. TELECOMUNICAÇÕES S.A\Rodolfo Pollmann - Acionamentos PR\ASSISTME"
    pasta_destino = os.path.join(pasta_base, protocolo)

    os.makedirs(pasta_destino, exist_ok=True)

    print("📄 Lendo lista de notas...")
    notas = extrair_lista_notas(page)
    print(f"Encontradas {len(notas)} notas.")

    for nota in notas:
        baixar_nota_fiscal(page, nota, pasta_destino)

    print("🏁 Finalizado: todas as NFs foram baixadas com sucesso!")
