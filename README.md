# CapitaSelectaSE
[![](https://github.com/ZhongXiLu/CapitaSelectaSE/workflows/Docker%20Compose%20CI/badge.svg)](https://github.com/ZhongXiLu/CapitaSelectaSE/actions?query=workflow%3A%22Docker+Compose+CI%22) [![](https://github.com/ZhongXiLu/CapitaSelectaSE/workflows/Minikube%20CI/badge.svg)](https://github.com/ZhongXiLu/CapitaSelectaSE/actions?query=workflow%3A%22Minikube+CI%22)


## How to Set Up

- Set up all the pods:
```bash
minikube addons enable heapster
minikube addons enable metrics-server
minikube start --memory=8192 --cpus=4 --vm-driver=none
kubectl create -f export
kubectl get pods
./runAllTests.sh
./setup.sh
```

- Scaling algorithm:
```bash
kubectl autoscale deployment order --cpu-percent=70 --min=1 --max=10
kubectl get hpa
```

- Load test (use `python3.7` or later with `requests` and `aiohttp` installed):
```bash
python test/load_test.py
```

## Build and Push Docker Images

```bash
curl -L https://github.com/kubernetes/kompose/releases/download/v1.18.0/kompose-linux-amd64 -o kompose
chmod +x kompose
docker login
kompose -f docker-compose-dev-kube.yml up
```
