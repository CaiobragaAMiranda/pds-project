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
    # Pega as configurações das variáveis de ambiente com fallbacks seguros
    user = os.getenv("DB_USER", "postgres")
    pw = os.getenv("DB_PASS", "postgres")
    db_name = os.getenv("DB_NAME", "pds_db")
    
    # IMPORTANTE: Dentro da rede do Docker, usamos o nome do serviço 'db' e a porta interna 5432.
    # Se estiver rodando localmente (fora do docker), usaria localhost e 5433.
    host = os.getenv("DB_HOST", "db") 
    port = os.getenv("DB_PORT", "5432")
    
    url = f"postgresql+pg8000://{user}:{pw}@{host}:{port}/{db_name}"
    engine = create_engine(url)
    
    try:
        with engine.connect() as conn:
            # Métricas Básicas
            total_files = conn.execute(text("SELECT COUNT(*) FROM file_metrics")).scalar()
            total_fails = conn.execute(text("SELECT COUNT(*) FROM file_metrics WHERE build_fail = True")).scalar()
            total_projects = conn.execute(text("SELECT COUNT(*) FROM projects")).scalar()
            
            # Verificação da Materialized View (IA Health)
            try:
                view_count = conn.execute(text("SELECT COUNT(*) FROM vw_rl_features")).scalar()
                view_status = "Pronta" if view_count > 0 else "Vazia"
            except:
                view_count = 0
                view_status = "Não Criada"
            
            # Progresso da Mineração (Limitado para economizar RAM)
            df_progress = pd.read_sql(text("""
                SELECT p.name, mp.status, mp.processed_releases, mp.total_releases
                FROM projects p
                JOIN mining_progress mp ON p.id = mp.project_id
                ORDER BY mp.updated_at DESC LIMIT 20
            """), conn)

            # Volume por Projeto (Top 10)
            df_proj = pd.read_sql(text("""
                SELECT p.name, COUNT(f.id) as count 
                FROM projects p 
                JOIN releases r ON p.id = r.project_id 
                JOIN file_metrics f ON r.id = f.release_id 
                GROUP BY p.name 
                ORDER BY count DESC LIMIT 10
            """), conn)
            
            return total_files, total_fails, total_projects, view_count, view_status, df_proj, df_progress
    finally:
        engine.dispose()

def refresh_rl_view():
    user = os.getenv("DB_USER", "postgres")
    pw = os.getenv("DB_PASS", "postgres")
    host = os.getenv("DB_HOST", "db")
    port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "pds_db")
    url = f"postgresql+pg8000://{user}:{pw}@{host}:{port}/{db_name}"
    engine = create_engine(url)
    try:
        with engine.begin() as conn:
            conn.execute(text("REFRESH MATERIALIZED VIEW vw_rl_features"))
        st.success("View de IA atualizada com sucesso!")
    except Exception as e:
        st.error(f"Erro ao atualizar View: {e}")
    finally:
        engine.dispose()

# Sidebar
st.sidebar.header("⚙️ Controles")
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
if st.sidebar.button("🔄 Atualizar View de IA"):
    refresh_rl_view()

# Layout de métricas
c1, c2, c3, c4 = st.columns(4)

try:
    stats = get_stats()
    if stats:
        total_files, total_fails, total_projects, view_count, view_status, df_proj, df_progress = stats
        
        c1.metric("Arquivos Minerados", f"{total_files:,}")
        c2.metric("Falhas de Build", f"{total_fails:,}")
        c3.metric("Projetos Ativos", total_projects)
        c4.metric("Dataset IA (RL)", f"{view_count:,}", help=f"Status: {view_status}")

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("📊 Top 10 Projetos por Volume")
            if not df_proj.empty:
                fig = px.bar(df_proj, x='name', y='count', color='count', 
                             color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
        
        with col_right:
            st.subheader("🕒 Atividade Recente do ETL")
            if not df_progress.empty:
                st.dataframe(df_progress, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhuma atividade de mineração registrada.")
except Exception as e:
    st.error(f"Erro de Conexão: {e}")
    st.info("Dica: Certifique-se que o banco de dados está rodando e a porta interna é 5432.")

if auto_refresh:
    time.sleep(10)
    st.rerun()
