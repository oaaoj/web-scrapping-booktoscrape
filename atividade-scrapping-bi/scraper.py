import csv
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
ARQUIVO_SAIDA = "produtos_books.csv" # O arquivo é gerado na pasta onde ele é executado

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ProjetoAcademicoWebScraping/1.0)"
}


def obter_html(url):
    """
    Acessa uma URL e retorna o conteúdo HTML tratado pelo BeautifulSoup.
    """
    resposta = requests.get(url, headers=HEADERS, timeout=15)
    resposta.raise_for_status()

    return BeautifulSoup(resposta.text, "html.parser")


def extrair_categorias():
    """
    Extrai as categorias disponíveis no menu lateral do site.
    """
    soup = obter_html(BASE_URL)

    categorias = []

    links_categorias = soup.select("div.side_categories ul.nav-list ul li a")

    for link in links_categorias:
        nome_categoria = link.get_text(strip=True)
        url_categoria = urljoin(BASE_URL, link.get("href"))

        categorias.append({
            "categoria": nome_categoria,
            "url": url_categoria
        })

    return categorias


def extrair_avaliacao(card_produto):
    """
    Extrai a avaliação do produto com base na classe star-rating.
    Exemplo de classe encontrada no HTML:
    <p class="star-rating Three">
    """
    avaliacao_tag = card_produto.select_one("p.star-rating")

    if avaliacao_tag is None:
        return ""

    classes = avaliacao_tag.get("class", [])

    for classe in classes:
        if classe != "star-rating":
            return classe

    return ""


def extrair_produtos_da_pagina(url_pagina, categoria):
    """
    Extrai todos os produtos de uma página específica.
    """
    soup = obter_html(url_pagina)

    produtos = []

    cards_produtos = soup.select("article.product_pod")

    for card in cards_produtos:
        titulo_tag = card.select_one("h3 a")
        preco_tag = card.select_one("p.price_color")
        disponibilidade_tag = card.select_one("p.instock.availability")

        titulo = titulo_tag.get("title", "").strip() if titulo_tag else ""
        preco = preco_tag.get_text(strip=True) if preco_tag else ""
        disponibilidade = disponibilidade_tag.get_text(strip=True) if disponibilidade_tag else ""
        avaliacao = extrair_avaliacao(card)

        link_relativo = titulo_tag.get("href", "") if titulo_tag else ""
        url_produto = urljoin(url_pagina, link_relativo)

        produto = {
            "categoria": categoria,
            "titulo": titulo,
            "preco": preco,
            "disponibilidade": disponibilidade,
            "avaliacao": avaliacao,
            "url_produto": url_produto
        }

        produtos.append(produto)

    return produtos, soup


def obter_proxima_pagina(soup, url_atual):
    """
    Verifica se existe uma próxima página.
    Se existir, retorna a URL completa da próxima página.
    """
    proxima_pagina = soup.select_one("li.next a")

    if proxima_pagina:
        href = proxima_pagina.get("href")
        return urljoin(url_atual, href)

    return None


def coletar_dados():
    """
    Controla o fluxo principal de coleta:
    1. Coleta categorias;
    2. Percorre as páginas de cada categoria;
    3. Extrai os dados dos produtos.
    """
    produtos_extraidos = []

    categorias = extrair_categorias()

    print(f"Total de categorias encontradas: {len(categorias)}")

    for categoria_info in categorias:
        categoria = categoria_info["categoria"]
        url_atual = categoria_info["url"]

        print(f"\nColetando categoria: {categoria}")

        while url_atual:
            print(f"Acessando página: {url_atual}")

            produtos_pagina, soup = extrair_produtos_da_pagina(url_atual, categoria)

            produtos_extraidos.extend(produtos_pagina)

            url_atual = obter_proxima_pagina(soup, url_atual)

            time.sleep(1)

    return produtos_extraidos


def salvar_csv(produtos, nome_arquivo):
    """
    Salva os dados coletados em um arquivo CSV.
    """
    colunas = [
        "categoria",
        "titulo",
        "preco",
        "disponibilidade",
        "avaliacao",
        "url_produto"
    ]

    with open(nome_arquivo, mode="w", encoding="utf-8-sig", newline="") as arquivo_csv:
        escritor = csv.DictWriter(
            arquivo_csv,
            fieldnames=colunas,
            delimiter=";"
        )

        escritor.writeheader()
        escritor.writerows(produtos)


def main():
    """
    Função principal do programa.
    """
    print("Iniciando coleta de dados...")

    produtos = coletar_dados()

    if produtos:
        salvar_csv(produtos, ARQUIVO_SAIDA)

        print("\nColeta finalizada com sucesso.")
        print(f"Total de produtos extraídos: {len(produtos)}")
        print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    else:
        print("\nNenhum produto foi extraído.")


if __name__ == "__main__":
    main()