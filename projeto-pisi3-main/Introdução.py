import streamlit as st

st.set_page_config(
    page_title="Análise Exploratória de Dados TMDB",
    layout="wide",
)

st.title("Análise e predição de sucesso de filmes com alto orçamento")
st.write("""Este aplicativo viza realizar uma análise exploratória no dataset "TMDB_movie_dataset_v11" pós o tratamento feito (ler próximo parágrafo) e utilizar modelos de classificação para predizer o sucesso de um filme de alto orçamento. Também utilizamos algoritmos de clusterização com a finalidade de perceber quais gêneros de filmes mais fizeram sucesso em determinada década e também para ajudar os modelos de classificação. """)
st.write("""No tratamento, foram removidos filmes com orçamento menor que 1 milhão de
dólares e registros com valores nulos nas colunas que informam o orçamento e receita do filme foram removidos. Tipos de filmes que não são exibidos em cinemas também foram removidos.
""")
st.write("""Utilize o menu lateral para navegar entre as páginas.""")
