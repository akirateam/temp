USE [DBDINDIN]
GO

/****** Object:  Table [dbo].[tbClienteSimilaridade]    Script Date: 18/05/2022 12:48:37 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[tbClienteSimilaridade](
	[nomeClienteOrigem] [varchar](50) NOT NULL,
	[nomeClienteDestino] [varchar](50) NOT NULL,
	[similaridade] [float] NOT NULL,
 CONSTRAINT [PK_tbClienteDistancia] PRIMARY KEY CLUSTERED 
(
	[nomeClienteOrigem] ASC,
	[nomeClienteDestino] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[tbClienteSimilaridade]  WITH CHECK ADD  CONSTRAINT [FK_tbClienteDistancia_tbCliente] FOREIGN KEY([nomeClienteOrigem])
REFERENCES [dbo].[tbCliente] ([nomeCliente])
GO

ALTER TABLE [dbo].[tbClienteSimilaridade] CHECK CONSTRAINT [FK_tbClienteDistancia_tbCliente]
GO

ALTER TABLE [dbo].[tbClienteSimilaridade]  WITH CHECK ADD  CONSTRAINT [FK_tbClienteDistancia_tbCliente1] FOREIGN KEY([nomeClienteDestino])
REFERENCES [dbo].[tbCliente] ([nomeCliente])
GO

ALTER TABLE [dbo].[tbClienteSimilaridade] CHECK CONSTRAINT [FK_tbClienteDistancia_tbCliente1]
GO

