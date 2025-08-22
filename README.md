# Gerenciador de Tarefas de Auditoria (SIAI)

Este é um sistema de desktop completo desenvolvido em Python para gerenciar tarefas, atividades e relatórios relacionados a processos de auditoria interna. O projeto foi construído do zero, abrangendo desde a lógica de banco de dados até a interface gráfica do usuário.

## Funcionalidades Principais
- **Sistema de Login Seguro:** Autenticação de múltiplos usuários com senhas criptografadas (hash).
- **Hierarquia de Acesso:** Níveis de usuário (ex: Junior, Manager) que controlam o acesso a funcionalidades críticas.
- **Gerenciamento de Relatórios (CRUD):**
    - Criação de novos relatórios com numeração sequencial e automática por ano (ex: `2025.001`).
    - Visualização e listagem de todos os relatórios existentes.
    - Exclusão segura de relatórios, com pedido de senha e registro em log de auditoria.
- **Gerenciamento de Atividades (CRUD):**
    - Adição, visualização, edição e exclusão de atividades dentro de cada relatório.
    - Formulário detalhado com campos de texto e listas de seleção (dropdowns).
- **Emissão de Relatórios em PDF:** Geração de um documento PDF profissional com o resumo das atividades da auditoria.
- **Controle de Versão:** Todo o histórico de desenvolvimento é gerenciado com Git e hospedado no GitHub.

## Tecnologias Utilizadas
* **Linguagem:** Python 3
* **Interface Gráfica (GUI):** Tkinter
* **Banco de Dados:** SQLite3
* **Geração de PDF:** ReportLab
* **Controle de Versão:** Git & GitHub

## Como Executar o Projeto

1.  **Clone o Repositório**
    ```bash
    git clone [https://github.com/Krsoliveira/gerenciador-de-tarefas.git](https://github.com/Krsoliveira/gerenciador-de-tarefas.git)
    cd gerenciador-de-tarefas
    ```
2.  **Crie e Ative um Ambiente Virtual**
    ```bash
    # Criar
    python -m venv gerenciador_tarefas
    # Ativar (Windows)
    .\gerenciador_tarefas\Scripts\activate
    ```
3.  **Instale as Dependências**
    ```bash
    pip install reportlab
    ```
4.  **Inicialize o Banco de Dados**
    Execute o `database.py` uma vez para criar o banco de dados e os dados de exemplo:
    ```bash
    python database.py
    ```
5.  **Inicie a Aplicação**
    ```bash
    python main_app.py
    ```