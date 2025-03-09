import pandas as pd
from sklearn.svm import SVC
from sklearn.metrics import classification_report


def processar_dados(caminho_arquivo):
    # Carregar os dados
    dados = pd.read_parquet(caminho_arquivo)

    # Selecionar colunas relevantes
    dados = dados[["release_date", "revenue", "budget", "runtime", "genres", 
                  "original_language", "production_countries", "spoken_languages", "adult", "cluster", "clusters_n"]]

    # Filtrar dados (adult == False)
    dados = dados[dados["adult"] == False].copy()

    # Criar coluna 'disponibilidade_lucro'
    dados["disponibilidade_lucro"] = (
        dados["revenue"].apply(lambda x: isinstance(x, (int, float)) and x > 0) & 
        dados["budget"].apply(lambda x: isinstance(x, (int, float)) and x > 0)
    ).astype(int)

    # Eliminar registros com 'disponibilidade_lucro' igual a 0
    dados = dados[dados["disponibilidade_lucro"] == 1].copy()

    # Calcular 'lucro' e 'classificacao'
    dados['lucro'] = dados.apply(lambda row: row['revenue'] - row['budget']
                                 if isinstance(row['budget'], (int, float)) and isinstance(row['revenue'], (int, float))
                                 else None, axis=1)

    dados['classificacao'] = dados.apply(lambda row: 1 if row['lucro'] is not None and row['lucro'] > 0 and row['disponibilidade_lucro'] == 1 else 0, axis=1)

    # Criar o dataset 'dados_com_lucro' (classificacao == 1)
    dados_com_lucro = dados[dados['classificacao'] == 1]

    dados_com_lucro = dados_com_lucro[dados_com_lucro["budget"] >= 1000000]

    # Criar o dataset 'dados_sem_lucro' (classificacao == 0)
    dados_sem_lucro = dados[dados['classificacao'] == 0]

    # Criar duas amostras representativas de 'dados_com_lucro' (50% cada)
    metade_lucro_1 = dados_com_lucro.sample(frac=0.5, random_state=42)
    metade_lucro_2 = dados_com_lucro.drop(metade_lucro_1.index)  # O restante dos dados

    # Criar duas amostras representativas de 'dados_sem_lucro' (50% cada)
    metade_sem_lucro_1 = dados_sem_lucro.sample(frac=0.5, random_state=42)
    metade_sem_lucro_2 = dados_sem_lucro.drop(metade_sem_lucro_1.index)  # O restante dos dados

    # Concatenar as metades sem lucro com suas respectivas metades com lucro
    conjunto_1 = pd.concat([metade_lucro_1, metade_sem_lucro_1], ignore_index=True)
    conjunto_2 = pd.concat([metade_lucro_2, metade_sem_lucro_2], ignore_index=True)
    
    return conjunto_1, conjunto_2


def aplicar_one_hot_encoding_generos(df, generos):
    for genero in generos:
        df[genero] = df['genres'].apply(lambda x: 1 if isinstance(x, str) and genero in x.split(', ') else 0)
    return df


def aplicar_one_hot_encoding_limitado(df, idiomas_permitidos, selected_countries):

    df['original_language_encoded'] = df['original_language']
    df['production_countries_encoded'] = df['production_countries']
    df['original_language_encoded'] = df['original_language_encoded'].apply(
        lambda x: x if x in idiomas_permitidos else 'other_language'
    )
    df['production_countries_encoded'] = df['production_countries_encoded'].apply(
        lambda x: x if x in selected_countries else 'other_country'
    )
    df = pd.get_dummies(df, columns=['original_language_encoded', 'production_countries_encoded'], prefix=['lang', 'country'])

    return df

def lingua_idade(dados_treino_filtrado, dados_teste):

    for df in [dados_treino_filtrado, dados_teste]:

        df["num_languages"] = df["spoken_languages"].apply(lambda x: len(x.split(",")) if isinstance(x, str) else 0)
        df["idade"] = df["release_date"].apply(lambda x: 2025 - int(x.split("-")[0]) if isinstance(x, str) else 0)

    return  dados_treino_filtrado, dados_teste

def encoding(dados_teste_balanceado, dados_treino_balanceado, idiomas_permitidos, selected_countries, generos):

    dados_teste = dados_teste_balanceado.copy()

    dados_treino_filtrado = dados_treino_balanceado.copy()
    #   Criar novas colunas (número de idiomas e idade)

    dados_treino_filtrado, dados_teste = lingua_idade(dados_treino_filtrado, dados_teste)
    
    # Aplicar one-hot-encoding generos
    i=0
    for df in [dados_teste_balanceado, dados_treino_balanceado]:

        df = aplicar_one_hot_encoding_generos(df, generos)
        
        if i==0:
            dados_teste_balanceado = df
        else:
            dados_treino_balanceado = df


    # Aplicar one-hot encoding limitado
    dados_treino_encoded = aplicar_one_hot_encoding_limitado(dados_treino_filtrado, idiomas_permitidos, selected_countries)
    dados_teste_encoded = aplicar_one_hot_encoding_limitado(dados_teste, idiomas_permitidos, selected_countries)

    # Garantir que a coluna 'genres' seja preservada
    dados_treino_encoded['genres'] = dados_treino_filtrado['genres']
    dados_teste_encoded['genres'] = dados_teste['genres']

    # Alinhar colunas
    dados_treino_encoded, dados_teste_encoded = dados_treino_encoded.align(dados_teste_encoded, join='outer', axis=1, fill_value=0)

    return dados_teste_encoded, dados_treino_encoded

# Função para aplicar filtros com base nos inputs do usuário
def filtrando(df, countries=None, language=None, min_runtime=None, max_runtime=None, min_budget=None, max_budget=None, genres=None):

    if countries:
        df = df[df['production_countries'].astype(str).str.contains('|'.join(countries), na=False, case=False)]
    if language:
        df = df[df['original_language'] == language]
    if min_runtime is not None:
        df = df[df['runtime'] >= min_runtime]
    if max_runtime is not None:
        df = df[df['runtime'] <= max_runtime]
    if min_budget is not None:
        df = df[df['budget'] >= min_budget]
    if max_budget is not None:
        df = df[df['budget'] <= max_budget]
    if genres:
        df = df[df['genres'].astype(str).str.contains('|'.join(genres), na=False, case=False)]
    return df


def pegar_inputs(countries, language, min_runtime, max_runtime, min_budget, max_budget, genres):

    return countries, language, min_runtime, max_runtime, min_budget, max_budget, genres

def filtrar_dados(dados_teste_encoded, dados_treino_encoded, countries, language, min_runtime,
                    max_runtime, min_budget,
                    max_budget, genres): 

    i=0
    for  df in [dados_teste_encoded, dados_treino_encoded]:

        df = filtrando(df,countries = countries, language = language, min_runtime = min_runtime,
                           max_runtime = max_runtime, min_budget = min_budget,
                             max_budget = max_budget, genres = genres )
        if i ==0 :
            dados_teste_encoded = df.copy()
            i+=1
        else:
            dados_treino_encoded = df.copy()

    return dados_treino_encoded, dados_teste_encoded


def calcular_media_probabilidades(probs):
    return probs.mean()

# Função para aplicar o modelo SVM e calcular as probabilidades
def aplicar_modelo(dados_treino_encoded, dados_teste_encoded):
    X_train = dados_treino_encoded.drop(columns=['classificacao'])
    y_train = dados_treino_encoded['classificacao']

    X_test = dados_teste_encoded.drop(columns=['classificacao'])
    y_test = dados_teste_encoded['classificacao']

    # Criando e treinando o modelo SVM
    svm_model = SVC(kernel='rbf', C=1.0, gamma='scale', probability=True)
    svm_model.fit(X_train, y_train)

    # Fazendo previsões de probabilidade
    y_test_probs = svm_model.predict_proba(X_test)[:, 1]  # Pegando a probabilidade da classe positiva
    
    # Calculando a média das probabilidades
    media_prob = calcular_media_probabilidades(y_test_probs)
    print(f"Média das probabilidades da classe positiva: {media_prob:.4f}")

    # Fazendo previsões finais
    y_train_pred = svm_model.predict(X_train)
    y_test_pred = svm_model.predict(X_test)

    # Printando o classification report
    print("Classification Report para Treino (SVM):")
    print(classification_report(y_train, y_train_pred))

    print("\nClassification Report para Teste (SVM):")
    print(classification_report(y_test, y_test_pred))

    return media_prob

def dropar_colunas(dados_treino_encoded, dados_teste_encoded):


    colunas_para_remover = ["release_date", "revenue", "budget", "genres", "original_language", 
                        "production_countries", "spoken_languages", "adult", 
                        "disponibilidade_lucro", "lucro", "runtime", "idade"]
    

    for i, df in enumerate([dados_teste_encoded, dados_treino_encoded]):
        df = df.drop(columns=colunas_para_remover, errors='ignore')

    # Atribuir de volta ao DataFrame correto
        if i == 0:
            dados_teste_encoded = df
        else:
            dados_treino_encoded = df
    
    print(dados_treino_encoded.columns)
    return dados_teste_encoded, dados_treino_encoded




def resultado(countries, language, min_runtime, max_runtime, min_budget, max_budget, genres):

    # Listas de idiomas e países permitidos
    idiomas_permitidos = ['en', 'fr', 'es', 'de', 'ja', 'zh', "pt", 'it']

    selected_countries = ['United States', 'France', 'United Kingdom', 'Germany', 
                      'Canada', 'Japan', 'China', 'India', 'Italy', 'Spain']
    
    generos = ['Action', 'Science Fiction', 'Adventure', 'Drama', 'Crime',
           'Thriller', 'Fantasy', 'Comedy', 'Romance', 'Western', 'Mystery', 'War',
           'Animation', 'Family', 'Horror', 'Music']
    
    dados_teste_balanceado, dados_treino_balanceado = processar_dados("data/df_com_clusters_atualizados.parquet")
    dados_teste_encoded, dados_treino_encoded = encoding(dados_teste_balanceado, dados_treino_balanceado,
                                                         idiomas_permitidos, selected_countries,generos)
    countries, language,min_runtime,max_runtime,min_budget,max_budget,genres = pegar_inputs(countries, language, min_runtime, max_runtime, min_budget, max_budget, genres)

    dados_treino_encoded, dados_teste_encoded = filtrar_dados(dados_teste_encoded, dados_treino_encoded,countries, 
    language, min_runtime, max_runtime, min_budget, max_budget, genres)

    dados_teste_encoded, dados_treino_encoded = dropar_colunas(dados_treino_encoded, dados_teste_encoded)

    return(aplicar_modelo(dados_treino_encoded, dados_teste_encoded))








    





