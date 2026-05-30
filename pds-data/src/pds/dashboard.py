import streamlit as st
import pandas as pd
from pds.repository import PDSRepository
import plotly.express as px
import time

st.set_page_config(page_title="PDS Data Monitor", layout="wide")

st.title("📊 PDS - Monitor de Mineração de Dados")

def get_stats():
    repo = PDSRepository()
    with repo.engine.connect() as conn:
        # Total de arquivos
        total_files = conn.execute(repo.text("SELECT COUNT(*) FROM file_metrics")).scalar()
        # Total de falhas
        total_fails = conn.execute(repo.text("SELECT COUNT(*) FROM file_metrics WHERE build_fail = True")).scalar()
        # Projetos processados
        total_projects = conn.execute(repo.text("SELECT COUNT(*) FROM projects")).scalar()
        # Releases processadas
        total_releases = conn.execute(repo.text("SELECT COUNT(*) FROM releases")).scalar()
        
        # Dados para gráfico por projeto
        df_proj = pd.read_sql(repo.text("""
            SELECT p.name, COUNT(f.id) as count 
            FROM projects p 
            JOIN releases r ON p.id = r.project_id 
            JOIN file_metrics f ON r.id = f.release_id 
            GROUP BY p.name 
            ORDER BY count DESC LIMIT 10
        """), repo.engine)
        
    repo.close()
    return total_files, total_fails, total_projects, total_releases, df_proj

# Sidebar de atualização
auto_refresh = st.sidebar.checkbox("Auto-refresh (10s)", value=True)

# Layout de métricas
c1, c2, c3, c4 = st.columns(4)

try:
    total_files, total_fails, total_projects, total_releases, df_proj = get_stats()
    
    c1.metric("Arquivos Minerados", f"{total_files:,}")
    c2.metric("Falhas Detectadas", f"{total_fails:,}")
    c3.metric("Projetos na Base", total_projects)
    c4.metric("Releases Analisadas", total_releases)

    st.subheader("Top 10 Projetos por Volume de Dados")
    if not df_proj.empty:
        fig = px.bar(df_proj, x='name', y='count', color='count', labels={'name': 'Projeto', 'count': 'Arquivos'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum dado encontrado ainda. Inicie a pipeline!")

except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")

if auto_refresh:
    time.sleep(10)
    st.rerun()
