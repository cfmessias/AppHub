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
        raise ValueError("O tabuleiro deve ter 81 células")
    
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

def print_grid(grid):
    """
    Exibe o grid de Sudoku de forma legível.
    
    Args:
        grid: Uma matriz 9x9 representando o tabuleiro de Sudoku
    """
    for i in range(9):
        if i % 3 == 0 and i > 0:
            print('-' * 33)
        
        for j in range(9):
            if j % 3 == 0 and j > 0:
                print('|', end=' ')
            
            cell = grid[i][j]
            if isinstance(cell, int):
                print(f"{cell}", end=' ')
            else:
                print('.', end=' ')
        
        print()

def print_grid_with_candidates(grid):
    """
    Exibe o grid de Sudoku com todos os candidatos.
    
    Args:
        grid: Uma matriz 9x9 representando o tabuleiro de Sudoku
    """
    for i in range(9):
        print('+' + '-' * 33 + '+')
        for j in range(9):
            cell = grid[i][j]
            if isinstance(cell, int):
                print(f"|  {cell}  ", end='')
            else:
                candidates = ''.join(str(n) for n in cell)
                print(f"|{candidates:^6}", end='')
        print('|')
    print('+' + '-' * 33 + '+')

def example_with_x_wing():
    """
    Demonstra a técnica X-Wing com um exemplo.
    """
    # Este exemplo tem um X-Wing para o número 7 nas linhas 1 e 7 (linhas 0-indexed)
    # e colunas 2 e 5 (colunas 0-indexed)
    sudoku_str = """
    .....9.7.
    ..7...9..
    9..287..3
    .8.154.3.
    ...8.3...
    .5.967.8.
    3..571..6
    ..5...1..
    .7.3.....
    """
    
    # Converter para matriz 9x9 e preencher candidatos
    grid = parse_sudoku(sudoku_str)
    grid = fill_candidates(grid)
    
    print("Grid inicial:")
    print_grid(grid)
    print("\nCandidatos iniciais (versão simplificada para visualização):")
    print_grid_with_candidates(grid)
    
    print("\nBuscando padrões X-Wing...")
    eliminations = find_x_wings(grid)
    
    if eliminations:
        print(f"Encontrados {len(eliminations)} eliminações possíveis usando X-Wing:")
        for row, col, val in eliminations:
            print(f"  Pode eliminar {val} da célula ({row+1},{col+1})")
        
        # Aplicar eliminações
        was_applied, grid = apply_x_wing(grid)
        if was_applied:
            print("\nGrid após aplicar X-Wing:")
            print_grid(grid)
            print("\nCandidatos após X-Wing:")
            print_grid_with_candidates(grid)
    else:
        print("Nenhum padrão X-Wing encontrado neste quebra-cabeça.")

def solve_with_x_wing(sudoku_str):
    """
    Tenta resolver um Sudoku usando a técnica X-Wing.
    
    Args:
        sudoku_str: String representando o tabuleiro de Sudoku
    """
    grid = parse_sudoku(sudoku_str)
    grid = fill_candidates(grid)
    
    print("Grid inicial:")
    print_grid(grid)
    
    iteration = 1
    while True:
        print(f"\nIteração {iteration}:")
        was_applied, grid = apply_x_wing(grid)
        
        if not was_applied:
            print("Nenhuma nova eliminação usando X-Wing.")
            break
        
        print(f"X-Wing aplicado com sucesso na iteração {iteration}.")
        iteration += 1
    
    print("\nCandidatos finais:")
    print_grid_with_candidates(grid)

if __name__ == "__main__":
    # Demonstrar a técnica X-Wing com um exemplo
    example_with_x_wing()
