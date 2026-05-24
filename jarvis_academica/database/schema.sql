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
('[BUG] IA respondendo "não sei" para tudo', 'Modelo treinado com excesso de humildade. Investigate se o problema está no dataset ou se ela simplesmente desistiu da vida.', 'alta'),
('[FEATURE] Adicionar memória de longo prazo ao agente', 'Usuário pediu para o agente lembrar que ele não gosta de café. O agente esqueceu. Usuário está chateado.', 'alta'),
('[MELHORIA] Reduzir tempo de resposta do chatbot', 'Atualmente o bot pensa por 40 segundos antes de dizer "olá". Usuários acharam que era meditação guiada.', 'normal'),
('[REVISÃO] Checar alucinações no relatório gerado', 'O modelo incluiu três referências bibliográficas que não existem e citou um autor chamado "Prof. Dr. Fictício da Silva".', 'normal'),
('[DOCS] Escrever tutorial de uso do sistema', 'Ninguém leu o último tutorial. Talvez porque estava em LaTeX. Reescrever em linguagem humana desta vez.', 'baixa');