# Django-React-k8s

A three-tier College app deployed on Kubernetes.

```
Browser -> Nginx + React (college-frontend) -> Django API (college-app) -> MongoDB replica set
```

| Tier | Tech | Port |
| --- | --- | --- |
| Frontend | React 19, Vite, Nginx | 80 |
| Backend | Python 3.12, Django 5.2, Gunicorn | 8090 |
| Database | MongoDB 7 (3-replica StatefulSet) | 27017 |

This is the Python version of the earlier Java (Spring Boot) backend. The API is compatible: `GET /students` returns `id`, `name`, `age`, `city`.

## API

| Method | Path | What it does |
| --- | --- | --- |
| GET | `/students` | List all students |
| POST | `/students` | Add a student (`name`, `age`, `city`) |
| GET | `/students/<id>` | Get one student |
| PUT | `/students/<id>` | Update a student |
| DELETE | `/students/<id>` | Remove a student |
| GET | `/health` | Liveness probe |
| GET | `/health/ready` | Readiness probe (pings MongoDB) |

## Run locally

Backend (needs a MongoDB on localhost:27017):

```bash
cd college-app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py seed            # optional sample data
python manage.py runserver 8090
```

Frontend (in another terminal):

```bash
cd college-frontend
npm install
npm run dev                      # http://localhost:5173, /students is proxied to :8090
```

## Run with Docker Compose (one machine)

```bash
docker compose up -d --build
docker compose exec college-svc python manage.py seed
```

Open `http://<machine-ip>/`. On EC2, allow inbound port 80 in the security group.

## Deploy on Kubernetes

1. Build and push the images (change the Docker Hub username if needed):

```bash
docker build -t imran5152/college-app-django:v1 college-app
docker build -t imran5152/college-frontend-k8s:v2 college-frontend
docker push imran5152/college-app-django:v1
docker push imran5152/college-frontend-k8s:v2
```

2. Create the Django secret key (not stored in Git):

```bash
kubectl create secret generic django-secret \
  --from-literal=DJANGO_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')"
```

3. Start MongoDB and initialise the replica set once:

```bash
kubectl apply -f k8s/sts-svc.yaml -f k8s/sts.yaml
kubectl rollout status statefulset/mongodb

kubectl exec mongodb-0 -- mongosh --eval 'rs.initiate({_id:"rs0",members:[
  {_id:0,host:"mongodb-0.mongodb:27017"},
  {_id:1,host:"mongodb-1.mongodb:27017"},
  {_id:2,host:"mongodb-2.mongodb:27017"}]})'
```

4. Deploy the app:

```bash
kubectl apply -f k8s/configmap.yaml -f k8s/django-deploy.yml -f k8s/django-svc.yml \
              -f k8s/react-deploy.yml -f k8s/react-svc.yml
kubectl rollout status deployment/college-app
kubectl exec deploy/college-app -- python manage.py seed   # optional sample data
```

5. Get the public address:

```bash
kubectl get svc college-frontend-service    # EXTERNAL-IP (or hostname) column
```
## Project Screenshots

### Django Backend API

![Django Backend API](screenshots/WhatsApp%20Image%202026-09-24%20at%205.49.32%20PM.jpeg)

### MongoDB Database

![MongoDB Database](screenshots/WhatsApp%20Image%202026-09-24%20at%205.49.33%20PM.jpeg)

### Kubernetes Deployment

![Kubernetes Deployment](screenshots/WhatsApp%20Image%202026-09-24%20at%205.49.33%20PM1.jpeg)

## Troubleshooting

- Pods `college-app` stay `0/1 Ready`: the MongoDB replica set is not initialised yet (step 3), so `/health/ready` fails.
- `kubectl logs deploy/college-app` shows Django and Gunicorn output.
- Browser shows "Can't reach the students API": check `kubectl get svc college-svc` and the pod logs.
