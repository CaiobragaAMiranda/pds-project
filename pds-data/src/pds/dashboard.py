import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px
import time
import os
from dotenv import load_dotenv

# Configuração da Página
st.set_page_config(page_title="PDS Data Monitor", layout="wide")
st.title("📊 PDS - Monitor de Mineração de Dados")

# Sidebar - Definição precoce para evitar NameError
auto_refresh = st.sidebar.checkbox("Auto-refresh (10s)", value=True)

def get_stats():
    # Conexão direta para evitar dependência de classe externa instável no container
    user = os.getenv("DB_USER", "postgres")
    pw = os.getenv("DB_PASS", "postgres")
    # Dentro do Docker, o host é 'db'. Fora é '127.0.0.1'
    host = os.getenv("DB_HOST", "db") 
    port = os.getenv("DB_PORT", "5432")
    db = os.getenv("DB_NAME", "pds_db")
    
    url = f"postgresql+pg8000://{user}:{pw}@{host}:{port}/{db}"
    engine = create_engine(url)
    
    try:
        with engine.connect() as conn:
            total_files = conn.execute(text("SELECT COUNT(*) FROM file_metrics")).scalar()
            total_fails = conn.execute(text("SELECT COUNT(*) FROM file_metrics WHERE build_fail = True")).scalar()
            total_projects = conn.execute(text("SELECT COUNT(*) FROM projects")).scalar()
            total_releases = conn.execute(text("SELECT COUNT(*) FROM releases")).scalar()
            
            df_progress = pd.read_sql(text("""
                SELECT p.name, mp.status, mp.processed_releases, mp.total_releases, mp.last_release_tag
                FROM projects p
                LEFT JOIN mining_progress mp ON p.id = mp.project_id
            """), conn)

            df_proj = pd.read_sql(text("""
                SELECT p.name, COUNT(f.id) as count 
                FROM projects p 
                JOIN releases r ON p.id = r.project_id 
                JOIN file_metrics f ON r.id = f.release_id 
                GROUP BY p.name 
                ORDER BY count DESC LIMIT 10
            """), conn)
            
            return total_files, total_fails, total_projects, total_releases, df_proj, df_progress
    finally:
        engine.dispose()

# Layout de métricas
c1, c2, c3, c4 = st.columns(4)

try:
    stats = get_stats()
    if stats:
        total_files, total_fails, total_projects, total_releases, df_proj, df_progress = stats
        
        c1.metric("Arquivos Minerados", f"{total_files:,}")
        c2.metric("Falhas Detectadas", f"{total_fails:,}")
        c3.metric("Projetos na Base", total_projects)
        c4.metric("Releases Analisadas", total_releases)

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("Volume por Projeto")
            if not df_proj.empty:
                fig = px.bar(df_proj, x='name', y='count', color='count')
                st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("Status da Mineração")
            if not df_progress.empty:
                st.dataframe(df_progress, use_container_width=True, hide_index=True)
            else:
                st.info("Aguardando início da pipeline...")
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.info("Dica: Certifique-se que o banco de dados está rodando e o schema foi aplicado.")

if auto_refresh:
    time.sleep(10)
    st.rerun()
