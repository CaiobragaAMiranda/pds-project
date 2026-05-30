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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(release_id, file_path)
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_file_metrics_release ON file_metrics(release_id);
CREATE INDEX IF NOT EXISTS idx_releases_project ON releases(project_id);
