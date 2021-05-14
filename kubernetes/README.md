# Kubernetes Setup

## AWS

Refer to [Get started tutorial](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html) for creating VM instances, with Ubuntu Server 18.04 LTS (HVM), SSD Volume Type for machine images.

We will have 1 Master + 3 Workers setup of Kubernetes. Besides, we will have a client machine operating outsides the Kubernetes cluster for feeding loads. The choice of machines are as follows:

| Role | Instance Type |
|---|---|
|Master|t3.small (2 vCPU, 2 GB)|
|Worker|t3.xlarge (4 vCPU, 16 GB)|
|Client|t3.small (2 vCPU, 2 GB)|

## Install Kubernetes

Read [Creating a cluster with kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/create-cluster-kubeadm/) for more information on how to create a Kubernetes cluster. The following is a brief summary. SSH to the instance and login as 'ubuntu' using the key specified at launch.

1. Install kubeadm, kubelet, kubectl across all nodes. Besides, pay attention to the following points:
    - Swap disabled. You MUST disable swap in order for the kubelet to work properly. You can do that by `swapoff -a`.
    - [Letting iptables see bridged traffic](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/#letting-iptables-see-bridged-traffic).
    - Choose one container runtime (eg. Docker) and pre-install it.
2. Initialize control-plane node.
3. Install a Pod network add-on.
4. Join worker nodes.

## Install Ingress Controller

Read [Installation Guide](https://kubernetes.github.io/ingress-nginx/deploy/#using-helm) for installing Nginx Ingress Controller via Helm v3.0. Also read [Helm](https://helm.sh/docs/intro/install/) for how to install Helm. After that, you run the following commands on your master nodes:

Note that you need to delete ValidatingWebhookConfiguration due to this [issue](https://github.com/kubernetes/ingress-nginx/issues/5401).

```
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx
```

## Install Prometheus System

1. Apply Prometheus prerequisite YAML first

```
kubectl apply -R -f prometheus-prerequisite
```

2. Apply Prometheus operator YAML

```
kubectl apply -R -f prometheus-operator
```

3. Apply Prometheus adapter YAML

Note that you need to generate some necessary certs for serving HTTPS traffic first (see [gencerts.sh](https://github.com/kubernetes-sigs/prometheus-adapter/tree/master/deploy)). Run `sh gencerts.sh` and ddd the generated YAML file `cm-adapter-serving-certs.yaml` to the prometheus-adapter folder.

Then, apply Prometheus adapter YAML.

```
kubectl apply -R -f prometheus-adapter
```

## Install Acme Air

1. Install Acme Air components, MongoDB and Ingress

```
kubectl apply -R -f acmeair
```

2. If you want to enable qps-based HPA, apply the HPA YAML separately.

```
kubectl apply -R -f hpa
```


