# ebpf-analise-trafego
Laboratório para comparar o consumo de CPU sob ataques de negação de serviço (DoS) em ambiente virtualizado.

## 1. Setup do Ambiente DOCKER
```bash
# Instalar dependências (Ubuntu)
sudo apt update && sudo apt install -y docker.io docker-compose hping3 bpfcc-tools

# Clonar e subir ambiente
git clone [https://github.com/ludsc/ebpf-analise-trafego.git](https://github.com/ludsc/ebpf-analise-trafego.git)
cd ebpf-analise-trafego
sudo docker-compose up -d

# Criar gráfico no Prometheus
sum(rate(node_cpu_seconds_total{mode="softirq"}[1m])) by (instance) * 100

#Na VM vítima
# Bloquear porta 8080
sudo iptables -A INPUT -p tcp --dport 8080 -j DROP
#Na atacante
# Substitua <IP_DA_VM> pelo IP real
sudo hping3 -S -p 8080 --flood <IP_DA_VM>
#Na vítima
sudo iptables -F
#Na vítima
# Rodar o filtro XDP (certifique-se de ajustar a interface no script se necessário)
sudo python3 xdp_drop.py
#Na atacante
# Mesmo comando de ataque
sudo hping3 -S -p 8080 --flood <IP_DA_VM>
## AMBIENTE KUBERNETES 
## 🚀 Pré-requisitos

* Uma VM Linux (Ubuntu recomendado) com acesso root.
* Python 3 e BCC Tools instalados (`sudo apt-get install bpfcc-tools linux-headers-$(uname -r)`).
* Git.

---

## 🛠️ Instalação e Configuração

### 1. Setup do Kubernetes (K3s)
Instalação leve do Kubernetes para ambientes de laboratório.

```bash
curl -sfL [https://get.k3s.io](https://get.k3s.io) | sh -
# Configurar permissão para o usuário atual
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
export KUBECONFIG=~/.kube/config

# Instalar Helm
sudo snap install helm --classic

# Adicionar repositório e instalar
helm repo add prometheus-community [https://prometheus-community.github.io/helm-charts](https://prometheus-community.github.io/helm-charts)
helm repo update
helm install monitor prometheus-community/kube-prometheus-stack
# aplicar configurações na vm vítima 
kubectl apply -f vitima.yaml
# checar a senha do grafana
kubectl get secret monitor-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
# redirecionar a porta
kubectl port-forward svc/monitor-grafana 3000:80 --address 0.0.0.0
# crie a dashboard no grafana
sum(rate(node_cpu_seconds_total{mode="softirq"}[1m])) by (instance) * 100
# na máquina atacante simule o ataque
# Ataque direcionado à porta do NodePort
sudo hping3 -S -p 30080 --flood <IP-DA-VM>
#na vm vítima aplique o ebpf
sudo python3 xdp_drop_k8s.py
# repita o ataque

