-- Schema inicial para o sistema PDS

-- Tabela de Projetos
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    owner VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    UNIQUE(owner, name)
);

-- Tabela de Releases
CREATE TABLE IF NOT EXISTS releases (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
    tag_name VARCHAR(100) NOT NULL,
    published_at TIMESTAMP WITH TIME ZONE NOT NULL,
    UNIQUE(project_id, tag_name)
);

-- Tabela de Métricas de Código
CREATE TABLE IF NOT EXISTS file_metrics (
    id SERIAL PRIMARY KEY,
    release_id INTEGER REFERENCES releases(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    loc INTEGER,
    com INTEGER,
    blk INTEGER,
    nof INTEGER,
    noc INTEGER,
    apf FLOAT,
    amc FLOAT,
    ner INTEGER,
    neh INTEGER,
    cyc INTEGER,
    mad INTEGER,
    build_fail BOOLEAN DEFAULT FALSE,
    commit_hash VARCHAR(40),
    commit_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(release_id, file_path)
);

-- View para Engenharia de Features de RL
CREATE MATERIALIZED VIEW IF NOT EXISTS vw_rl_features AS
WITH base_metrics AS (
    SELECT 
        fm.*,
        p.id as project_id,
        p.name as project_name,
        -- Calcula o LAG para obter a versão anterior do mesmo arquivo
        LAG(loc) OVER (PARTITION BY fm.file_path ORDER BY r.published_at) as prev_loc,
        LAG(cyc) OVER (PARTITION BY fm.file_path ORDER BY r.published_at) as prev_cyc,
        LAG(mad) OVER (PARTITION BY fm.file_path ORDER BY r.published_at) as prev_mad,
        -- Extrai componentes temporais
        EXTRACT(ISODOW FROM COALESCE(fm.commit_date, r.published_at)) as day_of_week
    FROM file_metrics fm
    JOIN releases r ON fm.release_id = r.id
    JOIN projects p ON r.project_id = p.id
),
normalized_metrics AS (
    SELECT 
        *,
        -- Deltas (Evolução)
        loc - COALESCE(prev_loc, loc) as delta_loc,
        cyc - COALESCE(prev_cyc, cyc) as delta_cyc,
        mad - COALESCE(prev_mad, mad) as delta_mad,
        -- Z-Scores por Projeto (Normalização de Escala)
        (loc - AVG(loc) OVER (PARTITION BY project_id)) / NULLIF(STDDEV(loc) OVER (PARTITION BY project_id), 0) as z_loc,
        (cyc - AVG(cyc) OVER (PARTITION BY project_id)) / NULLIF(STDDEV(cyc) OVER (PARTITION BY project_id), 0) as z_cyc,
        (mad - AVG(mad) OVER (PARTITION BY project_id)) / NULLIF(STDDEV(mad) OVER (PARTITION BY project_id), 0) as z_mad,
        -- Features Cíclicas (Temporalidade)
        SIN(day_of_week * 2 * PI() / 7) as sin_dow,
        COS(day_of_week * 2 * PI() / 7) as cos_dow
    FROM base_metrics
)
SELECT * FROM normalized_metrics;

-- Tabela para rastreamento de progresso da mineração
CREATE TABLE IF NOT EXISTS mining_progress (
    project_id INTEGER PRIMARY KEY REFERENCES projects(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, PROCESSING, COMPLETED, FAILED
    last_release_tag VARCHAR(100),
    total_releases INTEGER DEFAULT 0,
    processed_releases INTEGER DEFAULT 0,
    error_log TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Metadados do Sistema (Treino, Versões, etc)
CREATE TABLE IF NOT EXISTS system_metadata (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inicializa o contador de releases treinadas
INSERT INTO system_metadata (key, value) VALUES ('last_trained_release_count', '0')
ON CONFLICT DO NOTHING;
