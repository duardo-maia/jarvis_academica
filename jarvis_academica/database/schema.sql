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

-- Tabela de histórico do quiz (active recall)
CREATE TABLE IF NOT EXISTS historico_quiz (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topico TEXT NOT NULL,
    nota INTEGER NOT NULL CHECK(nota BETWEEN 0 AND 10),
    data_tentativa DATETIME DEFAULT (datetime('now', 'localtime'))
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
('Corrida Beneficente', 'Organização da corrida da cidade', '2026-06-07', '06:00', '09:00', 'Coxim-MS', 2),
('Prova de Banco de Dados', 'Prova da disciplina de Banco de Dados', '2026-06-12', '09:00', '12:00', 'Sala 101', NULL),
('Aula de Machine Learning', 'Aula sobre algoritmos supervisionados', '2026-06-13', '08:00', '10:00', 'Sala 203', NULL),
('Reunião de Orientação', 'Reunião com orientador sobre o TCC', '2026-06-15', '15:00', '16:00', 'Sala dos Professores', 1),
('Aula de Processamento de Linguagem Natural', 'Aula sobre tokenização, embeddings e modelos de linguagem', '2026-06-16', '08:00', '10:00', 'Sala 203', NULL),
('Monitoria de Programação Web', 'Atendimento de dúvidas da lista 3', '2026-06-17', '14:00', '15:00', 'Lab 2', NULL),
('Prova de Inteligência Artificial', 'Prova da disciplina de IA: deep learning, LLMs, RAG', '2026-06-20', '09:00', '11:00', 'Sala 101', NULL);

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