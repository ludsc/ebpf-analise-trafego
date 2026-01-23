# ebpf-analise-trafego
Laboratório para comparar o consumo de CPU sob ataques de negação de serviço (DoS) em ambiente virtualizado.

## 1. Setup do Ambiente
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
