INSERT INTO tbCliente (nomeCliente) VALUES ( 'Ana' ); 
INSERT INTO tbCliente (nomeCliente) VALUES ( 'Claudia' ); 
INSERT INTO tbCliente (nomeCliente) VALUES ( 'Marcos' ); 
INSERT INTO tbCliente (nomeCliente) VALUES ( 'Pedro' );
SELECT * FROM tbCliente 

INSERT INTO tbProduto (nomeProduto,quantidadeLikes) VALUES ('Cartão de Crédito',1); 
INSERT INTO tbProduto (nomeProduto,quantidadeLikes) VALUES ('Conta Corrente',3); 
INSERT INTO tbProduto (nomeProduto,quantidadeLikes) VALUES ('Crédito Pessoal',2); 
INSERT INTO tbProduto (nomeProduto,quantidadeLikes) VALUES ('Poupança',0); 
INSERT INTO tbProduto (nomeProduto,quantidadeLikes) VALUES ('Renda Fixa',0); 
INSERT INTO tbProduto (nomeProduto,quantidadeLikes) VALUES ('Renda Variável',0); 
select * from tbProduto

INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Ana','Cartão de Crédito',1); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Ana','Conta Corrente',2); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Ana','Crédito Pessoal',3); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Ana','Poupança',4); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Ana','Renda Fixa',5); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Marcos','Cartão de Crédito',2); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Marcos','Conta Corrente',3); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Marcos','Poupança',4); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Marcos','Renda Fixa',5); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Marcos','Renda Variável',0.6); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Pedro','Cartão de Crédito',3); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Pedro','Conta Corrente',4); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Pedro','Poupança',5); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Pedro','Crédito Pessoal',7);
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Claudia','Cartão de Crédito',4); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Claudia','Conta Corrente',5); 
INSERT INTO tbClienteProduto(nomeCliente,nomeProduto,valor) VALUES ('Claudia','Poupança',6); 
SELECT * from tbClienteProduto

INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Ana','Claudia',0.16); 
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Ana','Marcos',0.33);
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Ana','Pedro',0.20);
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Claudia','Ana',0.16);
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Claudia','Marcos',0.20); 
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Claudia','Pedro',0.36); 
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Marcos','Ana',0.33); 
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Marcos','Claudia',0.22); 
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Marcos','Pedro',0.36); 
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Pedro','Ana',0.20); 
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Pedro','Claudia',0.36);
INSERT INTO tbClienteSimilaridade(nomeClienteOrigem,nomeClienteDestino,similaridade) VALUES ('Pedro','Marcos',0.36);
SELECT * from tbClienteSimilaridade

select * from tbClienteSimilaridade where nomeClienteOrigem = 'Ana' order by similaridade desc LIMIT 1; 

select b.* from tbCliente a, tbClienteProduto b, tbProduto c
where a.nomeCliente = b.nomeCliente and b.nomeProduto = c.nomeProduto and b.nomeCliente = 'Marcos'
 and b.nomeProduto not in 
  (select b.nomeProduto from tbCliente a, tbClienteProduto b, tbProduto c
   where a.nomeCliente = b.nomeCliente and b.nomeProduto = c.nomeProduto and b.nomeCliente = 'Ana');
   
SELECT * FROM tbProduto ORDER BY quantidadeLikes DESC

UPDATE tbProduto SET quantidadeLikes = quantidadeLikes + 1 WHERE nomeProduto = 'Cartão de Crédito'
UPDATE tbProduto SET quantidadeLikes = quantidadeLikes - 1 WHERE nomeProduto = 'Cartão de Crédito'

