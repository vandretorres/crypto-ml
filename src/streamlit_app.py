import sys
import os
# Ajusta o path para incluir raiz do projeto
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import argparse
import streamlit as st
import pandas as pd
import locale
from src.config import VS_CURRENCY

# Ajusta locale para português brasileiro (opcional)
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except locale.Error:
        pass

# Mapeia código de moeda para símbolo
CURRENCY_SYMBOLS = {
    'usd': '$',
    'brl': 'R$'
}
currency_symbol = CURRENCY_SYMBOLS.get(VS_CURRENCY.lower(), '$')

# Parser para argumento --file
parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, help='Caminho para o arquivo CSV de avaliação')
args, unknown = parser.parse_known_args()
csv_path = args.file if (args and args.file) else None

st.set_page_config(page_title='Avaliação de Simulação', layout='wide')
st.title("📊 Avaliação de Simulação de Compra")

# Carregamento do CSV
if not csv_path:
    st.sidebar.header("Configuração")
    csv_path = st.sidebar.text_input("Caminho do CSV de avaliação:", '')
    uploaded = st.sidebar.file_uploader("Ou faça upload do CSV", type=['csv'])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    elif csv_path:
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")
            st.stop()
    else:
        st.info("Por favor, informe um caminho de arquivo ou faça upload de um CSV.")
        st.stop()
else:
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {csv_path}: {e}")
        st.stop()

st.markdown(f"**Arquivo carregado:** `{csv_path}`")

# Preserve dados originais para cálculos
# df_raw manterá dados numéricos originais
if 'df_raw' not in locals():
    df_raw = df.copy()

# Formatação dos dados para exibição
currency_cols = [
    col for col in df.columns
    if col.lower() in ['asset_cost', 'exchange_fee', 'network_fee', 'total_cost', 'price', 'current_price', 'current_value', 'profit']
]
percent_cols = ['profit_pct']

# Aplica formatação somente na cópia de exibição
df_display = df.copy()
for col in currency_cols:
    df_display[col] = df_display[col].apply(lambda x: f"{currency_symbol} {x:,.2f}")
for col in percent_cols:
    if col in df_display.columns:
        # Remove possível '%' anterior e converta para float
        df_display[col] = df_display[col].astype(float) if df_display[col].dtype != 'float' else df_display[col]
        df_display[col] = df_display[col].apply(lambda x: f"{x*100:,.2f}%")

# Exibição da tabela formatada
st.subheader("Tabela de Avaliação")
with st.expander("Mostrar Tabela Completa"):
    st.dataframe(df_display, use_container_width=True)

# Estatísticas resumidas usando df_raw
st.subheader("Resumo Estatístico")
# Calcule métricas a partir de df_raw
total_cost_sum = df_raw['total_cost'].sum()
current_value_sum = df_raw['current_value'].sum()
profit_sum = df_raw['profit'].sum()
profit_pct_mean = df_raw['profit_pct'].mean() * 100

summary_df = pd.DataFrame({
    'Métrica': ['Total Investido', 'Valor Atual', 'Lucro Bruto', 'Lucro (%)'],
    'Valor': [
        f"{currency_symbol} {total_cost_sum:,.2f}",
        f"{currency_symbol} {current_value_sum:,.2f}",
        f"{currency_symbol} {profit_sum:,.2f}",
        f"{profit_pct_mean:,.2f}%"
    ]
})
st.table(summary_df)
cols_summary = ['total_cost', 'current_value', 'profit', 'profit_pct']
summary_df = pd.DataFrame({
    'Métrica': ['Total Investido', 'Valor Atual', 'Lucro Bruto', 'Lucro (%)'],
    'Valor': [
        f"{currency_symbol} {df['total_cost'].sum():,.2f}",
        f"{currency_symbol} {df['current_value'].sum():,.2f}",
        f"{currency_symbol} {df['profit'].sum():,.2f}",
        f"{df['profit_pct'].mean()*100:,.2f}%"
    ]
})
st.table(summary_df)
