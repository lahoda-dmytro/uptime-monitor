CREATE TABLE IF NOT EXISTS sites (
    id SERIAL PRIMARY KEY,
    url VARCHAR(2048) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ping_logs (
    id SERIAL PRIMARY KEY,
    site_id INTEGER NOT NULL REFERENCES sites(id) ON DELETE CASCADE,
    status_code INTEGER,
    response_time_ms INTEGER,
    is_up BOOLEAN NOT NULL,
    checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    error_message VARCHAR(1024)
);

INSERT INTO sites (url, name, is_active)
VALUES 
    ('https://www.google.com', 'Google', TRUE),
    ('https://github.com', 'GitHub', TRUE)
ON CONFLICT (url) DO NOTHING;
