# PDF Cuter

Aplicação desktop para separar as páginas de um arquivo PDF e salvar cada uma
delas como um novo arquivo individual.

O projeto foi desenvolvido em Python com uma interface gráfica leve, suporte a
arrastar e soltar, processamento em segundo plano e cancelamento seguro.

## Funcionalidades

- Seleção de PDF por janela de arquivos.
- Suporte a arrastar e soltar arquivos PDF.
- Exibição do nome do arquivo e da quantidade de páginas.
- Separação de todas as páginas em arquivos PDF individuais.
- Numeração automática com três dígitos:

  ```text
  documento_pagina_001.pdf
  documento_pagina_002.pdf
  documento_pagina_003.pdf
  ```

- Criação automática da pasta de resultados na área de Downloads.
- Processamento em `threading.Thread`, mantendo a interface responsiva.
- Cancelamento cooperativo usando `threading.Event`.
- Remoção dos arquivos parciais quando o processamento é cancelado.
- Tema claro como padrão.
- Alternância funcional entre tema claro e escuro.
- Janela de ajuda com informações do criador.
- Link clicável para o portfólio: [me.gaqtech.dev](https://me.gaqtech.dev).
- Tratamento de PDFs inválidos, vazios, protegidos ou inexistentes.
- Geração de executável Windows com PyInstaller.

## Tecnologias

- Python 3.13+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — interface gráfica.
- [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) — arrastar e soltar.
- [pypdf](https://github.com/py-pdf/pypdf) — leitura e separação dos PDFs.
- `threading` e `threading.Event` — processamento e cancelamento.
- [uv](https://docs.astral.sh/uv/) — gerenciamento do ambiente e dependências.
- [PyInstaller](https://pyinstaller.org/) — geração do executável Windows.

## Estrutura do projeto

```text
pdf_cuter/
├── .gitignore              # Arquivos ignorados pelo Git
├── .python-version         # Versão do Python usada pelo uv
├── AGENTS.md               # Diretrizes para desenvolvimento
├── LAUDO.pdf               # PDF local de exemplo
├── README.md               # Documentação do projeto
├── build.ps1               # Script PowerShell para gerar o executável
├── main.py                 # Interface gráfica e fluxo da aplicação
├── pdf_service.py          # Leitura, validação e separação de PDFs
├── pyproject.toml          # Metadados e dependências do projeto
├── tests/
│   └── test_pdf_service.py # Testes do serviço de separação
├── build/                  # Gerado pelo PyInstaller; não versionar
├── dist/                   # Executável gerado; não versionar
└── .venv/                  # Ambiente virtual gerenciado pelo uv
```

As pastas `build/`, `dist/` e `.venv/` são geradas localmente e ficam fora do
controle de versão.

## Requisitos

- Windows 10 ou superior para o fluxo de build documentado.
- Python 3.13 ou superior.
- PowerShell.
- `uv` instalado e disponível no `PATH`.

Para verificar as ferramentas:

```powershell
python --version
uv --version
```

## Instalação para desenvolvimento

Na raiz do projeto, execute:

```powershell
uv sync
```

Esse comando cria o ambiente virtual `.venv` e instala as dependências de
execução, testes e empacotamento.

## Executar a aplicação

```powershell
uv run python main.py
```

Também é possível executar diretamente pelo Python do ambiente virtual:

```powershell
.\.venv\Scripts\python.exe main.py
```

## Como usar

1. Abra a aplicação.
2. Selecione um PDF pelo botão `Selecionar PDF` ou arraste um arquivo para a
   área indicada.
3. Confira o nome do arquivo e a quantidade de páginas exibida.
4. Clique em `Executar`.
5. Aguarde a conclusão ou clique em `Cancelar` durante o processamento.
6. Use o botão `Ajuda` para visualizar as informações do criador e acessar o
   portfólio.

O modo claro é carregado por padrão. O controle `Modo escuro` altera o tema
imediatamente, sem reiniciar a aplicação.

## Local dos arquivos gerados

Os resultados são salvos em:

```text
Downloads/PDF_CUTER_RESULT/<nome-do-pdf>/
```

Exemplo:

```text
Downloads/
└── PDF_CUTER_RESULT/
    └── LAUDO/
        ├── LAUDO_pagina_001.pdf
        ├── LAUDO_pagina_002.pdf
        └── LAUDO_pagina_003.pdf
```

Se uma pasta com o mesmo nome já existir, uma nova pasta será criada com
sufixo numérico, como `LAUDO_2`, evitando sobrescrever resultados anteriores.

O PDF original não é alterado, movido ou removido.

## Cancelamento

O processamento usa uma thread separada para não bloquear a interface. O
botão `Cancelar` sinaliza um `threading.Event`, que é verificado entre as
páginas.

Quando o cancelamento é solicitado:

- a página atual termina, quando aplicável;
- nenhuma nova página é processada;
- os arquivos parciais são removidos;
- a pasta incompleta do processamento também é removida.

## Testes

Execute a suíte completa com:

```powershell
uv run pytest
```

Os testes cobrem:

- leitura da quantidade de páginas;
- separação de múltiplas páginas;
- numeração dos arquivos;
- PDFs de uma página;
- arquivos inexistentes e não-PDF;
- PDF inválido;
- criação de pastas exclusivas por processamento;
- limpeza de arquivos após cancelamento.

## Gerar o executável Windows

O script `build.ps1` automatiza a sincronização das dependências e a execução
do PyInstaller.

Build normal:

```powershell
.\build.ps1
```

Build removendo as saídas anteriores:

```powershell
.\build.ps1 -Clean
```

O executável único será criado em:

```text
dist/PDF-Cuter.exe
```

O build usa `--onefile` e `--windowed`: o cliente recebe apenas um arquivo
`.exe`, sem precisar transportar uma pasta adicional. Os recursos necessários
do `tkinterdnd2` são incorporados ao executável.

### Voltar para o formato onedir

Se no futuro for necessário distribuir uma pasta com o executável e seus
arquivos internos, remova a opção `--onefile` do `build.ps1`. Nesse formato, o
resultado será gerado em:

```text
dist/PDF-Cuter/PDF-Cuter.exe
```

Nesse caso, a pasta `dist/PDF-Cuter/` deverá ser enviada completa ao cliente.

Se o PowerShell bloquear a execução do script por política local, execute a
permissão apenas para a sessão atual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build.ps1
```

## Convenções de desenvolvimento

- Use quatro espaços para indentação Python.
- Mantenha funções pequenas e com responsabilidades claras.
- Adicione ou atualize testes para cada alteração de comportamento.
- Não atualize widgets diretamente a partir da thread de processamento.
- Use `after()` para enviar atualizações à thread principal da GUI.
- Valide caminhos, extensões e entradas externas.
- Não versionar credenciais, PDFs privados, `.venv/`, `build/` ou `dist/`.

## Licença e autoria

Criado por **Gustavo de Amorim Quinup**.

Portfólio: [me.gaqtech.dev](https://me.gaqtech.dev)
