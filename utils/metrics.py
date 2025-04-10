from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze
import ast
from typing import Dict, List, Any

def calculate_code_metrics(code_files: Dict[str, str]) -> Dict[str, Any]:
    """
    Calculate various code metrics for the given code files.
    
    Args:
        code_files: Dictionary of filename to code content
        
    Returns:
        Dictionary containing various code metrics
    """
    metrics = {
        'overall': {
            'total_files': len(code_files),
            'total_lines': 0,
            'total_complexity': 0,
            'average_maintainability': 0
        },
        'files': {}
    }
    
    total_maintainability = 0
    
    for filename, code in code_files.items():
        file_metrics = {
            'lines': len(code.split('\n')),
            'complexity': 0,
            'maintainability': 0,
            'functions': [],
            'classes': []
        }
        
        # Calculate cyclomatic complexity
        try:
            complexity_results = cc_visit(code)
            file_metrics['complexity'] = sum(c.complexity for c in complexity_results)
            file_metrics['functions'] = [
                {
                    'name': c.name,
                    'complexity': c.complexity,
                    'line': c.lineno
                }
                for c in complexity_results
            ]
        except Exception:
            pass
        
        # Calculate maintainability index
        try:
            maintainability = mi_visit(code, multi=True)
            file_metrics['maintainability'] = maintainability
            total_maintainability += maintainability
        except Exception:
            pass
        
        # Parse AST for class information
        try:
            tree = ast.parse(code)
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            file_metrics['classes'] = [
                {
                    'name': cls.name,
                    'line': cls.lineno,
                    'methods': len([n for n in ast.walk(cls) if isinstance(n, ast.FunctionDef)])
                }
                for cls in classes
            ]
        except Exception:
            pass
        
        metrics['files'][filename] = file_metrics
        metrics['overall']['total_lines'] += file_metrics['lines']
        metrics['overall']['total_complexity'] += file_metrics['complexity']
    
    if metrics['overall']['total_files'] > 0:
        metrics['overall']['average_maintainability'] = total_maintainability / metrics['overall']['total_files']
    
    return metrics 