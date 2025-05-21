#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import difflib
import os

def generate_diff(file1_path, file2_path, from_label='antes', to_label='depois'):
    """
    Gera um diff unificado entre dois arquivos e imprime no stdout.
    Retorna 0 em sucesso, 1 em erro.
    """
    try:
        if not os.path.exists(file1_path):
            sys.stderr.write(f"Erro: Arquivo 'antes' não encontrado em '{file1_path}'\n")
            return 1
        if not os.path.exists(file2_path):
            sys.stderr.write(f"Erro: Arquivo 'depois' não encontrado em '{file2_path}'\n")
            return 1

        with open(file1_path, 'r', encoding='utf-8') as f1:
            text1_lines = f1.readlines()
        with open(file2_path, 'r', encoding='utf-8') as f2:
            text2_lines = f2.readlines()

        # Garante que os nomes dos arquivos no cabeçalho do diff sejam apenas os nomes base
        # e não os caminhos completos dos arquivos temporários.
        from_label_display = os.path.basename(from_label)
        to_label_display = os.path.basename(to_label)

        diff_lines = difflib.unified_diff(
            text1_lines,
            text2_lines,
            fromfile=from_label_display,
            tofile=to_label_display,
            lineterm='' # Evita linhas em branco extras no diff
        )

        for line in diff_lines:
            sys.stdout.write(line)
        
        return 0

    except Exception as e:
        sys.stderr.write(f"Erro inesperado ao gerar diff: {str(e)}\n")
        return 1

if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.stderr.write("Uso: python custom_diff.py <caminho_arquivo1> <caminho_arquivo2> <label_arquivo1> <label_arquivo2>\n")
        sys.stderr.write("Exemplo: python custom_diff.py temp_antes.yml temp_depois.yml antes.yml depois.yml\n")
        sys.exit(2) # Código de erro diferente para uso incorreto

    file1 = sys.argv[1]
    file2 = sys.argv[2]
    label1 = sys.argv[3] # Label para o arquivo "antes" no cabeçalho do diff
    label2 = sys.argv[4] # Label para o arquivo "depois" no cabeçalho do diff
    
    exit_code = generate_diff(file1, file2, label1, label2)
    sys.exit(exit_code)