# SmartLensOCR - Deployment Guide

## Deployment Options

### Option 1: Local Development (Recommended for Testing)

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
npm run dev
```

### Option 2: Docker Compose (Single Machine)

```bash
# From root directory
docker-compose up --build

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 3: Kubernetes (Production-Ready)

Create `k8s/backend-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: smartlensocr-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: smartlensocr-backend
  template:
    metadata:
      labels:
        app: smartlensocr-backend
    spec:
      containers:
      - name: backend
        image: your-registry/smartlensocr-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: gemini
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: smartlensocr-backend-service
spec:
  selector:
    app: smartlensocr-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f k8s/backend-deployment.yaml
```

### Option 4: Cloud Platforms

#### Vercel (Frontend)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
# VITE_API_URL=https://your-api.example.com
```

#### Railway (Backend)

1. Push code to GitHub
2. Connect repository on railway.app
3. Set environment variables
4. Deploy

#### Fly.io (Backend)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Initialize
flyctl apps create smartlensocr-backend

# Configure fly.toml
cat > fly.toml << EOF
app = "smartlensocr-backend"
primary_region = "sjc"

[build]
  dockerfile = "backend/Dockerfile"

[env]
  ENVIRONMENT = "production"

[deploy]
  release_command = "python models.py"

[http_service]
  internal_port = 8000
  force_https = true
EOF

# Deploy
flyctl deploy
```

#### AWS EC2

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-instance.com

# Install dependencies
sudo apt update
sudo apt install -y python3 python3-pip nodejs npm

# Clone repository
git clone your-repo.git
cd SmartLensOCR

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your keys

# Setup systemd service
sudo tee /etc/systemd/system/smartlensocr.service << EOF
[Unit]
Description=SmartLensOCR Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/SmartLensOCR/backend
ExecStart=/home/ubuntu/SmartLensOCR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable smartlensocr
sudo systemctl start smartlensocr

# Setup frontend
cd ../
npm install
npm run build

# Serve frontend with Nginx
sudo apt install -y nginx
sudo tee /etc/nginx/sites-available/smartlensocr << EOF
server {
    listen 80;
    server_name your-domain.com;
    
    root /home/ubuntu/SmartLensOCR/dist;
    
    location / {
        try_files $uri /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/smartlensocr /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Google Cloud Run

```bash
# Build and push backend image
gcloud builds submit --tag gcr.io/YOUR_PROJECT/smartlensocr-backend ./backend

# Deploy backend
gcloud run deploy smartlensocr-backend \
  --image gcr.io/YOUR_PROJECT/smartlensocr-backend \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --timeout 300 \
  --set-env-vars GEMINI_API_KEY=YOUR_KEY,ENVIRONMENT=production

# Deploy frontend to Cloud Storage
cd frontend
npm run build
gsutil -m cp -r dist/* gs://YOUR_BUCKET/

# Setup Cloud CDN and SSL
```

#### Azure App Service

```bash
# Create resource group
az group create --name smartlensocr --location eastus

# Create App Service Plan
az appservice plan create \
  --name smartlensocr-plan \
  --resource-group smartlensocr \
  --sku B1 --is-linux

# Deploy backend
az webapp create \
  --resource-group smartlensocr \
  --plan smartlensocr-plan \
  --name smartlensocr-api \
  --runtime "PYTHON:3.9"

# Configure deployment
az webapp deployment source config-zip \
  --resource-group smartlensocr \
  --name smartlensocr-api \
  --src backend.zip

# Deploy frontend to Static Web Apps
az staticwebapp create \
  --name smartlensocr-web \
  --resource-group smartlensocr \
  --source ./dist \
  --location westus2 \
  --app-location "dist"
```

## Production Checklist

### Before Deployment

- [ ] Update API endpoints in frontend
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure CORS origins
- [ ] Use strong database passwords
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up rate limiting
- [ ] Configure API authentication
- [ ] Add monitoring and logging
- [ ] Test all endpoints
- [ ] Database backups configured
- [ ] Error handling implemented
- [ ] Security headers enabled
- [ ] Input validation on all endpoints

### Environment Variables

```bash
# Backend .env
GEMINI_API_KEY=your_production_key
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
DATABASE_URL=postgresql://user:pass@host:5432/smartlensocr
FRONTEND_URL=https://yourdomain.com
CORS_ORIGINS=["https://yourdomain.com"]
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Frontend .env
VITE_API_URL=https://api.yourdomain.com
VITE_ENVIRONMENT=production
```

### Monitoring Setup

#### Application Performance Monitoring

```python
# Add to backend/main.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# Configure APM
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

#### Logging

```python
# Add to backend/main.py
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
```

#### Error Tracking

```python
# Add to backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if ENVIRONMENT == "production":
    sentry_sdk.init(
        dsn="https://your-sentry-dsn@sentry.io/project-id",
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
    )
```

### Security Hardening

#### API Security Headers

```python
# Add to backend/main.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

#### Rate Limiting

```python
# pip install slowapi

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/extract-text")
@limiter.limit("10/minute")
async def extract_text(request: Request, data: ExtractTextRequest):
    pass
```

#### Database Security

```python
# Use PostgreSQL instead of SQLite
# backend/requirements.txt
psycopg2-binary==2.9.6

# backend/config.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/smartlensocr"
)

# Connection pooling
from sqlalchemy.pool import QueuePool
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
)
```

### Scaling Considerations

1. **Horizontal Scaling**
   - Use load balancer (Nginx, AWS ALB)
   - Deploy multiple backend instances
   - Use shared database (PostgreSQL)
   - Implement session management (Redis)

2. **Caching**
   - Redis for processed images
   - CloudFront for static assets
   - Browser caching for frontend

3. **Database Optimization**
   - Add indexes on frequently queried columns
   - Implement query caching
   - Use read replicas for high traffic

4. **Cost Optimization**
   - Use image compression
   - Implement CDN for assets
   - Optimize API calls
   - Use serverless for bursty traffic

## Rollback Procedure

```bash
# Git rollback
git revert HEAD~1
git push origin main

# Docker rollback
docker pull your-registry/smartlensocr-backend:previous-tag
docker-compose down
docker-compose up -d

# Kubernetes rollback
kubectl rollout history deployment/smartlensocr-backend
kubectl rollout undo deployment/smartlensocr-backend --to-revision=2
```

## Backup & Disaster Recovery

```bash
# Database backup
pg_dump smartlensocr > backup-$(date +%Y%m%d-%H%M%S).sql

# Restore
psql smartlensocr < backup.sql

# Automated backup (cron)
0 2 * * * pg_dump smartlensocr | gzip > /backups/smartlensocr-$(date +\%Y\%m\%d).sql.gz
```

## Support & Troubleshooting

### Common Issues

1. **High API response times**
   - Check Gemini API quota
   - Implement caching
   - Optimize image processing

2. **Database connection errors**
   - Verify connection string
   - Check network connectivity
   - Scale database resources

3. **Memory leaks**
   - Monitor memory usage
   - Implement resource limits
   - Update dependencies

### Getting Help

- Check logs: `docker-compose logs -f`
- Monitor dashboard (Datadog, New Relic)
- Check error tracking (Sentry)
- Review metrics (Prometheus)

---

**Last Updated**: December 2024
**Version**: 1.0.0
