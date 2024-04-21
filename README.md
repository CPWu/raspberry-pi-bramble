# Raspberry Pi Kubernetes Cluster (Bramble Cluster)

This will repository will be used to contain my approach and thoughts in written form as I build out a cluster of Raspberry Pis. Inspired by the work of [Jeff Geerling](https://www.youtube.com/c/JeffGeerling) and [Network Chuck](https://www.youtube.com/@NetworkChuck) to build my own Pi cluster and some other over ambitious ideas I have.

## Equipment

The following pieces of equipment was used in this build: 

1. 4x Raspberry Pi 4 8GB
2. 4x Raspberry Pi PoE+ HAT
3. UniFi Lite 8-Port Gigabit PoE+ Compliant Managed Switch
4. 6x Cat 6 Patch Cables (1 Feet)
5. Yahboom Raspberry Pi Cluster Case

Raspberry Pi 4's obtained through Adafruit, Pi-Shop and Ebay...

## Specs
16 ARMv7 CPU Cores
32 GB RAM
32 GB microSD flash-based storage
1 Gbps private network with PoE

## Build Log
"14.april: Ansible" 
Automated the bring-up of the Bramble Cluster using Ansible. Running `ansible-playbook ./playbooks/playbook.yml` will create bring-up cluster and place a kubeconfig in the playbook directory. Thereafter copy the k3sconfig to ~/.kube/config and you should be able to do `kubectl get nodes` from your local machine. Reminder to update to the IP address specified in the k3sconfig from 127.0.0.1 to 192.168.1.100.

## Feature's On my Mind
Under Construction

## FAQ

## References:
1. https://devopscube.com/node-exporter-kubernetes/
2. https://devopscube.com/setup-prometheus-monitoring-on-kubernetes/
3. https://man.ilayk.com/gist/kubernetes%20cloudflared%20deployment%20with%20podmonitor/
4. https://github.com/cloudflare/argo-tunnel-examples/blob/master/named-tunnel-k8s/cloudflared.yaml
5. https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/deploy-tunnels/deployment-guides/kubernetes/
