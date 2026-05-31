import unittest
import importlib
import sys
import os

# Adiciona src ao path para o teste
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

class TestPipelineIntegrity(unittest.TestCase):
    
    def test_import_pipeline(self):
        """Verifica se o pipeline pode ser importado sem erros de sintaxe."""
        try:
            import pds.pipeline as pipeline
            importlib.reload(pipeline)
            self.assertTrue(hasattr(pipeline, 'start'), "Função 'start' não encontrada.")
            self.assertTrue(hasattr(pipeline, 'discover_repositories'), "Função 'discover_repositories' não encontrada.")
        except Exception as e:
            self.fail(f"Falha ao importar pds.pipeline: {e}")

    def test_import_tasks(self):
        """Verifica se as tarefas do Celery estão corretas."""
        try:
            import pds.tasks as tasks
            importlib.reload(tasks)
            self.assertTrue(hasattr(tasks, 'analyze_release_task'), "Tarefa 'analyze_release_task' não encontrada.")
        except Exception as e:
            self.fail(f"Falha ao importar pds.tasks: {e}")

    def test_import_repository(self):
        """Verifica integridade do repositório."""
        try:
            import pds.repository as repo
            importlib.reload(repo)
            self.assertTrue(hasattr(repo, 'PDSRepository'), "Classe 'PDSRepository' não encontrada.")
        except Exception as e:
            self.fail(f"Falha ao importar pds.repository: {e}")

if __name__ == '__main__':
    unittest.main()
