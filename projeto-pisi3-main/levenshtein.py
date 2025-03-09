from typing import List, Tuple

def levenshtein(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j  # Inserções
            elif j == 0:
                dp[i][j] = i  # Remoções
            elif s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]  # Nenhuma operação
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],    # Remoção
                                   dp[i][j - 1],    # Inserção
                                   dp[i - 1][j - 1]) # Substituição
    
    return dp[m][n]

import difflib

def encontrar_palavra_mais_proxima(palavra, lista):
    """Encontra a palavra mais próxima em uma lista usando a distância de Levenshtein."""
    palavra_proxima = difflib.get_close_matches(palavra, lista, n=1)
    return (palavra_proxima[0] if palavra_proxima else palavra, 0 if palavra_proxima else -1)

def main(palavra, lista_selecionada):
    generos = ['Action', 'Science Fiction', 'Adventure', 'Drama', 'Crime',
               'Thriller', 'Fantasy', 'Comedy', 'Romance', 'Western', 'Mystery', 'War',
               'Animation', 'Family', 'Horror', 'Music']

    idiomas_permitidos = ['en', 'fr', 'es', 'de', 'ja', 'zh', 'pt', 'it']
    selected_countries = ['United States', 'France', 'United Kingdom', 'Germany', 
                          'Canada', 'Japan', 'China', 'India', 'Italy', 'Spain']

    listas = {
        "generos": generos,
        "idiomas": idiomas_permitidos,
        "paises": selected_countries
    }

    # Entrada do usuário:
   
    lista_selecionada = listas[lista_selecionada]

    # Verifica se a lista existe e encontra a palavra mais próxima  
    palavra_proxima, distancia = encontrar_palavra_mais_proxima(palavra, lista_selecionada)

    return palavra_proxima
        

if __name__ == "__main__":
    main()
