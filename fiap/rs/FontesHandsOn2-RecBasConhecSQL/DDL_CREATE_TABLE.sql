CREATE TABLE [tbCliente](
 [nomeCliente] [varchar](50) NOT NULL,
 CONSTRAINT [PK_tbCliente] PRIMARY KEY([nomeCliente] ASC))
 
CREATE TABLE [tbProduto](
 [nomeProduto] [varchar](50) NOT NULL,
 [quantidadeLikes] [int] NULL,
 CONSTRAINT [PK_tbProduto] PRIMARY KEY([nomeProduto] ASC))
 
CREATE TABLE [tbClienteProduto](
 [nomeCliente] [varchar](50) NOT NULL,
 [nomeProduto] [varchar](50) NOT NULL,
 [valor] [float] NULL,
 CONSTRAINT [PK_tbClienteProduto] PRIMARY KEY([nomeCliente] ASC, [nomeProduto] ASC))
 
CREATE TABLE [tbClienteSimilaridade](
 [nomeClienteOrigem] [varchar](50) NOT NULL,
 [nomeClienteDestino] [varchar](50) NOT NULL,
 [similaridade] [float] NOT NULL,
 CONSTRAINT [PK_tbClienteDistancia] PRIMARY KEY([nomeClienteOrigem] ASC, [nomeClienteDestino] ASC))