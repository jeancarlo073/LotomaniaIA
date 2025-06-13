import random
from collections import Counter
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import requests
import json
import time
import os
import numpy as np
import threading

# --- Configurações de Arquivo e Jogo (LOTOMANIA) ---
HISTORICO_FILE = "historico_lotomania.json"
NUM_DEZENAS_TOTAL = 100 # De 00 a 99
NUM_DEZENAS_POR_APOSTA = 50 # Você escolhe 50 números
NUM_DEZENAS_SORTEADAS = 20 # 20 números são sorteados no concurso

# --- Funções Auxiliares ---
def _is_prime(n):
    if n < 2:
        return False
    # 0 e 1 não são primos. Numeros primos de 00 a 99:
    # 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97
    # Total de 25 primos entre 0 e 99.
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

# --- Funções de Dados e Análise para LOTOMANIA ---

def salvar_historico(historico_data_map):
    """Salva o histórico de sorteios em um arquivo JSON.
    historico_data_map: Dicionário no formato {concurso_num: [dezenas_sorteadas]}
    """
    try:
        with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
            json.dump(historico_data_map, f, indent=4)
        print(f"Histórico salvo em {HISTORICO_FILE}")
    except Exception as e:
        print(f"Erro ao salvar histórico: {e}")
        messagebox.showerror("Erro de Salvamento", f"Não foi possível salvar o histórico em {HISTORICO_FILE}. Erro: {e}")

def carregar_historico_map():
    """Carrega o histórico de sorteios de um arquivo JSON.
    Retorna um dicionário no formato {concurso_num: [dezenas_sorteadas]}.
    """
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
                historico_json = json.load(f)
                # Converte as chaves de string para int ao carregar
                historico_map = {int(k): v for k, v in historico_json.items()}
            print(f"Histórico de {len(historico_map)} concursos carregado de {HISTORICO_FILE}")
            return historico_map
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON do histórico: {e}. O arquivo pode estar corrompido.")
            messagebox.showwarning("Erro de Leitura", "O arquivo de histórico local está corrompido ou vazio. Será feito um novo download ou simulação.")
            if os.path.exists(HISTORICO_FILE):
                os.remove(HISTORICO_FILE) # Remover arquivo corrompido para evitar loop
            return {} # Retorna dicionário vazio para indicar que não há histórico válido
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
            messagebox.showerror("Erro de Carregamento", f"Não foi possível carregar o histórico de {HISTORICO_FILE}. Erro: {e}")
            return {}
    return {} # Retorna dicionário vazio se o arquivo não existe

def simular_historico_lotomania(num_sorteios=10000): # Simula 10 mil sorteios para Lotomania
    historico_dezenas_list = []
    # Números de 0 a 99
    numeros_possiveis = list(range(NUM_DEZENAS_TOTAL))
    for i in range(num_sorteios):
        # Lotomania sorteia 20 dezenas
        sorteio = sorted(random.sample(numeros_possiveis, NUM_DEZENAS_SORTEADAS))
        historico_dezenas_list.append(sorteio)
    return historico_dezenas_list


def analisar_frequencia_lotomania(historico_dezenas_list):
    """
    Analisa a frequência e o atraso dos números sorteados.
    historico_dezenas_list: Uma lista de listas de dezenas (ex: [[0,1,...],[50,60,...]]).
    """
    frequencias = Counter()
    atrasos_corretos = {num: 0 for num in range(NUM_DEZENAS_TOTAL)}
    
    for sorteio in historico_dezenas_list:
        for numero in sorteio:
            frequencias[numero] += 1
            
    # Garante que todos os números de 0 a 99 estejam nas frequências, mesmo que com 0
    for i in range(NUM_DEZENAS_TOTAL):
        if i not in frequencias:
            frequencias[i] = 0
            
    if historico_dezenas_list:
        for num_loteria in range(NUM_DEZENAS_TOTAL):
            count_atraso = 0
            # Percorre o histórico do mais recente para o mais antigo para calcular o atraso
            for sorteio in reversed(historico_dezenas_list):
                if num_loteria in sorteio:
                    break
                count_atraso += 1
            atrasos_corretos[num_loteria] = count_atraso

    return frequencias, atrasos_corretos

def calcular_estatisticas_historicas_lotomania(historico_dezenas_list):
    """
    Calcula as estatísticas médias e desvios padrão para os critérios de balanceamento
    com base no histórico de sorteios reais.
    """
    somas = []
    pares_counts = []
    impares_counts = []
    moldura_counts = []
    miolo_counts = []
    primos_counts = []

    moldura_nums = {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9,   # Linha 0
        10, 19, 20, 29, 30, 39, 40, 49, 50, 59, # Meio: colunas 0 e 9
        60, 69, 70, 79, 80, 89, 90, 91, 92, 93, # Meio: colunas 0 e 9
        94, 95, 96, 97, 98, 99 # Linha 9
    }
    
    for sorteio in historico_dezenas_list:
        somas.append(sum(sorteio))
        pares_counts.append(sum(1 for n in sorteio if n % 2 == 0))
        impares_counts.append(NUM_DEZENAS_SORTEADAS - sum(1 for n in sorteio if n % 2 == 0))
        
        cont_moldura = sum(1 for n in sorteio if n in moldura_nums)
        moldura_counts.append(cont_moldura)
        miolo_counts.append(NUM_DEZENAS_SORTEADAS - cont_moldura)

        primos_counts.append(sum(1 for n in sorteio if _is_prime(n)))
    
    if not historico_dezenas_list:
        return {}

    estatisticas = {
        'soma_media': np.mean(somas),
        'soma_std': np.std(somas),
        'pares_media': np.mean(pares_counts),
        'pares_std': np.std(pares_counts),
        'impares_media': np.mean(impares_counts),
        'impares_std': np.std(impares_counts),
        'moldura_media': np.mean(moldura_counts),
        'moldura_std': np.std(moldura_counts),
        'miolo_media': np.mean(miolo_counts),
        'miolo_std': np.std(miolo_counts),
        'primos_media': np.mean(primos_counts),
        'primos_std': np.std(primos_counts),
    }
    return estatisticas

# --- Funções de Geração para LOTOMANIA ---

def gerar_aleatorio_lotomania(num_jogos):
    # Lotomania sempre aposta 50 números
    numeros_possiveis = list(range(NUM_DEZENAS_TOTAL))
    jogos_gerados = []
    for _ in range(num_jogos):
        jogos_gerados.append(sorted(random.sample(numeros_possiveis, NUM_DEZENAS_POR_APOSTA)))
    return jogos_gerados

def gerar_baseado_em_frequencia_lotomania(frequencias_counter, num_jogos):
    # Lotomania sempre aposta 50 números
    
    # Seleciona mais números que o necessário para ter uma base para sortear, priorizando os mais frequentes
    # Por exemplo, os 60 números mais frequentes para sortear 50
    num_frequentes_para_selecao = min(NUM_DEZENAS_TOTAL, NUM_DEZENAS_POR_APOSTA + 10) 
    lista_frequentes_base = [num for num, count in frequencias_counter.most_common(num_frequentes_para_selecao)]

    jogos_gerados = []
    for _ in range(num_jogos):
        if len(lista_frequentes_base) >= NUM_DEZENAS_POR_APOSTA:
            jogos_gerados.append(sorted(random.sample(lista_frequentes_base, NUM_DEZENAS_POR_APOSTA)))
        else:
            # Caso raro onde não há números suficientes na lista de frequentes (ex: histórico muito pequeno)
            numeros_faltantes = NUM_DEZENAS_POR_APOSTA - len(lista_frequentes_base)
            complemento_aleatorio = random.sample(
                [n for n in range(NUM_DEZENAS_TOTAL) if n not in lista_frequentes_base],
                numeros_faltantes
            )
            jogos_gerados.append(sorted(lista_frequentes_base + complemento_aleatorio))

    return jogos_gerados

def gerar_com_filtros_lotomania(filtros_inclusao, filtros_exclusao, num_jogos):
    # Lotomania sempre aposta 50 números
    jogos_gerados = []
    numeros_possiveis = set(range(NUM_DEZENAS_TOTAL))

    for _ in range(num_jogos):
        combinacao = set()
        
        # Adiciona números de inclusão
        for num_incluir in filtros_inclusao:
            if 0 <= num_incluir < NUM_DEZENAS_TOTAL and num_incluir not in combinacao:
                combinacao.add(num_incluir)

        # Remove números de exclusão e os já incluídos das opções restantes
        opcoes_restantes = list(numeros_possiveis - set(filtros_exclusao) - combinacao)

        # Se já tiver mais números do que o permitido devido aos filtros de inclusão (erro do usuário)
        if len(combinacao) > NUM_DEZENAS_POR_APOSTA:
            # Já tratado na GUI, mas para garantir a robustez
            combinacao = set(random.sample(list(combinacao), NUM_DEZENAS_POR_APOSTA))
            opcoes_restantes = [] # Não precisa de mais opções

        # Preenche o restante da combinação com números aleatórios das opções restantes
        while len(combinacao) < NUM_DEZENAS_POR_APOSTA:
            if not opcoes_restantes:
                # Este caso deve ser capturado pela GUI antes da chamada, mas é um fallback
                raise ValueError("Não há números suficientes para gerar a combinação com os filtros fornecidos.")
            
            num_escolhido = random.choice(opcoes_restantes)
            combinacao.add(num_escolhido)
            opcoes_restantes.remove(num_escolhido) # Remove para evitar duplicatas na mesma combinação
            
        jogos_gerados.append(sorted(list(combinacao)))
        
    return jogos_gerados


def _checar_criterios_balanceados_lotomania(combinacao, criterios):
    # Critério de Soma
    soma_atual = sum(combinacao)
    if not (criterios['soma_min'] <= soma_atual <= criterios['soma_max']):
        return False

    # Critério de Pares/Ímpares
    pares = sum(1 for n in combinacao if n % 2 == 0)
    impares = NUM_DEZENAS_POR_APOSTA - pares
    if not (criterios['pares_min'] <= pares <= criterios['pares_max'] and
            criterios['impares_min'] <= impares <= criterios['impares_max']):
        return False
    
    # Critério de Moldura/Miolo (apenas 34 números na moldura de 0 a 99)
    moldura_nums = {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9,   # Linha 0
        10, 19, 20, 29, 30, 39, 40, 49, 50, 59, # Meio: colunas 0 e 9
        60, 69, 70, 79, 80, 89, 90, 91, 92, 93, # Meio: colunas 0 e 9
        94, 95, 96, 97, 98, 99 # Linha 9
    }
    cont_moldura = sum(1 for n in combinacao if n in moldura_nums)
    cont_miolo = NUM_DEZENAS_POR_APOSTA - cont_moldura
    
    if not (criterios['moldura_min'] <= cont_moldura <= criterios['moldura_max'] and
            criterios['miolo_min'] <= cont_miolo <= criterios['miolo_max']):
        return False

    # Critério de Números Consecutivos
    if criterios['max_consecutivos'] is not None:
        sequencia_max_atual = 0
        sequencia_atual = 0
        combinacao_ordenada = sorted(combinacao)
        for i in range(len(combinacao_ordenada)):
            if i > 0 and combinacao_ordenada[i] == combinacao_ordenada[i-1] + 1:
                sequencia_atual += 1
            else:
                sequencia_atual = 1
            sequencia_max_atual = max(sequencia_max_atual, sequencia_atual)
        if sequencia_max_atual > criterios['max_consecutivos']:
            return False
            
    # Critério de Números Primos
    cont_primos = sum(1 for n in combinacao if _is_prime(n))
    if not (criterios['primos_min'] <= cont_primos <= criterios['primos_max']):
        return False
            
    return True

def gerar_balanceado_lotomania(criterios, num_jogos, progress_callback=None, stop_event=None, tentativas_por_jogo=20000):
    # Lotomania sempre aposta 50 números
    numeros_possiveis = list(range(NUM_DEZENAS_TOTAL))
    jogos_gerados = []
    warnings_issued = 0

    for i in range(num_jogos):
        if stop_event and stop_event.is_set():
            return [] # Aborta a geração se o evento de parada for ativado

        combinacao_encontrada = False
        for tentativa in range(tentativas_por_jogo):
            combinacao = sorted(random.sample(numeros_possiveis, NUM_DEZENAS_POR_APOSTA))
            if _checar_criterios_balanceados_lotomania(combinacao, criterios):
                jogos_gerados.append(combinacao)
                combinacao_encontrada = True
                break
            
            if progress_callback and (tentativa % 500 == 0): # Atualiza a cada 500 tentativas
                progress_callback(i, num_jogos, tentativa, tentativas_por_jogo)
        
        if not combinacao_encontrada:
            if warnings_issued < 5: # Limita o número de avisos para não sobrecarregar
                messagebox.showwarning("Aviso de Geração Balanceada", f"Não foi possível encontrar uma combinação balanceada para o jogo {i+1} dentro de {tentativas_por_jogo} tentativas. Gerando um jogo aleatório de {NUM_DEZENAS_POR_APOSTA} números para este. Considere suavizar os critérios.")
                warnings_issued += 1
            jogos_gerados.append(gerar_aleatorio_lotomania(1)[0]) # Gera um jogo aleatório

    return jogos_gerados

# --- Funções de Plotagem ---
def plotar_frequencias_lotomania(frequencias):
    top = tk.Toplevel()
    top.title("Análise Gráfica de Frequência - Lotomania")
    top.geometry("1000x600")
    top.transient(top.master) # Mantém a janela no topo da principal
    top.grab_set() # Bloqueia interação com a janela principal

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle('Frequência de Números - Lotomania (00 a 99)', fontsize=16)
    
    todos_numeros = {num: frequencias.get(num, 0) for num in range(NUM_DEZENAS_TOTAL)}
    numeros = sorted(todos_numeros.keys())
    counts = [todos_numeros[n] for n in numeros]

    ax.bar(numeros, counts, color='lightcoral')
    ax.set_xlabel('Número')
    ax.set_ylabel('Frequência')
    ax.set_xticks([i for i in numeros if i % 5 == 0]) # Exibir ticks a cada 5 números para não sobrecarregar
    ax.set_xticklabels([f"{i:02d}" for i in numeros if i % 5 == 0], rotation=45, ha="right") # Formata para 00, 05, etc.
    ax.set_ylim(bottom=0)
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # Ajusta layout para evitar corte de títulos/rótulos

    canvas = FigureCanvasTkAgg(fig, master=top)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    canvas.draw()

# --- Funções de Probabilidade ---

def combinacoes(n, k):
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    if k > n // 2:
        k = n - k
    
    res = 1
    for i in range(k):
        res = res * (n - i) // (i + 1)
    return res

def calcular_probabilidade_lotomania(acertos_desejados):
    """
    Calcula a probabilidade de acertar um número específico de dezenas na Lotomania.
    - NUM_DEZENAS_TOTAL = 100 (de 00 a 99)
    - NUM_DEZENAS_POR_APOSTA = 50 (você aposta 50 dezenas)
    - NUM_DEZENAS_SORTEADAS = 20 (sorteadas)
    
    A fórmula é: C(50, acertos) * C(50, 20 - acertos) / C(100, 20)
    Onde:
    - C(N, K) é o número de combinações de N elementos tomados K a K.
    - C(50, acertos): combinações de 50 dezenas que você escolheu que acertaram
    - C(50, 20 - acertos): combinações das 50 dezenas que você NÃO escolheu que foram sorteadas (20 - acertos)
    - C(100, 20): Total de combinações possíveis de 20 dezenas em 100.
    """
    
    # 50 dezenas apostadas (acertadas)
    # 50 dezenas não apostadas
    
    prob = {}
    acertos_possiveis = [0, 15, 16, 17, 18, 19, 20] # Lotomania premia 0, 15, 16, 17, 18, 19, 20
    
    # Total de combinações possíveis de 20 dezenas em 100
    total_combinacoes = combinacoes(NUM_DEZENAS_TOTAL, NUM_DEZENAS_SORTEADAS)
    
    for acerto in acertos_possiveis:
        # Número de formas de escolher 'acerto' dezenas entre as 50 que você apostou
        combinacoes_acertadas_da_aposta = combinacoes(NUM_DEZENAS_POR_APOSTA, acerto)
        
        # Número de formas de escolher (20 - acerto) dezenas entre as 50 que você NÃO apostou
        combinacoes_nao_acertadas_da_aposta = combinacoes(NUM_DEZENAS_TOTAL - NUM_DEZENAS_POR_APOSTA, NUM_DEZENAS_SORTEADAS - acerto)
        
        # O resultado é a multiplicação desses dois dividido pelo total de combinações
        probabilidade_num = (combinacoes_acertadas_da_aposta * combinacoes_nao_acertadas_da_aposta) / total_combinacoes
        
        prob[acerto] = probabilidade_num
        
    return prob


# --- Classe da Aplicação GUI para LOTOMANIA ---
class LotomaniaIA(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("IA de Geração de Números Lotomania")
        self.geometry("750x650") # Tamanho ajustado para caber o notebook e ficar mais compacto
        self.resizable(True, True) # Permite redimensionar a janela

        self.historico = [] # Lista de listas de dezenas (20 sorteadas) para análise
        self.historico_map = {} # Dicionário {concurso_num: [dezenas_sorteadas]} para gerenciamento de persistência
        self.frequencias = Counter()
        self.atrasos = {}
        self.estatisticas_historicas = {} # Para sugestões de balanceamento
        self.num_jogos_gerar = tk.IntVar(value=1)

        self.style = ttk.Style(self) # Estilo para os widgets ttk
        self.current_theme = "Padrão" # Tema padrão

        self.create_widgets() # <--- IMPORTANTE: CRIE OS WIDGETS PRIMEIRO
        self.apply_theme(self.current_theme) # <--- AGORA O apply_theme PODE CONFIGURAR OS WIDGETS JÁ EXISTENTES

        self.carregar_dados_iniciais()

        self.stop_event = None
        self.progress_window = None

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        
        # Reset colors for ttk widgets
        self.style.configure("TNotebook", background=self.winfo_rgb("#f0f0f0"))
        self.style.map("TNotebook.Tab", background=[("selected", "#d3d3d3")], foreground=[("selected", "#000")])
        
        # Default colors
        self.config(bg="#f0f0f0")
        default_label_bg = "#f0f0f0"
        default_frame_bg = "#fff"
        default_fg = "#333"
        default_btn_bg = "#4CAF50"
        default_btn_fg = "white"

        if theme_name == "Padrão":
            self.style.configure("TNotebook", background="#f0f0f0")
            self.style.map("TNotebook.Tab", background=[("selected", "#d3d3d3")], foreground=[("selected", "#000")])
            self.config(bg="#f0f0f0")
            default_label_bg = "#f0f0f0"
            default_frame_bg = "#fff"
            default_fg = "#333"
            default_btn_bg = "#4CAF50"
            default_btn_fg = "white"

        elif theme_name == "Azul Escuro":
            self.style.configure("TNotebook", background="#334455")
            self.style.map("TNotebook.Tab", background=[("selected", "#445566")], foreground=[("selected", "#eee")])
            self.config(bg="#223344")
            default_label_bg = "#223344"
            default_frame_bg = "#334455"
            default_fg = "#eee"
            default_btn_bg = "#1E88E5" # Azul mais forte
            default_btn_fg = "white"

        elif theme_name == "Verde Claro":
            self.style.configure("TNotebook", background="#e0f2f1")
            self.style.map("TNotebook.Tab", background=[("selected", "#c1e2e0")], foreground=[("selected", "#000")])
            self.config(bg="#e0f2f1")
            default_label_bg = "#e0f2f1"
            default_frame_bg = "#f0fcfb"
            default_fg = "#2e7d32" # Verde escuro para texto
            default_btn_bg = "#4CAF50"
            default_btn_fg = "white"

        # Apply general styles to all widgets
        for widget in self.winfo_children():
            if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                widget.config(bg=default_frame_bg)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=default_frame_bg, fg=default_fg)
                    elif isinstance(child, tk.Button):
                        child.config(bg=default_btn_bg, fg=default_btn_fg)
            elif isinstance(widget, tk.Label):
                widget.config(bg=default_label_bg, fg=default_fg)
            elif isinstance(widget, tk.Button):
                widget.config(bg=default_btn_bg, fg=default_btn_fg)

        # Apply specific styles for the result text area and status label
        self.resultado_text_area.config(bg=default_frame_bg, fg=default_fg, insertbackground=default_fg) # Set insertion cursor color
        self.status_data_label.config(bg=default_label_bg, fg=default_fg)
        
        # Apply style to Notebook tabs
        self.style.configure("TNotebook.Tab", font=("Arial", 10, "bold"))
        self.style.configure("TNotebook", background=self.cget('bg')) # Match notebook background to root window

        # Update specific elements for better contrast/visibility if needed
        if theme_name == "Azul Escuro":
            self.status_data_label.config(fg="#88eeff") # Light blue for status in dark theme
        elif theme_name == "Verde Claro":
            self.status_data_label.config(fg="#1b5e20") # Darker green for status in light green theme


    def carregar_dados_iniciais(self):
        """Tenta carregar o histórico existente e, se necessário, o atualiza."""
        self.status_data_label.config(text="Status dos Dados: Carregando/Verificando histórico...", fg="blue")
        self.update_idletasks() # Força a atualização da GUI

        self.atualizar_dados_online(force_full_download=False)

    def atualizar_dados_online(self, force_full_download=False):
        """
        Atualiza o histórico de sorteios da Lotomania, baixando apenas os novos concursos.
        Se force_full_download for True, baixa todo o histórico novamente.
        """
        self.status_data_label.config(text="Status dos Dados: Atualizando dados...", fg="blue")
        self.update_idletasks()

        self.historico_map = carregar_historico_map()
        
        last_local_concurso = 0
        if self.historico_map:
            last_local_concurso = max(self.historico_map.keys())

        concurso_to_start_download = 1
        if not force_full_download and last_local_concurso > 0:
            concurso_to_start_download = last_local_concurso + 1
            print(f"Último concurso local: {last_local_concurso}. Buscando a partir do concurso: {concurso_to_start_download}")
        else:
            print("Forçando download completo ou nenhum histórico local. Baixando desde o concurso 1.")
            self.historico_map = {} # Zera o mapa para um download completo

        try:
            # Busca o último concurso online
            response_latest = requests.get(f"https://loteriascaixa-api.herokuapp.com/api/lotomania/latest")
            response_latest.raise_for_status()
            latest_data = response_latest.json()
            latest_online_concurso = latest_data['concurso']
            print(f"Concurso mais recente online: {latest_online_concurso}")

            if latest_online_concurso >= concurso_to_start_download:
                print(f"Baixando sorteios de {concurso_to_start_download} até {latest_online_concurso}")
                
                # Baixa os novos sorteios e adiciona/atualiza no dicionário
                for concurso_num in range(concurso_to_start_download, latest_online_concurso + 1):
                    try:
                        url = f"https://loteriascaixa-api.herokuapp.com/api/lotomania/{concurso_num}"
                        response = requests.get(url)
                        response.raise_for_status()
                        data = response.json()
                        
                        if 'dezenas' in data and len(data['dezenas']) == NUM_DEZENAS_SORTEADAS:
                            # As dezenas da API podem vir como strings, converte para int e ordena
                            dezenas = sorted([int(d) for d in data['dezenas']])
                            self.historico_map[concurso_num] = dezenas
                        else:
                            print(f"Aviso: Dados incompletos ou inesperados para o concurso {concurso_num}. Pulando.")
                    except requests.exceptions.RequestException as e:
                        print(f"Erro ao buscar concurso {concurso_num}: {e}. Tentando próximo.")
                    except json.JSONDecodeError as e:
                        print(f"Erro ao decodificar JSON do concurso {concurso_num}: {e}. Pulando.")
                    time.sleep(0.01) # Pequeno atraso para ser educado com a API e evitar bloqueios

                salvar_historico(self.historico_map)

                self.historico = [self.historico_map[c] for c in sorted(self.historico_map.keys())]

                messagebox.showinfo("Atualização Concluída", f"Histórico atualizado! Total de {len(self.historico)} sorteios.")
            else:
                messagebox.showinfo("Atualização Concluída", "Seu histórico já está atualizado!")
                self.historico = [self.historico_map[c] for c in sorted(self.historico_map.keys())]

        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão ao tentar buscar o último concurso online: {e}")
            messagebox.showerror("Erro de Conexão", "Não foi possível buscar o último concurso online. Verifique sua conexão ou a disponibilidade da API.")
            if not self.historico_map:
                self.historico = simular_historico_lotomania(10000)
                messagebox.showwarning("Dados", "Não foi possível carregar ou baixar dados reais. Usando histórico simulado.")
            else:
                messagebox.showwarning("Dados", "Não foi possível atualizar os dados online. Usando o histórico local existente.")
                self.historico = [self.historico_map[c] for c in sorted(self.historico_map.keys())]


        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON do último concurso online: {e}")
            messagebox.showerror("Erro de Dados", "Formato de dados inesperado ao buscar o último concurso online.")
            if not self.historico_map:
                self.historico = simular_historico_lotomania(10000)
                messagebox.showwarning("Dados", "Não foi possível carregar ou baixar dados reais. Usando histórico simulado.")
            else:
                messagebox.showwarning("Dados", "Erro ao processar dados online. Usando o histórico local existente.")
                self.historico = [self.historico_map[c] for c in sorted(self.historico_map.keys())]
        
        if self.historico:
            self.frequencias, self.atrasos = analisar_frequencia_lotomania(self.historico)
            sample_size = min(500, len(self.historico))
            self.estatisticas_historicas = calcular_estatisticas_historicas_lotomania(self.historico[-sample_size:])
        else:
            self.frequencias = Counter()
            self.atrasos = {num: 0 for num in range(NUM_DEZENAS_TOTAL)}
            self.estatisticas_historicas = {}

        self.update_status_label()


    def create_widgets(self):
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_rowconfigure(0, weight=0)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        tk.Label(main_frame, text="IA de Geração de Números Lotomania", font=("Arial", 20, "bold"), fg="#333").grid(row=0, column=0, pady=(0, 15))

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        # --- Aba 1: Geração de Jogos ---
        self.tab_geracao = tk.Frame(self.notebook)
        self.notebook.add(self.tab_geracao, text="Geração de Jogos")
        self.create_geracao_tab(self.tab_geracao)

        # --- Aba 2: Análises ---
        self.tab_analises = tk.Frame(self.notebook)
        self.notebook.add(self.tab_analises, text="Análises")
        self.create_analises_tab(self.tab_analises)

        # --- Aba 3: Gerenciar Jogos ---
        self.tab_gerenciar = tk.Frame(self.notebook)
        self.notebook.add(self.tab_gerenciar, text="Gerenciar Jogos")
        self.create_gerenciar_tab(self.tab_gerenciar)

        # --- Aba 4: Ferramentas ---
        self.tab_ferramentas = tk.Frame(self.notebook)
        self.notebook.add(self.tab_ferramentas, text="Ferramentas")
        self.create_ferramentas_tab(self.tab_ferramentas)

        # Área de Resultados (fora das abas para ser sempre visível)
        tk.Label(main_frame, text=f"Aposta: {NUM_DEZENAS_POR_APOSTA} números (FIXO para Lotomania)", font=("Arial", 10, "bold"), fg="#555").grid(row=2, column=0, pady=(10, 5), padx=10, sticky="ew")

        self.resultado_text_area = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=60, height=8, font=("Courier New", 12), relief="groove", bd=2, padx=10, pady=10)
        self.resultado_text_area.grid(row=3, column=0, pady=(0, 10), sticky="nsew")
        self.resultado_text_area.insert(tk.END, "Números Gerados:\n")
        self.resultado_text_area.config(state=tk.DISABLED)

        self.status_data_label = tk.Label(main_frame, text="Status dos Dados: Carregando...", font=("Arial", 10, "italic"), fg="#666")
        self.status_data_label.grid(row=4, column=0, pady=(0, 10), sticky="ew")

        tk.Button(main_frame, text="Sair", command=self.quit, font=("Arial", 12, "bold"), bg="#D32F2F", fg="white", padx=15, pady=8, relief="raised").grid(row=5, column=0, pady=(15, 0))
        
        # self.apply_theme(self.current_theme) # Esta linha foi movida para o __init__ após create_widgets


    def create_geracao_tab(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(1, weight=1)

        num_jogos_frame = tk.LabelFrame(parent_frame, text="Quantidade de Jogos a Gerar", font=("Arial", 10, "bold"), fg="#555", padx=10, pady=5)
        num_jogos_frame.grid(row=0, column=0, columnspan=2, pady=(10, 15), padx=10, sticky="ew")
        tk.Label(num_jogos_frame, text="Escolha:").pack(side=tk.LEFT, padx=(5, 0))
        self.num_jogos_spinner = tk.Spinbox(num_jogos_frame, from_=1, to=15, textvariable=self.num_jogos_gerar, width=5, font=("Arial", 10))
        self.num_jogos_spinner.pack(side=tk.LEFT, padx=5)
        tk.Label(num_jogos_frame, text="jogos").pack(side=tk.LEFT)

        tk.Button(parent_frame, text="Gerar Aleatório", command=self.gerar_e_exibir_aleatorio, font=("Arial", 11), bg="#4CAF50", fg="white", padx=10, pady=5, relief="raised").grid(row=1, column=0, pady=8, padx=5, sticky="ew")
        tk.Button(parent_frame, text="Gerar Baseado em Frequência", command=self.gerar_e_exibir_frequencia, font=("Arial", 11), bg="#2196F3", fg="white", padx=10, pady=5, relief="raised").grid(row=1, column=1, pady=8, padx=5, sticky="ew")
        tk.Button(parent_frame, text="Gerar com Filtros Personalizados", command=self.abrir_config_filtros, font=("Arial", 11), bg="#FFC107", fg="#333", padx=10, pady=5, relief="raised").grid(row=2, column=0, pady=8, padx=5, sticky="ew")
        tk.Button(parent_frame, text="Gerar Combinação 'Balanceada'", command=self.abrir_config_balanceado, font=("Arial", 11), bg="#9C27B0", fg="white", padx=10, pady=5, relief="raised").grid(row=2, column=1, pady=8, padx=5, sticky="ew")
        tk.Button(parent_frame, text="Atualizar Dados (Buscar Online)", command=lambda: self.atualizar_dados_online(force_full_download=False), font=("Arial", 11), bg="#607D8B", fg="white", padx=10, pady=5, relief="raised").grid(row=3, column=0, columnspan=2, pady=8, padx=5, sticky="ew")


    def create_analises_tab(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(1, weight=1)

        tk.Label(parent_frame, text="Estatísticas e Gráficos do Histórico", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(10,15))

        tk.Button(parent_frame, text="Mostrar Análise de Frequência (Gráfico)", command=self.mostrar_analise_frequencia_grafico, font=("Arial", 11), bg="#FF5722", fg="white", padx=10, pady=5, relief="raised").grid(row=1, column=0, columnspan=2, pady=8, padx=5, sticky="ew")
        tk.Button(parent_frame, text="Mostrar Análises Detalhadas (Texto)", command=self.mostrar_analises_detalhadas, font=("Arial", 11), bg="#8BC34A", fg="white", padx=10, pady=5, relief="raised").grid(row=2, column=0, columnspan=2, pady=8, padx=5, sticky="ew")

    def create_gerenciar_tab(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(1, weight=1)

        tk.Label(parent_frame, text="Ferramentas de Gerenciamento de Jogos", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(10,15))

        tk.Button(parent_frame, text="Limpar Resultados na Tela", command=self.limpar_resultados, font=("Arial", 11), bg="#F44336", fg="white", padx=10, pady=5, relief="raised").grid(row=1, column=0, pady=8, padx=5, sticky="ew")
        tk.Button(parent_frame, text="Salvar Jogos Gerados em Arquivo", command=self.salvar_jogos_gerados, font=("Arial", 11), bg="#009688", fg="white", padx=10, pady=5, relief="raised").grid(row=1, column=1, pady=8, padx=5, sticky="ew")
        tk.Button(parent_frame, text="Carregar Jogos de Arquivo", command=self.carregar_jogos_de_arquivo, font=("Arial", 11), bg="#673AB7", fg="white", padx=10, pady=5, relief="raised").grid(row=2, column=0, columnspan=2, pady=8, padx=5, sticky="ew")
        tk.Button(parent_frame, text="Preparar para Impressão", command=self.preparar_para_impressao, font=("Arial", 11), bg="#FF9800", fg="white", padx=10, pady=5, relief="raised").grid(row=3, column=0, columnspan=2, pady=8, padx=5, sticky="ew")


    def create_ferramentas_tab(self, parent_frame):
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(1, weight=1)

        tk.Label(parent_frame, text="Outras Ferramentas e Configurações", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(10,15))

        # Seção de Probabilidades
        prob_frame = tk.LabelFrame(parent_frame, text="Calculadora de Probabilidades", font=("Arial", 10, "bold"), fg="#555", padx=10, pady=5)
        prob_frame.grid(row=1, column=0, columnspan=2, pady=(5, 10), padx=10, sticky="ew")
        tk.Button(prob_frame, text="Mostrar Probabilidades", command=self.mostrar_probabilidades, font=("Arial", 11), bg="#4A90E2", fg="white", padx=10, pady=5, relief="raised").pack(pady=5)

        # Seção de Comparador
        comp_frame = tk.LabelFrame(parent_frame, text="Comparar Jogo com Concurso", font=("Arial", 10, "bold"), fg="#555", padx=10, pady=5)
        comp_frame.grid(row=2, column=0, columnspan=2, pady=(5, 10), padx=10, sticky="ew")
        tk.Label(comp_frame, text="Nº Concurso:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.concurso_entry = tk.Entry(comp_frame, width=10, font=("Arial", 10))
        self.concurso_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        tk.Label(comp_frame, text="Seu Jogo (50 dezenas, vírgula):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.jogo_comparar_entry = tk.Entry(comp_frame, width=30, font=("Arial", 10))
        self.jogo_comparar_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        tk.Button(comp_frame, text="Comparar", command=self.comparar_jogo_com_concurso, font=("Arial", 11), bg="#C2185B", fg="white", padx=10, pady=5, relief="raised").grid(row=2, column=0, columnspan=2, pady=5)

        # Seção de Temas
        tema_frame = tk.LabelFrame(parent_frame, text="Escolher Tema", font=("Arial", 10, "bold"), fg="#555", padx=10, pady=5)
        tema_frame.grid(row=3, column=0, columnspan=2, pady=(5, 10), padx=10, sticky="ew")
        self.tema_var = tk.StringVar(value=self.current_theme)
        ttk.Radiobutton(tema_frame, text="Padrão", variable=self.tema_var, value="Padrão", command=lambda: self.apply_theme("Padrão")).pack(anchor="w")
        ttk.Radiobutton(tema_frame, text="Azul Escuro", variable=self.tema_var, value="Azul Escuro", command=lambda: self.apply_theme("Azul Escuro")).pack(anchor="w")
        ttk.Radiobutton(tema_frame, text="Verde Claro", variable=self.tema_var, value="Verde Claro", command=lambda: self.apply_theme("Verde Claro")).pack(anchor="w")


    def update_status_label(self):
        if self.historico:
            self.status_data_label.config(text=f"Status dos Dados: REAIS ({len(self.historico)} sorteios)", fg="green")
        else:
            self.status_data_label.config(text="Status dos Dados: Nenhum dado carregado/simulado.", fg="red")
        self.apply_theme(self.current_theme) # Re-apply theme to ensure label color is correct


    def atualizar_resultado_text_area(self, jogos, tempo_geracao=None):
        self.resultado_text_area.config(state=tk.NORMAL)
        self.resultado_text_area.delete(1.0, tk.END)
        
        if not jogos:
            self.resultado_text_area.insert(tk.END, "Nenhum jogo gerado.")
            self.resultado_text_area.config(state=tk.DISABLED)
            return

        self.resultado_text_area.insert(tk.END, "Jogos Gerados:\n\n")
        for i, jogo in enumerate(jogos):
            jogo_formatado = [f"{num:02d}" for num in jogo]
            self.resultado_text_area.insert(tk.END, f"Jogo {i+1:02d}: {', '.join(jogo_formatado)}\n")
        
        if tempo_geracao is not None:
            self.resultado_text_area.insert(tk.END, f"\nTempo de Geração: {tempo_geracao:.2f} segundos\n")

        self.resultado_text_area.config(state=tk.DISABLED)


    def limpar_resultados(self):
        """Limpa o conteúdo da área de texto de resultados."""
        self.resultado_text_area.config(state=tk.NORMAL)
        self.resultado_text_area.delete(1.0, tk.END)
        self.resultado_text_area.insert(tk.END, "Números Gerados:\n")
        self.resultado_text_area.config(state=tk.DISABLED)

    def salvar_jogos_gerados(self):
        """Salva o conteúdo da área de texto de resultados em um arquivo."""
        conteudo = self.resultado_text_area.get(1.0, tk.END).strip()
        if not conteudo or conteudo == "Números Gerados:":
            messagebox.showwarning("Nada para Salvar", "Não há jogos gerados para salvar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
            title="Salvar Jogos Gerados"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(conteudo)
                messagebox.showinfo("Salvo", f"Jogos salvos com sucesso em:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar os jogos. Erro: {e}")

    def carregar_jogos_de_arquivo(self):
        """Carrega jogos de um arquivo de texto e os exibe na área de resultados."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")],
            title="Carregar Jogos de Arquivo"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conteudo = f.read()
                
                # Tenta formatar para exibir como jogos, se possível
                jogos_carregados = []
                for line in conteudo.split('\n'):
                    if "Jogo" in line and ":" in line:
                        try:
                            # Extrai os números após o ': ' e remove espaços
                            nums_str = line.split(': ')[1].strip()
                            nums = sorted([int(n) for n in nums_str.split(',') if n.strip().isdigit()])
                            if len(nums) == NUM_DEZENAS_POR_APOSTA:
                                jogos_carregados.append(nums)
                        except (ValueError, IndexError):
                            # Se a linha não for um formato de jogo reconhecível, ignora
                            pass
                
                if jogos_carregados:
                    self.atualizar_resultado_text_area(jogos_carregados)
                    messagebox.showinfo("Carregado", f"Jogos carregados com sucesso de:\n{file_path}")
                else:
                    self.resultado_text_area.config(state=tk.NORMAL)
                    self.resultado_text_area.delete(1.0, tk.END)
                    self.resultado_text_area.insert(tk.END, f"Conteúdo do arquivo:\n\n{conteudo}")
                    self.resultado_text_area.config(state=tk.DISABLED)
                    messagebox.showwarning("Carregado", f"Arquivo carregado, mas nenhum jogo no formato padrão foi encontrado. Exibindo conteúdo bruto.")

            except Exception as e:
                messagebox.showerror("Erro ao Carregar", f"Não foi possível carregar os jogos. Erro: {e}")

    def preparar_para_impressao(self):
        """Abre uma nova janela com os jogos formatados para impressão."""
        conteudo = self.resultado_text_area.get(1.0, tk.END).strip()
        if not conteudo or conteudo == "Números Gerados:":
            messagebox.showwarning("Nada para Imprimir", "Não há jogos gerados para preparar para impressão.")
            return

        jogos_para_impressao = []
        for line in conteudo.split('\n'):
            if "Jogo" in line and ":" in line:
                try:
                    nums_str = line.split(': ')[1].strip()
                    nums = [int(n) for n in nums_str.split(',') if n.strip().isdigit()]
                    if len(nums) == NUM_DEZENAS_POR_APOSTA:
                        jogos_para_impressao.append(nums)
                except (ValueError, IndexError):
                    pass
        
        if not jogos_para_impressao:
            messagebox.showwarning("Formato Inválido", "Nenhum jogo no formato reconhecível encontrado para impressão.")
            return

        top = tk.Toplevel(self)
        top.title("Jogos para Impressão - Lotomania")
        top.geometry("600x600")
        top.transient(self)
        top.grab_set()

        text_area = scrolledtext.ScrolledText(top, wrap=tk.WORD, width=70, height=30, font=("Courier New", 12))
        text_area.pack(padx=10, pady=10)

        text_area.insert(tk.END, "--- Jogos Lotomania para Impressão ---\n\n")
        
        for i, jogo in enumerate(jogos_para_impressao):
            text_area.insert(tk.END, f"--------------------------------------\n")
            text_area.insert(tk.END, f"Jogo {i+1:02d} - Lotomania\n")
            text_area.insert(tk.END, f"--------------------------------------\n")
            
            # Formatar em linhas de 10 números, 5 linhas
            for j in range(0, NUM_DEZENAS_POR_APOSTA, 10):
                line_dezenas = [f"{num:02d}" for num in jogo[j:j+10]]
                text_area.insert(tk.END, f"{' '.join(line_dezenas)}\n")
            text_area.insert(tk.END, "\n")
        
        text_area.insert(tk.END, "--- Boa Sorte! ---\n")
        text_area.config(state=tk.DISABLED)

        # Botão para copiar
        def copiar_para_clipboard():
            top.clipboard_clear()
            top.clipboard_append(text_area.get(1.0, tk.END))
            messagebox.showinfo("Copiado", "Conteúdo copiado para a área de transferência!")

        copy_button = tk.Button(top, text="Copiar para Área de Transferência", command=copiar_para_clipboard, font=("Arial", 11), bg="#2196F3", fg="white", padx=10, pady=5, relief="raised")
        copy_button.pack(pady=10)


    def gerar_e_exibir_aleatorio(self):
        start_time = time.time()
        num_jogos = self.num_jogos_gerar.get()
        jogos = gerar_aleatorio_lotomania(num_jogos)
        end_time = time.time()
        self.atualizar_resultado_text_area(jogos, end_time - start_time)

    def gerar_e_exibir_frequencia(self):
        if not self.historico:
            messagebox.showwarning("Dados Ausentes", "Nenhum histórico disponível para gerar jogos baseados em frequência. Por favor, atualize os dados online ou use outro método.")
            return
        start_time = time.time()
        num_jogos = self.num_jogos_gerar.get()
        jogos = gerar_baseado_em_frequencia_lotomania(self.frequencias, num_jogos)
        end_time = time.time()
        self.atualizar_resultado_text_area(jogos, end_time - start_time)


    def mostrar_analise_frequencia_grafico(self):
        if not self.historico:
            messagebox.showwarning("Dados Ausentes", "Nenhum histórico disponível para plotar frequências. Por favor, atualize os dados online.")
            return
        plotar_frequencias_lotomania(self.frequencias)

    def mostrar_analises_detalhadas(self):
        if not self.historico:
            messagebox.showwarning("Dados Ausentes", "Nenhum histórico disponível para análises detalhadas. Por favor, atualize os dados online.")
            return
            
        top = tk.Toplevel(self)
        top.title("Análises Detalhadas - Lotomania")
        top.geometry("450x600")
        top.transient(self)
        top.grab_set()

        text_area = scrolledtext.ScrolledText(top, wrap=tk.WORD, width=50, height=30, font=("Courier New", 10))
        text_area.pack(padx=10, pady=10)
        
        text_area.insert(tk.END, "--- Números Quentes (Mais Frequentes) ---\n", "title")
        quentes_sorted = sorted(self.frequencias.items(), key=lambda item: item[1], reverse=True)
        for num, freq in quentes_sorted[:20]:
            text_area.insert(tk.END, f"Número {num:02d}: {freq} vezes\n")
        text_area.insert(tk.END, "\n")

        text_area.insert(tk.END, "--- Números Frios (Menos Frequentes) ---\n", "title")
        frios_sorted = sorted(self.frequencias.items(), key=lambda item: item[1])
        for num, freq in frios_sorted[:20]:
            text_area.insert(tk.END, f"Número {num:02d}: {freq} vezes\n")
        text_area.insert(tk.END, "\n")

        text_area.insert(tk.END, "--- Análise de Atrasos ---\n", "title")
        atrasos_sorted = sorted(self.atrasos.items(), key=lambda item: item[1], reverse=True)
        for num, atraso in atrasos_sorted[:20]:
            text_area.insert(tk.END, f"Número {num:02d}: Atraso de {atraso} sorteios\n")
        text_area.insert(tk.END, "\n")

        text_area.tag_config("title", font=("Courier New", 12, "bold"), foreground="blue")
        text_area.config(state=tk.DISABLED)


    def mostrar_probabilidades(self):
        top = tk.Toplevel(self)
        top.title("Probabilidades - Lotomania")
        top.geometry("400x300")
        top.transient(self)
        top.grab_set()

        text_area = scrolledtext.ScrolledText(top, wrap=tk.WORD, width=40, height=15, font=("Courier New", 10))
        text_area.pack(padx=10, pady=10)

        text_area.insert(tk.END, "--- Probabilidades de Acerto (Lotomania) ---\n\n", "title")
        text_area.insert(tk.END, "Acertos |  Probabilidade (1 em X)\n")
        text_area.insert(tk.END, "--------|------------------------\n")

        acertos_a_exibir = list(range(21)) # De 0 a 20
        
        for acertos in acertos_a_exibir:
            prob_dict = calcular_probabilidade_lotomania(acertos)
            prob_val = prob_dict.get(acertos, 0)

            if prob_val > 0:
                chance_em_x = 1 / prob_val
                text_area.insert(tk.END, f"{acertos:^7d} | 1 em {chance_em_x:,.0f}\n")
            else:
                text_area.insert(tk.END, f"{acertos:^7d} | Prob. muito baixa (ou 0)\n")
        
        prob_0_acertos = calcular_probabilidade_lotomania(0)[0]
        text_area.insert(tk.END, f"\nNota: Acertar 0 dezenas também é premiado!\n")
        text_area.insert(tk.END, f"Probabilidade de 0 acertos: 1 em {1/prob_0_acertos:,.0f}\n")


        text_area.tag_config("title", font=("Courier New", 12, "bold"), foreground="blue")
        text_area.config(state=tk.DISABLED)


    def comparar_jogo_com_concurso(self):
        concurso_num_str = self.concurso_entry.get()
        jogo_str = self.jogo_comparar_entry.get()

        if not concurso_num_str or not jogo_str:
            messagebox.showwarning("Entrada Inválida", "Por favor, digite o número do concurso e seu jogo.")
            return

        try:
            concurso_num = int(concurso_num_str)
        except ValueError:
            messagebox.showerror("Erro", "Número de concurso inválido. Digite apenas números.")
            return

        try:
            seu_jogo = sorted([int(n.strip()) for n in jogo_str.split(',') if n.strip().isdigit()])
            if len(seu_jogo) != NUM_DEZENAS_POR_APOSTA:
                messagebox.showwarning("Aviso", f"Seu jogo deve ter {NUM_DEZENAS_POR_APOSTA} dezenas. Foram detectadas {len(seu_jogo)}. A comparação prosseguirá com as dezenas fornecidas, mas pode não ser representativa.")
            if any(n < 0 or n > 99 for n in seu_jogo):
                 messagebox.showerror("Erro", "As dezenas do jogo devem estar entre 00 e 99.")
                 return
        except ValueError:
            messagebox.showerror("Erro", "Formato de jogo inválido. Use números separados por vírgula (ex: 01,05,12...).")
            return
        
        if not self.historico_map:
            messagebox.showwarning("Dados Ausentes", "Histórico de sorteios não carregado. Por favor, atualize os dados online primeiro.")
            return

        concurso_sorteado = self.historico_map.get(concurso_num)
        
        if concurso_sorteado:
            acertos = len(set(seu_jogo).intersection(set(concurso_sorteado)))
            messagebox.showinfo("Resultado da Comparação", f"No concurso {concurso_num}, você acertaria {acertos} dezenas!")
        else:
            messagebox.showwarning("Concurso Não Encontrado", f"O concurso {concurso_num} não foi encontrado no histórico local. Tente atualizar os dados ou digite um concurso válido.")


    def abrir_config_filtros(self):
        top = tk.Toplevel(self)
        top.title("Configurar Filtros - Lotomania")
        top.geometry("450x350")
        top.transient(self)
        top.grab_set()

        tk.Label(top, text=f"Aposta: {NUM_DEZENAS_POR_APOSTA} números (FIXO para Lotomania)", font=("Arial", 9, "bold")).pack(pady=(10, 5))

        num_jogos_frame = tk.LabelFrame(top, text="Quantidade de Jogos a Gerar", font=("Arial", 9, "bold"), padx=5, pady=2)
        num_jogos_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(num_jogos_frame, text="Escolha:").pack(side=tk.LEFT, padx=(5, 0))
        tk.Spinbox(num_jogos_frame, from_=1, to=15, textvariable=self.num_jogos_gerar, width=5, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Label(num_jogos_frame, text="jogos").pack(side=tk.LEFT)


        tk.Label(top, text="Números para Incluir (00-99, separados por vírgula):", font=("Arial", 10, "bold")).pack(pady=(10,0))
        entry_incluir_str = tk.Entry(top, width=50)
        entry_incluir_str.pack(pady=(0,10))

        tk.Label(top, text="Números para Excluir (00-99, separados por vírgula):", font=("Arial", 10, "bold")).pack(pady=(10,0))
        entry_excluir_str = tk.Entry(top, width=50)
        entry_excluir_str.pack(pady=(0,10))

        def parse_numbers_input(input_str, min_val, max_val):
            numbers = set()
            errors = []
            parts = input_str.replace(" ", "").split(',')
            for p in parts:
                if not p: continue
                try:
                    num = int(p)
                    if min_val <= num <= max_val:
                        numbers.add(num)
                    else:
                        errors.append(f"Número '{num}' fora da faixa permitida ({min_val}-{max_val}).")
                except ValueError:
                    errors.append(f"Entrada inválida '{p}'. Apenas números e vírgulas são permitidos.")
            return list(numbers), errors

        def aplicar_filtros():
            filtros_inclusao_str = entry_incluir_str.get()
            filtros_exclusao_str = entry_excluir_str.get()
            num_jogos = self.num_jogos_gerar.get()

            incluir_nums, erros_incluir = parse_numbers_input(filtros_inclusao_str, 0, 99)
            excluir_nums, erros_excluir = parse_numbers_input(filtros_exclusao_str, 0, 99)

            todos_erros = erros_incluir + erros_excluir
            if todos_erros:
                messagebox.showerror("Erro de Filtro", "\n".join(todos_erros))
                return
            
            conflitos = set(incluir_nums).intersection(set(excluir_nums))
            if conflitos:
                messagebox.showerror("Erro de Conflito", f"Conflito: Os números {sorted(list(conflitos))} estão marcados para incluir E excluir.")
                return

            if len(incluir_nums) > NUM_DEZENAS_POR_APOSTA:
                messagebox.showwarning("Aviso", f"Você incluiu {len(incluir_nums)} números. A aposta de Lotomania é de {NUM_DEZENAS_POR_APOSTA} números. Serão selecionados {NUM_DEZENAS_POR_APOSTA} aleatoriamente entre os incluídos.")
                incluir_nums = random.sample(incluir_nums, NUM_DEZENAS_POR_APOSTA)

            numeros_ja_incluidos = set(incluir_nums)
            numeros_a_serem_excluidos = set(excluir_nums)
            
            opcoes_para_sorteio_adicional = set(range(NUM_DEZENAS_TOTAL)) - numeros_a_serem_excluidos - numeros_ja_incluidos
            
            num_restantes_para_gerar = NUM_DEZENAS_POR_APOSTA - len(numeros_ja_incluidos)

            if num_restantes_para_gerar < 0:
                pass 
            elif len(opcoes_para_sorteio_adicional) < num_restantes_para_gerar:
                messagebox.showerror("Erro", f"Você excluiu muitos números! Com suas escolhas, é impossível gerar {NUM_DEZENAS_POR_APOSTA} números. Você precisa de pelo menos {num_restantes_para_gerar} números adicionais, mas só há {len(opcoes_para_sorteio_adicional)} disponíveis após inclusões e exclusões.")
                return
            
            start_time = time.time()
            jogos_gerados = gerar_com_filtros_lotomania(incluir_nums, excluir_nums, num_jogos)
            end_time = time.time()
            self.atualizar_resultado_text_area(jogos_gerados, end_time - start_time)
            top.destroy()

        tk.Button(top, text="Gerar com Estes Filtros", command=aplicar_filtros, font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", padx=10, pady=5, relief="raised").pack(pady=20)

    def abrir_config_balanceado(self):
        """
        Abre uma nova janela Toplevel para configurar os critérios da geração balanceada.
        """
        top = tk.Toplevel(self)
        top.title("Configurar Geração Balanceada - Lotomania")
        top.geometry("600x750")
        top.transient(self)
        top.grab_set()

        num_jogos_frame = tk.LabelFrame(top, text="Quantidade de Jogos a Gerar", font=("Arial", 9, "bold"), padx=5, pady=2)
        num_jogos_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(num_jogos_frame, text="Escolha:").pack(side=tk.LEFT, padx=(5, 0))
        tk.Spinbox(num_jogos_frame, from_=1, to=15, textvariable=self.num_jogos_gerar, width=5, font=("Arial", 9)).pack(side=tk.LEFT, padx=5)
        tk.Label(num_jogos_frame, text="jogos").pack(side=tk.LEFT)


        criterios_frame = tk.LabelFrame(top, text="Defina os Critérios para o Jogo Balanceado", font=("Arial", 10, "bold"), padx=10, pady=10)
        criterios_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        criterios_frame.grid_columnconfigure(1, weight=1)

        row_idx = 0

        tk.Label(criterios_frame, text="Soma das Dezenas:", font=("Arial", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        soma_frame = tk.Frame(criterios_frame)
        soma_frame.grid(row=row_idx, column=1, sticky="ew", pady=2, padx=5)
        self.soma_min_var = tk.IntVar(value=2000)
        self.soma_max_var = tk.IntVar(value=3000)
        soma_min_spin = tk.Spinbox(soma_frame, from_=0, to=4950, textvariable=self.soma_min_var, width=6)
        soma_min_spin.pack(side=tk.LEFT, padx=2)
        tk.Label(soma_frame, text="Max:").pack(side=tk.LEFT)
        soma_max_spin = tk.Spinbox(soma_frame, from_=0, to=4950, textvariable=self.soma_max_var, width=6)
        soma_max_spin.pack(side=tk.LEFT, padx=2)
        self.add_tooltip(soma_min_spin, "Soma mínima desejada das 50 dezenas (mín 0, máx 4950).")
        self.add_tooltip(soma_max_spin, "Soma máxima desejada das 50 dezenas (mín 0, máx 4950).")
        row_idx += 1

        tk.Label(criterios_frame, text="Números Pares:", font=("Arial", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        pares_frame = tk.Frame(criterios_frame)
        pares_frame.grid(row=row_idx, column=1, sticky="ew", pady=2, padx=5)
        self.pares_min_var = tk.IntVar(value=20)
        self.pares_max_var = tk.IntVar(value=30)
        pares_min_spin = tk.Spinbox(pares_frame, from_=0, to=50, textvariable=self.pares_min_var, width=6)
        pares_min_spin.pack(side=tk.LEFT, padx=2)
        tk.Label(pares_frame, text="Max:").pack(side=tk.LEFT)
        pares_max_spin = tk.Spinbox(pares_frame, from_=0, to=50, textvariable=self.pares_max_var, width=6)
        pares_max_spin.pack(side=tk.LEFT, padx=2)
        self.add_tooltip(pares_min_spin, "Número mínimo de dezenas pares (0-50).")
        self.add_tooltip(pares_max_spin, "Número máximo de dezenas pares (0-50).")
        row_idx += 1

        tk.Label(criterios_frame, text="Números Ímpares:", font=("Arial", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        impares_frame = tk.Frame(criterios_frame)
        impares_frame.grid(row=row_idx, column=1, sticky="ew", pady=2, padx=5)
        self.impares_min_var = tk.IntVar(value=20)
        self.impares_max_var = tk.IntVar(value=30)
        impares_min_spin = tk.Spinbox(impares_frame, from_=0, to=50, textvariable=self.impares_min_var, width=6)
        impares_min_spin.pack(side=tk.LEFT, padx=2)
        tk.Label(impares_frame, text="Max:").pack(side=tk.LEFT)
        impares_max_spin = tk.Spinbox(impares_frame, from_=0, to=50, textvariable=self.impares_max_var, width=6)
        impares_max_spin.pack(side=tk.LEFT, padx=2)
        self.add_tooltip(impares_min_spin, "Número mínimo de dezenas ímpares (0-50).")
        self.add_tooltip(impares_max_spin, "Número máximo de dezenas ímpares (0-50).")
        row_idx += 1

        tk.Label(criterios_frame, text="Números na Moldura:", font=("Arial", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        moldura_frame = tk.Frame(criterios_frame)
        moldura_frame.grid(row=row_idx, column=1, sticky="ew", pady=2, padx=5)
        self.moldura_min_var = tk.IntVar(value=12)
        self.moldura_max_var = tk.IntVar(value=22)
        moldura_min_spin = tk.Spinbox(moldura_frame, from_=0, to=34, textvariable=self.moldura_min_var, width=6)
        moldura_min_spin.pack(side=tk.LEFT, padx=2)
        tk.Label(moldura_frame, text="Max:").pack(side=tk.LEFT)
        moldura_max_spin = tk.Spinbox(moldura_frame, from_=0, to=34, textvariable=self.moldura_max_var, width=6)
        moldura_max_spin.pack(side=tk.LEFT, padx=2)
        self.add_tooltip(moldura_min_spin, "Número mínimo de dezenas da moldura (0-34).")
        self.add_tooltip(moldura_max_spin, "Número máximo de dezenas da moldura (0-34).")
        row_idx += 1

        tk.Label(criterios_frame, text="Números no Miolo:", font=("Arial", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        miolo_frame = tk.Frame(criterios_frame)
        miolo_frame.grid(row=row_idx, column=1, sticky="ew", pady=2, padx=5)
        self.miolo_min_var = tk.IntVar(value=28)
        self.miolo_max_var = tk.IntVar(value=38)
        miolo_min_spin = tk.Spinbox(miolo_frame, from_=0, to=66, textvariable=self.miolo_min_var, width=6)
        miolo_min_spin.pack(side=tk.LEFT, padx=2)
        tk.Label(miolo_frame, text="Max:").pack(side=tk.LEFT)
        miolo_max_spin = tk.Spinbox(miolo_frame, from_=0, to=66, textvariable=self.miolo_max_var, width=6)
        miolo_max_spin.pack(side=tk.LEFT, padx=2)
        self.add_tooltip(miolo_min_spin, "Número mínimo de dezenas do miolo (0-66).")
        self.add_tooltip(miolo_max_spin, "Número máximo de dezenas do miolo (0-66).")
        row_idx += 1

        tk.Label(criterios_frame, text="Máx. Consecutivos:", font=("Arial", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        self.max_consecutivos_var = tk.IntVar(value=3)
        max_consecutivos_spin = tk.Spinbox(criterios_frame, from_=0, to=10, textvariable=self.max_consecutivos_var, width=6)
        max_consecutivos_spin.grid(row=row_idx, column=1, sticky="w", pady=2, padx=5)
        self.add_tooltip(max_consecutivos_spin, "Número máximo de dezenas consecutivas permitidas (ex: 01, 02, 03).")
        row_idx += 1

        tk.Label(criterios_frame, text="Números Primos:", font=("Arial", 9, "bold")).grid(row=row_idx, column=0, sticky="w", pady=2, padx=5)
        primos_frame = tk.Frame(criterios_frame)
        primos_frame.grid(row=row_idx, column=1, sticky="ew", pady=2, padx=5)
        self.primos_min_var = tk.IntVar(value=10)
        self.primos_max_var = tk.IntVar(value=18)
        primos_min_spin = tk.Spinbox(primos_frame, from_=0, to=25, textvariable=self.primos_min_var, width=6)
        primos_min_spin.pack(side=tk.LEFT, padx=2)
        tk.Label(primos_frame, text="Max:").pack(side=tk.LEFT)
        primos_max_spin = tk.Spinbox(primos_frame, from_=0, to=25, textvariable=self.primos_max_var, width=6)
        primos_max_spin.pack(side=tk.LEFT, padx=2)
        self.add_tooltip(primos_min_spin, "Número mínimo de dezenas primas (0-25).")
        self.add_tooltip(primos_max_spin, "Número máximo de dezenas primas (0-25).")
        row_idx += 1
        
        def aplicar_sugestoes_historicas():
            if not self.estatisticas_historicas:
                messagebox.showwarning("Dados Ausentes", "Nenhuma estatística histórica disponível para sugestões. Por favor, atualize os dados online ou use dados simulados.")
                return

            stats = self.estatisticas_historicas
            
            self.soma_min_var.set(max(0, int(stats['soma_media'] - 2 * stats['soma_std'])))
            self.soma_max_var.set(min(4950, int(stats['soma_media'] + 2 * stats['soma_std'])))

            self.pares_min_var.set(max(0, int(stats['pares_media'] - 1 * stats['pares_std'])))
            self.pares_max_var.set(min(50, int(stats['pares_media'] + 1 * stats['pares_std'])))
            
            self.impares_min_var.set(max(0, int(stats['impares_media'] - 1 * stats['impares_std'])))
            self.impares_max_var.set(min(50, int(stats['impares_media'] + 1 * stats['impares_std'])))

            self.moldura_min_var.set(max(0, int(stats['moldura_media'] - 1 * stats['moldura_std'])))
            self.moldura_max_var.set(min(34, int(stats['moldura_media'] + 1 * stats['moldura_std'])))

            self.miolo_min_var.set(max(0, int(stats['miolo_media'] - 1 * stats['miolo_std'])))
            self.miolo_max_var.set(min(66, int(stats['miolo_media'] + 1 * stats['miolo_std'])))

            self.primos_min_var.set(max(0, int(stats['primos_media'] - 1 * stats['primos_std'])))
            self.primos_max_var.set(min(25, int(stats['primos_media'] + 1 * stats['primos_std'])))

            self.max_consecutivos_var.set(3) 

            messagebox.showinfo("Sugestões Aplicadas", "Critérios preenchidos com sugestões baseadas no histórico de sorteios.")

        tk.Button(top, text="Sugestões Baseadas no Histórico", command=aplicar_sugestoes_historicas, font=("Arial", 10), bg="#FFD700", fg="#333", padx=10, pady=5, relief="raised").pack(pady=(10, 5))


        def aplicar_balanceado():
            try:
                criterios = {
                    'soma_min': self.soma_min_var.get(),
                    'soma_max': self.soma_max_var.get(),
                    'pares_min': self.pares_min_var.get(),
                    'pares_max': self.pares_max_var.get(),
                    'impares_min': self.impares_min_var.get(),
                    'impares_max': self.impares_max_var.get(),
                    'moldura_min': self.moldura_min_var.get(),
                    'moldura_max': self.moldura_max_var.get(),
                    'miolo_min': self.miolo_min_var.get(),
                    'miolo_max': self.miolo_max_var.get(),
                    'max_consecutivos': self.max_consecutivos_var.get(),
                    'primos_min': self.primos_min_var.get(),
                    'primos_max': self.primos_max_var.get()
                }

                if not (criterios['soma_min'] <= criterios['soma_max']):
                    messagebox.showerror("Erro de Critério", "Soma Mínima deve ser menor ou igual à Soma Máxima.")
                    return
                if not (criterios['pares_min'] <= criterios['pares_max'] and criterios['impares_min'] <= criterios['impares_max']):
                    messagebox.showerror("Erro de Critério", "Mínimo deve ser menor ou igual ao Máximo para Pares/Ímpares.")
                    return
                if not (criterios['moldura_min'] <= criterios['moldura_max'] and criterios['miolo_min'] <= criterios['miolo_max']):
                    messagebox.showerror("Erro de Critério", "Mínimo deve ser menor ou igual ao Máximo para Moldura/Miolo.")
                    return
                if not (criterios['primos_min'] <= criterios['primos_max']):
                    messagebox.showerror("Erro de Critério", "Mínimo deve ser menor ou igual ao Máximo para Primos.")
                    return
                
                if (criterios['pares_min'] + criterios['impares_min'] > NUM_DEZENAS_POR_APOSTA or
                    criterios['pares_max'] + criterios['impares_max'] < NUM_DEZENAS_POR_APOSTA):
                    messagebox.showwarning("Aviso de Critério", f"A soma dos intervalos de Pares/Ímpares ({criterios['pares_min']}-{criterios['pares_max']} e {criterios['impares_min']}-{criterios['impares_max']}) pode não permitir uma combinação de {NUM_DEZENAS_POR_APOSTA} números. Verifique seus limites. Note que os totais para pares e ímpares devem somar {NUM_DEZENAS_POR_APOSTA}.")

                if (criterios['moldura_min'] + criterios['miolo_min'] > NUM_DEZENAS_POR_APOSTA or
                    criterios['moldura_max'] + criterios['miolo_max'] < NUM_DEZENAS_POR_APOSTA):
                    messagebox.showwarning("Aviso de Critério", f"A soma dos intervalos de Moldura/Miolo ({criterios['moldura_min']}-{criterios['moldura_max']} e {criterios['miolo_min']}-{criterios['miolo_max']}) pode não permitir uma combinação de {NUM_DEZENAS_POR_APOSTA} números. Verifique seus limites. Note que os totais para moldura e miolo devem somar {NUM_DEZENAS_POR_APOSTA}.")
                    
                num_jogos = self.num_jogos_gerar.get()
                
                self.show_progress_window(num_jogos)

                start_time = time.time()
                jogos = gerar_balanceado_lotomania(criterios, num_jogos, 
                                                progress_callback=self.update_progress_bar,
                                                stop_event=self.stop_event)
                end_time = time.time()
                
                self.hide_progress_window()

                if not self.stop_event.is_set():
                    self.atualizar_resultado_text_area(jogos, end_time - start_time)
                    top.destroy()
                else:
                    self.limpar_resultados()
                    messagebox.showinfo("Geração Cancelada", "A geração de jogos balanceados foi cancelada pelo usuário.")

            except ValueError as e:
                self.hide_progress_window()
                messagebox.showerror("Erro de Entrada", f"Verifique os valores inseridos. Erro: {e}")
            except Exception as e:
                self.hide_progress_window()
                messagebox.showerror("Erro", f"Ocorreu um erro ao gerar combinações: {e}")


        tk.Button(top, text="Gerar com Critérios Balanceados", command=aplicar_balanceado, font=("Arial", 11, "bold"), bg="#9C27B0", fg="white", padx=10, pady=5, relief="raised").pack(pady=20)

    def show_progress_window(self, total_jogos):
        self.progress_window = tk.Toplevel(self)
        self.progress_window.title("Gerando Jogos...")
        self.progress_window.geometry("350x150")
        self.progress_window.transient(self)
        self.progress_window.grab_set()
        self.progress_window.protocol("WM_DELETE_WINDOW", self.on_progress_window_close)

        self.progress_label = tk.Label(self.progress_window, text="Preparando...", font=("Arial", 12))
        self.progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(self.progress_window, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.progress_bar["maximum"] = total_jogos * 100

        self.cancel_button = tk.Button(self.progress_window, text="Cancelar", command=self.cancel_generation, bg="#F44336", fg="white")
        self.cancel_button.pack(pady=5)
        
        self.stop_event = threading.Event()

        self.progress_window.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (self.progress_window.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (self.progress_window.winfo_height() // 2)
        self.progress_window.geometry(f"+{int(x)}+{int(y)}")

    def update_progress_bar(self, current_game_idx, total_games, current_attempt, max_attempts_per_game):
        if self.progress_window and self.progress_bar:
            progress_value = (current_game_idx * 100) + (current_attempt / max_attempts_per_game) * 100
            self.progress_bar["value"] = progress_value
            self.progress_label.config(text=f"Gerando jogo {current_game_idx + 1}/{total_games}...")
            self.progress_window.update_idletasks()

    def hide_progress_window(self):
        if self.progress_window:
            self.progress_window.destroy()
            self.progress_window = None
            self.stop_event = None

    def cancel_generation(self):
        if self.stop_event:
            self.stop_event.set()
            self.hide_progress_window()
            messagebox.showinfo("Cancelado", "A geração de jogos está sendo cancelada. Aguarde a finalização da operação atual.")

    def on_progress_window_close(self):
        self.cancel_generation()


    def add_tooltip(self, widget, text):
        tool_tip = ToolTip(widget, text)
        widget.bind('<Enter>', tool_tip.show)
        widget.bind('<Leave>', tool_tip.hide)

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = 0
        self.y = 0

    def show(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # Cria a janela do tooltip
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True) # Remove bordas e barra de título
        tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None

if __name__ == "__main__":
    app = LotomaniaIA()
    app.mainloop()