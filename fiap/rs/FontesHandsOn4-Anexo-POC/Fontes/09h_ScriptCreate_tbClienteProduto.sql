USE [DBDINDIN]
GO

/****** Object:  Table [dbo].[tbClienteProduto]    Script Date: 18/05/2022 12:48:20 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[tbClienteProduto](
	[nomeCliente] [varchar](50) NOT NULL,
	[nomeProduto] [varchar](50) NOT NULL,
	[valor] [float] NULL,
 CONSTRAINT [PK_tbClienteProduto] PRIMARY KEY CLUSTERED 
(
	[nomeCliente] ASC,
	[nomeProduto] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[tbClienteProduto]  WITH CHECK ADD  CONSTRAINT [FK_tbClienteProduto_tbCliente] FOREIGN KEY([nomeCliente])
REFERENCES [dbo].[tbCliente] ([nomeCliente])
GO

ALTER TABLE [dbo].[tbClienteProduto] CHECK CONSTRAINT [FK_tbClienteProduto_tbCliente]
GO

ALTER TABLE [dbo].[tbClienteProduto]  WITH CHECK ADD  CONSTRAINT [FK_tbClienteProduto_tbProduto] FOREIGN KEY([nomeProduto])
REFERENCES [dbo].[tbProduto] ([nomeProduto])
GO

ALTER TABLE [dbo].[tbClienteProduto] CHECK CONSTRAINT [FK_tbClienteProduto_tbProduto]
GO

