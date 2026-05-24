-- =========================================
-- CRIAÇÃO DO BANCO DE DADOS DA AGENDA
-- =========================================

-- Tabela de contatos
CREATE TABLE IF NOT EXISTS contatos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    telefone TEXT,
    email TEXT,
    observacoes TEXT
);

-- Tabela de eventos
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    data_evento DATE NOT NULL,
    hora_inicio TIME,
    hora_fim TIME,
    local TEXT,
    contato_id INTEGER,
    FOREIGN KEY (contato_id) REFERENCES contatos(id)
);

-- Tabela de lembretes
CREATE TABLE IF NOT EXISTS lembretes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    evento_id INTEGER NOT NULL,
    data_lembrete DATETIME NOT NULL,
    enviado INTEGER DEFAULT 0,
    FOREIGN KEY (evento_id) REFERENCES eventos(id)
);

-- Tabela de tarefas
CREATE TABLE IF NOT EXISTS tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    prioridade TEXT DEFAULT 'normal' CHECK(prioridade IN ('baixa', 'normal', 'alta')),
    status TEXT DEFAULT 'pendente' CHECK(status IN ('pendente', 'concluida')),
    data_criacao DATETIME DEFAULT (datetime('now', 'localtime')),
    data_conclusao DATETIME
);

-- =========================================
-- DADOS EXEMPLO
-- =========================================

INSERT INTO contatos (nome, telefone, email, observacoes)
VALUES
('Pedro Henrique', '(67)99999-1111', 'pedro@email.com', 'Amigo da faculdade'),
('Maria Souza', '(67)98888-2222', 'maria@email.com', 'Organização de eventos');

INSERT INTO eventos (titulo, descricao, data_evento, hora_inicio, hora_fim, local, contato_id)
VALUES
('Reunião do Projeto', 'Discussão do sistema acadêmico', '2026-05-25', '14:00', '16:00', 'UFMS', 1),
('Corrida Beneficente', 'Organização da corrida da cidade', '2026-06-07', '06:00', '09:00', 'Coxim-MS', 2);

INSERT INTO lembretes (evento_id, data_lembrete)
VALUES
(1, '2026-05-25 12:00:00'),
(2, '2026-06-06 18:00:00');

INSERT INTO tarefas (titulo, descricao, prioridade)
VALUES
('Estudar para a prova de Cálculo', 'Revisar integrais e derivadas', 'alta'),
('Entregar relatório do projeto', 'Finalizar e enviar o relatório da disciplina de ES', 'alta'),
('Comprar material de escritório', NULL, 'baixa');