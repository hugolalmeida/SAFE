import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from pathlib import Path
import threading


class ExcelMergerApp:
    def __init__(self, root):
        self.root = root
        self.manual_selection = tk.BooleanVar(value=False)  # Variável para o checkbox
        self.setup_window()
        self.create_widgets()
        self.df1_columns = []
        self.df2_columns = []
        
        
    def setup_window(self):
        """Configura a janela principal com design moderno"""
        self.root.title("SAFE - Sistema de Alocação e Formatação de Elementos")
        self.root.geometry("6500x650")
        self.root.resizable(True, True)
        self.root.configure(bg='#f0f0f0')
        
        # Centralizar janela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (750 // 2)
        y = (self.root.winfo_screenheight() // 2) - (650 // 2)
        self.root.geometry(f"650x650+{x}+{y}")
        
        # Estilo moderno
        self.setup_modern_style()
    
    def create_header_config_section(self, parent, row):
        """Cria seção de configurações de cabeçalho"""
        skip_frame = ttk.LabelFrame(parent, text="Configurações de Cabeçalho", padding="10")
        skip_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        skip_frame.columnconfigure(1, weight=1)
        skip_frame.columnconfigure(3, weight=1)
        
        ttk.Label(skip_frame, text="Pular linhas - Origem:").grid(row=0, column=0, sticky=tk.W)
        self.spin_skip1 = ttk.Spinbox(skip_frame, from_=0, to=100, width=10, value=0)
        self.spin_skip1.grid(row=0, column=1, padx=(5, 20))
        self.spin_skip1.set(0)
        
        ttk.Label(skip_frame, text="Destino:").grid(row=0, column=2, sticky=tk.W)
        self.spin_skip2 = ttk.Spinbox(skip_frame, from_=0, to=100, width=10, value=0)
        self.spin_skip2.grid(row=0, column=3, padx=(5, 0))
        self.spin_skip2.set(0)
        
    def setup_modern_style(self):
        """Configura um estilo visual moderno"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores modernas
        style.configure('Modern.TFrame', background='#ffffff', relief='flat')
        style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), 
                       background='#ffffff', foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10, 'bold'), 
                       background='#ffffff', foreground='#34495e')
        style.configure('Modern.TButton', font=('Segoe UI', 10))
        style.configure('Success.TLabel', foreground='#27ae60', font=('Segoe UI', 9))
        style.configure('Error.TLabel', foreground='#e74c3c', font=('Segoe UI', 9))
        style.configure('Info.TLabel', foreground='#3498db', font=('Segoe UI', 9))
        
    def create_widgets(self):
        """Cria interface moderna com melhor organização"""
        # Canvas e scrollbar para scroll completo
        canvas = tk.Canvas(self.root, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame principal com padding
        main_frame = ttk.Frame(scrollable_frame, style='Modern.TFrame', padding="25")
        main_frame.pack(fill='both', expand=True)
        
        row = 0
        
        # Cabeçalho moderno
        self.create_header(main_frame, row)
        row += 2
        
        # Seção de arquivos
        self.create_file_sections(main_frame, row)
        row += 6
        
        # Configurações de cabeçalho (movido para antes de carregar colunas)
        self.create_header_config_section(main_frame, row)
        row += 2
        
        # Botão de carregar colunas
        self.create_preview_button(main_frame, row)
        row += 2
        
        # Seção de configurações avançada
        self.create_advanced_config_section(main_frame, row)
        row += 8
        
        # Botões de ação (apenas executar vinculação)
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
        header_frame = ttk.Frame(parent, style='Modern.TFrame')
        header_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 30))
        
        title_label = ttk.Label(header_frame, text="🔗 S.A.F.E", 
                               style='Header.TLabel')
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Combine dados de múltiplas colunas entre planilhas Excel",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(pady=(5, 0))
        
    def create_file_sections(self, parent, row):
        """Cria seções de seleção de arquivos com design moderno"""
        # Frame origem
        origem_frame = ttk.LabelFrame(parent, text="📁 Arquivo Origem (fonte dos dados)", 
                                     padding="15", style='Modern.TFrame')
        origem_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        origem_frame.columnconfigure(0, weight=1)
        
        self.entrada_arquivo1 = ttk.Entry(origem_frame, font=('Segoe UI', 10))
        self.entrada_arquivo1.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        btn_origem = ttk.Button(origem_frame, text="Selecionar", 
                               command=self.selecionar_arquivo1, style='Modern.TButton')
        btn_origem.grid(row=0, column=1)
        
        # Frame destino
        destino_frame = ttk.LabelFrame(parent, text="📋 Arquivo Destino (receberá os dados)", 
                                      padding="15", style='Modern.TFrame')
        destino_frame.grid(row=row+2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        destino_frame.columnconfigure(0, weight=1)
        
        self.entrada_arquivo2 = ttk.Entry(destino_frame, font=('Segoe UI', 10))
        self.entrada_arquivo2.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        btn_destino = ttk.Button(destino_frame, text="Selecionar", 
                                command=self.selecionar_arquivo2, style='Modern.TButton')
        btn_destino.grid(row=0, column=1)
        
    def create_advanced_config_section(self, parent, row):
        """Cria seção de configurações avançada com seleção múltipla"""
        self.config_frame = ttk.LabelFrame(parent, text="⚙️ Configurações Avançadas", 
                                        padding="20", style='Modern.TFrame')
        self.config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        self.config_frame.columnconfigure(1, weight=1)
        
        current_row = 0
        
        # Coluna chave (modo automático)
        self.label_chave_auto = ttk.Label(self.config_frame, 
                                        text="🔑 Coluna-chave (comum aos dois arquivos):")
        self.label_chave_auto.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.combo_chave = ttk.Combobox(self.config_frame, width=40, state="readonly", 
                                    font=('Segoe UI', 10))
        self.combo_chave.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        current_row += 1
        
        # Colunas chave (modo manual)
        self.label_chave_origem = ttk.Label(self.config_frame, 
                                        text="🔑 Coluna-chave (Arquivo Origem):")
        self.label_chave_origem.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.combo_chave_origem = ttk.Combobox(self.config_frame, width=40, state="readonly", 
                                            font=('Segoe UI', 10))
        self.combo_chave_origem.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        current_row += 1
        
        self.label_chave_destino = ttk.Label(self.config_frame, 
                                            text="🔑 Coluna-chave (Arquivo Destino):")
        self.label_chave_destino.grid(row=current_row, column=0, sticky=tk.W, pady=(0, 5))
        self.combo_chave_destino = ttk.Combobox(self.config_frame, width=40, state="readonly", 
                                            font=('Segoe UI', 10))
        self.combo_chave_destino.grid(row=current_row, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(0, 5))
        current_row += 1
        
        # Separador
        ttk.Separator(self.config_frame).grid(row=current_row, column=0, columnspan=2, 
                                            sticky=(tk.W, tk.E), pady=15)
        current_row += 1
        
        # Seleção múltipla de colunas
        ttk.Label(self.config_frame, text="📋 Colunas a copiar (seleção múltipla):").grid(
            row=current_row, column=0, sticky=(tk.W, tk.N), pady=(0, 5))
        # Subtítulo/instrução
        ttk.Label(self.config_frame, text="Aperte Ctrl + Click para múltiplas seleções", font=("TkDefaultFont", 8, "italic"), foreground="gray").grid(
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
        scrollbar_list = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        
        self.listbox_colunas.configure(yscrollcommand=scrollbar_list.set)
        scrollbar_list.configure(command=self.listbox_colunas.yview)
        
        self.listbox_colunas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_list.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        current_row += 1
        
        # Botões de seleção rápida
        btn_frame = ttk.Frame(self.config_frame)
        btn_frame.grid(row=current_row, column=1, sticky=tk.W, padx=(10, 0), pady=(5, 15))
        
        ttk.Button(btn_frame, text="Selecionar Todas", 
                command=self.selecionar_todas_colunas).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Limpar Seleção", 
                command=self.limpar_selecao_colunas).pack(side=tk.LEFT, padx=(0, 5))
        
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
        button_frame = ttk.Frame(parent, style='Modern.TFrame')
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        # Checkbox para seleção manual
        self.manual_check = ttk.Checkbutton(button_frame, text="Seleção Manual de Colunas-Chave", 
                                        variable=self.manual_selection)
        self.manual_check.pack(pady=(0, 5))
        
        self.btn_preview = ttk.Button(button_frame, text="🔍 Carregar Colunas", 
                                    command=self.preview_columns, state="disabled",
                                    style='Modern.TButton', width=20)
        self.btn_preview.pack()
    
    def create_action_buttons(self, parent, row):
        """Cria botões de ação com design moderno"""
        button_frame = ttk.Frame(parent, style='Modern.TFrame')
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        self.btn_execute = ttk.Button(button_frame, text="🚀 Executar Vinculação", 
                                     command=self.executar_comparacao, state="disabled",
                                     style='Modern.TButton', width=20)
        self.btn_execute.pack(side=tk.LEFT, padx=10)
        
        # Contador de colunas selecionadas
        self.label_contador = ttk.Label(button_frame, text="", style='Info.TLabel')
        self.label_contador.pack(side=tk.LEFT, padx=20)
        
    def create_progress_section(self, parent, row):
        """Cria seção de progresso e status"""
        # Barra de progresso
        self.progress = ttk.Progressbar(parent, mode='indeterminate', length=400)
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status com ícones
        self.status_var = tk.StringVar(value="📋 Selecione os arquivos para começar")
        self.status_label = ttk.Label(parent, textvariable=self.status_var, 
                                     style='Info.TLabel', font=('Segoe UI', 10))
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
            self.label_contador.config(text="📊 1 coluna selecionada")
        else:
            self.label_contador.config(text=f"📊 {selecionadas} colunas selecionadas")
            
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
                
            # Detecta tipo de arquivo e tenta ler
            if caminho.lower().endswith('.csv'):
                pd.read_csv(caminho, nrows=1)
            else:
                pd.read_excel(caminho, nrows=1)
                
            self.status_var.set(f"✅ Arquivo {numero} carregado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("❌ Erro no Arquivo", 
                               f"Erro ao validar arquivo {numero}:\n{str(e)}")
            self.status_var.set(f"❌ Erro no arquivo {numero}")
            
    def check_ready_state(self):
        """Verifica se pode habilitar os botões"""
        arquivo1_ok = bool(self.entrada_arquivo1.get().strip())
        arquivo2_ok = bool(self.entrada_arquivo2.get().strip())
        
        if arquivo1_ok and arquivo2_ok:
            self.btn_preview.config(state="normal")
            self.status_var.set("✅ Arquivos prontos! Clique em 'Carregar Colunas'")
        else:
            self.btn_preview.config(state="disabled")
            self.btn_execute.config(state="disabled")
            
    def preview_columns(self):
        """Carrega e exibe as colunas disponíveis"""
        try:
            self.progress.start()
            self.status_var.set("⏳ Carregando colunas...")
            
            thread = threading.Thread(target=self._load_columns_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("❌ Erro", f"Erro ao carregar colunas:\n{str(e)}")
            
    def _load_columns_thread(self):
        """Thread para carregar colunas sem travar a interface"""
        
        try:
            arquivo1 = self.entrada_arquivo1.get()
            arquivo2 = self.entrada_arquivo2.get()
            skip1 = self.spin_skip1.get()
            skip2 = self.spin_skip2.get()
            
            # Valida campos de pular linhas
            if not int(skip1) or not int(skip2):
                print()
            
            # Carrega dados baseado no tipo de arquivo
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
            
            # No modo automático, verifica colunas em comum
            if not self.manual_selection.get():
                colunas_comuns = list(set(self.df1_columns) & set(self.df2_columns))
                if not colunas_comuns:
                    self._handle_column_error("Nenhuma coluna em comum encontrada entre os arquivos")
                    return
            
            self.root.after(0, self._update_column_combos)
        except Exception as e:
            self._handle_column_error("Os campos 'Pular linhas' não podem estar vazios, e devem ser números inteiros")
            self.root.after(0, lambda: self._handle_column_error(str(e)))
            
            
    def _update_column_combos(self):
        """Atualiza os comboboxes e listbox com as colunas carregadas"""
        self.progress.stop()
        
        # Atualiza interface com base no modo
        if self.manual_selection.get():
            # Modo manual: popula os dois comboboxes com todas as colunas
            self.combo_chave_origem['values'] = self.df1_columns
            self.combo_chave_destino['values'] = self.df2_columns
            if self.df1_columns:
                self.combo_chave_origem.set(self.df1_columns[0])
            if self.df2_columns:
                self.combo_chave_destino.set(self.df2_columns[0])
            self.toggle_manual_selection()
            self.btn_execute.config(state="normal")
            self.status_var.set(f"🎉 Colunas carregadas! Selecione as colunas-chave manualmente")
        else:
            # Modo automático: popula o combobox com colunas comuns
            colunas_comuns = list(set(self.df1_columns) & set(self.df2_columns))
            self.combo_chave['values'] = colunas_comuns
            if colunas_comuns:
                self.combo_chave.set(colunas_comuns[0])
            self.toggle_manual_selection()
            self.btn_execute.config(state="normal")
            self.status_var.set(f"🎉 Colunas carregadas! {len(colunas_comuns)} colunas-chave disponíveis, "
                            f"{len(self.df1_columns)} colunas para copiar")
        
        # Atualiza listbox com colunas do arquivo origem
        self.listbox_colunas.delete(0, tk.END)
        for coluna in self.df1_columns:
            self.listbox_colunas.insert(tk.END, coluna)
            
        # Vincula evento de seleção
        self.listbox_colunas.bind('<<ListboxSelect>>', 
                                lambda e: self.atualizar_contador_colunas())
        
    def _handle_column_error(self, error_msg):
        """Trata erros no carregamento de colunas"""
        self.progress.stop()
        messagebox.showerror("❌ Erro ao Carregar Colunas", error_msg)
        self.status_var.set("❌ Erro ao carregar colunas")
        
    def executar_comparacao(self):
        """Executa a vinculação das colunas"""
        if not self.validar_inputs():
            return
            
        try:
            self.progress.start()
            self.btn_execute.config(state="disabled")
            self.status_var.set("⚙️ Processando vinculação...")
            
            thread = threading.Thread(target=self._executar_merge_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.progress.stop()
            self.btn_execute.config(state="normal")
            messagebox.showerror("❌ Erro", f"Erro inesperado:\n{str(e)}")
            
    def _executar_merge_thread(self):
        """Thread para executar o merge sem travar a interface"""
        try:
            arquivo1 = self.entrada_arquivo1.get()
            arquivo2 = self.entrada_arquivo2.get()
            skip1 = int(self.spin_skip1.get())
            skip2 = int(self.spin_skip2.get())
            
            # Obter colunas selecionadas
            indices_selecionados = self.listbox_colunas.curselection()
            colunas_selecionadas = [self.df1_columns[i] for i in indices_selecionados]
            
            # Carrega os dados completos
            if arquivo1.lower().endswith('.csv'):
                df1 = pd.read_csv(arquivo1, skiprows=skip1)
            else:
                df1 = pd.read_excel(arquivo1, skiprows=skip1)
                
            if arquivo2.lower().endswith('.csv'):
                df2 = pd.read_csv(arquivo2, skiprows=skip2)
            else:
                df2 = pd.read_excel(arquivo2, skiprows=skip2)
            
            # Obter colunas-chave com base no modo
            if self.manual_selection.get():
                chave_origem = self.combo_chave_origem.get()
                chave_destino = self.combo_chave_destino.get()
                if not chave_origem or not chave_destino:
                    raise ValueError("Selecione as colunas-chave para ambos os arquivos")
                # Renomeia temporariamente a coluna do arquivo origem para corresponder ao destino
                df1 = df1.rename(columns={chave_origem: chave_destino})
                chave = chave_destino
            else:
                chave = self.combo_chave.get()
                if not chave:
                    raise ValueError("Selecione a coluna-chave")
            
            # Verifica se as colunas existem
            if chave not in df1.columns or chave not in df2.columns:
                raise ValueError(f"Coluna-chave '{chave}' não encontrada em um dos arquivos")
                
            for coluna in colunas_selecionadas:
                if coluna not in df1.columns:
                    raise ValueError(f"Coluna '{coluna}' não encontrada no arquivo origem")
            
            # Colunas para merge (chave + selecionadas)
            colunas_merge = [chave] + [col for col in colunas_selecionadas if col != chave]
            
            # Realiza o merge
            df_merge = df2.merge(df1[colunas_merge], on=chave, how='left')
            
            # Abre caixa de diálogo para escolher nome e local do arquivo de saída
            arquivo_base = Path(arquivo2)
            extensao = '.csv' if arquivo2.lower().endswith('.csv') else '.xlsx'
            nome_sugerido = f"{arquivo_base.stem}_vinculado{extensao}"
            
            # Executa a caixa de diálogo na thread principal
            nome_saida = filedialog.asksaveasfilename(
                title="Salvar Arquivo Vinculado",
                initialdir=arquivo_base.parent,
                initialfile=nome_sugerido,
                filetypes=[("Excel files", "*.xlsx *.xls") if extensao == '.xlsx' else ("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not nome_saida:
                raise ValueError("Nenhum arquivo de saída selecionado")
                
            # Garante que o arquivo tenha a extensão correta
            if not nome_saida.lower().endswith(('.xlsx', '.xls', '.csv')):
                nome_saida += extensao
                
            # Salva o resultado
            if nome_saida.lower().endswith('.csv'):
                df_merge.to_csv(nome_saida, index=False)
            else:
                df_merge.to_excel(nome_saida, index=False)
            
            # Estatísticas
            total_linhas = len(df_merge)
            colunas_adicionadas = len(colunas_selecionadas)
            
            self.root.after(0, lambda: self._merge_success(str(nome_saida), total_linhas, 
                                                        colunas_adicionadas, colunas_selecionadas))
            
        except Exception as e:
            self.root.after(0, lambda: self._merge_error(str(e)))
            
    def _merge_success(self, caminho_saida, total_linhas, colunas_adicionadas, nomes_colunas):
        """Trata sucesso do merge com estatísticas detalhadas"""
        self.progress.stop()
        self.btn_execute.config(state="normal")
        self.status_var.set("🎉 Vinculação concluída com sucesso!")
        
        colunas_texto = '\n'.join([f"• {col}" for col in nomes_colunas])
        
        messagebox.showinfo("🎉 Sucesso!", 
                           f"Vinculação concluída com sucesso!\n\n"
                           f"📁 Arquivo salvo em:\n{caminho_saida}\n\n"
                           f"📊 Estatísticas:\n"
                           f"• Total de linhas: {total_linhas:,}\n"
                           f"• Colunas adicionadas: {colunas_adicionadas}\n\n"
                           f"📋 Colunas vinculadas:\n{colunas_texto}")
        
    def _merge_error(self, error_msg):
        """Trata erro no merge"""
        self.progress.stop()
        self.btn_execute.config(state="normal")
        messagebox.showerror("❌ Erro na Vinculação", error_msg)
        self.status_var.set("❌ Erro na vinculação")
        
    def validar_inputs(self):
        """Valida todas as entradas antes de executar"""
        if not self.entrada_arquivo1.get().strip():
            messagebox.showerror("❌ Erro", "Selecione o arquivo origem")
            return False
            
        if not self.entrada_arquivo2.get().strip():
            messagebox.showerror("❌ Erro", "Selecione o arquivo destino")
            return False
            
        if self.manual_selection.get():
            if not self.combo_chave_origem.get() or not self.combo_chave_destino.get():
                messagebox.showerror("❌ Erro", "Selecione as colunas-chave para ambos os arquivos")
                return False
        else:
            if not self.combo_chave.get():
                messagebox.showerror("❌ Erro", "Selecione a coluna-chave")
                return False
            
        if not self.listbox_colunas.curselection():
            messagebox.showerror("❌ Erro", "Selecione pelo menos uma coluna para copiar")
            return False
            
        try:
            int(self.spin_skip1.get())
            int(self.spin_skip2.get())
        except ValueError:
            messagebox.showerror("❌ Erro", "Valores de 'pular linhas' devem ser números inteiros")
            return False
            
        return True


def main():
    """Função principal para executar a aplicação"""
    root = tk.Tk()
    app = ExcelMergerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()