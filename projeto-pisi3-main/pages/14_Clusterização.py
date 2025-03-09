#Análise exploratória dos resultados da clusterização
#Importando bibliotecas
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime

# Função para carregar os dados
def carregar_dados(filepath):
    return pd.read_parquet(filepath)

#Carregando dados
dataset = pd.read_parquet("data/df_com_clusters_atualizados.parquet")

#Explorando os clusters provenientes do KModes (clusterização dos dados categóricos)
cores_cinema = ["#1B1B1B", "#D90429", "#FFD700", "#FFAA33", "#A2A2A2", 
                "#001F3F", "#8B4513", "#F5C518", "#5A5A5A", "#B22222"]

cluster0kmodes = dataset[dataset['cluster_kmodes'] == 0]
cluster1kmodes = dataset[dataset['cluster_kmodes'] == 1]
cluster2kmodes = dataset[dataset['cluster_kmodes'] == 2]
cluster3kmodes = dataset[dataset['cluster_kmodes'] == 3]

# Dicionário de tradução
traducao = {
    'genres': 'Gêneros',
    'spoken_languages': 'Línguas Faladas',
    'production_countries': 'Países de Produção'
}

def grafico_barras(cluster, data, coluna, qtd):
    contagem = data.groupby(coluna).size()
    top_10_contagem = contagem.nlargest(qtd)
    top_10_contagem = top_10_contagem.sort_values(ascending=True)
    
    coluna_traduzida = traducao.get(coluna, coluna)  # Traduz a coluna se houver tradução disponível
    
    fig = px.bar(top_10_contagem, x=top_10_contagem.values, y=top_10_contagem.index, 
                 title=f"{coluna_traduzida} mais presentes no cluster {cluster}", 
                 labels={"x": "Contagem", coluna: coluna_traduzida})
    fig.update_traces(marker=dict(color=cores_cinema))
    return fig

#Comparação de existência de lucro
def contar_lucro (df):
    return (df['revenue'] > df['budget']).sum() / ((df['revenue'] > df['budget']).sum() + (df['revenue'] < df['budget']).sum())

#Quantidades de filmes que lucraram por cluster
lucrou0 = contar_lucro(cluster0kmodes)
lucrou1 = contar_lucro(cluster1kmodes)
lucrou2 = contar_lucro(cluster2kmodes)
lucrou3 = contar_lucro(cluster3kmodes)

#Explorando os clusters provenientes do KMeans (clusterização dos dados numéricos)
cluster0kmeans = dataset[dataset['cluster_kmeans'] == 0]
cluster1kmeans = dataset[dataset['cluster_kmeans'] == 1]

#Porcentagem de filmes que lucraram por cluster
lucrou0kmeans = contar_lucro(cluster0kmeans)
lucrou1kmeans = contar_lucro(cluster1kmeans)

#Porcentagem de lucro nas regiões do heatmap
contagem_lucro_regioes = dataset.groupby(['cluster_kmodes', 'cluster_kmeans'], group_keys=False).apply(contar_lucro, include_groups=False).reset_index(name='porcentagem_lucro')

#Definindo funções
#Retorna a década em que o filme foi lançado
def get_decada(idade):
    ano_atual = datetime.now().year
    ano_do_filme = ano_atual - idade
    decada = (ano_do_filme // 10) * 10
    return f"{decada}s"

#Retorna um dicionário com décadas sendo suas chaves e a lucratividade total que um cluster obteve naquela década como seus valores
def coletar_lucro_medio_decada(dataset, filmes_decada, cluster):
    lucro_total = {decada: 0 for decada in filmes_decada}
    contagem_filmes = {decada: 0 for decada in filmes_decada}
    for _, row in dataset.iterrows():
        decada_filme = get_decada(row['idade'])
        lucro = row['lucro']
        if decada_filme in filmes_decada:
            lucro_total[decada_filme] += lucro
            contagem_filmes[decada_filme] += 1
    for decada in filmes_decada:
        if contagem_filmes[decada] > 0:
            filmes_decada[decada][cluster] = lucro_total[decada] / contagem_filmes[decada]
        else:
            filmes_decada[decada][cluster] = 0 
    
    return filmes_decada

#Plota um gráfico de barras que mostra o lucro médio de um cluster através das décadas
def plotar_lucro_decada(filmes_decada, cluster):
    df = pd.DataFrame([(decada, valores[str(cluster)]) for decada, valores in filmes_decada.items()],
                      columns=['Década', 'Lucro Médio'])
    df = df.sort_values(by='Década')
    fig = px.bar(df, x='Década', y='Lucro Médio', 
                 title=f'Lucro Médio do Cluster {cluster} por Década',
                 labels={'Lucro Médio': f'Lucro Médio do Cluster {cluster}', 'Década': 'Década'},
                 text_auto=True)
    fig.update_traces(marker=dict(color=cores_cinema)) 
    return fig

#Plota um gráfico com a maior lucratividade média por década, informando de qual cluster veio essa lucratividade
def plotar_maior_lucro_decada(filmes_decada):
    cluster_nomes = {
        '0': '0',
        '1': '1',
        '2': '2',
        '3': '3'
    }
    dados = []
    for decada, clusters in filmes_decada.items():
        max_cluster = max(clusters, key=clusters.get)  
        max_lucro = clusters[max_cluster]  
        dados.append((decada, max_lucro, cluster_nomes[max_cluster]))
    
    df = pd.DataFrame(dados, columns=['Década', 'Lucro Máximo', 'Cluster'])
    df = df.sort_values(by='Década')

    # Criando uma nova coluna para exibir no eixo X com quebra de linha
    df["Década_Cluster"] = df["Década"].astype(str) + "<br>" + df["Cluster"]

    fig = px.bar(df, x='Década_Cluster', y='Lucro Máximo', text_auto=True,
                 title='Maior Lucratividade por Década e Cluster',
                 labels={'Lucro Máximo': 'Maior Lucro na Década', 'Década_Cluster': 'Década e Cluster'},
                 hover_data=['Cluster'])

    fig.update_traces(marker=dict(color=cores_cinema)) 

    # Evita inclinação dos rótulos
    fig.update_layout(xaxis_tickangle=0)

    return fig

#Criando o dicionário que guardará a lucratividade por cluster em cada época
filmes_decada = {'1910s': {'0': 0, '1': 0, '2': 0, '3': 0},'1920s': {'0': 0, '1': 0, '2': 0, '3': 0}, '1930s': {'0': 0, '1': 0, '2': 0, '3': 0}, '1940s': {'0': 0, '1': 0, '2': 0, '3': 0}, '1950s': {'0': 0, '1': 0, '2': 0, '3': 0}, '1960s': {'0': 0, '1': 0, '2': 0, '3': 0}, '1970s': {'0': 0, '1': 0, '2': 0, '3': 0}, '1980s': {'0': 0, '1': 0, '2': 0, '3': 0}, '1990s': {'0': 0, '1': 0, '2': 0, '3': 0}, '2000s': {'0': 0, '1': 0, '2': 0, '3': 0}, '2010s': {'0': 0, '1': 0, '2': 0, '3': 0}, '2020s': {'0': 0, '1': 0, '2': 0, '3': 0}}

# Título da aplicação
st.title("Visualização da Clusterização 👀")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Escolha dos Clusters", "Clusters KModes", "Clusters KMeans", "Lucro KModes", "Lucro KMeans", "Heatmap e Lucro"])

with tab1:
    st.header("🎯 Escolha dos Clusters")
    st.write("A clusterização é uma técnica de aprendizado não supervisionado que tem como objetivo dividir um conjunto de dados em grupos de acordo com suas características. Neste projeto, utilizamos dois algoritmos de clusterização: KModes e KMeans. O KModes é um algoritmo que agrupa por dados categóricos, enquanto o KMeans agrupa por dados numéricos.")
    
    st.subheader("Elbow Method (KMeans)")
    st.image("imagens\Elbow Method KModes.png")
    st.write("O Elbow Method é um método utilizado para encontrar o número ideal de clusters em um conjunto de dados. O método consiste em plotar o valor da função objetivo (no caso, a soma dos quadrados das distâncias dos pontos ao centróide) em função do número de clusters. O ponto de inflexão do gráfico é o número ideal de clusters. No caso, 4.")

    st.subheader("Silhueta (KMeans)")
    st.image("imagens\Silhueta Kmeans.png")
    st.text("O método da silhueta é uma técnica de validação interna para medir a qualidade de um agrupamento. A técnica fornece uma maneira de avaliar a coerência interna de um agrupamento, ou seja, a distância média entre os pontos de um cluster e a distância média entre os pontos de clusters vizinhos.")

    st.subheader("Elbow Method (KModes)")
    st.image("imagens\Elbow Method KMeans.png")
    st.text("O Elbow Method é um método utilizado para encontrar o número ideal de clusters em um conjunto de dados. O método consiste em plotar o valor da função objetivo (no caso, a soma dos quadrados das distâncias dos pontos ao centróide) em função do número de clusters. O ponto de inflexão do gráfico é o número ideal de clusters. No caso, 2.")

with tab2:
    st.header("🔍 Entendendo os Clusters KModes")
    st.write("O algoritmo KModes é um algoritmo de clusterização que agrupa baseando-se em dados categóricos. Neste projeto, utilizamos o KModes para agrupar os filmes de acordo com seus gêneros, línguas faladas e países de produção. Abaixo, você pode visualizar os clusters gerados pelo KModes e as características de cada um deles.")
    cluster_selecionado = st.selectbox("Selecione o Cluster", ["0", "1", "2", "3"])
    if cluster_selecionado == "0":
        #Gêneros mais presentes no cluster 0
        st.subheader("Gêneros 🎬")
        fig = grafico_barras('0', cluster0kmodes, 'genres', 5)
        st.plotly_chart(fig)
        st.text("O algoritmo KModes selecionou para o cluster 0 filmes de comédia e seus subgêneros.")
        #Línguas mais faladas no cluster 0
        st.subheader("Línguas Faladas 🗣️")
        fig = grafico_barras('0', cluster0kmodes, 'spoken_languages', 8)
        st.plotly_chart(fig)
        st.text("O inglês é a língua mais falada no cluster, as outras seguem equilibradas.")
        #Páises mais presentes no cluster 0
        st.subheader("Países de Produção 🌍")
        fig = grafico_barras('0', cluster0kmodes, 'production_countries', 8)
        st.plotly_chart(fig)
        st.text("A maioria dos filmes presentes no cluster possuem o país Estados Unidos da América em suas produções.")
    elif cluster_selecionado == "1":
        #Gêneros mais presentes no cluster 1
        st.subheader("Gêneros 🎬")
        fig = grafico_barras('1', cluster1kmodes, 'genres', 5)
        st.plotly_chart(fig)
        st.text("O algoritmo KModes selecionou para o cluster 1 filmes de ação e seus subgêneros.")
        #Línguas mais faladas no cluster 1
        st.subheader("Línguas Faladas 🗣️")
        fig = grafico_barras('1', cluster1kmodes, 'spoken_languages', 8)
        st.plotly_chart(fig)
        st.text("O inglês é a língua mais falada no cluster, as outras seguem equilibradas.")
        #Páises mais presentes no cluster 1
        st.subheader("Países de Produção 🌍")
        fig = grafico_barras('1', cluster1kmodes, 'production_countries', 8)
        st.plotly_chart(fig)
        st.text("A maioria dos filmes presentes no cluster possuem o país Estados Unidos da América em suas produções.")
    elif cluster_selecionado == "2":
        st.subheader("Gêneros 🎬")
        #Gêneros mais presentes no cluster 2
        fig = grafico_barras('2', cluster2kmodes, 'genres', 5)
        st.plotly_chart(fig)
        st.text("O algoritmo KModes selecionou para o cluster 2 filmes de terror/suspense e seus subgêneros.")
        #Línguas mais faladas no cluster 2
        st.subheader("Línguas Faladas 🗣️")
        fig = grafico_barras('2', cluster2kmodes, 'spoken_languages', 8)
        st.plotly_chart(fig)
        st.text("O inglês é a língua mais falada no cluster, as outras seguem equilibradas.")
        #Páises mais presentes no cluster 2
        st.subheader("Países de Produção 🌍")
        fig = grafico_barras('2', cluster2kmodes, 'production_countries', 8)
        st.plotly_chart(fig)
        st.text("A maioria dos filmes presentes no cluster possuem o país Estados Unidos da América em suas produções.")
    else:
        st.subheader("Gêneros 🎬")
        #Gêneros mais presentes no cluster 3
        fig = grafico_barras('3', cluster3kmodes, 'genres', 5)
        st.plotly_chart(fig)
        st.text("O algoritmo KModes selecionou para o cluster 3 filmes de drama e seus subgêneros.")
        #Línguas mais faladas no cluster 3
        st.subheader("Línguas Faladas 🗣️")
        fig = grafico_barras('3', cluster3kmodes, 'spoken_languages', 8)
        st.plotly_chart(fig)
        st.text("O inglês é a língua mais falada no cluster, as outras seguem equilibradas.")
        #Páises mais presentes no cluster 3
        st.subheader("Países de Produção 🌍")
        fig = grafico_barras('3', cluster3kmodes, 'production_countries', 8)
        st.plotly_chart(fig)
        st.text("A maioria dos filmes presentes no cluster possuem o país Estados Unidos da América em suas produções.")

with tab3:
    st.header("🔍 Entendendo os Clusters KMeans")
    st.text("O algoritmo KMeans é um algoritmo de clusterização que agrupa baseando-se em dados numéricos. Neste projeto, utilizamos o KMeans para agrupar os filmes de acordo com seus valores nas colunas numéricas 'Receita', 'Orçamento' e 'Duração' do dataset. Abaixo, você pode visualizar os clusters gerados pelo KMeans e as características de cada um deles.")
    cluster_selecionado = st.selectbox("Selecione o Cluster", ["0", "1"])
    if cluster_selecionado == "0":
        #Gêneros mais presentes no cluster 0
        st.subheader("Gêneros 🎬")
        fig = grafico_barras('0', cluster0kmeans, 'genres', 5)
        st.plotly_chart(fig)
        st.text("O cluster 0 gerado pelo KMeans é o cluster que não possui apenas filmes que foram altamente lucrativos, então podemos observar através desse gráfico os gêneros menos propensos a terem uma lucratividade extrema.")
        #Línguas mais faladas no cluster 0
        st.subheader("Línguas Faladas 🗣️")
        fig = grafico_barras('0', cluster0kmeans, 'spoken_languages', 8)
        st.plotly_chart(fig)
        st.text("A maioria dos filmes do cluster são de língua inglêsa.")
        #Páises mais presentes no cluster 0
        st.subheader("Países de Produção 🌍")
        fig = grafico_barras('0', cluster0kmeans, 'production_countries', 8)
        st.plotly_chart(fig)
        st.text("A maioria dos filmes do cluster possuem os Estados Unidos da América em sua produção.")
    else:
        #Gêneros mais presentes no cluster 1
        st.subheader("Gêneros 🎬")
        fig = grafico_barras('1', cluster1kmeans, 'genres', 5)
        st.plotly_chart(fig)
        st.text("O cluster 1 gerado pelo KMeans é o cluster que possui filmes com as mais altas lucratividades, então podemos observar através do gráficos os gêneros mais propensos a fazerem tanto sucesso.")
        #Línguas mais faladas no cluster 1
        st.subheader("Línguas Faladas 🗣️")
        fig = grafico_barras('1', cluster1kmeans, 'spoken_languages', 8)
        st.plotly_chart(fig)
        st.text("A maioria dos filmes do cluster são de língua inglêsa.")
        #Páises mais presentes no cluster 1
        st.subheader("Países de Produção 🌍")
        fig = grafico_barras('1', cluster1kmeans, 'production_countries', 8)
        st.plotly_chart(fig)
        st.text("A maioria dos filmes do cluster possuem os Estados Unidos da América em sua produção.")

with tab4:
    st.header("💸 Lucro KModes")
    st.text("Aqui, você pode visualizar a porcentagem de filmes que lucraram em cada cluster gerado pelo KModes.")
    st.text("Além disso, é possível ver o lucro médio dos clusters por década.")
    #Porcentagem de filmes que lucraram por cluster

    dic_lucrou = {'Cluster' : ['0', '1', '2', '3'], 'Quantidade' : [lucrou0, lucrou1, lucrou2, lucrou3]}

    fig = go.Figure(
        data=[go.Bar(
            x=dic_lucrou['Cluster'], 
            y=dic_lucrou['Quantidade'], 
            marker_color=cores_cinema
        )]
    )

    fig.update_layout(
        title="Porcentagem de Filmes que Lucraram por Cluster",
        xaxis_title="Clusters",
        yaxis_title="Quantidade de Filmes",
        yaxis=dict(range=[0, 1])
    )

    fig.update_traces(hovertemplate='%{y:.1%}')

    st.plotly_chart(fig)

    st.text("Podemos observar que essa é a sequência do cluster mais lucrativo pro menos: cluster 1 (ação e subgêneros), cluster 0 (comédia e subgêneros), cluster 2 (terror/suspende e subgêneros), cluster 3 (drama e subgêneros).")

    # Sucesso do cluster 0 (cluster que possui filmes de comédia ou subgêneros relacionados) através das décadas
    filmes_decada0 = coletar_lucro_medio_decada(cluster0kmodes, filmes_decada, '0')
    fig = plotar_lucro_decada(filmes_decada0, '0')
    st.plotly_chart(fig)
    st.text("A década em que o cluster 0 (comédia e subgêneros) foi mais lucrativo foi na década de 2010.")

    # Sucesso do cluster 1 (cluster que possui filmes de ação e subgêneros relacionados) através das décadas
    filmes_decada1 = coletar_lucro_medio_decada(cluster1kmodes, filmes_decada, '1')
    fig = plotar_lucro_decada(filmes_decada1, '1')
    st.plotly_chart(fig)
    st.text("A década em que o cluster 1 (ação e subgêneros) foi mais lucrativo foi na década de 2010.")

    # Sucesso do cluster 2 (cluster que possui filmes de terror, suspense e subgêneros relacionados) através das décadas
    filmes_decada2 = coletar_lucro_medio_decada(cluster2kmodes, filmes_decada, '2')
    fig = plotar_lucro_decada(filmes_decada2, '2')
    st.plotly_chart(fig)
    st.text("A década em que o cluster 2 (terror, suspense e subgêneros) foi mais lucrativo foi na década de 1970.")

    # Sucesso do cluster 3 (cluster que possui filmes de drama e subgêneros relacionados) através das décadas
    filmes_decada3 = coletar_lucro_medio_decada(cluster3kmodes, filmes_decada, '3')
    fig = plotar_lucro_decada(filmes_decada3, '3')
    st.plotly_chart(fig)
    st.text("A década em que o cluster 3 (drama e subgêneros) foi mais lucrativo foi na década de 1990.")

    
    filmes_decada0 = coletar_lucro_medio_decada(cluster0kmodes, filmes_decada, '0')
    filmes_decada1 = coletar_lucro_medio_decada(cluster1kmodes, filmes_decada, '1')
    filmes_decada2 = coletar_lucro_medio_decada(cluster2kmodes, filmes_decada, '2')
    filmes_decada3 = coletar_lucro_medio_decada(cluster3kmodes, filmes_decada, '3')

    # Cluster mais lucrativo 
    fig = plotar_maior_lucro_decada(filmes_decada)
    st.plotly_chart(fig)
    st.text("Neste gráfico, podemos observar qual foi a maior lucratividade em cada década. Cada coluna representa o lucro médio do cluster que mais lucrou, e embaixo da década é possível ver o número do cluster em questão.")


with tab5:
    st.header("💸 Lucro KMeans")
    st.text("Aqui, você pode visualizar a porcentagem de filmes que lucraram em cada cluster gerado pelo KMeans.")
    #Porcentagem de filmes que lucraram por cluster

    dic_lucrou = {'Cluster' : ['0', '1'], 'Quantidade' : [lucrou0kmeans, lucrou1kmeans]}

    fig = go.Figure(
        data=[go.Bar(
            x=dic_lucrou['Cluster'], 
            y=dic_lucrou['Quantidade'], 
            marker_color=cores_cinema
        )]
    )

    fig.update_layout(
        title="Porcentagem de Filmes que Lucraram por Cluster",
        xaxis_title="Clusters",
        yaxis_title="Quantidade de Filmes",
        yaxis=dict(range=[0, 1]),
    )

    fig.update_traces(hovertemplate='%{y:.1%}')

    st.plotly_chart(fig)

    st.text("Podemos observar a porcentagem de lucro extrema do cluster 1 (outliers) e, mesmo o cluster 0 não possuindo outliers, podemos perceber")



with tab6:
    st.header("🔥 Heatmap e Lucro")
    st.text("Aqui, você pode visualizar a relação entre os clusters categóricos e numéricos, além da porcentagem de lucro por região no heatmap.")
    # Contando quantos registros pertencem a cada combinação de clusters
    heatmap_data = dataset.groupby(['cluster_kmodes', 'cluster_kmeans']).size().reset_index(name='Contagem')

    colorscale_cinema = [
        [0.0, "#0D0D0D"],
        [0.2, "#383838"],
        [0.4, "#FFC300"],
        [0.6, "#E25822"],
        [0.8, "#8B0000"],
        [1.0, "#FF0000"]
    ]

    # Criando um heatmap para melhor observar a relação entre a clusterização categórica e a numérica

    heatmap_data['cluster_kmodes'] = heatmap_data['cluster_kmodes'].astype(str)
    heatmap_data['cluster_kmeans'] = heatmap_data['cluster_kmeans'].astype(str)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data['Contagem'],
        x=heatmap_data['cluster_kmeans'],
        y=heatmap_data['cluster_kmodes'],
        colorscale=colorscale_cinema,
        text=heatmap_data['Contagem'],
        texttemplate="%{text}",
        hovertemplate="Cluster Numérico: %{x}<br>Cluster Categórico: %{y}<br>Contagem: %{text}<extra></extra>"
    ))

    fig.update_layout(
        title="Heatmap da Relação entre Clusters Categóricos e Numéricos",
        xaxis_title="Clusters Numéricos",
        yaxis_title="Clusters Categóricos"
    )

    st.plotly_chart(fig)

    st.text("O Heatmap demonstra a relação na distribuição dos registros entre os clusters categóricos e numéricos. Podemos observar, por exemplo, que a maioria dos filmes com lucratividade muito alta (filmes na posição 1 do eixo X) fazem parte do cluster 1 categórico (filmes de ação e subgêneros).")

    contagem_lucro_regioes['categoria'] = contagem_lucro_regioes['cluster_kmodes'].astype(str) + '-' + contagem_lucro_regioes['cluster_kmeans'].astype(str)

    fig = px.bar(
        contagem_lucro_regioes, 
        x='categoria', 
        y='porcentagem_lucro', 
        text='porcentagem_lucro',
        labels={'categoria': 'Região do Heatmap', 'porcentagem_lucro': 'Porcentagem de Lucro'},
        title='Porcentagem de Lucro por região no Heatmap',
        color = 'categoria',
        color_discrete_sequence = cores_cinema
    )

    fig.update_traces(texttemplate='%{text:.1%}', hovertemplate='%{y:.1%}')

    st.plotly_chart(fig)

    st.text("Podemos observar que as regiões que fazem parte do cluster 1 numérico possuem, em média, lucratividades extremamente altas (acima de 90%), devido ao algoritmo ter selecionado filmes que foram muito lucrativos para esse cluster. As outras regiões, embora não tão altas, também possuem boas porcentagens de lucro. Isso é devido ao fato de estarmos trabalhando apenas com filmes que possuíram um grande orçamento.")