#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/var/www/html/bankapp
APP_USER=bankapp
VENV_DIR=${APP_DIR}/venv
SERVICE_NAME=bankapp
LOG_DIR=${APP_DIR}/logs
DB_FILE=${APP_DIR}/data/bankapp.sqlite3
GUNICORN_SOCKET=/run/${SERVICE_NAME}.sock
NGINX_CONF=/etc/nginx/sites-available/${SERVICE_NAME}.conf

echo "[DEPLOY] Starting automated deployment..."

mkdir -p ${LOG_DIR} ${APP_DIR}/data
chown -R ${APP_USER}:${APP_USER} ${APP_DIR}
chmod -R 750 ${APP_DIR}

echo "[DEPLOY] Syncing code..."
rsync -a --exclude 'venv' ./ ${APP_DIR}/

echo "[DEPLOY] Setting up Python environment..."
sudo -u ${APP_USER} bash <<EOF
python3 -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate
pip install --upgrade pip
pip install -r ${APP_DIR}/requirements.txt
EOF

echo "[DEPLOY] Applying database migrations..."
sudo -u ${APP_USER} bash <<EOF
source ${VENV_DIR}/bin/activate
python3 ${APP_DIR}/scripts/migrate.py
EOF

if [ ! -f "${DB_FILE}" ] || [ ! -s "${DB_FILE}" ]; then
    echo "[DEPLOY] Seeding database with initial users..."
    sudo -u ${APP_USER} bash <<EOF
source ${VENV_DIR}/bin/activate
python3 -c "from app import create_app; from core.database import init_db, get_db_session, seed_database; app=create_app(); init_db(app); from core.database import DB_SESSION; seed_database(DB_SESSION())"
EOF
else
    echo "[DEPLOY] Database exists, skipping seed."
fi

echo "[DEPLOY] Setting up systemd service..."
SERVICE_FILE=/etc/systemd/system/${SERVICE_NAME}.service
sudo bash -c "cat > ${SERVICE_FILE}" <<EOL
[Unit]
Description=Gunicorn instance to serve BankApp
After=network.target

[Service]
User=${APP_USER}
Group=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment="PATH=${VENV_DIR}/bin"
ExecStart=${VENV_DIR}/bin/gunicorn --workers 3 --bind unix:${GUNICORN_SOCKET} wsgi:app

[Install]
WantedBy=multi-user.target
EOL

echo "[DEPLOY] Reloading systemd and starting service..."
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}
sudo systemctl status ${SERVICE_NAME} --no-pager

echo "[DEPLOY] Setting up Nginx..."
sudo bash -c "cat > ${NGINX_CONF}" <<EOL
server {
    listen 80;
    server_name _;

    access_log ${LOG_DIR}/access.log;
    error_log ${LOG_DIR}/error.log;

    location / {
        proxy_pass http://unix:${GUNICORN_SOCKET};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias ${APP_DIR}/static/;
    }
}
EOL

sudo ln -sf ${NGINX_CONF} /etc/nginx/sites-enabled/${SERVICE_NAME}.conf
sudo nginx -t
sudo systemctl restart nginx

echo "[DEPLOY] Deployment complete! Application is running via Gunicorn + Nginx."
echo "Visit your server IP in the browser to access the app."
