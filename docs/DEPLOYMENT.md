# Sentio 2.0 Deployment Guide

## Prerequisites

### System Requirements
- Python 3.9 or higher
- 4GB RAM minimum (8GB recommended)
- 10GB disk space
- PostgreSQL 13+ (optional, for persistence)
- Redis 6+ (optional, for caching)

### Required Services
- Market data provider API (Alpaca, Interactive Brokers, etc.)
- Stripe account (for billing, optional)
- SSL certificate (for production)

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/JamieT18/Sentio-2.0.git
cd Sentio-2.0
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Package
```bash
pip install -e .
```

### 5. Configuration

#### Create .env File
```bash
cp .env.example .env
```

#### Edit .env with Your Credentials
```env
# Market Data
MARKET_DATA_API_KEY=your_alpaca_api_key
MARKET_DATA_API_SECRET=your_alpaca_api_secret

# Database (optional)
DATABASE_URL=postgresql://user:password@localhost:5432/sentio

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password

# API Configuration
SECRET_KEY=generate_a_secure_random_key_here
API_HOST=0.0.0.0
API_PORT=8000

# Stripe (optional)
STRIPE_API_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Trading Configuration
TRADING_MODE=paper  # or 'live' for production
ENABLE_LIVE_TRADING=false
```

#### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. Database Setup (Optional)

If using PostgreSQL for persistence:

```bash
# Create database
createdb sentio

# Run migrations (if implemented)
# alembic upgrade head
```

### 7. Verify Installation
```bash
# Test package structure
python test_import.py

# Test CLI
sentio --help
```

## Running the System

### Development Mode

#### Start API Server
```bash
sentio api --host localhost --port 8000 --workers 1
```

#### Run Paper Trading
```bash
sentio paper AAPL MSFT GOOGL --initial-capital 100000
```

#### Analyze Symbol
```bash
sentio analyze AAPL
```

### Production Deployment

#### Using Uvicorn (Simple)
```bash
uvicorn sentio.ui.api:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Gunicorn + Uvicorn (Recommended)
```bash
gunicorn sentio.ui.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

#### Using Docker (Future)
```bash
# Build image
docker build -t sentio:2.0 .

# Run container
docker run -d \
  --name sentio \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env \
  sentio:2.0
```

## Systemd Service (Linux)

### Create Service File
```bash
sudo nano /etc/systemd/system/sentio.service
```

### Service Configuration
```ini
[Unit]
Description=Sentio 2.0 Trading System
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=sentio
Group=sentio
WorkingDirectory=/opt/sentio
Environment="PATH=/opt/sentio/venv/bin"
ExecStart=/opt/sentio/venv/bin/gunicorn \
  sentio.ui.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Enable and Start
```bash
sudo systemctl enable sentio
sudo systemctl start sentio
sudo systemctl status sentio
```

## Nginx Reverse Proxy

### Install Nginx
```bash
sudo apt install nginx
```

### Configure Site
```nginx
server {
    listen 80;
    server_name trading.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name trading.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/trading.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/trading.yourdomain.com/privkey.pem;
    
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
    
    # API Proxy
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }
    
    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/sentio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d trading.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

## Monitoring Setup

### Log Rotation
```bash
sudo nano /etc/logrotate.d/sentio
```

```
/opt/sentio/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 sentio sentio
    sharedscripts
    postrotate
        systemctl reload sentio > /dev/null 2>&1 || true
    endscript
}
```

### System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor logs
tail -f logs/sentio_*.log

# Monitor API
watch -n 5 curl -s http://localhost:8000/api/v1/health
```

## Backup Strategy

### Database Backup
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump sentio > /backups/sentio_$DATE.sql
find /backups -name "sentio_*.sql" -mtime +7 -delete
```

### Configuration Backup
```bash
# Backup configs
tar czf config_backup_$(date +%Y%m%d).tar.gz \
  .env config.json
```

## Performance Tuning

### PostgreSQL
```sql
-- Optimize for trading workload
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '4MB';
SELECT pg_reload_conf();
```

### Redis
```conf
# redis.conf
maxmemory 512mb
maxmemory-policy allkeys-lru
save ""
appendonly no
```

### API Server
- Use multiple workers (4-8 for production)
- Enable HTTP/2
- Use connection pooling
- Implement caching headers

## Security Hardening

### Firewall Configuration
```bash
# UFW
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### API Security
- Enable rate limiting
- Use JWT with short expiration
- Rotate API keys regularly
- Log all authentication attempts
- Implement IP whitelisting for admin

### Environment Security
- Never commit .env to git
- Use environment-specific configs
- Restrict file permissions
- Enable audit logging

## Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Find process
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

#### Database Connection Error
```bash
# Test connection
psql -h localhost -U sentio -d sentio

# Check service
sudo systemctl status postgresql
```

#### High Memory Usage
```bash
# Check memory
free -h

# Monitor processes
htop

# Restart service
sudo systemctl restart sentio
```

#### API Not Responding
```bash
# Check logs
journalctl -u sentio -n 100 -f

# Check service status
sudo systemctl status sentio

# Restart service
sudo systemctl restart sentio
```

## Maintenance

### Daily Tasks
- Monitor system logs
- Check API health endpoint
- Review trade history
- Verify circuit breaker status

### Weekly Tasks
- Review performance metrics
- Update market data
- Backup configuration
- Check disk space

### Monthly Tasks
- Update dependencies
- Review security logs
- Optimize database
- Test backup restoration

## Scaling

### Horizontal Scaling
```bash
# Run multiple instances behind load balancer
# Instance 1
sentio api --port 8001

# Instance 2
sentio api --port 8002

# Load balancer (HAProxy/Nginx)
# Distribute traffic across instances
```

### Database Scaling
- Read replicas for analysis queries
- Write master for trade execution
- Partitioning for historical data
- Regular vacuum and analyze

### Caching Strategy
- Redis for hot data
- API response caching
- Computed indicator caching
- Session management

## Production Checklist

### Before Launch
- [ ] All credentials configured
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Backup system tested
- [ ] Monitoring enabled
- [ ] Rate limiting configured
- [ ] Error tracking setup
- [ ] Log rotation configured
- [ ] Database optimized
- [ ] Load testing completed

### Live Trading Activation
- [ ] Paper trading tested thoroughly
- [ ] Risk limits configured
- [ ] Circuit breakers tested
- [ ] Stop-loss verified
- [ ] Position sizing validated
- [ ] Emergency contacts ready
- [ ] Rollback plan prepared

## Support

For issues or questions:
- GitHub Issues: https://github.com/JamieT18/Sentio-2.0/issues
- Documentation: https://github.com/JamieT18/Sentio-2.0/wiki
- Email: support@sentio-trading.com (if configured)

---

**Last Updated**: 2024
**Version**: 2.0.0
