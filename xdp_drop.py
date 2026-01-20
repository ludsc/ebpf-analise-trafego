#!/usr/bin/python3
from bcc import BPF
import time
import sys

# Defina sua interface de rede aqui (ex: eth0, ens33)
device = "eth0" 

# Código C que roda no Kernel (eBPF)
prog = """
#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>

int xdp_drop_tcp_8080(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    struct ethhdr *eth = data;

    // Verificar se é IP
    if ((void*)eth + sizeof(*eth) <= data_end) {
        struct iphdr *ip = data + sizeof(*eth);
        if ((void*)ip + sizeof(*ip) <= data_end) {
            // Verificar se é TCP
            if (ip->protocol == IPPROTO_TCP) {
                struct tcphdr *tcp = (void*)ip + sizeof(*ip);
                if ((void*)tcp + sizeof(*tcp) <= data_end) {
                    // Se porta for 8080, DROP (XDP_DROP)
                    if (tcp->dest == ntohs(8080)) {
                        return XDP_DROP;
                    }
                }
            }
        }
    }
    return XDP_PASS;
}
"""

# Carrega o programa eBPF
b = BPF(text=prog)
fn = b.load_func("xdp_drop_tcp_8080", BPF.XDP)

# Anexa o programa à interface de rede
print(f"Carregando eBPF XDP drop na interface {device}...")
b.attach_xdp(device, fn, 0)

try:
    print("Rodando... Pressione Ctrl+C para parar.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Removendo filtro...")
    b.remove_xdp(device, 0)