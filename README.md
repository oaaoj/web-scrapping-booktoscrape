# Web Scraping de Preços com Python (Atividade Business Intelligence)

Este projeto foi desenvolvido com o objetivo de realizar um web scraping em um website com uma estrutura semelhante à de um e-commerce, de onde extraímos informações de produtos e preços de forma automatizada.

A aplicação foi construída em Python, utlizando as biblioteas requests e BeautifulSoup para acessar, interpretar e extrair dados do HTML das páginas. Os dados coletados são armazenados em um arquivo .CSV, possibilitando futuras análises em alguma ferramenta de BI.

## Website escolhido para o Projeto

O site escolhido para esta atividade foi o Books To Scrape:

https://books.toscrape.com/

Este site foi criado especificamente para práticas de web scraping, o que o torna um ambiente adequado para fins educacionais, dessa forma, evita de extrairmos dados indevidos.

O Books to Scrape é um site que simula uma loja virtual de livros, contendo categorias, listagem de produtos, preços, disponibilidade de estoque etc. Sua estrutura é muito semelhante a de um site brasileiro de livros:

https://www.estantevirtual.com.br/

Porém, o Books to Scrape possui uma estrutura mais simples e adequada para fins didáticos.

## Estrutura HTML do website < https://books.toscrape.com/ >

Antes de desenvolver o script para extração, é importante realizarmos uma análise da estrutura HTML do site que estamos estudando. Essa etapa é feita de maneira bastante simples, através da ferramenta "inspecionar" do navegador, que permite que visualizemos o código - fonte da página e identifiquemos onde as informações dos produtos estão localizadas.

A estrutura principal dos produtos segue um padrão HTML repetido. Cada produto aparece em um bloco individual, contendo as principais informações necessárias para a coleta de dados. Visualmente, cada item apresenta o nome do livro, o preço, a disponibilidade e um botão de adição ao carrinho.

Inspecionando a estrutura HTML, é possível identificar os seguintes elementos relevantes:


| Informação          | Localização no HTML                        | Seletor utilizado                         |
| ------------------- | ------------------------------------------ | ----------------------------------------- |
| Produto             | Bloco principal do produto                 | `article.product_pod`                     |
| Título              | Tag `a` dentro de `h3`                     | `h3 a`                                    |
| Preço               | Tag `p` com classe `price_color`           | `p.price_color`                           |
| Disponibilidade     | Tag `p` com classes `instock availability` | `p.instock.availability`                  |
| Avaliação           | Tag `p` com classe `star-rating`           | `p.star-rating`                           |
| Link do produto     | Atributo `href` da tag `a`                 | `h3 a[href]`                              |
| Próxima página      | Link dentro da classe `next`               | `li.next a`                               |
| Categorias          | Menu lateral do site                       | `div.side_categories ul.nav-list ul li a` |

## Exemplo da estrutura HTML de um produto

Abaixo está um exemplo simplificado da estrutura HTML de um produto dentro do site. Esse bloco representa um item da listagem de livros e contém as informações que serão utilizadas no processo de extração dos dados.

```html
<article class="product_pod">
    <div class="image_container">
        <a href="catalogue/a-light-in-the-attic_1000/index.html">
            <img src="..." alt="A Light in the Attic">
        </a>
    </div>

    <p class="star-rating Three">
        <i class="icon-star"></i>
    </p>

    <h3>
        <a href="catalogue/a-light-in-the-attic_1000/index.html" 
           title="A Light in the Attic">
           A Light in the ...
        </a>
    </h3>

    <div class="product_price">
        <p class="price_color">£51.77</p>
        <p class="instock availability">In stock</p>
    </div>
</article> 
```

Com essa análise, foi possível definir os seletores que serão utilizados no código Python para localizar e extrair os dados automaticamente.

## Desenvolvimento do script em Python 

Após a análise da estrutura HTML do site, foi iniciado o desenvolvimento do script que será o responsável pela extração dos dados. A aplicação, como dito antes, será construída em Python e utilizando duas bibliotecas principais: Requests e BeautifulSoup.

A biblioteca requests será utilizada para realizar as requisições HTTP às páginas do site. Com ela, o script consegue acessar o conteúdo HTML de cada página, simulando uma navegação básica. Já a biblioteca BeautifulSoup será utilizada para interpretar esse HTML e localizar os elementos onde estão armazenadas as informações dos produtos.

O script foi construído seguindo uma lógica organizada em Etapas. Primeiramente, o código irá acessar a página inicial do website e coletar os links das categorias disponíveis no menu lateral. Em seguida, o algoritmo irá percorrer cada categoria individualmente, acessando suas páginas e extraindo os dados de cada produto listado. 

Para cada produto encontrado, o script coleta as seguintes informações:

* Categoria do Produto;
* Título do Livro;
* Preço;
* Disponibilidade em Estoque;
* Avaliação;
* Link da página individual do Produto.

A coleta dessa informações dos produtos será feita utilizando os seletores que localizamos na etapa anterior, onde entedemos a estrutura do site em que estamos trabalhando. Cada produto é localizado pelo seletor article.product_pod. Dentro desse bloco, o script busca o título em h3 a, o preço em p.price_color, a dispobilidade em p.instock.availability e a avaliação em p.star-rating.

Além disso, implementamos uma rotina para tratar a paginação do site. Onde, ao final de cada página, o script verifica se existe o elemento li.next a, que indica a presença de uma próxima página. Caso esse elemento exista, o programa acessa a próxima página e continua o processo. Do contrário, a coleta da categoria é finalizada e o algoritmo passa para a próxima categoria.

Com a finalidade de tornar a coleta mais controlada e respeitosa ao servidor do site, alguns cuidados foram adicionados, como o uso de User - Agent, onde são tratados erros nas requisições e pausa entre os acessos às páginas. Uma boa prática também é a verificação do arquivo robots.txt, porém, esse site não dispõe desse arquivo para verificação, então ele foi ignorado.

Ao final do processo, os dados são extraídos e armazenados em um arquivo CSV com nome de 'produtos_books.csv'.

Script desenvolvido para extraírmos os dados:

``` python
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
```

Abaixo, as 10 primeiras linhas do arquivo .csv, que pode ser acesseado dentro do repositório:

```csv
categoria;titulo;preco;disponibilidade;avaliacao;url_produto
Travel;It's Only the Himalayas;Â£45.17;In stock;Two;https://books.toscrape.com/catalogue/its-only-the-himalayas_981/index.html
Travel;Full Moon over Noahâ's Ark: An Odyssey to Mount Ararat and Beyond;Â£49.43;In stock;Four;https://books.toscrape.com/catalogue/full-moon-over-noahs-ark-an-odyssey-to-mount-ararat-and-beyond_811/index.html
Travel;See America: A Celebration of Our National Parks & Treasured Sites;Â£48.87;In stock;Three;https://books.toscrape.com/catalogue/see-america-a-celebration-of-our-national-parks-treasured-sites_732/index.html
Travel;Vagabonding: An Uncommon Guide to the Art of Long-Term World Travel;Â£36.94;In stock;Two;https://books.toscrape.com/catalogue/vagabonding-an-uncommon-guide-to-the-art-of-long-term-world-travel_552/index.html
Travel;Under the Tuscan Sun;Â£37.33;In stock;Three;https://books.toscrape.com/catalogue/under-the-tuscan-sun_504/index.html
Travel;A Summer In Europe;Â£44.34;In stock;Two;https://books.toscrape.com/catalogue/a-summer-in-europe_458/index.html
Travel;The Great Railway Bazaar;Â£30.54;In stock;One;https://books.toscrape.com/catalogue/the-great-railway-bazaar_446/index.html
Travel;A Year in Provence (Provence #1);Â£56.88;In stock;Four;https://books.toscrape.com/catalogue/a-year-in-provence-provence-1_421/index.html
Travel;The Road to Little Dribbling: Adventures of an American in Britain (Notes From a Small Island #2);Â£23.21;In stock;One;https://books.toscrape.com/catalogue/the-road-to-little-dribbling-adventures-of-an-american-in-britain-notes-from-a-small-island-2_277/index.html
Travel;Neither Here nor There: Travels in Europe;Â£38.95;In stock;Three;https://books.toscrape.com/catalogue/neither-here-nor-there-travels-in-europe_198/index.html
```
## Desafios enfretados durante o Desenvolvimento

A principal delas foi compreender corretamente a estrutura HTML do site, pois escolher um elemento incorreto, faria com que a extração viesse errada e prejudicaria a qualidade dos dados.

Outra dificuldade foi lidar com a paginação do site, pois nem todos estavam disponíveis em uma única página, então foi necessário criar uma função que olhava justamente para o botão de próxima página. Além disso, foi necessário tratar alguns links que não apareciam com o endereço completo do site. E, para contornar essa situação, foi utilizada a função urljoin, que permitiu transformar esses caminhos relativos em URLs completas.

# Conclusão

O desenvolvimento da aplicação permitiu compreender, na prática, as principais etapas de um processo de web scraping. Inicialmente, foi feita a análise da estrutura HTML do site, identificando os elementos que continham as informações relevantes dos produtos. Em seguida, foi desenvolvido um script em Python para automatizar a extração desses dados.

A utilização das bibliotecas requests e BeautifulSoup possibilitou acessar as páginas do site, interpretar o conteúdo HTML e coletar informações como categoria, título, preço, disponibilidade, avaliação e link do produto. A implementação da paginação permitiu que o script percorresse múltiplas páginas dentro das categorias, tornando a coleta mais completa.

Como resultado, foi gerado um arquivo CSV contendo os dados extraídos, permitindo que essas informações sejam analisadas posteriormente em outras ferramentas. Assim, o projeto atendeu ao objetivo proposto, demonstrando como Python pode ser utilizado para automatizar a coleta de dados em páginas web de forma organizada e estruturada.

