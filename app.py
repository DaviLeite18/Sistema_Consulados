import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- CONFIGURAÇÃO GOOGLE SHEETS ---
# O sistema vai buscar as credenciais que você colocou nos "Secrets" do Streamlit
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def conectar_google_sheets():
    # Carrega as credenciais do cofre do Streamlit
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    
    # Abre a planilha pelo nome (tem que ser igualzinho ao que você criou)
    sheet = client.open("Banco de Dados Gincana")
    return sheet

# --- CADASTROS ---
PESSOAS = {
    "Augusto": "Fiéis ao Rei",
    "Benjamin": "Fiéis ao Rei",
    "Isac": "Fiéis ao Rei",
    "Thales": "Fiéis ao Rei",
    "Atila": "Carruagem",
    "Alejandro": "Carruagem",
    "Helio": "Carruagem",
    "João Victor": "Carruagem"
}
LISTA_GRUPOS = sorted(list(set(PESSOAS.values())))

REGRAS_INDIVIDUAL = {
    "Atraso": -200,
    "Falta (Apenas registro)": 0,
    "Presença (Apenas registro)" : 0,
}

REGRAS_COLETIVA = {
   # GANHOS
    "Vitoria nas brincadeiras": 300,
    "Gincana": 1000,
    "Videos": 250,
    "Presença na Reunião": 300,
    "Presença no Culto": 250,
    "Presença na EBD": 300,
    "Dever de Casa": 200,
    "Trouxe Material": 50,

    # PERDAS 
    "Time não gravou versículos": -200,
    "Caixa da Desgraça": -100,
    "Grupo faltou a reunião": -250,
    "Grupo faltou o culto": -400,
    "Desrespeito regras Esportes": -100,
    "Palavra Torpe": -1000,
    "Desrespeito à Organização": -5000
}

# --- FUNÇÕES DE DADOS (AGORA NA NUVEM) ---

def carregar_dados(aba_nome):
    """Lê os dados diretamente do Google Sheets e transforma em DataFrame"""
    try:
        sh = conectar_google_sheets()
        worksheet = sh.worksheet(aba_nome)
        dados = worksheet.get_all_records()
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return pd.DataFrame()

def salvar_na_nuvem(aba_nome, lista_dados):
    """Adiciona uma nova linha lá no Google Sheets"""
    try:
        sh = conectar_google_sheets()
        worksheet = sh.worksheet(aba_nome)
        worksheet.append_row(lista_dados)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
        return False

# --- INTERFACE ---
st.title("⚔️ Consulados (Online)")

# Verifica conexão logo de início
try:
    conectar_google_sheets()
    st.toast("Conectado ao Google Sheets!", icon="🟢")
except:
    st.error("Erro de conexão. Verifique os Segredos (Secrets) no painel do Streamlit.")
    st.stop()

aba1, aba2, aba3, aba4 = st.tabs(["👤 Pessoas", "🛡️ Equipe", "🤝 Visitantes", "🏆 Placar"])

# --- ABA 1: INDIVIDUAL ---
with aba1:
    st.header("Chamada Individual")
    c1, c2 = st.columns(2)
    with c1:
        nome = st.selectbox("Membro", list(PESSOAS.keys()))
        grupo = PESSOAS[nome]
        st.info(f"Grupo: {grupo}")
    with c2:
        motivo = st.selectbox("Ação", list(REGRAS_INDIVIDUAL.keys()))
        pontos = REGRAS_INDIVIDUAL[motivo]
    
    if st.button("Salvar Ação", use_container_width=True):
        data_hoje = datetime.now().strftime("%d/%m %H:%M")
        # Ordem das colunas: Data, Nome, Grupo, Motivo, Pontos
        if salvar_na_nuvem("pontos", [data_hoje, nome, grupo, motivo, pontos]):
            st.success("Salvo no Google Sheets!")

# --- ABA 2: EQUIPE ---
with aba2:
    st.header("Pontos da Equipe")
    grp = st.selectbox("Grupo", LISTA_GRUPOS)
    motivo_grp = st.selectbox("Motivo", list(REGRAS_COLETIVA.keys()))
    pts_grp = st.number_input("Valor", value=REGRAS_COLETIVA[motivo_grp], step=50)
    
    if st.button("Lançar para Equipe", use_container_width=True):
        data_hoje = datetime.now().strftime("%d/%m %H:%M")
        if salvar_na_nuvem("pontos", [data_hoje, "EQUIPE", grp, motivo_grp, pts_grp]):
            st.success("Pontos de equipe salvos!")

# --- ABA 3: VISITANTES ---
with aba3:
    st.header("Visitantes")
    col_vis1, col_vis2 = st.columns(2)
    with col_vis1:
        quem_trouxe = st.selectbox("Quem trouxe?", list(PESSOAS.keys()))
        grupo_destino = PESSOAS[quem_trouxe]
    with col_vis2:
        nome_visitante = st.text_input("Nome do Visitante")
    
    if st.button("Registrar Visitante", use_container_width=True, type="primary"):
        if nome_visitante:
            data_hoje = datetime.now().strftime("%d/%m %H:%M")
            
            # 1. Salva na aba VISITANTES
            # Colunas: Data, Nome_Visitante, Quem_Trouxe, Grupo_Destino
            salvar_na_nuvem("visitantes", [data_hoje, nome_visitante, quem_trouxe, grupo_destino])
            
            # 2. Salva os pontos na aba PONTOS
            salvar_na_nuvem("pontos", [data_hoje, quem_trouxe, grupo_destino, f"Trouxe: {nome_visitante}", 500])
            
            st.balloons()
            st.success("Visitante registrado e pontos atribuídos!")

# --- ABA 4: PLACAR ---
with aba4:
    if st.button("🔄 Atualizar Dados"):
        st.rerun()
        
    df = carregar_dados("pontos")
    
    if not df.empty:
        # Garante que a coluna Pontos é número (evita erro se alguém escrever texto na planilha)
        df["Pontos"] = pd.to_numeric(df["Pontos"], errors='coerce').fillna(0)
        
        st.markdown("### 🏆 PLACAR GERAL")
        ranking = df.groupby("Grupo")["Pontos"].sum().sort_values(ascending=False)
        st.bar_chart(ranking, color="#FF4B4B")
        
        cols = st.columns(len(LISTA_GRUPOS))
        for i, g in enumerate(LISTA_GRUPOS):
            try:
                p = int(ranking[g]) # Mostra como inteiro
            except:
                p = 0
            cols[i].metric(label=g, value=p)
            
        st.divider()
        st.write("Últimos Registros (Lidos do Google Sheets):")
        st.dataframe(df.iloc[::-1].head(10), use_container_width=True, hide_index=True)
    else:
        st.info("A planilha está vazia ou a carregar...")
