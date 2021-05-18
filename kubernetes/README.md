# Kubernetes Setup

## AWS

Refer to [Get started tutorial](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html) for creating VM instances, with Ubuntu Server 18.04 LTS (HVM), SSD Volume Type for machine images.

We will have 1 Master + 3 Workers setup of Kubernetes. Besides, we will have a client machine operating outsides the Kubernetes cluster for feeding loads. The choices of machines are as follows:

| Role | Instance Type |
|---|---|
|Master|t3.medium (2 vCPU, 4 GB)|
|Worker|t3.xlarge (4 vCPU, 16 GB)|
|Client|t3.medium (2 vCPU, 4 GB)|

## Install Kubernetes

Read [Deploying to AWS](https://kops.sigs.k8s.io/getting_started/aws/) for more information on how to create a Kubernetes cluster on AWS EC2. The following is a brief summary. SSH to the client machine and login as 'ubuntu' with your ssh key.

```
ssh -i <YOUR_KEY_PAIR>.cer ubutnu@<YOUR_EC2_PUBLIC_IPV4_DNS>
```

1. Install kops (v1.20.1), kubectl(v1.21.1), aws cli(1.18.69) on client machine.
```shell
# install kops
curl -Lo kops https://github.com/kubernetes/kops/releases/download/$(curl -s https://api.github.com/repos/kubernetes/kops/releases/latest | grep tag_name | cut -d '"' -f 4)/kops-linux-amd64
chmod +x ./kops
sudo mv ./kops /usr/local/bin/

# install kubectl
curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
chmod +x ./kubectl
sudo mv ./kubectl /usr/local/bin/kubectl

# install aws cli
sudo apt update
sudo apt install awscli -y
```   
2. On AWS IAM console, create user, usergroup with the name `kops`. Assign `kops` with full access (AdministratorAccess). Keep your Access key ID, Secret access key, then configure aws on your client machine.
```shell
$ aws configure
AWS Access Key ID [None]: xxxxxxx
AWS Secret Access Key [None]: xxxxxxxxxxxxxxxxx
Default region name [None]: eu-central-1
Default output format [None]:

$ aws iam list-users
{
    "Users": [
        {
            "Path": "/",
            "UserName": "kops",
            "UserId": "xxxxxxxx",
            "Arn": "arn:aws:iam::xxxxxx:user/kops",
            "CreateDate": "2021-04-14T18:36:40Z"
        }
    ]
}
```   
3. Configure DNS. On AWS Route53 console, create a private, hosted zone. In our example, we name it `huanggze.example.com`. Test your DNS setup:
```shell
$ dig ns huanggze.example.com
;; ANSWER SECTION:
huanggze.example.com.        172800  IN  NS  ns-1.<example-aws-dns>-1.net.
huanggze.example.com.        172800  IN  NS  ns-2.<example-aws-dns>-2.org.
huanggze.example.com.        172800  IN  NS  ns-3.<example-aws-dns>-3.com.
huanggze.example.com.        172800  IN  NS  ns-4.<example-aws-dns>-4.co.uk.
```  
4. Crete cluster State storage. In our example,we name it `huanggze-example-com-state-store`.
```shell
aws s3api create-bucket \
    --bucket huanggze-example-com-state-store \
    --region eu-central-1
```
5. Prepare cluster instance for creation. We will create in your existing VPC where the client is located.
```shell
export NAME=myfirstcluster.huanggze.example.com
export KOPS_STATE_STORE=s3://huanggze-example-com-state-store
export VPC_ID=<YOUR_VPC_ID>
export NETWORK_CIDR=<YOUR_VPC_CIDR>
export SUBNET_ID=<YOUR_SUBNET_ID>
export SUBNET_CIDR=<YOUR_SUBNET_CIDR>
export SUBNET_IDS=$SUBNET_ID

kops create cluster $NAME \
    --zones eu-central-1a \
    --networking cilium \
    --vpc=${VPC_ID} \
    --subnets=${SUBNET_IDS} \
    --node-count 3 \
    --node-size t3.xlarge \
    --master-size t3.medium \
    --dns private \
    --dry-run \
    -o yaml > $NAME.yaml
```
6. Customize your setup.
- [add additional policies](https://kops.sigs.k8s.io/iam_roles/#adding-additional-policies)
```json
 spec:
  additionalPolicies:
    master: |
      [
        {
          "Effect": "Allow",
          "Action": "*",
          "Resource": "*"
        }
      ]
    node: |
      [
        {
          "Effect": "Allow",
          "Action": "*",
          "Resource": "*"
        }
      ]
```
- increase log level for kubernetes control-plane components.
```json
spec:
  kubeControllerManager:
    logLevel: 9
  kubelet:
    logLevel: 9
  kubeScheduler:
    logLevel: 9
```
- choose docker as container runtime
```json
spec:
  containerRuntime: docker
```
- cilium in debug mode
```json
spec:
  networking:
    cilium:
      debug: true
```
7. Create your cluster
```shell
kops create -f myfirstcluster.huanggze.example.com.yaml
ssh-keygen
kops create secret --name myfirstcluster.huanggze.example.com sshpublickey admin -i ~/.ssh/id_rsa.pub
kops update cluster myfirstcluster.huanggze.example.com --yes
```
8. Export kubeconfig so that you can use kubectl on your client machine
```shell
kops export kubecfg --admin
```
9. Verify your cluster. It may take minutues to have your cluster up and running.
```shell
kubectl get nodes
```

## Install Ingress Controller

Read [Installation Guide](https://kubernetes.github.io/ingress-nginx/deploy/#aws) for installing Nginx Ingress Controller for aws.

```shell
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.46.0/deploy/static/provider/aws/deploy.yaml
```

## Install Prometheus System

1. Apply Prometheus YAML files:
```
git clone  https://github.com/huanggze/MScProject.git
cd MScProject/kubernetes
kubectl apply -f kube-prometheus/setup
kubectl apply -f kube-prometheus
```

2. Verify custom metrics endpoints
```shell
$ kubectl get apiservice v1beta2.custom.metrics.k8s.io
NAME                            SERVICE                         AVAILABLE   AGE
v1beta2.custom.metrics.k8s.io   monitoring/prometheus-adapter   True        9m1s

$ sudo apt install jq -y
$ kubectl get --raw "/apis/custom.metrics.k8s.io/v1beta2" | jq
{
  "kind": "APIResourceList",
  "apiVersion": "v1",
  "groupVersion": "custom.metrics.k8s.io/v1beta2",
  "resources": []
}
```

3. View prometheus console on your browser
```shell
$ kubectl get svc -n monitoring prometheus-k8s
NAME             TYPE           CLUSTER-IP      EXTERNAL-IP                                                                 PORT(S)          AGE
prometheus-k8s   LoadBalancer   100.62.135.64   xxxx.eu-central-1.elb.amazonaws.com   9090:30993/TCP   22m
```

Now you can see Prometheus console with the url http://xxxx.eu-central-1.elb.amazonaws.com:9090


## Install EFK for logging (Optional)

1. Install helm.
We will use [helm](https://helm.sh/docs/intro/install/#from-apt-debianubuntu) to install elasticsearch and kibana.
```shell
curl https://baltocdn.com/helm/signing.asc | sudo apt-key add -
sudo apt-get install apt-transport-https --yes
echo "deb https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```   
2. Install elasticsearch
```shell
kubectl create ns logging
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch --namespace logging --set service.type=LoadBalancer
```

Verify your ES cluster
```shell
$ kubectl get svc -n logging
NAME                            TYPE           CLUSTER-IP      EXTERNAL-IP                                                                  PORT(S)                         AGE
elasticsearch-master            LoadBalancer   100.56.73.190   xxxxx.eu-central-1.elb.amazonaws.com   9200:32657/TCP,9300:32616/TCP   7s

$ curl xxxxx.eu-central-1.elb.amazonaws.com:9200
{
  "name" : "elasticsearch-master-2",
  "cluster_name" : "elasticsearch",
  "cluster_uuid" : "oRRxyMQeQFmNWiin6HCaaA",
  "version" : {
    "number" : "7.12.1",
    "build_flavor" : "default",
    "build_type" : "docker",
    "build_hash" : "3186837139b9c6b6d23c3200870651f10d3343b7",
    "build_date" : "2021-04-20T20:56:39.040728659Z",
    "build_snapshot" : false,
    "lucene_version" : "8.8.0",
    "minimum_wire_compatibility_version" : "6.8.0",
    "minimum_index_compatibility_version" : "6.0.0-beta1"
  },
  "tagline" : "You Know, for Search"
}
```

To clear all es data:
```shell
curl -XDELETE xxxxx.eu-central-1.elb.amazonaws.com:9200/_all
```

3. Install kibana for browsing logs
```shell
helm install kibana elastic/kibana --namespace logging --set service.type=LoadBalancer,elasticsearchHosts="http://elasticsearch-master.logging:9200"
```

4. Install Fluentbit
We will deploy Fluentbit daemonset to collect kube-apiserver logs only.
```shell
cd /MScProject/kubernetes
kubectl apply -f /logging
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


