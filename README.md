# TGV Max Finder Avançado

Uma aplicação desktop para buscar viagens TGV Max diretas ou com conexões, utilizando dados da SNCF Open Data.

## Funcionalidades

* Busca de viagens TGV Max por Origem e Destino.
* Suporte para busca de viagens com até 1 conexão (expansível).
* Histórico das últimas N pesquisas.
* Interface gráfica amigável construída com CustomTkinter.

## Configuração e Instalação

1.  **Pré-requisitos:**
    * Python 3.7+
    * Git (opcional, para clonar, mas recomendado)

2.  **Clonar o repositório (opcional):**
    ```bash
    git clone URL_DO_SEU_REPOSITORIO_AQUI
    cd tgvmax-finder
    ```

3.  **Criar e ativar um ambiente virtual:**
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

4.  **Instalar as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## Como Rodar

Com o ambiente virtual ativado e as dependências instaladas, execute:

```bash
python src/main.py