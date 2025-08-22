# main_app.py

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import date

from database import *
try:
    from gerador_pdf import gerar_pdf_relatorio
except ImportError:
    def gerar_pdf_relatorio(id_caso, caminho):
        messagebox.showerror("Erro Crítico", "Arquivo gerador_pdf.py não encontrado.")
        return False

LISTA_ATIVIDADES_FICTICIAS = ["Coleta de amostras para classificação", "Preenchimento dos registros de portaria", "Variação nas taras de caminhões", "Modificação no tíquete de pesagem", "Controle de utilização dos formulários da moega", "Serviços de pesagem para terceiros"]
LISTA_SITUACAO = ["ABERTO", "FINALIZADO", "AGUARD. JUSTIF.", "PENDENTE"]

class PasswordPrompt(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.password = None
        super().__init__(parent, title)
    def body(self, master):
        tk.Label(master, text="Por segurança, digite sua senha:").pack(padx=20, pady=5)
        self.password_entry = tk.Entry(master, show="*"); self.password_entry.pack(padx=20, pady=5)
        return self.password_entry
    def apply(self):
        self.password = self.password_entry.get()

class LogScreen:
    def __init__(self, root):
        self.log_window = tk.Toplevel(root); self.log_window.title("Log de Exclusões de Relatórios"); self.log_window.geometry("800x500"); self.log_window.grab_set()
        log_frame = tk.LabelFrame(self.log_window, text="Registros", padx=10, pady=10); log_frame.pack(expand=True, fill="both", padx=10, pady=10)
        colunas = ('id', 'num_relatorio', 'titulo', 'usuario', 'data')
        self.tree_log = ttk.Treeview(log_frame, columns=colunas, show='headings'); self.tree_log.heading('id', text='ID'); self.tree_log.column('id', width=30); self.tree_log.heading('num_relatorio', text='Nº Relatório'); self.tree_log.column('num_relatorio', width=100); self.tree_log.heading('titulo', text='Título Excluído'); self.tree_log.column('titulo', width=250); self.tree_log.heading('usuario', text='Excluído Por'); self.tree_log.column('usuario', width=200); self.tree_log.heading('data', text='Data/Hora'); self.tree_log.column('data', width=150); self.tree_log.pack(expand=True, fill='both')
        self.carregar_logs()
    def carregar_logs(self):
        for i in self.tree_log.get_children(): self.tree_log.delete(i)
        for log in buscar_log_exclusoes(): self.tree_log.insert('', tk.END, values=log)

class ReportScreen:
    def __init__(self, root, id_caso, dados_usuario):
        self.id_caso, self.dados_usuario = id_caso, dados_usuario
        self.usuario_logado = dados_usuario[1] # Apenas o nome para fins de log de atividade
        self.id_atividade_selecionada = None
        self.report_window = tk.Toplevel(root); self.report_window.title("Detalhes do Relatório"); self.report_window.geometry("1000x800"); self.report_window.grab_set()
        header_frame = tk.LabelFrame(self.report_window, text="Cabeçalho do Relatório", padx=10, pady=10); header_frame.pack(fill="x", padx=10, pady=5)
        form_frame = tk.LabelFrame(self.report_window, text="Formulário da Atividade", padx=10, pady=10); form_frame.pack(fill="x", padx=10, pady=5)
        activities_frame = tk.LabelFrame(self.report_window, text="Atividades do Relatório", padx=10, pady=10); activities_frame.pack(expand=True, fill="both", padx=10, pady=5)
        tk.Label(header_frame, text="Título:").grid(row=0, column=0, sticky="w"); self.titulo_entry = tk.Entry(header_frame, state='readonly'); self.titulo_entry.grid(row=0, column=1, sticky="ew", padx=5)
        tk.Label(header_frame, text="Nº Relatório:").grid(row=0, column=2, sticky="w", padx=5); self.numero_entry = tk.Entry(header_frame, state='readonly'); self.numero_entry.grid(row=0, column=3, sticky="w", padx=5)
        tk.Label(header_frame, text="Situação:").grid(row=1, column=0, sticky="w", pady=5); self.situacao_entry = tk.Entry(header_frame, state='readonly'); self.situacao_entry.grid(row=1, column=1, sticky="ew", padx=5)
        header_frame.grid_columnconfigure(1, weight=1)
        tk.Label(form_frame, text="Atividade:").grid(row=0, column=0, sticky="w", pady=2); self.form_atividade_desc = ttk.Combobox(form_frame, values=LISTA_ATIVIDADES_FICTICIAS); self.form_atividade_desc.grid(row=0, column=1, columnspan=4, sticky="ew", padx=5)
        tk.Label(form_frame, text="Testes Realizados:").grid(row=1, column=0, sticky="w", pady=2); self.form_testes = tk.Entry(form_frame); self.form_testes.grid(row=1, column=1, columnspan=4, sticky="ew", padx=5)
        tk.Label(form_frame, text="Extensão Exames:").grid(row=2, column=0, sticky="w", pady=2); self.form_extensao = tk.Entry(form_frame); self.form_extensao.grid(row=2, column=1, sticky="ew", padx=5)
        tk.Label(form_frame, text="Critério Amostragem:").grid(row=2, column=2, sticky="w", padx=5); self.form_criterio = tk.Entry(form_frame); self.form_criterio.grid(row=2, column=3, columnspan=2, sticky="ew", padx=5)
        tk.Label(form_frame, text="Período/Situação:").grid(row=3, column=0, sticky="w", pady=2); self.form_periodo = tk.Entry(form_frame); self.form_periodo.grid(row=3, column=1, sticky="ew", padx=5)
        tk.Label(form_frame, text="Situação Atividade:").grid(row=3, column=2, sticky="w", padx=5); self.form_situacao = ttk.Combobox(form_frame, values=LISTA_SITUACAO); self.form_situacao.grid(row=3, column=3, columnspan=2, sticky="ew", padx=5)
        tk.Label(form_frame, text="Observação/Resumo:").grid(row=4, column=0, sticky="w", pady=2); self.form_observacao = tk.Entry(form_frame); self.form_observacao.grid(row=4, column=1, columnspan=4, sticky="ew", padx=5)
        novo_button = tk.Button(form_frame, text="Limpar (Nova)", command=self.handle_limpar_formulario); novo_button.grid(row=5, column=1, sticky="e", pady=10)
        deletar_button = tk.Button(form_frame, text="Deletar Atividade", command=self.handle_deletar_atividade, bg="#ff8c8c"); deletar_button.grid(row=5, column=2, sticky="e", padx=5)
        pdf_button = tk.Button(form_frame, text="Gerar PDF", command=self.handle_gerar_pdf); pdf_button.grid(row=5, column=3, sticky="e", padx=5)
        salvar_button = tk.Button(form_frame, text="Salvar Atividade", command=self.handle_salvar_atividade); salvar_button.grid(row=5, column=4, sticky="e", padx=5)
        form_frame.grid_columnconfigure(1, weight=1); form_frame.grid_columnconfigure(3, weight=1)
        colunas = ('id', 'atividade', 'realizado_por', 'data', 'situacao')
        self.tree_atividades = ttk.Treeview(activities_frame, columns=colunas, show='headings'); self.tree_atividades.heading('id', text='ID'); self.tree_atividades.column('id', width=30); self.tree_atividades.heading('atividade', text='Atividade'); self.tree_atividades.column('atividade', width=350); self.tree_atividades.heading('realizado_por', text='Realizado Por'); self.tree_atividades.column('realizado_por', width=150); self.tree_atividades.heading('data', text='Data'); self.tree_atividades.column('data', width=100); self.tree_atividades.heading('situacao', text='Situação'); self.tree_atividades.column('situacao', width=100); self.tree_atividades.pack(expand=True, fill="both")
        self.tree_atividades.bind("<<TreeviewSelect>>", self.on_activity_select)
        self.popular_dados()
    def handle_deletar_atividade(self):
        if self.id_atividade_selecionada is None: messagebox.showwarning("Aviso", "Por favor, selecione uma atividade na lista para deletar.", parent=self.report_window); return
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja deletar a atividade ID {self.id_atividade_selecionada}?", parent=self.report_window):
            if deletar_atividade_por_id(self.id_atividade_selecionada): messagebox.showinfo("Sucesso", "Atividade deletada.", parent=self.report_window); self.atualizar_lista_atividades(); self.handle_limpar_formulario()
            else: messagebox.showerror("Erro", "Ocorreu um erro ao deletar a atividade.", parent=self.report_window)
    def handle_gerar_pdf(self):
        caminho = filedialog.asksaveasfilename(title="Salvar Relatório", defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")], initialfile=f"Relatorio_{self.id_caso}.pdf")
        if caminho and gerar_pdf_relatorio(self.id_caso, caminho): messagebox.showinfo("Sucesso", f"PDF salvo em:\n{caminho}", parent=self.report_window)
    def handle_limpar_formulario(self):
        self.id_atividade_selecionada = None; self.form_atividade_desc.set(""); self.form_testes.delete(0, tk.END); self.form_extensao.delete(0, tk.END); self.form_criterio.delete(0, tk.END); self.form_periodo.delete(0, tk.END); self.form_situacao.set(""); self.form_observacao.delete(0, tk.END); self.form_atividade_desc.focus_set()
    def on_activity_select(self, event):
        selecionado = self.tree_atividades.focus();
        if not selecionado: return
        id_selecionado = self.tree_atividades.item(selecionado)['values'][0]; dados = buscar_atividade_por_id(id_selecionado)
        if dados: self.handle_limpar_formulario(); self.id_atividade_selecionada = id_selecionado; self.form_atividade_desc.set(dados.get("atividade_desc", "")); self.form_testes.insert(0, dados.get("testes_realizados", "")); self.form_extensao.insert(0, dados.get("extensao_exames", "")); self.form_criterio.insert(0, dados.get("criterio_amostragem", "")); self.form_periodo.insert(0, dados.get("periodo_situacao", "")); self.form_situacao.set(dados.get("situacao", "")); self.form_observacao.insert(0, dados.get("observacao_resumo", ""))
    def handle_salvar_atividade(self):
        if not self.form_atividade_desc.get(): messagebox.showwarning("Campo Obrigatório", "O campo 'Atividade' é obrigatório.", parent=self.report_window); return
        dados = {"atividade_desc": self.form_atividade_desc.get(), "testes_realizados": self.form_testes.get(), "extensao_exames": self.form_extensao.get(), "criterio_amostragem": self.form_criterio.get(), "periodo_situacao": self.form_periodo.get(), "situacao": self.form_situacao.get(), "observacao_resumo": self.form_observacao.get()}
        if self.id_atividade_selecionada is None:
            dados.update({"caso_id": self.id_caso, "realizado_por": self.usuario_logado, "data_registro": date.today().strftime("%Y-%m-%d"), "nao_conformidade": "", "reincidente": 0, "recomendacao": "", "data_p_solucao": ""})
            sucesso = salvar_atividade(dados)
        else: sucesso = atualizar_atividade(self.id_atividade_selecionada, dados)
        if sucesso: self.atualizar_lista_atividades(); self.handle_limpar_formulario()
        else: messagebox.showerror("Erro", "Não foi possível realizar a operação.", parent=self.report_window)
    def popular_dados(self):
        for entry in [self.titulo_entry, self.numero_entry, self.situacao_entry]: entry.config(state='normal'); entry.delete(0, tk.END)
        dados_caso = buscar_caso_por_id(self.id_caso)
        if dados_caso: self.titulo_entry.insert(0, dados_caso.get('titulo', '')); self.numero_entry.insert(0, dados_caso.get('numero_relatorio', '')); self.situacao_entry.insert(0, dados_caso.get('status', ''))
        for entry in [self.titulo_entry, self.numero_entry, self.situacao_entry]: entry.config(state='readonly')
        self.atualizar_lista_atividades()
    def atualizar_lista_atividades(self):
        for i in self.tree_atividades.get_children(): self.tree_atividades.delete(i)
        for atividade in buscar_atividades_por_caso_id(self.id_caso): self.tree_atividades.insert('', tk.END, values=atividade)

class MainScreen:
    def __init__(self, root, dados_usuario):
        self.root = root
        self.dados_usuario = dados_usuario
        self.usuario_codigo_logado, self.usuario_nome_logado, self.usuario_nivel_acesso = dados_usuario
        self.root.title(f"SIAI - Usuário: {self.usuario_nome_logado} (Nível: {self.usuario_nivel_acesso})")
        self.root.geometry("850x600")
        
        self.criar_menu()

        table_frame = tk.Frame(self.root, padx=10, pady=10); table_frame.pack(expand=True, fill="both")
        button_frame = tk.Frame(self.root, padx=10, pady=10); button_frame.pack(fill="x")
        colunas = ('id', 'relatorio', 'inicio', 'final', 'status', 'numero')
        self.tree = ttk.Treeview(table_frame, columns=colunas, show='headings'); self.tree.heading('id', text='ID'); self.tree.column('id', width=30); self.tree.heading('relatorio', text='Relatório'); self.tree.column('relatorio', width=250); self.tree.heading('inicio', text='Início'); self.tree.column('inicio', width=100); self.tree.heading('final', text='Final'); self.tree.column('final', width=100); self.tree.heading('status', text='Situação'); self.tree.column('status', width=100); self.tree.heading('numero', text='Nº Relatório'); self.tree.column('numero', width=100); self.tree.pack(expand=True, fill='both')
        self.carregar_casos()
        novo_button = tk.Button(button_frame, text="Novo Relatório", command=self.handle_novo_relatorio); novo_button.pack(side="left", padx=5)
        abrir_button = tk.Button(button_frame, text="Abrir Relatório", command=self.handle_abrir_relatorio); abrir_button.pack(side="left", padx=5)
        deletar_button = tk.Button(button_frame, text="Deletar Relatório", command=self.handle_deletar_relatorio, bg="#ff8c8c"); deletar_button.pack(side="left", padx=5)

    def criar_menu(self):
        menu_bar = tk.Menu(self.root); self.root.config(menu=menu_bar)
        arquivo_menu = tk.Menu(menu_bar, tearoff=0); menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu); arquivo_menu.add_command(label="Sair", command=self.root.quit)
        if self.usuario_nivel_acesso in ["Senior", "Manager"]:
            admin_menu = tk.Menu(menu_bar, tearoff=0); menu_bar.add_cascade(label="Administração", menu=admin_menu); admin_menu.add_command(label="Ver Log de Exclusões", command=self.abrir_tela_log)
    def abrir_tela_log(self):
        LogScreen(self.root)
    def carregar_casos(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for caso in buscar_casos(): self.tree.insert('', tk.END, values=caso)
    def handle_novo_relatorio(self):
        novo_id = adicionar_novo_caso("Novo Relatório (preencher)", "Auditoria", date.today().strftime("%Y-%m-%d"), "PLANEJADO")
        if novo_id: self.carregar_casos(); ReportScreen(self.root, novo_id, self.dados_usuario)
    def handle_abrir_relatorio(self):
        selecionado = self.tree.focus()
        if not selecionado: messagebox.showwarning("Aviso", "Por favor, selecione um relatório."); return
        id_caso = self.tree.item(selecionado)['values'][0]
        ReportScreen(self.root, id_caso, self.dados_usuario)
    def handle_deletar_relatorio(self):
        selecionado = self.tree.focus()
        if not selecionado: messagebox.showwarning("Aviso", "Por favor, selecione um relatório para deletar."); return
        id_caso = self.tree.item(selecionado)['values'][0]
        prompt = PasswordPrompt(self.root, title="Confirmação de Segurança")
        senha = prompt.password
        if not senha: return
        if not verificar_login(self.usuario_codigo_logado, senha): messagebox.showerror("Acesso Negado", "Senha incorreta."); return
        if messagebox.askyesno("CONFIRMAÇÃO FINAL", f"Você está prestes a DELETAR PERMANENTEMENTE o relatório ID {id_caso} e todas as suas atividades. Deseja continuar?"):
            if deletar_relatorio_e_registrar_log(id_caso, self.usuario_codigo_logado, self.usuario_nome_logado): messagebox.showinfo("Sucesso", "Relatório deletado com sucesso."); self.carregar_casos()
            else: messagebox.showerror("Erro", "Ocorreu um erro ao deletar o relatório.")

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self.login_window = tk.Toplevel(self.root); self.login_window.title("Login"); self.login_window.geometry("400x200")
        main_frame = tk.Frame(self.login_window, padx=10, pady=10); main_frame.pack(expand=True, fill="both")
        tk.Label(main_frame, text="Código:").grid(row=0, column=0, sticky="w", pady=5); self.codigo_combobox = ttk.Combobox(main_frame, state="readonly"); self.codigo_combobox.grid(row=0, column=1, sticky="ew")
        tk.Label(main_frame, text="Nome:").grid(row=1, column=0, sticky="w", pady=5); self.nome_entry = tk.Entry(main_frame, state="readonly"); self.nome_entry.grid(row=1, column=1, columnspan=2, sticky="ew")
        tk.Label(main_frame, text="Senha:").grid(row=2, column=0, sticky="w", pady=5); self.senha_entry = tk.Entry(main_frame, show="*"); self.senha_entry.grid(row=2, column=1, columnspan=2, sticky="ew")
        login_button = tk.Button(main_frame, text="Login", command=self.handle_login); login_button.grid(row=3, column=1, sticky="e", pady=10)
        cancel_button = tk.Button(main_frame, text="Cancelar", command=self.root.destroy); cancel_button.grid(row=3, column=2, sticky="w", padx=5)
        main_frame.grid_columnconfigure(1, weight=1)
        self.carregar_usuarios()
        self.codigo_combobox.bind("<<ComboboxSelected>>", self.on_user_select)
    def carregar_usuarios(self):
        self.mapa_usuarios = {user[0]: user[1] for user in buscar_usuarios()}; self.codigo_combobox['values'] = list(self.mapa_usuarios.keys())
    def on_user_select(self, event):
        nome = self.mapa_usuarios.get(self.codigo_combobox.get(), ""); self.nome_entry.config(state="normal"); self.nome_entry.delete(0, tk.END); self.nome_entry.insert(0, nome); self.nome_entry.config(state="readonly")
    def handle_login(self):
        codigo = self.codigo_combobox.get(); senha = self.senha_entry.get()
        if not codigo or not senha: messagebox.showerror("Erro de Login", "Código e Senha são obrigatórios."); return
        dados_usuario = verificar_login(codigo, senha)
        if dados_usuario: self.login_window.destroy(); self.root.deiconify(); MainScreen(self.root, dados_usuario) 
        else: messagebox.showerror("Erro de Login", "Código ou Senha inválidos.")

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    app = LoginScreen(root)
    root.mainloop()