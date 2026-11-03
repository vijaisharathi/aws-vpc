#!/usr/bin/env bash
# ==============================================================================
# Full Multi-Tier Application Deployment Script (Apache + Python Flask + RDS)
# Project: AWS VPC – Public and Private Subnet Demonstration
# ==============================================================================

set -euo pipefail

echo "=========================================================="
echo " Starting Full-Stack Application Deployment"
echo " Date: $(date)"
echo "=========================================================="

if [[ $EUID -ne 0 ]]; then
   echo "Error: This script must be run as root or with sudo privileges." >&2
   exit 1
fi

export DEBIAN_FRONTEND=noninteractive

# 1. Update APT Repositories & Install Core Packages
echo "[1/8] Updating package lists and installing runtimes..."
apt-get update -y
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    apache2 \
    libapache2-mod-php \
    php \
    php-cli \
    php-curl \
    mysql-client \
    curl \
    jq

# 2. Setup Dedicated Backend Directory & Python Virtual Environment
echo "[2/8] Setting up Python virtual environment in /opt/vpc-backend..."
mkdir -p /opt/vpc-backend
mkdir -p /var/log/vpc-app
mkdir -p /etc/vpc-app

python3 -m venv /opt/vpc-backend/venv
/opt/vpc-backend/venv/bin/pip install --upgrade pip

if [[ -f /opt/vpc-backend/requirements.txt ]]; then
    /opt/vpc-backend/venv/bin/pip install -r /opt/vpc-backend/requirements.txt
else
    /opt/vpc-backend/venv/bin/pip install \
        "Flask>=3.0.0,<3.1.0" \
        "gunicorn>=21.2.0,<22.0.0" \
        "boto3>=1.34.0,<1.35.0" \
        "pymysql>=1.1.0,<1.2.0" \
        "cryptography>=42.0.0,<43.0.0"
fi

# Set ownership of backend directory and log directory
chown -R www-data:www-data /opt/vpc-backend
chown -R www-data:www-data /var/log/vpc-app

# 3. Configure Systemd Service for Gunicorn / Flask
echo "[3/8] Configuring and enabling vpc-app systemd service..."
systemctl daemon-reload
systemctl enable vpc-app.service
systemctl restart vpc-app.service

# 4. Enable Apache Reverse Proxy Modules
echo "[4/8] Enabling Apache proxy and rewrite modules..."
a2enmod proxy
a2enmod proxy_http
a2enmod rewrite
a2enmod headers

# 5. Apply Apache VirtualHost Reverse Proxy Configuration
echo "[5/8] Applying Apache reverse proxy configuration..."
if [[ -f /etc/apache2/sites-available/000-default.conf.bak ]]; then
    cp /etc/apache2/sites-available/000-default.conf.bak /etc/apache2/sites-available/000-default.conf
fi
systemctl enable apache2

# 6. Apply Permissions on Static Web Root
echo "[6/8] Enforcing filesystem permissions on /var/www/html..."
mkdir -p /var/www/html/api
chown -R www-data:www-data /var/www/html
find /var/www/html -type d -exec chmod 755 {} \;
find /var/www/html -type f -exec chmod 644 {} \;

if [[ -f /var/www/html/network-config.json ]]; then
    chmod 640 /var/www/html/network-config.json
    chown root:www-data /var/www/html/network-config.json
fi

# 7. Test and Restart Web Services
echo "[7/8] Verifying Apache syntax and restarting services..."
apache2ctl configtest
systemctl restart apache2

# 8. Post-Deployment Verification
echo "[8/8] Performing local loopback sanity tests..."
sleep 2

# Check Flask service status
if systemctl is-active --quiet vpc-app; then
    echo " -> [OK] vpc-app systemd service is active."
else
    echo " -> [WARN] vpc-app systemd service is not active. Check /var/log/vpc-app/error.log."
fi

# Check Apache reverse proxy response
HEALTH_STATUS=$(curl -s -o /dev/null -w "%%{http_code}" http://127.0.0.1/api/health || echo "Failed")
echo " -> [API Health Check Response]: HTTP $HEALTH_STATUS"

echo "=========================================================="
echo " Deployment Complete!"
echo " Application URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 || echo 'localhost')/"
echo "=========================================================="
