# Ansible Playbook: Health Check de Aplicações em Namespaces de Negócio ARO

Este projeto realiza um health check em namespaces de negócio de clusters Azure Red Hat OpenShift (ARO), comparando o estado antes e depois de um upgrade ou manutenção. Ele gera um relatório HTML detalhado focado no impacto para as aplicações.

## Funcionalidades

* Coleta de snapshots de recursos Kubernetes (Deployments, Pods, etc.) em namespaces de negócio.
* Comparação "antes vs. depois" do upgrade.
* Análise detalhada do estado de Pods (fase, restarts) e Deployments (réplicas).
* Identificação de problemas Novos, Persistentes ou Resolvidos.
* Geração de um relatório HTML para consulta, otimizado para visualização em Grafana.

## Pré-requisitos

* Ansible (Core >= 2.12)
* Coleção `kubernetes.core` (`ansible-galaxy collection install kubernetes.core`)
* Python 3.x no nó de controle Ansible (com biblioteca `PyYAML` e `difflib` - `difflib` é padrão).
* `kubectl` ou `oc` CLI configurado com acesso ao cluster ARO.

## Estrutura de Diretórios

aro_health_check_apps/
├── health_check_main.yml
├── vars/
│   └── resource_definitions.yml
├── tasks/
│   ├── collect_namespace_snapshots.yml
│   └── generate_html_report.yml
├── scripts/
│   └── analyze_snapshots.py
├── templates/
│   └── report_template.html.j2
├── snapshots/                # Criado automaticamente
├── reports/                  # Criado automaticamente (contém analysis_results.json e o HTML)
└── README.md

## Como Usar

1.  **Configuração**:
    * Edite `vars/resource_definitions.yml` para listar os `kinds` que você quer monitorar.
    * Certifique-se que o script `scripts/analyze_snapshots.py` tem permissão de execução (`chmod +x scripts/analyze_snapshots.py`).

2.  **Execução**:
    * **Antes do Upgrade**:
        ```bash
        ansible-playbook health_check_main.yml -e "execution_phase=antes_upgrade" -e "cluster_name=meuclusteraro"
        ```
    * **Depois do Upgrade**:
        ```bash
        ansible-playbook health_check_main.yml -e "execution_phase=depois_upgrade" -e "cluster_name=meuclusteraro"
        ```
    * **Gerar Relatório (após as duas coletas)**:
        ```bash
        ansible-playbook health_check_main.yml -e "execution_phase=report_only" -e "cluster_name=meuclusteraro"
        ```
        O relatório HTML (`health_report_meuclusteraro.html`) e o JSON de análise (`analysis_results.json`) serão salvos no diretório `reports/`.

## Integração com Grafana

O relatório HTML gerado em `reports/` pode ser hospedado em um servidor web e embutido em um painel do Grafana usando um painel de Texto em modo HTML com um `<iframe>`.