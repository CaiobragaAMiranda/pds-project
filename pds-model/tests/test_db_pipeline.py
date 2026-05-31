import unittest
import os
import pandas as pd
from sqlalchemy import create_engine, text
from pds.pipeline import load_dataset, get_db_engine

class TestDBPipeline(unittest.TestCase):
    def setUp(self):
        """Prepara o ambiente de teste garantindo conexão com o banco."""
        self.engine = get_db_engine()
        
    def test_database_connection(self):
        """Verifica se o pipeline consegue falar com o Postgres."""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1")).scalar()
                self.assertEqual(result, 1)
        except Exception as e:
            self.fail(f"Falha ao conectar no Banco de Dados: {e}")

    def test_load_dataset_from_db(self):
        """Verifica se o load_dataset retorna um DataFrame válido vindo do banco."""
        # Garante que existe ao menos um dado mockado para o teste não vir vazio
        with self.engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO projects (owner, name) VALUES ('test_owner', 'test_repo')
                ON CONFLICT DO NOTHING
            """))
            project_id = conn.execute(text("SELECT id FROM projects WHERE name='test_repo'")).scalar()
            
            conn.execute(text(f"""
                INSERT INTO releases (project_id, tag_name, published_at) 
                VALUES ({project_id}, 'v1.0.0', CURRENT_TIMESTAMP)
                ON CONFLICT DO NOTHING
            """))
            release_id = conn.execute(text(f"SELECT id FROM releases WHERE project_id={project_id}")).scalar()

            conn.execute(text(f"""
                INSERT INTO file_metrics (release_id, file_path, loc, cyc, build_fail) 
                VALUES ({release_id}, 'test.py', 10, 2, False)
                ON CONFLICT DO NOTHING
            """))

        df = load_dataset()
        self.assertIsInstance(df, pd.DataFrame)
        self.assertFalse(df.empty, "O dataset carregado do banco não deveria estar vazio.")
        self.assertIn('BUG', df.columns)

    def test_csv_absence_resilience(self):
        """Garante que a pipeline funciona mesmo sem arquivos CSV no diretório."""
        csv_path = "dataset_fake_que_nao_existe.csv"
        if os.path.exists(csv_path):
            os.remove(csv_path)
        
        # O load_dataset deve ignorar o caminho inexistente e ir para o DB
        df = load_dataset(csv_path)
        self.assertIsInstance(df, pd.DataFrame)
        print("Teste de resiliência a ausência de CSV: OK")

if __name__ == '__main__':
    unittest.main()
