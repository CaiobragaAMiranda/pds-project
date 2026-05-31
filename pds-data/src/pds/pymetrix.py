import os
import ast
import csv
import tokenize
from multiprocessing import Pool, cpu_count

# Tipos de nó que contam como decisões para complexidade ciclomática
DECISION_NODES = (
    ast.If,
    ast.For,
    ast.While,
    ast.Try,
    ast.With,
    ast.BoolOp,
    ast.IfExp,
)

def count_decision_points(tree: ast.AST) -> int:
    """
    Conta nós de decisão no AST para calcular complexidade ciclomática.
    Cada BoolOp (and/or) adiciona decisões extras por cada operador lógico.
    """
    cnt = sum(isinstance(n, DECISION_NODES) for n in ast.walk(tree))
    cnt += sum(len(n.values) - 1 for n in ast.walk(tree)
               if isinstance(n, ast.BoolOp))
    return cnt + 1  # McCabe

def max_ast_depth(tree: ast.AST) -> int:
    """
    Calcula a profundidade máxima da árvore AST.
    """
    def visit(node: ast.AST, depth: int = 0):
        depths = [depth]
        for child in ast.iter_child_nodes(node):
            depths.append(visit(child, depth + 1))
        return max(depths)

    return visit(tree)

def count_comments_and_blanks(source: str) -> tuple[int, int]:
    """
    Conta comentários e linhas em branco usando uma string de código.
    """
    comments = blanks = 0
    lines = source.splitlines()
    
    # Contar linhas em branco
    for line in lines:
        if not line.strip():
            blanks += 1

    # Contar comentários usando tokenize
    try:
        import io
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for tok in tokens:
            if tok.type == tokenize.COMMENT:
                comments += 1
    except Exception:
        pass

    return comments, blanks

def calculate_metrics(source: str, file_label: str = "memory") -> dict:
    """
    Analisa o código fonte fornecido e extrai métricas.
    """
    try:
        tree = ast.parse(source)

        # Métricas básicas
        loc = sum(1 for l in source.splitlines() if l.strip())
        comments, blanks = count_comments_and_blanks(source)

        # Coleta funções e classes
        funcs = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

        n_funcs = len(funcs)
        n_classes = len(classes)

        avg_params = (sum(len(f.args.args) for f in funcs) / n_funcs) if n_funcs else 0.0

        methods_per_class = [
            sum(isinstance(n, ast.FunctionDef) for n in cls.body)
            for cls in classes
        ]

        avg_methods = (sum(methods_per_class) / n_classes) if n_classes else 0.0
        
        n_raises = sum(isinstance(n, ast.Raise) for n in ast.walk(tree))
        n_except = sum(isinstance(n, ast.ExceptHandler) for n in ast.walk(tree))

        cyclo = count_decision_points(tree)
        depth = max_ast_depth(tree)

        return {
            'FILE': file_label,
            'LOC': loc,
            'COM': comments,
            'BLK': blanks,
            'NOF': n_funcs,
            'NOC': n_classes,
            'APF': round(avg_params, 2),
            'AMC': round(avg_methods, 2),
            'NER': n_raises,
            'NEH': n_except,
            'CYC': cyclo,
            'MAD': depth
        }
    except Exception:
        return None

def analyze_file(path: str) -> dict:
    """
    Lê um arquivo e delega para calculate_metrics.
    """
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            src = f.read()
        return calculate_metrics(src, path)
    except Exception:
        return None

def scan_directory_parallel(root: str):
    """
    Varre um diretório e processa arquivos .py em paralelo.
    Limitado para evitar esgotamento de memória.
    """
    files_to_process = []
    for dirpath, _, files in os.walk(root):
        for name in files:
            if name.endswith('.py'):
                files_to_process.append(os.path.join(dirpath, name))
    
    # Limita o número de processos para evitar estourar a RAM
    # Especialmente importante se rodando dentro de um Celery Worker
    num_processes = min(cpu_count(), 4) 
    
    with Pool(processes=num_processes) as pool:
        results = pool.map(analyze_file, files_to_process)
    
    return [r for r in results if r is not None]

def save_to_csv(data: list[dict], outcsv: str) -> None:
    """
    Salva a lista de dicionários em um CSV.
    """
    if not data:
        return

    with open(outcsv, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
