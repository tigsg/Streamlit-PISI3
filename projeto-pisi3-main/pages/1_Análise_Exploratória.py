import streamlit as st
import pandas as pd
from utils import carregar_dados, grafico_barras, diagrama_pareto, grafico_heatmap

# Carregar os dados
df = carregar_dados("data/df_com_clusters_atualizados.parquet")

tab1, tab2 = st.tabs(['Gráficos', 'Gráfico Avançado'])

with tab1:
    # Dicionário para traduzir os gêneros
    traducao_generos = {
        'Drama': 'Drama',
        'Documentary': 'Documentário',
        'Comedy': 'Comédia',
        'Animation': 'Animação',
        'Horror': 'Terror',
        'Romance': 'Romance',
        'Music': 'Música',
        'Thriller': 'Suspense',
        'Action': 'Ação',
        'Crime': 'Crime',
        'Family': 'Família',
        'TV Movie': 'Filme de TV',
        'Adventure': 'Aventura',
        'Fantasy': 'Fantasia',
        'Science Fiction': 'Ficção Científica',
        'Mystery': 'Mistério',
        'History': 'História',
        'War': 'Guerra',
        'Western': 'Faroeste'
    }

    traducao_production_countries = {
        'United States of America': 'EUA',
        'France': 'França',
        'United Kingdom': 'Reino Unido',
        'Germany': 'Alemanha',
        'Japan': 'Japão',
        'Canada': 'Canadá',
        'India': 'India',
        'Italy': 'Itália',
        'Brazil': 'Brasil',
        'Spain': 'Espanha',
        'Mexico': 'México',
        'China': 'China',
        'Russia': 'Russia',
        'Soviet Union': 'União Soviética',
        'Belgium': 'Bélgica',
        'South Korea': 'Coreia do Sul',
        'Australia': 'Austrália'
    }

    traducao_spoken_language = {
        'English': 'Inglês',
        'French': 'Francês',
        'Spanish': 'Espanhol',
        'Japanese': 'Japonês',
        'German': 'Alemão',
        'No Language': 'Sem Idioma',
        'Russian': 'Russo',
        'Portuguese': 'Português',
        'Italian': 'Italiano',
        'Mandarin': 'Mandarim',
        'Arabic': 'Árabe',
        'Korean': 'Coreano',
        'Cantonese': 'Cantonês',
        'Latin': 'Latim'

    }

    # Função para traduzir os gêneros corretamente
    def traduzir_generos(genre_str, traducao):
        if pd.isna(genre_str):  # Verifica se é NaN
            return genre_str
        generos = genre_str.split(', ')  # Divide os gêneros em uma lista
        generos_traduzidos = [traducao.get(g, g) for g in generos]  # Traduz os gêneros
        return ', '.join(generos_traduzidos)  # Junta os gêneros traduzidos de volta

    def traduzir_spoken_languages(genre_str, traducao):
        if pd.isna(genre_str):  # Verifica se é NaN
            return genre_str
        generos = genre_str.split(', ')  # Divide os gêneros em uma lista
        generos_traduzidos = [traducao.get(g, g) for g in generos]  # Traduz os gêneros
        return ', '.join(generos_traduzidos)  # Junta os gêneros traduzidos de volta

    def traduzir_production_countries(genre_str, traducao):
        if pd.isna(genre_str):  # Verifica se é NaN
            return genre_str
        generos = genre_str.split(', ')  # Divide os gêneros em uma lista
        generos_traduzidos = [traducao.get(g, g) for g in generos]  # Traduz os gêneros
        return ', '.join(generos_traduzidos)

    df['genres'] = df['genres'].apply(traduzir_generos, args=(traducao_generos,))

    # df['status'] = df['status'].replace(traducao_status)

    df['spoken_languages'] = df['spoken_languages'].apply(traduzir_spoken_languages, args=(traducao_spoken_language,))

    df['production_countries'] = df['production_countries'].apply(traduzir_production_countries, args=(traducao_production_countries,))

    # Gráfico de barras - Aparições de Gêneros
    st.plotly_chart(grafico_barras(df, 'genres', 'Aparições de Gêneros'))
    st.write("Podemos observar que o gênero drama é o mais presente nos registros do dataseet, aparecêndo em quase metade, seguido dos gêneros comédia, ação, romance e suspense, sendo esses os 5 gêneros que mais aparecem no dataset. O dataset possui poucos filmes com gênero 'nulo', ou seja, com esse dado faltante.")

    # Gráfico de barras - Estado de lançamento das produções
    # st.plotly_chart(grafico_barras(df, 'status', 'Estado de Lançamento das Produções'))
    # st.write("Depois do tratamento é possível observar que não houveram mudanças significativas. Isto indica que o dataset segue útil para o estudo, visto que precisamos de dados sobre os resultados que os filmes obtiveram após seus lançamentos, dados esses que só os filmes que compõem a coluna 'Lançado' proporcionam.")

    # Diagrama de Pareto - Envolvimento de países
    st.plotly_chart(diagrama_pareto(df, 'production_countries', 'Envolvimento de Países nas Produções'))
    st.write("""O país 'Estados Unidos da América' está envolvido na produção da maioria dos filmes presentes no dataset. Em seguida temos: Reino Unido, França, Índia e Alemanha""")

    # Diagrama de Pareto - Distribuição de línguas faladas
    st.plotly_chart(diagrama_pareto(df, 'spoken_languages', 'Distribuição de Línguas Faladas'))
    st.write("A grande maioria dos filmes no dataset possuem o inglês sendo falado em algum momento do filme. As outras línguas possuem uma distribuição semelhante, não exercendo grande influência.")

with tab2:
    st.plotly_chart(grafico_heatmap(df, ['revenue', 'budget', 'runtime', 'lucro'], 'Correlação entre colunas numericas' ))
    st.text("O heatmap mostra a correlação entre diferentes variáveis numéricas relacionadas a filmes.")