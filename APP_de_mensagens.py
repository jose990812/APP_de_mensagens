import pyautogui as py
import time
import tkinter as tk
import pandas as pd
import customtkinter
import unicodedata
import pyperclip
import os
from threading import Thread

# Aparência futurista
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

janela = customtkinter.CTk()
janela.title(" Busca e Envio WhatsApp - FUTURISTIC")

# Centralizar janela
largura_janela = 750
altura_janela = 900
largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()
pos_x = int((largura_tela / 2) - (largura_janela / 2))
pos_y = int((altura_tela / 2) - (altura_janela / 2))
janela.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")
janela.resizable(False, False)

scroll_frame = customtkinter.CTkScrollableFrame(janela, width=750, height=900, fg_color="#0D0D0D")
scroll_frame.pack(fill="both", expand=True)

arquivo = "https://docs.google.com/spreadsheets/d/11Fw8g9alMZkxML-rDDQ-Za2KZwsbFFqgp6Tleat4-YI/export?format=csv"

def normalizar_texto(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

try:
    df = pd.read_csv(arquivo, dtype=str)
    df.columns = df.columns.str.strip().str.lower()
    if "cidade" not in df.columns:
        raise ValueError("A coluna 'cidade' não foi encontrada na planilha.")
    df["cidade"] = df["cidade"].apply(lambda x: normalizar_texto(str(x).strip().lower()))
    dados_carregados = True
except Exception as e:
    df = None
    dados_carregados = False
    print(f"Erro ao carregar a planilha: {e}")

def limpar_texto():
    resultado_textbox.delete("1.0", "end")
    numeros_textbox.delete("1.0", "end")
    contador_numeros_label.configure(text="")

def limpar_tudo():
    limpar_texto()
    mensagem_entry.delete("1.0", "end")
    mensagem_entry2.delete("1.0", "end")
    mensagem_entry3.delete("1.0", "end")
    status_label.configure(text="")
    progress_bar.set(0)

def buscar_cidade():
    limpar_texto()
    if df is None:
        resultado_textbox.insert("1.0", " Erro ao carregar os dados")
        status_label.configure(text=" Erro ao carregar a planilha. Verifique a URL.", text_color="#FF4444")
        return

    cidade_digitada = normalizar_texto(entrada_cidade.get().strip().lower())
    resultado = df[df["cidade"].str.contains(cidade_digitada, case=False, na=False)]

    if not resultado.empty:
        resultado = resultado.sort_values(by="cidade")
        colunas_exibir = ["cidade"] + [col for col in df.columns if col != "cidade"][:3]
        cabeçalho = "\t".join([coluna.upper() for coluna in colunas_exibir])
        resultado_textbox.insert("1.0", cabeçalho + "\n" + "-"*50 + "\n")

        numeros_encontrados = []
        for _, linha in resultado.iterrows():
            linha_texto = "\t".join([str(linha[coluna]) for coluna in colunas_exibir])
            resultado_textbox.insert("end", linha_texto + "\n")
            for valor in linha.values:
                if valor and any(char.isdigit() for char in str(valor)):
                    numeros_encontrados.append(str(valor).strip())

        numeros_encontrados = list(set(numeros_encontrados))
        if numeros_encontrados:
            numeros_textbox.insert("1.0", "\n".join(numeros_encontrados))
            contador_numeros_label.configure(text=f"📱 {len(numeros_encontrados)} número(s) encontrado(s)")
        else:
            numeros_textbox.insert("1.0", " Nenhum número encontrado.")
    else:
        resultado_textbox.insert("1.0", " Cidade não encontrada. Tente novamente.")
        status_label.configure(text=" Cidade não encontrada.", text_color="#FF4444")

    scroll_frame._parent_canvas.yview_moveto(0.3)

def pressionar_enter(event):
    buscar_cidade()

def enviar_mensagem():
    numeros = numeros_textbox.get("1.0", tk.END)
    mensagem1 = mensagem_entry.get("1.0", tk.END).strip()
    mensagem2 = mensagem_entry2.get("1.0", tk.END).strip()
    mensagem3 = mensagem_entry3.get("1.0", tk.END).strip()
    mensagens = [m for m in [mensagem1, mensagem2, mensagem3] if m]

    if numeros.strip() and mensagens:
        lista_numeros = [numero.strip() for numero in numeros.splitlines() if numero.strip()]
        diretorio = os.path.dirname(os.path.abspath(__file__))

        enviados = 0
        falhas = 0

        for i, numero in enumerate(lista_numeros):
            try:
                time.sleep(1)
                for imagem in ['foto.png', 'foto2.png']:
                    location = py.locateCenterOnScreen(os.path.join(diretorio, imagem), confidence=0.8)
                    if location:
                        py.click(location)
                        time.sleep(1.5)

                py.write(numero)
                time.sleep(4)

                py.press('tab')
                time.sleep(0.5)
                py.press('enter')
                time.sleep(2)

                for mensagem in mensagens:
                    location5 = py.locateCenterOnScreen(os.path.join(diretorio, 'foto5.png'), confidence=0.8)
                    if location5:
                        py.click(location5)
                        time.sleep(2)

                    pyperclip.copy(mensagem)
                    py.hotkey('ctrl', 'v')
                    time.sleep(1.5)

                    location4 = py.locateCenterOnScreen(os.path.join(diretorio, 'foto4.png'), confidence=0.8)
                    if location4:
                        py.click(location4)
                    else:
                        py.press('enter')
                    time.sleep(1.5)

                enviados += 1
                progress_bar.set((enviados + falhas) / len(lista_numeros))
                time.sleep(1.5)
                
                for imagem in ['foto.png', 'foto6.png']:
                    location = py.locateCenterOnScreen(os.path.join(diretorio, imagem), confidence=0.8)
                    if location:
                        py.click(location)
                        time.sleep(1.5)

            except Exception as e:
                print(f"Erro ao enviar para {numero}: {str(e)}")
                falhas += 1
                progress_bar.set((enviados + falhas) / len(lista_numeros))

        status_label.configure(
            text=f" Enviados: {enviados} |  Falhas: {falhas}",
            text_color="#00FF88" if falhas == 0 else "#FF4444"
        )

def enviar_mensagens_thread():
    status_label.configure(text=" Enviando mensagens...", text_color="#00FFFF")
    progress_bar.set(0)
    Thread(target=enviar_mensagem).start()

def copiar_numeros():
    pyperclip.copy(numeros_textbox.get("1.0", "end").strip())
    status_label.configure(text=" Números copiados!", text_color="#33CCFF")

def colar_do_maps():
    numero = pyperclip.paste().strip()
    if numero:
        numeros_textbox.insert("end", numero + "\n")
        status_label.configure(text=" Número colado do Maps!", text_color="#33FF99")

# LABEL STATUS
status_label = customtkinter.CTkLabel(scroll_frame, text="", font=("Consolas", 16), height=30, corner_radius=10, fg_color="#111", text_color="#39FF14")
status_label.pack(pady=(20, 10), fill="x", padx=20)

# FRAME CIDADE
entrada_frame = customtkinter.CTkFrame(scroll_frame, fg_color="#1A1A1A", border_color="#00FFFF", border_width=2)
entrada_frame.pack(pady=10, fill="x", padx=20)

customtkinter.CTkLabel(entrada_frame, text=" BUSCAR CIDADE", font=("Orbitron", 22, "bold"), text_color="#00FFFF").pack(pady=10)

entrada_cidade = customtkinter.CTkEntry(entrada_frame, placeholder_text="Digite o nome da cidade", width=350)
entrada_cidade.pack(pady=5)
entrada_cidade.bind("<Return>", pressionar_enter)

customtkinter.CTkButton(entrada_frame, text=" Buscar", command=buscar_cidade, fg_color="#001F3F", hover_color="#003366", cursor="hand2").pack(pady=5)

# RESULTADOS
resultados_section = customtkinter.CTkFrame(scroll_frame, fg_color="#1A1A1A", border_color="#00FFFF", border_width=2)
resultados_section.pack(pady=10, fill="x", padx=20)

customtkinter.CTkLabel(resultados_section, text=" RESULTADOS", font=("Orbitron", 18, "bold"), text_color="#00FFFF").pack(pady=10)

resultado_textbox = customtkinter.CTkTextbox(resultados_section, width=650, height=180, wrap="word", font=("Consolas", 12))
resultado_textbox.pack(pady=(0,10))

# NÚMEROS
numeros_section = customtkinter.CTkFrame(scroll_frame, fg_color="#1A1A1A", border_color="#00FFFF", border_width=2)
numeros_section.pack(pady=10, fill="x", padx=20)

customtkinter.CTkLabel(numeros_section, text=" NÚMEROS", font=("Orbitron", 18, "bold"), text_color="#00FFFF").pack(pady=10)

numeros_textbox = customtkinter.CTkTextbox(numeros_section, width=650, height=120, wrap="word", font=("Consolas", 12))
numeros_textbox.pack(pady=5)

contador_numeros_label = customtkinter.CTkLabel(numeros_section, text="", font=("Consolas", 14), text_color="#00FF88")
contador_numeros_label.pack(pady=5)

botoes_frame = customtkinter.CTkFrame(numeros_section, fg_color="transparent")
botoes_frame.pack(pady=5)

customtkinter.CTkButton(botoes_frame, text=" Copiar", command=copiar_numeros, fg_color="#333", hover_color="#555", cursor="hand2").pack(side="left", padx=5)
customtkinter.CTkButton(botoes_frame, text=" Colar do Maps", command=colar_do_maps, fg_color="#006600", hover_color="#009900", cursor="hand2").pack(side="left", padx=5)

# MENSAGENS
def criar_campo_mensagem_horizontal(parent, titulo):
    sub_frame = customtkinter.CTkFrame(parent, fg_color="transparent")
    sub_frame.pack(side="left", expand=True, padx=10)

    label = customtkinter.CTkLabel(sub_frame, text=titulo, text_color="#00FFFF", font=("Orbitron", 16, "bold"))
    label.pack(pady=(0, 5))

    textbox = customtkinter.CTkTextbox(sub_frame, width=220, height=100, wrap="word", font=("Consolas", 12))
    textbox.insert("1.0", "")
    textbox.bind("<FocusIn>", lambda e: textbox.delete("1.0", "end") if textbox.get("1.0", "end").strip() == "" else None)
    textbox.pack()
    return textbox

mensagens_frame = customtkinter.CTkFrame(scroll_frame, fg_color="transparent")
mensagens_frame.pack(pady=20)

mensagem_entry = criar_campo_mensagem_horizontal(mensagens_frame, " Mensagem 1")
mensagem_entry2 = criar_campo_mensagem_horizontal(mensagens_frame, " Mensagem 2")
mensagem_entry3 = criar_campo_mensagem_horizontal(mensagens_frame, " Mensagem 3")

# BOTÕES
customtkinter.CTkButton(scroll_frame, text=" Enviar Mensagens", command=enviar_mensagens_thread, fg_color="#00BFFF", hover_color="#007ACC", font=("Orbitron", 16, "bold"), cursor="hand2").pack(pady=10)
customtkinter.CTkButton(scroll_frame, text=" Limpar", command=limpar_tudo, fg_color="#FF3333", hover_color="#CC0000", font=("Orbitron", 16, "bold"), cursor="hand2").pack(pady=(0, 10))

# BARRA DE PROGRESSO
progress_bar = customtkinter.CTkProgressBar(scroll_frame, width=600, progress_color="#00FFFF")
progress_bar.pack(pady=10)
progress_bar.set(0)

if not dados_carregados:
    entrada_cidade.configure(state="disabled")
    resultado_textbox.insert("1.0", " Erro ao carregar a planilha. Verifique a URL.")
    resultado_textbox.configure(state="disabled")
    numeros_textbox.configure(state="disabled")
    status_label.configure(text=" Erro ao carregar a planilha.", text_color="#FF4444")


janela.mainloop()
