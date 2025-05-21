#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import yaml
import difflib
from datetime import datetime

# --- Funções Auxiliares de Análise ---
def analyze_pod_status(pod_before, pod_after):
    """Analisa e compara o status de um Pod antes e depois."""
    status_before = pod_before.get('status', {}) if pod_before else {}
    status_after = pod_after.get('status', {}) if pod_after else {}
    
    phase_before = status_before.get('phase', 'N/A')
    phase_after = status_after.get('phase', 'N/A')

    restarts_before = sum(c.get('restartCount', 0) for c in status_before.get('containerStatuses', []))
    restarts_after = sum(c.get('restartCount', 0) for c in status_after.get('containerStatuses', []))

    # Simplificado: considera problema se não for Running ou Succeeded
    is_problem_before = phase_before not in ['Running', 'Succeeded']
    is_problem_after = phase_after not in ['Running', 'Succeeded']

    change_type = "ok_no_change"
    if phase_before == phase_after and restarts_before == restarts_after:
        if is_problem_after:
            change_type = "persistent_problem_no_change"
    else: # Houve alguma mudança
        if is_problem_after and not is_problem_before:
            change_type = "new_problem"
        elif not is_problem_after and is_problem_before:
            change_type = "resolved_problem"
        elif is_problem_after and is_problem_before:
            change_type = "persistent_problem_changed" # Mudou, mas continua problemático
        elif not is_problem_after and not is_problem_before: # OK -> OK, mas com alguma mudança (ex: restart)
            change_type = "ok_changed_minor"
        else: # Outras transições
            change_type = "state_changed"


    return {
        "phase_before": phase_before, "phase_after": phase_after,
        "restarts_before": restarts_before, "restarts_after": restarts_after,
        "change_type": change_type,
        "summary": f"Fase: {phase_before} -> {phase_after}. Restarts: {restarts_before} -> {restarts_after}."
    }

def analyze_deployment_status(dep_before, dep_after):
    """Analisa e compara o status de um Deployment antes e depois."""
    spec_before = dep_before.get('spec', {}) if dep_before else {}
    status_before = dep_before.get('status', {}) if dep_before else {}
    spec_after = dep_after.get('spec', {}) if dep_after else {}
    status_after = dep_after.get('status', {}) if dep_after else {}

    replicas_spec_b = spec_before.get('replicas', 'N/A')
    replicas_ready_b = status_before.get('readyReplicas', 0)
    
    replicas_spec_a = spec_after.get('replicas', 'N/A')
    replicas_ready_a = status_after.get('readyReplicas', 0)

    problem_b = replicas_spec_b != 'N/A' and replicas_ready_b != replicas_spec_b
    problem_a = replicas_spec_a != 'N/A' and replicas_ready_a != replicas_spec_a
    
    change_type = "ok_no_change"
    if replicas_spec_b == replicas_spec_a and replicas_ready_b == replicas_ready_a:
        if problem_a: # e por consequência problem_b também
             change_type = "persistent_problem_no_change"
    else:
        if problem_a and not problem_b:
            change_type = "new_problem_replicas"
        elif not problem_a and problem_b:
            change_type = "resolved_problem_replicas"
        elif problem_a and problem_b:
            change_type = "persistent_problem_replicas_changed"
        elif not problem_a and not problem_b:
            change_type = "ok_changed_replicas"
        else:
            change_type = "state_changed_replicas"
            
    return {
        "spec_replicas_before": replicas_spec_b, "ready_replicas_before": replicas_ready_b,
        "spec_replicas_after": replicas_spec_a, "ready_replicas_after": replicas_ready_a,
        "change_type": change_type,
        "summary": f"Spec/Ready: {replicas_spec_b}/{replicas_ready_b} -> {replicas_spec_a}/{replicas_ready_a}."
    }

def generate_text_diff(yaml_before_str, yaml_after_str, from_label="antes", to_label="depois"):
    if yaml_before_str is None or yaml_after_str is None:
        return "Um dos conteúdos (antes ou depois) é nulo, não é possível gerar diff."
    if yaml_before_str == yaml_after_str:
        return "" # Sem diferenças

    diff = difflib.unified_diff(
        yaml_before_str.splitlines(keepends=True),
        yaml_after_str.splitlines(keepends=True),
        fromfile=from_label,
        tofile=to_label,
        lineterm=''
    )
    return "".join(list(diff))


def load_yaml_file(filepath):
    """Carrega uma lista de documentos YAML de um arquivo."""
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Se o arquivo contiver uma lista de recursos, from_yaml_all não é necessário
            # Assumindo que o arquivo ansible.builtin.copy já salvou uma lista YAML válida.
            content = yaml.safe_load(f)
            return content if isinstance(content, list) else [] # Garante que sempre retorna uma lista
    except Exception as e:
        print(f"Erro ao carregar YAML de {filepath}: {e}")
        return []

# --- Função Principal de Análise ---
def analyze_snapshots(before_dir, after_dir, namespaces, kinds_config, cluster_name):
    analysis_results = {
        "cluster_name": cluster_name,
        "report_time": datetime.now().isoformat(),
        "summary": {
            "namespaces_analyzed_count": len(namespaces),
            "total_new_pod_issues": 0,
            "total_persistent_pod_issues": 0,
            "total_resolved_pod_issues": 0,
            "total_new_deployment_issues": 0,
            "total_persistent_deployment_issues": 0,
            "total_resolved_deployment_issues": 0,
        },
        "namespaces": []
    }

    for ns_name in namespaces:
        ns_data = {
            "name": ns_name,
            "status_overall": "ok", # Será atualizado se problemas forem encontrados
            "resources": [] # Lista de todos os recursos analisados neste namespace
        }
        
        ns_summary_pods = {"new": 0, "persistent": 0, "resolved": 0}
        ns_summary_deployments = {"new": 0, "persistent": 0, "resolved": 0}

        for kind_info in kinds_config:
            kind_name = kind_info['kind']
            kind_filename = f"{kind_name.lower()}.yml" # Conforme salvo pelo Ansible

            resources_before_list = load_yaml_file(os.path.join(before_dir, ns_name, kind_filename))
            resources_after_list = load_yaml_file(os.path.join(after_dir, ns_name, kind_filename))

            # Criar dicionários para fácil lookup por nome
            resources_before_map = {res['metadata']['name']: res for res in resources_before_list if res and 'metadata' in res and 'name' in res['metadata']}
            resources_after_map = {res['metadata']['name']: res for res in resources_after_list if res and 'metadata' in res and 'name' in res['metadata']}

            all_resource_names = set(resources_before_map.keys()) | set(resources_after_map.keys())

            for res_name in all_resource_names:
                res_before = resources_before_map.get(res_name)
                res_after = resources_after_map.get(res_name)
                
                resource_analysis = {
                    "kind": kind_name,
                    "name": res_name,
                    "namespace": ns_name, # Adicionando namespace aqui para o template
                    "change_type": "unknown",
                    "details": {},
                    "raw_diff": ""
                }

                if res_before and not res_after:
                    resource_analysis["change_type"] = "removed"
                elif not res_before and res_after:
                    resource_analysis["change_type"] = "added"
                elif res_before and res_after:
                    # Comparar YAMLs para ver se houve modificação (mesmo que o status seja OK)
                    yaml_b_str = yaml.dump(res_before, sort_keys=True)
                    yaml_a_str = yaml.dump(res_after, sort_keys=True)

                    if yaml_b_str != yaml_a_str:
                        resource_analysis["change_type"] = "modified"
                        resource_analysis["raw_diff"] = generate_text_diff(yaml_b_str, yaml_a_str, f"{res_name}-antes", f"{res_name}-depois")
                    else:
                         resource_analysis["change_type"] = "unchanged"


                    # Análise específica por Kind
                    if kind_name == "Pod":
                        pod_analysis_details = analyze_pod_status(res_before, res_after)
                        resource_analysis["details"].update(pod_analysis_details)
                        # Atualiza o change_type com base na análise mais específica do Pod se não for apenas 'modified'
                        if pod_analysis_details["change_type"] not in ["ok_no_change", "ok_changed_minor", "state_changed"]:
                             resource_analysis["change_type"] = pod_analysis_details["change_type"]
                        
                        if pod_analysis_details["change_type"] == "new_problem":
                            ns_summary_pods["new"] += 1
                        elif "persistent_problem" in pod_analysis_details["change_type"]:
                            ns_summary_pods["persistent"] += 1
                        elif pod_analysis_details["change_type"] == "resolved_problem":
                            ns_summary_pods["resolved"] += 1
                            
                    elif kind_name in ["Deployment", "StatefulSet", "DaemonSet"]: # Generalizar para outros controladores
                        dep_analysis_details = analyze_deployment_status(res_before, res_after) # Reutiliza a função
                        resource_analysis["details"].update(dep_analysis_details)
                        if dep_analysis_details["change_type"] not in ["ok_no_change", "ok_changed_replicas", "state_changed_replicas"]:
                            resource_analysis["change_type"] = dep_analysis_details["change_type"]

                        if dep_analysis_details["change_type"] == "new_problem_replicas":
                            ns_summary_deployments["new"] += 1
                        elif "persistent_problem_replicas" in dep_analysis_details["change_type"]:
                            ns_summary_deployments["persistent"] += 1
                        elif dep_analysis_details["change_type"] == "resolved_problem_replicas":
                            ns_summary_deployments["resolved"] += 1
                    
                    # Se houve qualquer tipo de problema identificado, marca o namespace
                    if "problem" in resource_analysis["change_type"]:
                        ns_data["status_overall"] = "problems_found"
                    elif resource_analysis["change_type"] != "unchanged" and ns_data["status_overall"] == "ok":
                        ns_data["status_overall"] = "changes_only"


                ns_data["resources"].append(resource_analysis)
        
        # Atualiza sumários globais
        analysis_results["summary"]["total_new_pod_issues"] += ns_summary_pods["new"]
        analysis_results["summary"]["total_persistent_pod_issues"] += ns_summary_pods["persistent"]
        analysis_results["summary"]["total_resolved_pod_issues"] += ns_summary_pods["resolved"]
        analysis_results["summary"]["total_new_deployment_issues"] += ns_summary_deployments["new"]
        analysis_results["summary"]["total_persistent_deployment_issues"] += ns_summary_deployments["persistent"]
        analysis_results["summary"]["total_resolved_deployment_issues"] += ns_summary_deployments["resolved"]

        analysis_results["namespaces"].append(ns_data)
        
    return analysis_results

# --- Main Execution ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analisa snapshots de recursos Kubernetes antes e depois.")
    parser.add_argument("--before_dir", required=True, help="Diretório com snapshots 'antes_upgrade'")
    parser.add_argument("--after_dir", required=True, help="Diretório com snapshots 'depois_upgrade'")
    parser.add_argument("--namespaces", required=True, help="Lista de namespaces separados por vírgula")
    parser.add_argument("--kinds_config_path", required=True, help="Caminho para o arquivo YAML com a definição dos kinds (vars/resource_definitions.yml)")
    parser.add_argument("--output_json", required=True, help="Caminho para o arquivo JSON de saída dos resultados")
    parser.add_argument("--cluster_name", required=True, help="Nome do cluster para o relatório")
    
    args = parser.parse_args()

    try:
        with open(args.kinds_config_path, 'r', encoding='utf-8') as f:
            kinds_config_data = yaml.safe_load(f)
            resource_kinds_to_collect = kinds_config_data.get('resource_kinds_to_collect', [])
            if not resource_kinds_to_collect:
                raise ValueError("Nenhum 'resource_kinds_to_collect' encontrado no arquivo de configuração.")
    except Exception as e:
        print(f"Erro ao carregar configuração de kinds de {args.kinds_config_path}: {e}")
        sys.exit(1)

    namespaces_list = [ns.strip() for ns in args.namespaces.split(',')]
    
    results = analyze_snapshots(args.before_dir, args.after_dir, namespaces_list, resource_kinds_to_collect, args.cluster_name)
    
    try:
        os.makedirs(os.path.dirname(args.output_json), exist_ok=True)
        with open(args.output_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Análise completa. Resultados salvos em: {args.output_json}")
    except Exception as e:
        print(f"Erro ao salvar resultados JSON em {args.output_json}: {e}")
        sys.exit(1)