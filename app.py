import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Gestão de Lotes - Camisas", layout="wide")

VALOR_VENDA = 99.90
CUSTO_CAMISA = 30.00
LOTE_MINIMO = 6
ARQUIVO_DADOS = "vendas_lotes.csv"


# ==============================
# Funções
# ==============================

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS)
    else:
        return pd.DataFrame(columns=[
            "Lote", "Cliente", "Modelo", "Tamanho",
            "Forma Pagamento", "Valor Venda",
            "Custo", "Valor Recebido",
            "Valor a Receber", "Entregue"
        ])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)


# ==============================
# Inicialização
# ==============================

if "df" not in st.session_state:
    st.session_state.df = carregar_dados()

df = st.session_state.df

st.title("📦 Sistema Profissional - Controle de Lotes")

# ==============================
# Criar ou Selecionar Lote
# ==============================

st.header("📦 Gerenciar Lotes")

lotes_existentes = df["Lote"].unique().tolist()

novo_lote = st.text_input("Criar Novo Lote (ex: Lote 1)")

if st.button("Criar Lote"):
    if novo_lote and novo_lote not in lotes_existentes:
        st.success(f"Lote '{novo_lote}' criado! Agora selecione ele abaixo.")
    else:
        st.warning("Digite um nome válido ou lote já existe.")

lote_selecionado = st.selectbox("Selecionar Lote", options=lotes_existentes if lotes_existentes else ["Nenhum lote ainda"])

# ==============================
# Nova Venda
# ==============================

if lote_selecionado != "Nenhum lote ainda":

    st.header("➕ Nova Venda")

    with st.form("form_venda"):
        cliente = st.text_input("Nome do Cliente")
        modelo = st.text_input("Modelo da Camisa")
        tamanho = st.selectbox("Tamanho", ["P", "M", "G", "GG"])
        forma_pagamento = st.selectbox(
            "Forma de Pagamento",
            ["50% Reserva", "Pagamento total na entrega"]
        )

        submitted = st.form_submit_button("Cadastrar Venda")

        if submitted and cliente and modelo:
            valor_recebido = VALOR_VENDA * 0.5 if forma_pagamento == "50% Reserva" else 0

            nova_venda = {
                "Lote": lote_selecionado,
                "Cliente": cliente,
                "Modelo": modelo,
                "Tamanho": tamanho,
                "Forma Pagamento": forma_pagamento,
                "Valor Venda": VALOR_VENDA,
                "Custo": CUSTO_CAMISA,
                "Valor Recebido": valor_recebido,
                "Valor a Receber": VALOR_VENDA - valor_recebido,
                "Entregue": "Não"
            }

            df = pd.concat([df, pd.DataFrame([nova_venda])], ignore_index=True)
            salvar_dados(df)
            st.session_state.df = df
            st.success("Venda cadastrada com sucesso!")
            st.rerun()

    # ==============================
    # Dados do Lote
    # ==============================

    df_lote = df[df["Lote"] == lote_selecionado]

    st.header(f"📊 Resumo do {lote_selecionado}")

    total_vendas = len(df_lote)
    faltam = LOTE_MINIMO - total_vendas

    total_receita = df_lote["Valor Venda"].sum()
    total_custo = df_lote["Custo"].sum()
    total_lucro = total_receita - total_custo
    total_recebido = df_lote["Valor Recebido"].sum()
    total_a_receber = df_lote["Valor a Receber"].sum()
    roi = ((total_lucro / total_custo) * 100) if total_custo > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Vendidas", total_vendas)
    col2.metric("Faltam p/ fechar lote", max(faltam, 0))
    col3.metric("Lucro do Lote", f"R$ {total_lucro:.2f}")

    st.metric("ROI do Lote", f"{roi:.2f}%")
    st.metric("Total Recebido", f"R$ {total_recebido:.2f}")
    st.metric("Total a Receber", f"R$ {total_a_receber:.2f}")

    st.subheader("Vendas por Tamanho")
    st.dataframe(df_lote["Tamanho"].value_counts().reset_index().rename(columns={"index": "Tamanho", "Tamanho": "Quantidade"}))

# ==============================
# Resumo Geral
# ==============================

if not df.empty:

    st.header("💼 Resumo Geral do Negócio")

    receita_total = df["Valor Venda"].sum()
    custo_total = df["Custo"].sum()
    lucro_total = receita_total - custo_total
    roi_total = ((lucro_total / custo_total) * 100) if custo_total > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Receita Total", f"R$ {receita_total:.2f}")
    col2.metric("Lucro Total", f"R$ {lucro_total:.2f}")
    col3.metric("ROI Total", f"{roi_total:.2f}%")
