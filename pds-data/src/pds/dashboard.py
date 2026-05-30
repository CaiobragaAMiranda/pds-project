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
        total_files = conn.execute(text("SELECT COUNT(*) FROM file_metrics")).scalar()
        total_fails = conn.execute(text("SELECT COUNT(*) FROM file_metrics WHERE build_fail = True")).scalar()
        total_projects = conn.execute(text("SELECT COUNT(*) FROM projects")).scalar()
        total_releases = conn.execute(text("SELECT COUNT(*) FROM releases")).scalar()
        
        # Progresso por projeto
        df_progress = pd.read_sql(text("""
            SELECT p.name, mp.status, mp.processed_releases, mp.total_releases, mp.last_release_tag, mp.updated_at
            FROM projects p
            LEFT JOIN mining_progress mp ON p.id = mp.project_id
            ORDER BY mp.updated_at DESC NULLS LAST
        """), repo.engine)

        # Dados para gráfico
        df_proj = pd.read_sql(text("""
            SELECT p.name, COUNT(f.id) as count 
            FROM projects p 
            JOIN releases r ON p.id = r.project_id 
            JOIN file_metrics f ON r.id = f.release_id 
            GROUP BY p.name 
            ORDER BY count DESC LIMIT 10
        """), repo.engine)
        
    repo.close()
    return total_files, total_fails, total_projects, total_releases, df_proj, df_progress

from sqlalchemy import text
# ... rest of layout ...

try:
    total_files, total_fails, total_projects, total_releases, df_proj, df_progress = get_stats()
    
    c1.metric("Arquivos Minerados", f"{total_files:,}")
    c2.metric("Falhas Detectadas", f"{total_fails:,}")
    c3.metric("Projetos na Base", total_projects)
    c4.metric("Releases Analisadas", total_releases)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("Volume por Projeto")
        if not df_proj.empty:
            fig = px.bar(df_proj, x='name', y='count', color='count', labels={'name': 'Projeto', 'count': 'Arquivos'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("Status da Mineração")
        if not df_progress.empty:
            st.dataframe(df_progress, use_container_width=True, hide_index=True)
        else:
            st.info("Aguardando início da pipeline...")

except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}")

if auto_refresh:
    time.sleep(10)
    st.rerun()
