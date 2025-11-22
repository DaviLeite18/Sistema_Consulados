import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- CONFIGURAÇÕES DE ARQUIVOS ---
ARQUIVO_PONTOS = "registos_pontos_reais.csv"
ARQUIVO_VISITANTES = "registos_visitantes.csv"

# --- CADASTRO DE MEMBROS (FIXOS) ---
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

# --- REGRAS DE PONTUAÇÃO ---
REGRAS_INDIVIDUAL = {
    "Atraso": -200,
    "Falta (Apenas registro)": 0,
    "Presença (Apenas registro)" : 0,
    
    # Nota: "Trouxe Convidado" é inserido automaticamente pela aba de visitantes
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

# --- FUNÇÕES DE BANCO DE DADOS ---

# 1. Funções de Pontos (Geral)
def carregar_pontos():
    if not os.path.exists(ARQUIVO_PONTOS):
        df = pd.DataFrame(columns=["Data", "Nome", "Grupo", "Motivo", "Pontos"])
        df.to_csv(ARQUIVO_PONTOS, index=False)
        return df
    return pd.read_csv(ARQUIVO_PONTOS)

def salvar_pontos(nome, grupo, motivo, pontos):
    df = carregar_pontos()
    data_hoje = datetime.now().strftime("%d/%m %H:%M")
    novo_registo = pd.DataFrame({
        "Data": [data_hoje],
        "Nome": [nome],
        "Grupo": [grupo],
        "Motivo": [motivo],
        "Pontos": [pontos]
    })
    df = pd.concat([df, novo_registo], ignore_index=True)
    df.to_csv(ARQUIVO_PONTOS, index=False)

# 2. Funções Exclusivas de Visitantes
def carregar_visitantes():
    if not os.path.exists(ARQUIVO_VISITANTES):
        # Cria tabela específica para visitantes
        df = pd.DataFrame(columns=["Data", "Nome_Visitante", "Quem_Trouxe", "Grupo_Destino"])
        df.to_csv(ARQUIVO_VISITANTES, index=False)
        return df
    return pd.read_csv(ARQUIVO_VISITANTES)

def salvar_visitante(nome_visitante, quem_trouxe, grupo):
    df = carregar_visitantes()
    data_hoje = datetime.now().strftime("%d/%m %H:%M") # Data e hora atual
    novo_registo = pd.DataFrame({
        "Data": [data_hoje],
        "Nome_Visitante": [nome_visitante],
        "Quem_Trouxe": [quem_trouxe],
        "Grupo_Destino": [grupo]
    })
    df = pd.concat([df, novo_registo], ignore_index=True)
    df.to_csv(ARQUIVO_VISITANTES, index=False)

# --- INTERFACE ---
st.title("⚔️ Batalha dos Grupos")

# Criamos a nova aba "Visitantes"
aba1, aba2, aba3, aba4 = st.tabs(["👤 Pessoas", "🛡️ Equipe", "🤝 Visitantes", "🏆 Placar"])

# --- ABA 1: INDIVIDUAL ---
with aba1:
    st.header("Chamada e Ações")
    c1, c2 = st.columns(2)
    with c1:
        nome = st.selectbox("Membro", list(PESSOAS.keys()))
        grupo = PESSOAS[nome]
        st.info(f"Grupo: {grupo}")
    with c2:
        motivo = st.selectbox("Ação", list(REGRAS_INDIVIDUAL.keys()))
        pontos = REGRAS_INDIVIDUAL[motivo]

    if st.button("Confirmar Ação", use_container_width=True):
        salvar_pontos(nome, grupo, motivo, pontos)
        st.success("Registrado!")

# --- ABA 2: EQUIPE ---
with aba2:
    st.header("Pontos da Equipe")
    grp = st.selectbox("Grupo", LISTA_GRUPOS)
    motivo_grp = st.selectbox("Motivo", list(REGRAS_COLETIVA.keys()))
    pts_grp = st.number_input("Valor", value=REGRAS_COLETIVA[motivo_grp], step=50)

    if st.button("Lançar para Equipe", use_container_width=True):
        salvar_pontos("EQUIPE", grp, motivo_grp, pts_grp)
        st.success("Pontos de equipe salvos!")

# --- ABA 3: VISITANTES (NOVA!) ---
with aba3:
    st.header("Cadastro de Visitante")
    st.caption("Ao registrar, o membro ganha automaticamente +500 pontos.")

    # Formulário de Visitante
    col_vis1, col_vis2 = st.columns(2)
    with col_vis1:
        quem_trouxe = st.selectbox("Quem trouxe?", list(PESSOAS.keys()))
        grupo_destino = PESSOAS[quem_trouxe]
        st.info(f"Ponto vai para: {grupo_destino}")

    with col_vis2:
        nome_visitante = st.text_input("Nome do Visitante")

    if st.button("✅ Registrar Visitante (+500 pts)", use_container_width=True, type="primary"):
        if nome_visitante:
            # 1. Salva na lista de visitantes
            salvar_visitante(nome_visitante, quem_trouxe, grupo_destino)

            # 2. Salva os pontos na lista principal AUTOMATICAMENTE
            salvar_pontos(quem_trouxe, grupo_destino, f"Trouxe visitante: {nome_visitante}", 500)

            st.balloons()
            st.success(f"{nome_visitante} registrado! {quem_trouxe} ganhou 500 pontos.")
        else:
            st.error("Por favor, digite o nome do visitante.")

    st.divider()

    # Histórico de Visitantes
    st.subheader("Lista de Visitantes")
    df_vis = carregar_visitantes()
    if not df_vis.empty:
        # Mostra os mais recentes primeiro
        st.dataframe(df_vis.iloc[::-1], use_container_width=True, hide_index=True)

        # Ranking de Recrutadores
        st.write("**Quem traz mais gente?**")
        st.bar_chart(df_vis["Quem_Trouxe"].value_counts())
    else:
        st.info("Nenhum visitante registrado ainda.")

# --- ABA 4: PLACAR ---
with aba4:
    df = carregar_pontos()
    if not df.empty:
        st.markdown("### 🏆 PLACAR GERAL")
        ranking = df.groupby("Grupo")["Pontos"].sum().sort_values(ascending=False)
        st.bar_chart(ranking, color="#FF4B4B")

        cols = st.columns(len(LISTA_GRUPOS))
        for i, g in enumerate(LISTA_GRUPOS):
            try:
                p = ranking[g]
            except:
                p = 0
            cols[i].metric(label=g, value=p)

        st.divider()
        st.markdown("### 📜 Extrato Geral")
        st.dataframe(df[["Data", "Nome", "Motivo", "Pontos"]].iloc[::-1], use_container_width=True)

        with st.expander("Apagar Tudo"):
            if st.button("🗑️ Resetar Sistema Completo"):
                if os.path.exists(ARQUIVO_PONTOS): os.remove(ARQUIVO_PONTOS)
                if os.path.exists(ARQUIVO_VISITANTES): os.remove(ARQUIVO_VISITANTES)
                st.rerun()
