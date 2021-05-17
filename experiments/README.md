# Experiments

## Preparation

1. Install openjdk (11.0.11), jmeter (5.4.1) on client machine.
```shell
apt install default-jre -y
wget https://apache.newfountain.nl//jmeter/binaries/apache-jmeter-5.4.1.tgz
tar zxvf apache-jmeter-5.4.1.tgz
export PATH="$PATH":/home/ubuntu/apache-jmeter-5.4.1/bin
jmeter --version
```

2. On worker nodes, install kubectl and reuse kubelet's kubeconfig.
```shell
# install kubectl
curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

# reuse kubelet's kubeconfig
mkdir .kube
sudo cp /var/lib/kubelet/kubeconfig .kube/
sudo chmod +r .kube/kubeconfig
export KUBECONFIG=/home/ubuntu/.kube/kubeconfig
kubectl get nodes
```

## 1. Auto-scaling Performance Test for a single Service

The scaling target we examine is Flight Service. We use JMeter to generate and feed loads. 

First, you need to have Kubernetes and Acme Air system up and running. Load Flight Service database by invoking `<ingress-ip>/flight/loader/load`

Let Flight Service flies with constant, moderate traffic demand for over 5 minutes. Then start adding loading. Record the time spent for this auto-scaling test. Flight Service is expected to bring replicas from 1 to 3.

```
jmeter -n -t qps_500.jmx -l log_500.jtl 
```

Now, we elaborate on how to determine the time range of each substage. Note the timestamp is a millisecond precision level due to this is how Kubernetes code is structured (see https://github.com/kubernetes/kubernetes/issues/81026).

- Stage 1: Scaling Decision Making

It starts with loading high-demand traffic and ends with ScalingReplicaSet event first occurs. The event source is Deployment controller.

```
$ kubectl get event -o wide | grep ScalingReplicaSet
15m    Normal    ScalingReplicaSet    deployment/acmeair-flightservice    deployment-controller    Scaled up replica set acmeair-flightservice-658c694974 to 3    15m    1    acmeair-flightservice.167da521845d4c03
$ kubectl get event acmeair-flightservice.167da521845d4c03 -ojson | jq .firstTimestamp
"2021-05-10T07:50:04Z"
```

- Stage 2: Pod-to-Node Binding

It starts after ScalingReplicaSet event and ends with Scheduled event first occurs. The event source is kube-scheduler.

```
$ kubectl get event -o wide | grep Scheduled                                      
33m    Normal    Scheduled    pod/acmeair-flightservice-658c694974-c7kk7    default-scheduler, default-scheduler-minikube   Successfully assigned default/acmeair-flightservice-658c694974-c7kk7 to minikube    33m    1    acmeair-flightservice-658c694974-c7kk7.167da5218c3fd97e
33m    Normal    Scheduled    pod/acmeair-flightservice-658c694974-dccl4    default-scheduler, default-scheduler-minikube   Successfully assigned default/acmeair-flightservice-658c694974-dccl4 to minikube    33m    1    acmeair-flightservice-658c694974-dccl4.167da5218b6bfa34
$ kubectl get event acmeair-flightservice-658c694974-c7kk7.167da5218c3fd97e -o json | jq .metadata.creationTimestamp
"2021-05-10T07:50:04Z"
```

- Stage 3: Container Initialization

It starts after Scheduled event and ends with Created event first occurs. The event source is kubelet.

```
$ kubectl get event -owide | grep Created                                         
48m    Normal    Created    pod/acmeair-flightservice-658c694974-c7kk7    spec.containers{acmeair-flightservice-java}   kubelet, minikube    Created container acmeair-flightservice-java    48m    1    acmeair-flightservice-658c694974-c7kk7.167da522211b3a5b
48m    Normal    Created    pod/acmeair-flightservice-658c694974-dccl4    spec.containers{acmeair-flightservice-java}   kubelet, minikube    Created container acmeair-flightservice-java    48m    1    acmeair-flightservice-658c694974-dccl4.167da5226b1564e2
$ kubectl get event acmeair-flightservice-658c694974-dccl4.167da5226b1564e2 -ojson | jq .firstTimestamp
"2021-05-10T07:50:08Z"
```

- Stage 4: Code Initialization

It starts after Created event and ends with Pods passing health probe and Ready condition.

```
$ kubectl get po acmeair-flightservice-658c694974-c7kk7 -ojson | jq .status.conditions
[
  {
    "lastProbeTime": null,
    "lastTransitionTime": "2021-05-10T07:50:04Z",
    "status": "True",
    "type": "Initialized"
  },
  {
    "lastProbeTime": null,
    "lastTransitionTime": "2021-05-10T07:50:26Z",
    "status": "True",
    "type": "Ready"
  },
  {
    "lastProbeTime": null,
    "lastTransitionTime": "2021-05-10T07:50:26Z",
    "status": "True",
    "type": "ContainersReady"
  },
  {
    "lastProbeTime": null,
    "lastTransitionTime": "2021-05-10T07:50:04Z",
    "status": "True",
    "type": "PodScheduled"
  }
]
```

## 2. Auto-scaling Performance Test for coordinated Services

## 3. Image Size

```
kubectl scale --replicas=3 deployment acmeair-flightservice
```

## 4. Container Runtime