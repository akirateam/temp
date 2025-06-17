/****** Seleciona todos os clientes da tabela tbCliente ******/
SELECT nomeCliente FROM tbCliente

/****** Cliente mais similar: Seleciona 1 registro da tabela que armazena a similaridade entre os clientes, passando como crit�rio o cliente de origem (selecionado na tela), ordenado pela maior similaridade ******/
select top 1 a.* from tbClienteSimilaridade a where a.nomeClienteOrigem = 'Ana' order by similaridade desc

/****** Busca o produto que o cliente de origem n�o tenha contratado a partir do cliente de destino mais similar  ******/
select b.nomeProduto, b.valor*1000 as valor from tbCliente a, tbClienteProduto b, tbProduto c 
where a.nomeCliente = b.nomeCliente and b.nomeProduto = c.nomeProduto and b.nomeCliente = 'Marcos'
and b.nomeProduto not in (select b.nomeProduto from tbCliente a, tbClienteProduto b, tbProduto c 
where a.nomeCliente = b.nomeCliente and b.nomeProduto = c.nomeProduto
and b.nomeCliente = 'Ana')

/*consulta produto mais popular */
select a.* from tbProduto a order by a.quantidadeLikes desc;

/*Incrementa qtdLikes para o produto Poupan�a*/
UPDATE tbProduto SET quantidadeLikes = quantidadeLikes + 1 WHERE nomeProduto = 'Poupan�a' 

/*Decrementa qtdLikes para o produto Poupan�a*/
UPDATE tbProduto SET quantidadeLikes = quantidadeLikes - 1 WHERE nomeProduto = 'Poupan�a' 
