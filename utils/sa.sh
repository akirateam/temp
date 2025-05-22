Olá! Entendi que você precisa criar uma **ServiceAccount** com permissões de **cluster-admin** e um token que **não expira** (ou de longa duração) para automação em clusters ARO, como em processos de upgrade.

⚠️ **Importante:** Tokens sem expiração ou de longa duração representam um risco de segurança significativo se comprometidos. A prática recomendada é usar tokens de curta duração sempre que possível. Para automação, considere o uso de `kubeconfig` gerado para a ServiceAccount ou a TokenRequest API, se aplicável, que gerencia tokens de forma mais segura.

No entanto, para atender à sua solicitação, aqui estão os passos:

---

### 1. Criar a ServiceAccount

Primeiro, crie a ServiceAccount no namespace desejado. Se for para operações em nível de cluster, o namespace `kube-system` ou um namespace dedicado para automação pode ser apropriado. Usarei `kube-system` como exemplo:

```bash
oc create sa <nome-da-sua-serviceaccount> -n <namespace>
```

Exemplo:
```bash
oc create sa aro-upgrade-sa -n kube-system
```

---

### 2. Conceder Permissões de Cluster-Admin

Para dar à ServiceAccount as permissões de `cluster-admin`, crie um `ClusterRoleBinding`:

```bash
oc create clusterrolebinding <nome-do-binding> --clusterrole=cluster-admin --serviceaccount=<namespace>:<nome-da-sua-serviceaccount>
```

Exemplo:
```bash
oc create clusterrolebinding aro-upgrade-sa-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:aro-upgrade-sa
```

---

### 3. Criar um Secret para o Token da ServiceAccount (para Tokens de Longa Duração)

Por padrão, os tokens de ServiceAccounts são de curta duração e gerenciados pelo Kubernetes. Para obter um token que não expira automaticamente (ou que tenha uma vida útil muito longa, embora isso não seja mais o padrão desde o Kubernetes 1.24), você precisa criar um Secret do tipo `kubernetes.io/service-account-token` manualmente para essa ServiceAccount.

Crie um arquivo YAML, por exemplo, `sa-token-secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: <nome-do-secret-do-token>
  namespace: <namespace>
  annotations:
    kubernetes.io/service-account.name: <nome-da-sua-serviceaccount>
type: kubernetes.io/service-account-token
```

Exemplo (`aro-upgrade-sa-token-secret.yaml`):
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: aro-upgrade-sa-token
  namespace: kube-system
  annotations:
    kubernetes.ioio/service-account.name: aro-upgrade-sa
type: kubernetes.io/service-account-token
```

Aplique este YAML:
```bash
oc apply -f sa-token-secret.yaml
```

---

### 4. Obter o Token

Após a criação do Secret, o Kubernetes irá popular ele com o token. Você pode então extrair o token:

```bash
oc get secret <nome-do-secret-do-token> -n <namespace> -o jsonpath='{.data.token}' | base64 --decode
```

Exemplo:
```bash
oc get secret aro-upgrade-sa-token -n kube-system -o jsonpath='{.data.token}' | base64 --decode
```

Este comando irá exibir o token que você pode usar em suas automações.

---

### Resumo dos Comandos (Exemplo Completo):

```bash
# 1. Criar a ServiceAccount
oc create sa aro-upgrade-sa -n kube-system

# 2. Conceder permissões de cluster-admin
oc create clusterrolebinding aro-upgrade-sa-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:aro-upgrade-sa

# 3. Criar o Secret para o token (crie o arquivo aro-upgrade-sa-token-secret.yaml primeiro)
# Conteúdo de aro-upgrade-sa-token-secret.yaml:
# apiVersion: v1
# kind: Secret
# metadata:
#   name: aro-upgrade-sa-token
#   namespace: kube-system
#   annotations:
#     kubernetes.io/service-account.name: aro-upgrade-sa
# type: kubernetes.io/service-account-token
oc apply -f aro-upgrade-sa-token-secret.yaml

# Aguarde alguns segundos para o token ser populado no Secret

# 4. Obter o token
TOKEN=$(oc get secret aro-upgrade-sa-token -n kube-system -o jsonpath='{.data.token}' | base64 --decode)
echo "Seu token é: $TOKEN"
```

Lembre-se de **proteger este token** adequadamente, pois ele concede acesso de administrador ao seu cluster.

Se tiver mais alguma dúvida ou precisar de ajustes, me diga!