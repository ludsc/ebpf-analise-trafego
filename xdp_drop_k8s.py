#!/usr/bin/python3
from bcc import BPF
import time

device = "ens33" # Sua interface física

prog = """
#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/ip.h>
#include <linux/tcp.h>

int xdp_drop_nodeport(struct xdp_md *ctx) {
    void *data_end = (void *)(long)ctx->data_end;
    void *data = (void *)(long)ctx->data;
    struct ethhdr *eth = data;

    if ((void*)eth + sizeof(*eth) <= data_end) {
        struct iphdr *ip = data + sizeof(*eth);
        if ((void*)ip + sizeof(*ip) <= data_end) {
            if (ip->protocol == IPPROTO_TCP) {
                struct tcphdr *tcp = (void*)ip + sizeof(*ip);
                if ((void*)tcp + sizeof(*tcp) <= data_end) {
                    // AQUI MUDOU: Porta do NodePort (30080)
                    if (tcp->dest == ntohs(30080)) {
                        return XDP_DROP;
                    }
                }
            }
        }
    }
    return XDP_PASS;
}
"""

b = BPF(text=prog)
fn = b.load_func("xdp_drop_nodeport", BPF.XDP)
print(f"Protegendo Kubernetes NodePort 30080 na interface {device}...")
b.attach_xdp(device, fn, 0)

try:
    b.trace_print()
except KeyboardInterrupt:
    b.remove_xdp(device, 0)