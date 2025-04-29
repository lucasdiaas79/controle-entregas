import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

# Configurações iniciais
caminho_arquivo_json = 'meuarquivo.json'
id_planilha = '1bL_DHWIS8Su5wGIoXCSFUUGhxnjkgrvNbsE_FLZVVNc'

# Escopo necessário
escopo = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Autenticação
credenciais = Credentials.from_service_account_file(caminho_arquivo_json, scopes=escopo)
cliente = gspread.authorize(credenciais)

# Acesso à planilha
planilha = cliente.open_by_key(id_planilha)
sheet = planilha.sheet1

# Funções auxiliares
def ler_planilha():
    dados = sheet.get_all_records()
    df = pd.DataFrame(dados)
    if 'Pago' not in df.columns:
        df['Pago'] = 'Não'
    if 'Entregue' not in df.columns:
        df['Entregue'] = 'Não'
    return df

def adicionar_pedido(tipo_areia, condominio, lote, cacambeiro, custo_areia, custo_venda):
    nova_linha = [tipo_areia, condominio, lote, cacambeiro, custo_areia, custo_venda, 'Não', 'Não']
    sheet.append_row(nova_linha)

def atualizar_celula(linha, coluna, novo_valor):
    sheet.update_cell(linha, coluna, novo_valor)

def apagar_linha(linha):
    sheet.delete_rows(linha)

# Interface do Streamlit
st.set_page_config(page_title="Controle de Entregas", layout="wide")
st.title('🏗️ Controle de Entregas de Areia e Brita')

menu = st.sidebar.radio('Navegação', ['🏠 Dashboard', '📄 Visualizar Planilha', '➕ Adicionar Pedido', '✏️ Atualizar Célula'])

if menu == '🏠 Dashboard':
    df = ler_planilha()

    st.markdown(
        """
        <h2 style='text-align: center; color: #FFA500;'>📊 Visão Geral da Empresa</h2>
        <hr style="border:1px solid #FFA500">
        """, unsafe_allow_html=True
    )

    # Cálculos protegidos para planilha vazia
    if df.empty:
        total_pedidos = 0
        faturamento_total = 0
        saldo = 0
        entregas_pendentes = 0
    else:
        total_pedidos = len(df)
        faturamento_total = df[df['Pago'] == 'Sim']['Custo de Venda (R$)'].sum()
        saldo = (df[df['Pago'] == 'Sim']['Custo de Venda (R$)'] - df[df['Pago'] == 'Sim']['Custo da Areia (R$)']).sum()
        entregas_pendentes = len(df[(df['Pago'] != 'Sim') | (df['Entregue'] != 'Sim')])

    cor_saldo = "green" if saldo >= 0 else "red"

    # Mostrar cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div style="background-color: #333333; padding:20px; border-radius:10px; border:2px solid #FFA500;">
                <h3 style="text-align:center; color:white;">📦 Total de Pedidos</h3>
                <h2 style="text-align:center; color:#FFA500;">{total_pedidos}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div style="background-color: #333333; padding:20px; border-radius:10px; border:2px solid #FFA500;">
                <h3 style="text-align:center; color:white;">💵 Faturamento Total</h3>
                <h2 style="text-align:center; color:#FFA500;">R$ {faturamento_total:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div style="background-color: #333333; padding:20px; border-radius:10px; border:2px solid #FFA500;">
                <h3 style="text-align:center; color:white;">🚚 Entregas Pendentes</h3>
                <h2 style="text-align:center; color:#FFA500;">{entregas_pendentes}</h2>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div style="background-color: #333333; padding:20px; border-radius:10px; border:2px solid #FFA500;">
                <h3 style="text-align:center; color:white;">📈 Saldo Atual</h3>
                <h2 style="text-align:center; color:{cor_saldo};">R$ {saldo:,.2f}</h2>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader('🚚 Entregas Pendentes')

    df_pendentes = df[(df['Pago'] != 'Sim') | (df['Entregue'] != 'Sim')]

    for idx, row in df_pendentes.iterrows():
        linha_planilha = idx + 2
        cor_linha = "#D4EDDA" if row['Pago'] == 'Sim' else "#FFFFFF"

        with st.container():
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                st.markdown(f"<div style='background-color:{cor_linha};padding:10px'>{row['Tipo de Areia']}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='background-color:{cor_linha};padding:10px'>{row['Condomínio']}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div style='background-color:{cor_linha};padding:10px'>{row['Lote']}</div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div style='background-color:{cor_linha};padding:10px'>R$ {row['Custo de Venda (R$)']}</div>", unsafe_allow_html=True)
            with col5:
                if st.button('Marcar como Pago', key=f"pago_{idx}"):
                    atualizar_celula(linha_planilha, 7, 'Sim')
                    st.success('✅ Pedido marcado como Pago! Atualize a página.')
            with col6:
                if st.button('Marcar como Entregue', key=f"entregue_{idx}"):
                    atualizar_celula(linha_planilha, 8, 'Sim')
                    st.success('✅ Pedido marcado como Entregue! Atualize a página.')
            with col7:
                if st.button('Apagar Pedido', key=f"apagar_{idx}"):
                    apagar_linha(linha_planilha)
                    st.warning('⚠️ Pedido apagado! Atualize a página.')

elif menu == '📄 Visualizar Planilha':
    df = ler_planilha()
    st.subheader('📋 Histórico de Pedidos')

    for idx, row in df.iterrows():
        linha_planilha = idx + 2
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)
        with col1:
            st.write(row['Tipo de Areia'])
        with col2:
            st.write(row['Condomínio'])
        with col3:
            st.write(row['Lote'])
        with col4:
            st.write(row['Caçambeiro'])
        with col5:
            st.write(f"R$ {row['Custo da Areia (R$)']}")
        with col6:
            st.write(f"R$ {row['Custo de Venda (R$)']}")
        with col7:
            st.write(row['Pago'])
        with col8:
            st.write(row['Entregue'])
        with col9:
            if st.button('Apagar Histórico', key=f"apagar_hist_{idx}"):
                apagar_linha(linha_planilha)
                st.warning('⚠️ Pedido apagado do histórico! Atualize a página.')

elif menu == '➕ Adicionar Pedido':
    st.subheader('➕ Novo Pedido')

    materiais = [
        'Areia fina', 'Areia grossa', 'Aterro', 'Arenoso',
        'Areia Lavada', 'Terra Preta', 'Brita 0', 'Brita 3/4',
        'Brita 1', 'Pó de Brita', 'Seixo'
    ]

    tipo_areia = st.selectbox('Tipo de Material', materiais)
    condominio = st.text_input('Condomínio')
    lote = st.text_input('Lote')
    cacambeiro = st.text_input('Caçambeiro')
    custo_areia = st.number_input('Custo da Areia (R$)', min_value=0.0, step=0.01)
    custo_venda = st.number_input('Custo de Venda (R$)', min_value=0.0, step=0.01)

    if st.button('Salvar Pedido', type="primary"):
        adicionar_pedido(tipo_areia, condominio, lote, cacambeiro, custo_areia, custo_venda)
        st.success('✅ Pedido adicionado com sucesso! Atualize a página para ver.')

elif menu == '✏️ Atualizar Célula':
    df = ler_planilha()
    st.subheader('✏️ Atualizar Informação')
    linha = st.number_input('Número da linha (começa em 1)', min_value=1)
    coluna = st.number_input('Número da coluna (1 = Tipo de Areia, 2 = Condomínio, etc.)', min_value=1)
    novo_valor = st.text_input('Novo valor')

    if st.button('Atualizar Informação', type="primary"):
        atualizar_celula(linha, coluna, novo_valor)
        st.success('✅ Atualização realizada com sucesso!')
