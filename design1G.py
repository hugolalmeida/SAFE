import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pandas as pd
import os
from pathlib import Path
import threading
import uuid


class ExcelMergerApp:
    def __init__(self, root):
        self.root = root
        self.manual_selection = tk.BooleanVar(value=False)
        self.setup_window()
        self.create_widgets()
        self.df1_columns = []
        self.df2_columns = []
        
    def setup_window(self):
        """Configura a janela principal com design moderno usando ttkbootstrap"""
        self.root.title("SAFE - Sistema de Alocação e Formatação de Elementos")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.root.winfo_screenheight() // 2) - (650 // 2)
        self.root.geometry(f"700x650+{x}+{y}")
        
    def create_widgets(self):
        """Cria interface moderna com ttkbootstrap"""
        # Aplica o tema 'flatly'
        style = ttk.Style("flatly")
        
        # Configura estilos personalizados
        style.configure('Custom.TButton', font=('Segoe UI', 10, 'bold'), background='#3498db', foreground='white')
        style.configure('Success.TLabel', font=('Segoe UI', 10), foreground='#2ecc71')
        style.configure('Error.TLabel', font=('Segoe UI', 10), foreground='#e74c3c')
        style.configure('Info.TLabel', font=('Segoe UI', 10), foreground='#34495e')
        style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 11), foreground='#34495e')
        
        # Canvas e scrollbar para scroll completo
        canvas = ttk.Canvas(self.root, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview, bootstyle="primary")
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal com padding
        main_frame = ttk.Frame(scrollable_frame, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        row = 0
        
        # Cabeçalho moderno
        self.create_header(main_frame, row)
        row += 2
        
        # Seção de arquivos
        self.create_file_sections(main_frame, row)
        row += 6
        
        # Configurações de cabeçalho
        self.create_header_config_section(main_frame, row)
        row += 2
        
        # Botão de carregar colunas
        self.create_preview_button(main_frame, row)
        row += 2
        
        # Seção de configurações avançada
        self.create_advanced_config_section(main_frame, row)
        row += 8
        
        # Botões de ação
        self.create_action_buttons(main_frame, row)
        row += 2
        
        # Barra de progresso e status
        self.create_progress_section(main_frame, row)
        
        # Bind mouse wheel para scroll
        self.bind_mousewheel(canvas)
        
    def bind_mousewheel(self, canvas):
        """Habilita scroll com mouse wheel"""
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
    def create_header(self, parent, row):
        """Cria cabeçalho moderno"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="🔗 S.A.F.E", style='Header.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                 text="Combine dados de múltiplas colunas entre planilhas Excel",
                                 style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
    def create_file_sections(self, parent, row):
        """Cria seções de seleção de arquivos com design moderno"""
        # Frame origem
        origem_frame = ttk.LabelFrame(parent, text="📁 Arquivo Origem (fonte dos dados)", padding="15")
        origem_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        origem_frame.columnconfigure(0, weight=1)
        
        self.entrada_arquivo1 = ttk.Entry(origem_frame, font=('Segoe UI', 10))
        self.entrada_arquivo1.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        btn_origem = ttk.Button(origem_frame, text="Selecionar", 
                               command=self.selecionar_arquivo1, style='Custom.TButton', width=15)
        btn_origem.grid(row=0, column=1)
        
        # Frame destino
        destino_frame = ttk.LabelFrame(parent, text="📋 Arquivo Destino (receberá os dados)", padding="15")
        destino_frame.grid(row=row+2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        destino_frame.columnconfigure(0, weight=1)
        
        self.entrada_arquivo2 = ttk.Entry(destino_frame, font=('Segoe UI', 10))
        self.entrada_arquivo2.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        btn_destino = ttk.Button(destino_frame, text="Selecionar", 
                                command=self.selecionar_arquivo2, style='Custom.TButton', width=15)
        btn_destino.grid(row=0, column=1)
        
    def create_header_config_section(self, parent, row):
        """Cria seção de configurações de cabeçalho"""
        skip_frame = ttk.LabelFrame(parent, text="Configurações de Cabeçalho", padding="15")
        skip_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        skip_frame.columnconfigure(1, weight=1)
        skip_frame.columnconfigure(3, weight=1)
        
        ttk.Label(skip_frame, text="Pular linhas - Origem:", style='Info.TLabel').grid(row=0, column=0, sticky=tk.W)
        self.spin_skip1 = ttk.Spinbox(skip_frame, from_=0, to=100, width=10, font=('Segoe UI', 10))
        self.spin_skip1.grid(row=0, column=1, padx=(5, 20))
        self.spin_skip1.set(0)
        
        ttk.Label(skip_frame, text="Destino:", style='Info.TLabel').grid(row=0, column=2, sticky=tk.W)
        self.spin_skip2 = ttk.Spinbox(skip_frame, from_=0, to=100, width=10, font=('Segoe UI', 10))
        self.spin_skip2.grid(row=0, column=3, padx=(5, 0))
        self.spin_skip2.set(0)
        
    def create_advanced_config_section(self, parent, row):
        """Cria seção de configurações avançada com seleção múltipla"""
        self.config_frame = ttk.LabelFrame(parent, text="⚙️ Configurações Avançadas", padding="20")
        self.config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        self.config_frame.columnconfigure(1, weight=1)
        
        current_row = 0
        
        # Coluna chave (modo automático)
        self.label_chave_auto = ttk.Label(self.config_frame, 
                                         text="🔑 Coluna-chave (comum aos dois arquivos):", 
                                         style='Info.TLabel')
        self.label_chave_auto.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.combo_chave = ttk.Combobox(self.config_frame, width=40, state="readonly", 
                                       font=('Segoe UI', 10))
        self.combo_chave.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        current_row += 1
        
        # Colunas chave (modo manual)
        self.label_chave_origem = ttk.Label(self.config_frame, 
                                           text="🔑 Coluna-chave (Arquivo Origem):", 
                                           style='Info.TLabel')
        self.label_chave_origem.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.combo_chave_origem = ttk.Combobox(self.config_frame, width=40, state="readonly", 
                                             font=('Segoe UI', 10))
        self.combo_chave_origem.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        current_row += 1
        
        self.label_chave_destino = ttk.Label(self.config_frame, 
                                            text="🔑 Coluna-chave (Arquivo Destino):", 
                                            style='Info.TLabel')
        self.label_chave_destino.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.combo_chave_destino = ttk.Combobox(self.config_frame, width=40, state="readonly", 
                                               font=('Segoe UI', 10))
        self.combo_chave_destino.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        current_row += 1
        
        # Separador
        ttk.Separator(self.config_frame, bootstyle="primary").grid(row=current_row, column=0, columnspan=2, 
                                                                 sticky=(tk.W, tk.E), pady=15)
        current_row += 1
        
        # Seleção múltipla de colunas
        ttk.Label(self.config_frame, text="📋 Colunas a copiar (seleção múltipla):", 
                 style='Info.TLabel').grid(row=current_row, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        ttk.Label(self.config_frame, text="Aperte Ctrl + Click para múltiplas seleções", 
                 font=("Segoe UI", 8, "italic"), foreground="#7f8c8d").grid(
            row=current_row + 1, column=0, sticky=(tk.W), pady=(0, 5))
        
        # Frame para listbox com scrollbar
        list_frame = ttk.Frame(self.config_frame)
        list_frame.grid(row=current_row, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), 
                       padx=(10, 0), pady=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Listbox com scrollbar para seleção múltipla
        self.listbox_colunas = tk.Listbox(list_frame, selectmode=tk.EXTENDED, 
                                         height=6, font=('Segoe UI', 10))
        scrollbar_list = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, bootstyle="primary")
        
        self.listbox_colunas.configure(yscrollcommand=scrollbar_list.set)
        scrollbar_list.configure(command=self.listbox_colunas.yview)
        
        self.listbox_colunas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_list.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        current_row += 2
        
        # Botões de seleção rápida
        btn_frame = ttk.Frame(self.config_frame)
        btn_frame.grid(row=current_row, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 15))
        
        ttk.Button(btn_frame, text="Selecionar Todas", 
                  command=self.selecionar_todas_colunas, style='Custom.TButton').pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Limpar Seleção", 
                  command=self.limpar_selecao_colunas, style='Custom.TButton').pack(side=tk.LEFT)
        
        # Inicialmente, esconde os campos de seleção manual
        self.toggle_manual_selection()
        
    def toggle_manual_selection(self):
        """Mostra ou esconde os campos de seleção manual com base no checkbox"""
        if self.manual_selection.get():
            self.label_chave_auto.grid_remove()
            self.combo_chave.grid_remove()
            self.label_chave_origem.grid()
            self.combo_chave_origem.grid()
            self.label_chave_destino.grid()
            self.combo_chave_destino.grid()
        else:
            self.label_chave_auto.grid()
            self.combo_chave.grid()
            self.label_chave_origem.grid_remove()
            self.combo_chave_origem.grid_remove()
            self.label_chave_destino.grid_remove()
            self.combo_chave_destino.grid_remove()
    
    def create_preview_button(self, parent, row):
        """Cria checkbox e botão de carregar colunas"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        self.manual_check = ttk.Checkbutton(button_frame, text="Seleção Manual de Colunas-Chave", 
                                          variable=self.manual_selection, bootstyle="primary", 
                                          command=self.toggle_manual_selection)
        self.manual_check.pack(pady=(0, 10))
        
        self.btn_preview = ttk.Button(button_frame, text="🔍 Carregar Colunas", 
                                    command=self.preview_columns, style='Custom.TButton', 
                                    width=20, state="disabled")
        self.btn_preview.pack()
    
    def create_action_buttons(self, parent, row):
        """Cria botões de ação com design moderno"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.btn_execute = ttk.Button(button_frame, text="🚀 Executar Vinculação", 
                                     command=self.executar_comparacao, style='Custom.TButton', 
                                     width=20, state="disabled")
        self.btn_execute.pack(side=tk.LEFT, padx=10)
        
        self.label_contador = ttk.Label(button_frame, text="", style='Info.TLabel')
        self.label_contador.pack(side=tk.LEFT, padx=20)
        
    def create_progress_section(self, parent, row):
        """Cria seção de progresso e status"""
        self.progress = ttk.Progressbar(parent, mode='indeterminate', length=400, bootstyle="primary")
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_var = tk.StringVar(value="📋 Selecione os arquivos para começar")
        self.status_label = ttk.Label(parent, textvariable=self.status_var, style='Info.TLabel')
        self.status_label.grid(row=row+1, column=0, columnspan=3, pady=5)
        
    def selecionar_todas_colunas(self):
        """Seleciona todas as colunas na listbox"""
        self.listbox_colunas.select_set(0, tk.END)
        self.atualizar_contador_colunas()
        
    def limpar_selecao_colunas(self):
        """Limpa seleção de colunas"""
        self.listbox_colunas.selection_clear(0, tk.END)
        self.atualizar_contador_colunas()
        
    def atualizar_contador_colunas(self):
        """Atualiza contador de colunas selecionadas"""
        selecionadas = len(self.listbox_colunas.curselection())
        if selecionadas == 0:
            self.label_contador.config(text="")
        elif selecionadas == 1:
            self.label_contador.config(text="📊 1 coluna selecionada", style='Info.TLabel')
        else:
            self.label_contador.config(text=f"📊 {selecionadas} colunas selecionadas", style='Info.TLabel')
            
    def selecionar_arquivo1(self):
        """Seleciona o arquivo origem"""
        caminho = filedialog.askopenfilename(
            title="Selecionar arquivo ORIGEM",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if caminho:
            self.entrada_arquivo1.delete(0, tk.END)
            self.entrada_arquivo1.insert(0, caminho)
            self.validar_arquivo(caminho, 1)
            self.check_ready_state()
            
    def selecionar_arquivo2(self):
        """Seleciona o arquivo destino"""
        caminho = filedialog.askopenfilename(
            title="Selecionar arquivo DESTINO",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if caminho:
            self.entrada_arquivo2.delete(0, tk.END)
            self.entrada_arquivo2.insert(0, caminho)
            self.validar_arquivo(caminho, 2)
            self.check_ready_state()
            
    def validar_arquivo(self, caminho, numero):
        """Valida se o arquivo existe e é legível"""
        try:
            if not os.path.exists(caminho):
                raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
                
            if caminho.lower().endswith('.csv'):
                pd.read_csv(caminho, nrows=1)
            else:
                pd.read_excel(caminho, nrows=1)
                
            self.status_var.set(f"✅ Arquivo {numero} carregado com sucesso!")
            self.status_label.configure(style='Success.TLabel')
            
        except Exception as e:
            messagebox.showerror("❌ Erro no Arquivo", 
                               f"Erro ao validar arquivo {numero}:\n{str(e)}", 
                               parent=self.root)
            self.status_var.set(f"❌ Erro no arquivo {numero}")
            self.status_label.configure(style='Error.TLabel')
            
    def check_ready_state(self):
        """Verifica se pode habilitar os botões"""
        arquivo1_ok = bool(self.entrada_arquivo1.get().strip())
        arquivo2_ok = bool(self.entrada_arquivo2.get().strip())
        
        if arquivo1_ok and arquivo2_ok:
            self.btn_preview.config(state="normal")
            self.status_var.set("✅ Arquivos prontos! Clique em 'Carregar Colunas'")
            self.status_label.configure(style='Success.TLabel')
        else:
            self.btn_preview.config(state="disabled")
            self.btn_execute.config(state="disabled")
            
    def preview_columns(self):
        """Carrega e exibe as colunas disponíveis"""
        try:
            self.progress.start()
            self.status_var.set("⏳ Carregando colunas...")
            self.status_label.configure(style='Info.TLabel')
            
            thread = threading.Thread(target=self._load_columns_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("❌ Erro", f"Erro ao carregar colunas:\n{str(e)}", parent=self.root)
            self.status_var.set("❌ Erro ao carregar colunas")
            self.status_label.configure(style='Error.TLabel')
            
    def _load_columns_thread(self):
        """Thread para carregar colunas sem travar a interface"""
        try:
            arquivo1 = self.entrada_arquivo1.get()
            arquivo2 = self.entrada_arquivo2.get()
            skip1 = self.spin_skip1.get()
            skip2 = self.spin_skip2.get()
            
            # Valida campos de pular linhas
            try:
                skip1 = int(skip1)
                skip2 = int(skip2)
            except ValueError:
                self.root.after(0, lambda: self._handle_column_error("Os campos 'Pular linhas' devem ser números inteiros"))
                return
                
            if arquivo1.lower().endswith('.csv'):
                df1 = pd.read_csv(arquivo1, skiprows=skip1, nrows=5)
            else:
                df1 = pd.read_excel(arquivo1, skiprows=skip1, nrows=5)
                
            if arquivo2.lower().endswith('.csv'):
                df2 = pd.read_csv(arquivo2, skiprows=skip2, nrows=5)
            else:
                df2 = pd.read_excel(arquivo2, skiprows=skip2, nrows=5)
            
            self.df1_columns = list(df1.columns)
            self.df2_columns = list(df2.columns)
            
            if not self.manual_selection.get():
                colunas_comuns = list(set(self.df1_columns) & set(self.df2_columns))
                if not colunas_comuns:
                    self.root.after(0, lambda: self._handle_column_error("Nenhuma coluna em comum encontrada entre os arquivos"))
                    return
            
            self.root.after(0, self._update_column_combos)
        except Exception as e:
            self.root.after(0, lambda: self._handle_column_error(str(e)))
            
    def _update_column_combos(self):
        """Atualiza os comboboxes e listbox com as colunas carregadas"""
        self.progress.stop()
        
        if self.manual_selection.get():
            self.combo_chave_origem['values'] = self.df1_columns
            self.combo_chave_destino['values'] = self.df2_columns
            if self.df1_columns:
                self.combo_chave_origem.set(self.df1_columns[0])
            if self.df2_columns:
                self.combo_chave_destino.set(self.df2_columns[0])
            self.btn_execute.config(state="normal")
            self.status_var.set("🎉 Colunas carregadas! Selecione as colunas-chave manualmente")
            self.status_label.configure(style='Success.TLabel')
        else:
            colunas_comuns = list(set(self.df1_columns) & set(self.df2_columns))
            self.combo_chave['values'] = colunas_comuns
            if colunas_comuns:
                self.combo_chave.set(colunas_comuns[0])
            self.btn_execute.config(state="normal")
            self.status_var.set(f"🎉 Colunas carregadas! {len(colunas_comuns)} colunas-chave disponíveis, "
                              f"{len(self.df1_columns)} colunas para copiar")
            self.status_label.configure(style='Success.TLabel')
        
        self.listbox_colunas.delete(0, tk.END)
        for coluna in self.df1_columns:
            self.listbox_colunas.insert(tk.END, coluna)
            
        self.listbox_colunas.bind('<<ListboxSelect>>', 
                                 lambda e: self.atualizar_contador_colunas())
        self.toggle_manual_selection()
        
    def _handle_column_error(self, error_msg):
        """Trata erros no carregamento de colunas"""
        self.progress.stop()
        messagebox.showerror("❌ Erro ao Carregar Colunas", error_msg, parent=self.root)
        self.status_var.set("❌ Erro ao carregar colunas")
        self.status_label.configure(style='Error.TLabel')
        
    def executar_comparacao(self):
        """Executa a vinculação das colunas"""
        if not self.validar_inputs():
            return
            
        try:
            self.progress.start()
            self.btn_execute.config(state="disabled")
            self.status_var.set("⚙️ Processando vinculação...")
            self.status_label.configure(style='Info.TLabel')
            
            thread = threading.Thread(target=self._executar_merge_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.progress.stop()
            self.btn_execute.config(state="normal")
            messagebox.showerror("❌ Erro", f"Erro inesperado:\n{str(e)}", parent=self.root)
            self.status_var.set("❌ Erro na vinculação")
            self.status_label.configure(style='Error.TLabel')
            
    def _executar_merge_thread(self):
        """Thread para executar o merge sem travar a interface"""
        try:
            arquivo1 = self.entrada_arquivo1.get()
            arquivo2 = self.entrada_arquivo2.get()
            skip1 = int(self.spin_skip1.get())
            skip2 = int(self.spin_skip2.get())
            
            indices_selecionados = self.listbox_colunas.curselection()
            colunas_selecionadas = [self.df1_columns[i] for i in indices_selecionados]
            
            if arquivo1.lower().endswith('.csv'):
                df1 = pd.read_csv(arquivo1, skiprows=skip1)
            else:
                df1 = pd.read_excel(arquivo1, skiprows=skip1)
                
            if arquivo2.lower().endswith('.csv'):
                df2 = pd.read_csv(arquivo2, skiprows=skip2)
            else:
                df2 = pd.read_excel(arquivo2, skiprows=skip2)
            
            if self.manual_selection.get():
                chave_origem = self.combo_chave_origem.get()
                chave_destino = self.combo_chave_destino.get()
                if not chave_origem or not chave_destino:
                    raise ValueError("Selecione as colunas-chave para ambos os arquivos")
                df1 = df1.rename(columns={chave_origem: chave_destino})
                chave = chave_destino
            else:
                chave = self.combo_chave.get()
                if not chave:
                    raise ValueError("Selecione a coluna-chave")
            
            if chave not in df1.columns or chave not in df2.columns:
                raise ValueError(f"Coluna-chave '{chave}' não encontrada em um dos arquivos")
                
            for coluna in colunas_selecionadas:
                if coluna not in df1.columns:
                    raise ValueError(f"Coluna '{coluna}' não encontrada no arquivo origem")
            
            colunas_merge = [chave] + [col for col in colunas_selecionadas if col != chave]
            
            df_merge = df2.merge(df1[colunas_merge], on=chave, how='left')
            
            arquivo_base = Path(arquivo2)
            extensao = '.csv' if arquivo2.lower().endswith('.csv') else '.xlsx'
            nome_sugerido = f"{arquivo_base.stem}_vinculado{extensao}"
        
            
            def save_file():
                nome_saida = filedialog.asksaveasfilename(
                    title="Salvar Arquivo Vinculado",
                    initialdir=arquivo_base.parent,
                    initialfile=nome_sugerido,
                    filetypes=[("Excel files", "*.xlsx *.xls") if extensao == '.xlsx' else ("CSV files", "*.csv"), ("All files", "*.*")]
                )
                if not nome_saida:
                    self.root.after(0, lambda: self._merge_error("Nenhum arquivo de saída selecionado"))
                    return
                
                if not nome_saida.lower().endswith(('.xlsx', '.xls', '.csv')):
                    nome_saida += extensao
                    
                if nome_saida.lower().endswith('.csv'):
                    df_merge.to_csv(nome_saida, index=False)
                else:
                    df_merge.to_excel(nome_saida, index=False)
                
                total_linhas = len(df_merge)
                colunas_adicionadas = len(colunas_selecionadas)
                
                self.root.after(0, lambda: self._merge_success(str(nome_saida), total_linhas, 
                                                             colunas_adicionadas, colunas_selecionadas))
            
            self.root.after(0, save_file)
            
        except Exception as e:
            self.root.after(0, lambda: self._merge_error(str(e)))
            
    def _merge_success(self, caminho_saida, total_linhas, colunas_adicionadas, nomes_colunas):
        """Trata sucesso do merge com estatísticas detalhadas"""
        self.progress.stop()
        self.btn_execute.config(state="normal")
        self.status_var.set("🎉 Vinculação concluída com sucesso!")
        self.status_label.configure(style='Success.TLabel')
        
        colunas_texto = '\n'.join([f"• {col}" for col in nomes_colunas])
        
        messagebox.showinfo("🎉 Sucesso!", 
                           f"Vinculação concluída com sucesso!\n\n"
                           f"📁 Arquivo salvo em:\n{caminho_saida}\n\n"
                           f"📊 Estatísticas:\n"
                           f"• Total de linhas: {total_linhas:,}\n"
                           f"• Colunas adicionadas: {colunas_adicionadas}\n\n"
                           f"📋 Colunas vinculadas:\n{colunas_texto}", 
                           parent=self.root)
        
    def _merge_error(self, error_msg):
        """Trata erro no merge"""
        self.progress.stop()
        self.btn_execute.config(state="normal")
        messagebox.showerror("❌ Erro na Vinculação", error_msg, parent=self.root)
        self.status_var.set("❌ Erro na vinculação")
        self.status_label.configure(style='Error.TLabel')
        
    def validar_inputs(self):
        """Valida todas as entradas antes de executar"""
        if not self.entrada_arquivo1.get().strip():
            messagebox.showerror("❌ Erro", "Selecione o arquivo origem", parent=self.root)
            return False
            
        if not self.entrada_arquivo2.get().strip():
            messagebox.showerror("❌ Erro", "Selecione o arquivo destino", parent=self.root)
            return False
            
        if self.manual_selection.get():
            if not self.combo_chave_origem.get() or not self.combo_chave_destino.get():
                messagebox.showerror("❌ Erro", "Selecione as colunas-chave para ambos os arquivos", 
                                    parent=self.root)
                return False
        else:
            if not self.combo_chave.get():
                messagebox.showerror("❌ Erro", "Selecione a coluna-chave", parent=self.root)
                return False
            
        if not self.listbox_colunas.curselection():
            messagebox.showerror("❌ Erro", "Selecione pelo menos uma coluna para copiar", parent=self.root)
            return False
            
        try:
            int(self.spin_skip1.get())
            int(self.spin_skip2.get())
        except ValueError:
            messagebox.showerror("❌ Erro", "Valores de 'pular linhas' devem ser números inteiros", 
                                parent=self.root)
            return False
            
        return True


def main():
    """Função principal para executar a aplicação"""
    root = ttk.Window()
    app = ExcelMergerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()