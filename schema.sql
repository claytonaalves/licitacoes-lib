create table licitacoes (
    identificacao varchar(40) primary key,
    tipo varchar(20),
    comprador varchar(150),
    endereco varchar(150),
    cidade varchar(40),
    uf char(2),
    telefone varchar(20),
    email varchar(180),
    site varchar(180),

    codigo varchar(20),
    modalidade varchar(30),
    objeto text,
    informacoes varchar(150),
    segmento text,
    prazo_credenciamento datetime,
    prazo_proposta datetime,
    cotacao_inicio datetime,
    cotacao_fim datetime
);
