import pandas as pd
import plotly.express as px
import streamlit as st




#criar as funções de carregamentos de dados
@st.cache_data
def carregar_dados(dataset):
    dados = pd.read_parquet(dataset)
    dados = dados[dados['adult'] == False]
    return dados

def df_head(data_frame):
    return data_frame.head()

def df_tail(data_frame):
    return data_frame.tail()

def grafico_barras(data_frame, coluna, titulo):

    cores_generos = {
    'Drama': '#1B1B1B',
    'Comédia': '#D90429',
    'Ação': '#FFD700',
    'Suspense': '#FFAA33',
    'Romance': '#A2A2A2',
    'Aventura': '#001F3F',
    'Crime': '#8B4513',
    'Terror': '#F5C518',
    'Família': '#5A5A5A',
    'Ficção Científica': '#B22222',
    'Fantasia': '#004D73',
    'Mistério': '#33FFAA',
    'Animação': '#6A0DAD',
    'História': '#808000',
    'Guerra': '#FF69B4',
    'Música': '#556B2F',
    'Documentário': '#FFA07A',
    'Faroeste': '#4682B4',
    'Filme de TV': '#FFDAB9',
    }

    if coluna == 'genres':
        cores = cores_generos

    dados_separados = data_frame[coluna].str.split(', ').explode()
    aparicoes_dados = dados_separados.value_counts().sort_values(ascending=False)
    aparicoes_dados_df = aparicoes_dados.reset_index(name='Quantidade')

    fig = px.bar(
        data_frame=aparicoes_dados_df,
        x= 'Quantidade',
        y=coluna,
        title=titulo,
        color=coluna,  # Usar os valores do eixo y para definir as cores
        color_discrete_map=cores
    )

    fig.update_layout(
    xaxis=dict(
        title=None,  # Remove o título do eixo X
        tickfont=dict(
            color='black',
            size=14,
            family="Arial"
        )
    ),
    yaxis=dict(
        title=None,  # Remove o título do eixo Y
        tickfont=dict(
            color='black',
            size=10,
            family="Arial"
        )
    ),
    )
    

    return fig
def diagrama_pareto(data_frame, coluna, titulo):

    cores_linguas = {
    'Inglês': '#1B1B1B',
    'Francês': '#D90429',
    'Espanhol': '#FFD700',
    'Russo': '#FFAA33',
    'Alemão': '#A2A2A2',
    'Italiano': '#001F3F',
    'Hindi': '#8B4513',
    'Mandarin': '#F5C518',
    'Japonês': '#5A5A5A',
    'Arabic': '#B22222',
    'Português': '#004D73',
    'Korean': '#33FFAA',
    'Cantonese': '#6A0DAD',
    'Latin': '#808000',
    'Outros': '#FF69B4'
    }

    cores_paises = {
    'EUA': '#1B1B1B',
    'Reino Unido': '#D90429',
    'França': '#FFD700',
    'India': '#FFAA33',
    'Alemanha': '#A2A2A2',
    'Canadá': '#001F3F',
    'Espanha': '#8B4513',
    'Japão': '#F5C518',
    'China': '#5A5A5A',
    'Itália': '#B22222',
    'Russia': '#004D73',
    'Australia': '#33FFAA',
    'Belgium': '#6A0DAD',
    'Hong Kong': '#808000',
    'South Korea': '#FF69B4',
    'Outros': '#556B2F'
    }

    if coluna == 'spoken_languages':
        cores = cores_linguas
    elif coluna == 'production_countries':
        cores = cores_paises

    #Contando as aparições de dados
    dados_separados = data_frame[coluna].str.split(', ').explode()
    aparicoes_dados = dados_separados.value_counts().sort_values(ascending=False)
    agrupado = aparicoes_dados.reset_index(name='Contagem')
    agrupado = agrupado.sort_values('Contagem', ascending=False)

    #Criando a série do somas acumulativas
    agrupado['Acumulado'] = agrupado['Contagem'].cumsum() / agrupado['Contagem'].sum() * 100

    #Criando a barra 'outros' após a linha atingir os 70%
    agrupado_principal = agrupado[agrupado['Acumulado'] <= 90]
    agrupado_outros = agrupado[agrupado['Acumulado'] > 90]
    outros_contagem = agrupado_outros['Contagem'].sum()
    linha_outros = pd.DataFrame({coluna: ['Outros'], 'Contagem': [outros_contagem], 'Acumulado': [100]})
    agrupado_principal = pd.concat([agrupado_principal, linha_outros], ignore_index=True)

    #Criando o diagrama em si
    fig = px.bar(
        agrupado_principal,
        y=coluna,
        x='Contagem',
        title=titulo,
        color=coluna,
        color_discrete_map=cores,
        labels={'Contagem': 'Contagem'})
    fig.add_scatter(
        y=agrupado_principal[coluna],
        x=agrupado_principal['Acumulado'],
        mode='lines+markers',
        name='Porcentagem',
        line=dict(color='#800080', width=2),
        xaxis='x2',
    )
    fig.update_layout(
    xaxis=dict(
        title=None,  # Remove o título do eixo X
        tickfont=dict(
            color='black',
            size=14,
            family="Arial"
        )
    ),
    yaxis=dict(
        title=None,  # Remove o título do eixo Y
        tickfont=dict(
            color='black',
            size=14,
            family="Arial"
        ),
        tickmode='linear'  # Ensure all ticks are shown
    ),
    xaxis2=dict(title=None, overlaying='x', side='top', showgrid=False),  # Remove título do segundo eixo
)

    return fig


def grafico_caixa(data_frame, coluna, titulo):
    fig = px.box(data_frame, y=coluna, title=titulo)
    return fig

def grafico_heatmap(data_frame, colunas, titulo):
    # Filtra o DataFrame para as colunas desejadas
    df_filtrado = data_frame[colunas]
    
    # Calcula a matriz de correlação (apenas numéricas)
    matriz_correlacao = df_filtrado.corr()
    
    # Cria o heatmap com um colorscale válido
    fig = px.imshow(
        matriz_correlacao,
        text_auto=True,  # Mostra os valores diretamente no gráfico
        title=titulo,
        color_continuous_scale="viridis"  # Substitua por outro esquema se desejar
    )
    return fig


