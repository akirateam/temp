#!/usr/bin/env python

import json
import sys
import argparse
import os
import re
from kubernetes import client, config # Você precisará instalar a library kubernetes-client para Python

def get_acm_api_client():
    """
    Configura e retorna um cliente para interagir com a API do ACM Hub Cluster.
    Pode carregar a configuração via kubeconfig ou token de service account (comum no OCP/ACM).
    As credenciais viriam de variáveis de ambiente ou arquivos fornecidos pelo AAP Controller.
    """
    try:
        # Exemplo: Carregar config de um kubeconfig file (pode ser montado pelo AAP)
        # config.load_kubeconfig(config_file=os.environ.get('KUBECONFIG_PATH', '~/.kube/config'))

        # Exemplo: Carregar config de dentro de um cluster (se o EE roda no OCP/ACM)
        # config.load_incluster_config()

        # Exemplo: Usar um token e host (vindos de credenciais do AAP)
        host = os.environ.get('ACM_API_URL') # Variável de ambiente definida na Credencial/Fonte do AAP
        token = os.environ.get('ACM_API_TOKEN') # Variável de ambiente definida na Credencial/Fonte do AAP

        configuration = client.Configuration()
        configuration.host = host
        configuration.api_key['authorization'] = 'Bearer ' + token
        # Configurações adicionais para SSL, se necessário
        # configuration.verify_ssl = False
        # configuration.ssl_ca_cert = os.environ.get('ACM_CA_CERT_PATH') # Caminho para o CA cert

        api_client = client.ApiClient(configuration)
        return api_client

    except Exception as e:
        print(f"Erro ao configurar cliente da API do ACM: {e}", file=sys.stderr)
        sys.exit(1)


def get_managed_clusters(api_client):
    """
    Busca a lista de recursos ManagedCluster na API do ACM.
    """
    try:
        # A API de Managed Clusters está em 'cluster.open-cluster-management.io/v1'
        # Pode variar dependendo da versão do ACM/OCP
        api = client.CustomObjectsApi(api_client)

        # Lista recursos 'managedclusters' no grupo 'cluster.open-cluster-management.io', versão 'v1'
        # O namespace geralmente é 'default' ou vazio para recursos cluster-scoped
        clusters = api.list_cluster_custom_object(
            group="cluster.open-cluster-management.io",
            version="v1",
            plural="managedclusters"
        )
        return clusters.get('items', [])

    except client.ApiException as e:
        print(f"Erro na chamada da API do ACM: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Erro geral ao buscar clusters do ACM: {e}", file=sys.stderr)
        sys.exit(1)


def build_ansible_inventory(managed_clusters):
    """
    Processa a lista de ManagedClusters e constrói a estrutura JSON do inventário Ansible.
    Inclui a lógica da taxonomia para criar grupos.
    """
    # Estrutura inicial do inventário dinâmico
    inventory = {
        "_meta": {
            "hostvars": {}
        }
        # Grupos serão adicionados aqui dinamicamente
    }

    # Defina os grupos baseados na taxonomia
    groups = {
        "dv": [],
        "ho": [],
        "pr": [],
        "other_aro": [], # Para AROs que não se encaixam nos stages acima
        "non_aro": [] # Para outros tipos de clusters gerenciados pelo ACM
    }

    # Regex para extrair o stage da taxonomia aro{dv|ho|pr}...
    aro_regex = re.compile(r'^aro(dv|ho|pr)', re.IGNORECASE)

    for cluster in managed_clusters:
        cluster_name = cluster.get('metadata', {}).get('name')
        if not cluster_name:
            continue # Ignora clusters sem nome

        # Exemplo: Extrair API Endpoint (a localização exata pode variar na estrutura do ManagedCluster)
        # Você precisará inspecionar o objeto ManagedCluster retornado pela API
        # Pode estar em .status.apiServerURL, ou em annotations/labels
        # Para simplificar aqui, vamos apenas usar o nome como host e adicionar vars importantes
        host_name = cluster_name # Usando o nome do cluster ACM como nome do host Ansible

        # Exemplo: Obter o URL do API Server do cluster gerenciado (Essencial para playbooks)
        # Esta informação pode estar na estrutura 'status.clusterApiAddress' ou similar
        # ou em annotations como 'managed-cluster-api-server-url'
        api_server_url = None
        try:
             # Exemplo (pode variar): status.apiServerURL
             api_server_url = cluster.get('status', {}).get('apiServerURL')
             # Exemplo (pode variar): annotation específica
             if not api_server_url:
                 api_server_url = cluster.get('metadata', {}).get('annotations', {}).get('managed-cluster-api-server-url')
             # Outros lugares para procurar
             if not api_server_url:
                  connections = cluster.get('status', {}).get('clusterConnections', [])
                  for conn in connections:
                       if conn.get('type') == 'API': # Exemplo de tipo
                            api_server_url = conn.get('url')
                            break

        except AttributeError:
            api_server_url = None # Caso a estrutura esperada não exista

        # Adicionar variáveis específicas do host
        inventory["_meta"]["hostvars"][host_name] = {
            "acm_cluster_name": cluster_name,
            "acm_api_server_url": api_server_url, # Variável crucial para automação
            "cluster_type": cluster.get('spec', {}).get('provisioner', 'unknown'), # Exemplo de outra var
            # Adicione outras variáveis úteis baseadas nas propriedades do ManagedCluster
        }

        # Lógica para agrupar baseado na taxonomia do nome
        match = aro_regex.match(cluster_name)
        if match:
            stage = match.group(1).lower() # 'dv', 'ho', 'pr'
            if stage in groups:
                groups[stage].append(host_name)
            else:
                 # Caso a regex pegue algo que não seja dv, ho, pr (improvável com a regex atual, mas boa prática)
                groups["other_aro"].append(host_name)
        elif cluster_name.lower().startswith('aro'):
             # É um cluster ARO, mas o nome não segue a taxonomia dv/ho/pr esperada pela regex
            groups["other_aro"].append(host_name)
        else:
            # Não parece ser um cluster ARO (pelo nome)
            groups["non_aro"].append(host_name)

    # Adicionar os grupos preenchidos ao inventário final
    for group_name, hosts_list in groups.items():
        if hosts_list: # Só adiciona o grupo se ele tiver hosts
            inventory[group_name] = {"hosts": hosts_list}

    return inventory

def main():
    parser = argparse.ArgumentParser(description='Ansible dynamic inventory script for Red Hat ACM.')
    parser.add_argument('--list', action='store_true', help='List all hosts and groups.')
    # Embora --host seja parte da especificação, para muitos scripts modernos, --list é suficiente.
    # Implementar --host é mais complexo e raramente necessário para inventários simples.
    # parser.add_argument('--host', help='List vars for a specific host.')

    args = parser.parse_args()

    if args.list:
        api_client = get_acm_api_client()
        managed_clusters = get_managed_clusters(api_client)
        inventory_data = build_ansible_inventory(managed_clusters)
        print(json.dumps(inventory_data, indent=2))
    # elif args.host:
        # Implementação para --host (buscar vars para um host específico)
        # Geralmente envolve rodar a mesma lógica de busca de clusters e filtrar pelo host solicitado
        # e retornar apenas a estrutura: {"_meta": {"hostvars": {"hostname": {...}}}}
        # print(json.dumps({"_meta": {"hostvars": {args.host: {}}}}, indent=2)) # Exemplo mínimo

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
