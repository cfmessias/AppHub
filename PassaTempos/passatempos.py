import streamlit as st
import requests
import itertools
from bs4 import BeautifulSoup
from functools import lru_cache

tabs = st.tabs(["Cruzadas", "Sinonimos", "WOW", "Sudoku X-Wing"])

with tabs[0]:
    def obter_sinonimos(palavra, num_letras=None):
        url = "https://api.datamuse.com/words"
        params = {"rel_syn": palavra, "max": 50}
        resposta = requests.get(url, params=params)
        if resposta.status_code == 200:
            lista = [item["word"] for item in resposta.json()]
            if num_letras:
                lista = [w for w in lista if len(w) == num_letras]
            return lista
        return []

    def obter_relacionadas(palavra, num_letras=None):
        url = "https://api.datamuse.com/words"
        params = {"ml": palavra, "max": 50}
        resposta = requests.get(url, params=params)
        if resposta.status_code == 200:
            lista = [item["word"] for item in resposta.json()]
            if num_letras:
                lista = [w for w in lista if len(w) == num_letras]
            return lista
        return []

    def obter_definicoes(palavra):
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{palavra}"
        resposta = requests.get(url)
        if resposta.status_code == 200:
            try:
                dados = resposta.json()
                definicoes = []
                for sentido in dados[0]['meanings']:
                    for definicao in sentido['definitions']:
                        definicoes.append(definicao['definition'])
                return definicoes[:3]
            except Exception:
                return []
        return []

    # Interface do Streamlit
    st.title("🔠 Ajuda para Palavras Cruzadas")
    palavra = st.text_input("Insere uma palavra ou pista curta:")
    num_letras = st.number_input("Número de letras esperado (opcional):", min_value=1, max_value=30, step=1, format="%d", value=None)

    if palavra:
        st.markdown(f"### 🔍 Resultados para: `{palavra}`")
        
        definicoes = obter_definicoes(palavra)
        if definicoes:
            st.subheader("📘 Definições")
            for d in definicoes:
                st.markdown(f"- {d}")

        sinonimos = obter_sinonimos(palavra, num_letras)
        if sinonimos:
            st.subheader("🟢 Sinónimos")
            st.markdown(", ".join(sinonimos))

        relacionadas = obter_relacionadas(palavra, num_letras)
        if relacionadas:
            st.subheader("🔵 Palavras relacionadas")
            st.markdown(", ".join(relacionadas))

        if not (definicoes or sinonimos or relacionadas):
            st.warning("⚠️ Nenhuma informação encontrada.")

        
with tabs[1]:
    # Datamuse
    def obter_sinonimos_datamuse(palavra, numero_letras=None):
        url = "https://api.datamuse.com/words"
        params = {"rel_syn": palavra, "max": 100}
        try:
            resposta = requests.get(url, params=params)
            if resposta.status_code == 200:
                dados = resposta.json()
                sinonimos = [item["word"] for item in dados]
                if numero_letras:
                    sinonimos = [s for s in sinonimos if len(s) == numero_letras]
                return sinonimos
        except:
            pass
        return []

    # Dicio.com.br (scraping)
    def obter_sinonimos_dicio(palavra, numero_letras=None):
        try:
            url = f"https://www.dicio.com.br/{palavra.lower()}/"
            resposta = requests.get(url)
            if resposta.status_code != 200:
                return []
            soup = BeautifulSoup(resposta.text, "html.parser")
            bloco = soup.find("p", class_="adicional sinonimos")
            if not bloco:
                return []
            texto = bloco.get_text(strip=True)
            partes = texto.split(":")
            if len(partes) < 2:
                return []
            lista_sinonimos = [s.strip() for s in partes[1].split(",")]
            if numero_letras:
                lista_sinonimos = [s for s in lista_sinonimos if len(s) == numero_letras]
            return lista_sinonimos
        except:
            return []

    # Interface
    st.title("🔠 Ajuda para Palavras Cruzadas")
    palavra = st.text_input("Palavra de referência:", key="sin_palavra")
    num_letras = st.number_input("Número de letras (opcional):", min_value=1, max_value=30, step=1, format="%d", value=None, key="sin_num_letras")

    if st.button("🔍 Procurar sinónimos"):
        if palavra.strip():
            st.info("A procurar sinónimos em várias fontes...")
            resultados = set()

            resultados.update(obter_sinonimos_datamuse(palavra.strip(), numero_letras=num_letras))
            if len(resultados) < 5:
                resultados.update(obter_sinonimos_dicio(palavra.strip(), numero_letras=num_letras))

            if resultados:
                st.success("Sinónimos encontrados:")
                st.write(", ".join(sorted(resultados)))
            else:
                st.warning("Nenhum sinónimo encontrado.")
        else:
            st.warning("Por favor, insere uma palavra válida.")

with tabs[2]:
    

    # Título com letra pequena
    st.markdown("<h5 style='margin-bottom: 0.5em;'>🧩 Gerador de Palavras Válidas com Letras Repetidas (PT)</h5>", unsafe_allow_html=True)

    @lru_cache(maxsize=2048)
    def validar_datamuse(palavra):
        url = "https://api.datamuse.com/words"
        params = {"sp": palavra, "max": 1}
        try:
            resposta = requests.get(url, params=params, timeout=3)
            if resposta.status_code == 200:
                resultados = resposta.json()
                return any(item["word"].lower() == palavra.lower() for item in resultados)
        except Exception:
            pass
        return False

    @lru_cache(maxsize=2048)
    def validar_priberam(palavra):
        url = f"https://dicionario.priberam.org/{palavra}"
        try:
            resposta = requests.get(url, timeout=3)
            return "não foi encontrada" not in resposta.text.lower()
        except Exception:
            pass
        return False

    @lru_cache(maxsize=2048)
    def validar_wiktionary(palavra):
        url = f"https://pt.wiktionary.org/w/api.php"
        params = {
            "action": "query",
            "titles": palavra,
            "format": "json"
        }
        try:
            resposta = requests.get(url, params=params, timeout=3)
            data = resposta.json()
            pages = data.get("query", {}).get("pages", {})
            return not "-1" in pages
        except Exception:
            pass
        return False

    def validar_palavra(pt):
        return (
            validar_datamuse(pt) or
            validar_priberam(pt) or
            validar_wiktionary(pt)
        )

    def palavra_respeita_molde(palavra, molde):
        return all(m == "_" or m.lower() == p.lower() for m, p in zip(molde, palavra))

    def gerar_palavras_validas(letras, tamanho, molde=None):
        letras = letras.lower()
        todas = set(''.join(p) for p in itertools.permutations(letras, tamanho))
        if molde:
            molde = molde.lower()
            todas = [p for p in todas if palavra_respeita_molde(p, molde)]
        palavras_validas = [p for p in todas if validar_palavra(p)]
        return palavras_validas, todas

    st.markdown("""
    Insere letras (pode incluir acentos e repetir letras).  
    Exemplo: `rarroc`, `ação`, `amora`
    """)

    letras_input = st.text_input("Letras:", value="rarroc", key="wow_letras")

    if letras_input:
        tamanho = st.number_input(
            "Tamanho da palavra:", min_value=1, max_value=len(letras_input), step=1, key="wow_tamanho"
        )
        molde = st.text_input(
            "Molde da palavra (usa '_' para desconhecidos):", value="_"*tamanho, key="wow_molde"
        )

        if len(molde) != tamanho:
            st.warning("O molde deve ter o mesmo número de letras indicado no tamanho.")
        elif st.button("🔍 Gerar Palavras", key="wow_botao"):
            st.info("A procurar palavras válidas em múltiplos dicionários...")
            resultado, todas = gerar_palavras_validas(letras_input, tamanho, molde)

            if resultado:
                st.success(f"Encontradas {len(resultado)} palavra(s) reconhecidas:")
                st.markdown(", ".join(sorted(resultado)))
            else:
                st.warning("Nenhuma palavra reconhecida nos dicionários. Eis as possíveis combinações:")
                st.markdown(", ".join(sorted(todas)))
                st.info("Talvez alguma combinação seja válida mas não está listada nos dicionários online.")

with tabs[3]:
    st.title("🧩 Sudoku X-Wing Solver")
    st.markdown("""
    Esta ferramenta ajuda a identificar e aplicar a técnica X-Wing em quebra-cabeças de Sudoku.
    
    **O que é X-Wing?** 
    É uma técnica de resolução onde um número candidato aparece exatamente em duas células em cada uma
    de duas linhas diferentes, e essas células estão nas mesmas colunas. Isto permite eliminar esse número
    de outras células nas mesmas colunas.
    """)
    
    def find_x_wings(grid):
        """
        Identifica padrões X-Wing em um grid de Sudoku e retorna as eliminações possíveis.
        
        Args:
            grid: Uma matriz 9x9 onde cada célula contém um número de 1-9 se resolvida
                ou uma lista de candidatos possíveis se não resolvida
        
        Returns:
            Uma lista de eliminações no formato [(linha, coluna, valor), ...]
        """
        eliminations = []
        
        # Verifica X-Wings nas linhas
        for num in range(1, 10):
            # Para cada valor possível (1-9)
            for line1 in range(9):
                # Encontrar colunas onde o número aparece como candidato nesta linha
                cols_with_num = [col for col in range(9) if isinstance(grid[line1][col], list) and num in grid[line1][col]]
                
                # Precisamos de exatamente 2 posições para um X-Wing
                if len(cols_with_num) == 2:
                    for line2 in range(line1 + 1, 9):
                        # Procurar outra linha onde o número aparece nas mesmas colunas
                        cols_line2 = [col for col in range(9) if isinstance(grid[line2][col], list) and num in grid[line2][col]]
                        
                        # Se encontramos um padrão X-Wing
                        if cols_line2 == cols_with_num:
                            # Podemos eliminar este número de outras células nas mesmas colunas
                            col1, col2 = cols_with_num
                            
                            # Verificar todas as outras células nas colunas col1 e col2
                            for row in range(9):
                                if row != line1 and row != line2:
                                    # Coluna 1
                                    if isinstance(grid[row][col1], list) and num in grid[row][col1]:
                                        eliminations.append((row, col1, num))
                                    # Coluna 2
                                    if isinstance(grid[row][col2], list) and num in grid[row][col2]:
                                        eliminations.append((row, col2, num))
        
        # Verifica X-Wings nas colunas
        for num in range(1, 10):
            # Para cada valor possível (1-9)
            for col1 in range(9):
                # Encontrar linhas onde o número aparece como candidato nesta coluna
                rows_with_num = [row for row in range(9) if isinstance(grid[row][col1], list) and num in grid[row][col1]]
                
                # Precisamos de exatamente 2 posições para um X-Wing
                if len(rows_with_num) == 2:
                    for col2 in range(col1 + 1, 9):
                        # Procurar outra coluna onde o número aparece nas mesmas linhas
                        rows_col2 = [row for row in range(9) if isinstance(grid[row][col2], list) and num in grid[row][col2]]
                        
                        # Se encontramos um padrão X-Wing
                        if rows_col2 == rows_with_num:
                            # Podemos eliminar este número de outras células nas mesmas linhas
                            row1, row2 = rows_with_num
                            
                            # Verificar todas as outras células nas linhas row1 e row2
                            for col in range(9):
                                if col != col1 and col != col2:
                                    # Linha 1
                                    if isinstance(grid[row1][col], list) and num in grid[row1][col]:
                                        eliminations.append((row1, col, num))
                                    # Linha 2
                                    if isinstance(grid[row2][col], list) and num in grid[row2][col]:
                                        eliminations.append((row2, col, num))
        
        return eliminations

    def apply_x_wing(grid):
        """
        Aplica a técnica X-Wing ao grid de Sudoku.
        
        Args:
            grid: Uma matriz 9x9 onde cada célula contém um número de 1-9 se resolvida
                ou uma lista de candidatos possíveis se não resolvida
        
        Returns:
            Um booleano indicando se alguma eliminação foi feita
            O grid modificado
        """
        eliminations = find_x_wings(grid)
        
        if eliminations:
            # Aplicar as eliminações
            for row, col, val in eliminations:
                grid[row][col].remove(val)
            return True, grid
        
        return False, grid

    def parse_sudoku(board_str):
        """
        Converte uma string representando um tabuleiro de Sudoku em uma matriz 9x9.
        Células vazias são representadas por '0' ou '.'.
        
        Args:
            board_str: String representando o tabuleiro de Sudoku
        
        Returns:
            Uma matriz 9x9 representando o tabuleiro de Sudoku
        """
        # Remover espaços em branco e caracteres de nova linha
        board_str = ''.join(c for c in board_str if c not in ' \n\t')
        
        # Substituir pontos por zeros
        board_str = board_str.replace('.', '0')
        
        # Verificar se o tabuleiro tem 81 caracteres
        if len(board_str) != 81:
            return None
        
        # Converter para matriz 9x9
        board = []
        for i in range(9):
            row = []
            for j in range(9):
                cell = int(board_str[i*9 + j])
                # Se a célula estiver vazia, inicializar com todos os candidatos possíveis
                if cell == 0:
                    row.append(list(range(1, 10)))
                else:
                    row.append(cell)
            board.append(row)
        
        return board

    def fill_candidates(grid):
        """
        Preenche as células vazias com candidatos possíveis com base nas regras do Sudoku.
        
        Args:
            grid: Uma matriz 9x9 representando o tabuleiro de Sudoku
        
        Returns:
            Uma matriz 9x9 com candidatos preenchidos
        """
        # Para cada célula não resolvida
        for row in range(9):
            for col in range(9):
                if isinstance(grid[row][col], list):
                    # Obter valores já usados na linha, coluna e bloco 3x3
                    used_values = set()
                    
                    # Verificar linha
                    for c in range(9):
                        if isinstance(grid[row][c], int):
                            used_values.add(grid[row][c])
                    
                    # Verificar coluna
                    for r in range(9):
                        if isinstance(grid[r][col], int):
                            used_values.add(grid[r][col])
                    
                    # Verificar bloco 3x3
                    block_row, block_col = 3 * (row // 3), 3 * (col // 3)
                    for r in range(block_row, block_row + 3):
                        for c in range(block_col, block_col + 3):
                            if isinstance(grid[r][c], int):
                                used_values.add(grid[r][c])
                    
                    # Atualizar candidatos
                    grid[row][col] = [n for n in range(1, 10) if n not in used_values]
        
        return grid

    # Interface Streamlit para Sudoku
    st.subheader("Insira seu tabuleiro de Sudoku")
    st.markdown("""
    Insira o tabuleiro no formato de string, usando '.' ou '0' para células vazias.
    Exemplo:
    ```
    .....9.7.
    ..7...9..
    9..287..3
    .8.154.3.
    ...8.3...
    .5.967.8.
    3..571..6
    ..5...1..
    .7.3.....
    ```
    """)
    
    # Exemplo de Sudoku com X-Wing
    exemplo = """.....9.7.
    ..7...9..
    9..287..3
    .8.154.3.
    ...8.3...
    .5.967.8.
    3..571..6
    ..5...1..
    .7.3....."""
    
    sudoku_input = st.text_area("Tabuleiro de Sudoku:", value=exemplo, height=250)
    
    if st.button("Analisar X-Wing"):
        if sudoku_input:
            # Processar o tabuleiro
            grid = parse_sudoku(sudoku_input)
            
            if grid:
                # Preencher candidatos
                grid = fill_candidates(grid)
                
                # Exibir tabuleiro original
                st.subheader("Tabuleiro Original")
                tabuleiro_html = "<table style='border-collapse: collapse; font-size: 18px; margin: 0 auto;'>"
                for i in range(9):
                    if i % 3 == 0 and i > 0:
                        tabuleiro_html += "<tr><td colspan='9'><hr style='border: 2px solid black'></td></tr>"
                    tabuleiro_html += "<tr>"
                    for j in range(9):
                        if j % 3 == 0 and j > 0:
                            tabuleiro_html += "<td style='border: none; padding: 0 5px;'>|</td>"
                        cell = grid[i][j]
                        if isinstance(cell, int):
                            tabuleiro_html += f"<td style='width: 30px; height: 30px; text-align: center;'>{cell}</td>"
                        else:
                            tabuleiro_html += "<td style='width: 30px; height: 30px; text-align: center;'>.</td>"
                    tabuleiro_html += "</tr>"
                tabuleiro_html += "</table>"
                st.markdown(tabuleiro_html, unsafe_allow_html=True)
                
                # Encontrar padrões X-Wing
                eliminations = find_x_wings(grid)
                
                if eliminations:
                    st.success(f"Encontrados {len(eliminations)} candidatos que podem ser eliminados usando X-Wing!")
                    
                    # Mostrar padrões encontrados
                    st.subheader("Padrões X-Wing Encontrados")
                    patterns = {}
                    for row, col, val in eliminations:
                        if val not in patterns:
                            patterns[val] = []
                        patterns[val].append((row, col))
                    
                    for num, positions in patterns.items():
                        st.markdown(f"**Número {num}** pode ser eliminado das células:")
                        pos_text = ", ".join([f"({r+1},{c+1})" for r, c in positions])
                        st.markdown(pos_text)
                    
                    # Aplicar X-Wing
                    applied, updated_grid = apply_x_wing(grid)
                    
                    if applied:
                        st.subheader("Candidatos Após Aplicar X-Wing")
                        cand_html = "<table style='border-collapse: collapse; font-size: 12px; margin: 0 auto;'>"
                        for i in range(9):
                            if i % 3 == 0 and i > 0:
                                cand_html += "<tr><td colspan='9'><hr style='border: 2px solid black'></td></tr>"
                            cand_html += "<tr>"
                            for j in range(9):
                                if j % 3 == 0 and j > 0:
                                    cand_html += "<td style='border: none; padding: 0 5px;'>|</td>"
                                cell = updated_grid[i][j]
                                if isinstance(cell, int):
                                    cand_html += f"<td style='width: 40px; height: 40px; text-align: center; vertical-align: middle;'>{cell}</td>"
                                else:
                                    cand_text = "".join([str(n) for n in cell])
                                    cand_html += f"<td style='width: 40px; height: 40px; text-align: center; vertical-align: middle; font-size: 9px;'>{cand_text}</td>"
                            cand_html += "</tr>"
                        cand_html += "</table>"
                        st.markdown(cand_html, unsafe_allow_html=True)
                else:
                    st.warning("Nenhum padrão X-Wing encontrado neste quebra-cabeça.")
            else:
                st.error("Formato de tabuleiro inválido. Certifique-se de que ele tenha 81 caracteres.")
        else:
            st.warning("Por favor, insira um tabuleiro de Sudoku.")
    
    # Explicação da técnica X-Wing
    with st.expander("Explicação da Técnica X-Wing"):
        st.markdown("""
        ## Como Funciona o X-Wing
        
        1. **Conceito Básico**: Um X-Wing ocorre quando um determinado número candidato aparece exatamente em duas células em cada uma de duas linhas diferentes, e essas células estão nas mesmas colunas.
        
        2. **Exemplo Visual**:
           - Imagine que o número 7 aparece como candidato apenas em duas células da linha 2 (nas colunas 3 e 6)
           - E o número 7 também aparece como candidato apenas em duas células da linha 8 (nas mesmas colunas 3 e 6)
           - Isso forma um retângulo com os quatro cantos nas posições: (2,3), (2,6), (8,3) e (8,6)
        
        3. **A Lógica**:
           - Em cada uma dessas duas linhas, o número 7 DEVE ir em uma dessas duas posições
           - Portanto, nas colunas 3 e 6, o número 7 DEVE ocupar as linhas 2 e 8
           - Isto significa que o número 7 não pode aparecer em NENHUMA outra posição nas colunas 3 e 6
        
        4. **X-Wing por Coluna**:
           - O mesmo padrão pode ocorrer em colunas (em vez de linhas)
           - Quando um número aparece exatamente em duas células em cada uma de duas colunas
           - E essas células estão nas mesmas linhas
           - Você pode eliminar esse número de todas as outras células nessas linhas
        """)