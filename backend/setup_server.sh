#!/bin/bash
# Setup backend Manantiales Invest en Ubuntu 22.04
# Ejecutar como: sudo bash setup_server.sh

set -e
echo "=== Setup Manantiales Backend ==="

# 1. Dependencias del sistema
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib

# 2. Crear base de datos y usuario PostgreSQL
echo "--- Configurando PostgreSQL ---"
sudo -u postgres psql <<EOF
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'manantiales') THEN
    CREATE USER manantiales WITH PASSWORD 'manantiales123';
  END IF;
END
\$\$;

SELECT 'CREATE DATABASE manantiales_db OWNER manantiales'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'manantiales_db')\gexec
GRANT ALL PRIVILEGES ON DATABASE manantiales_db TO manantiales;
EOF

# 3. Crear virtualenv e instalar dependencias
echo "--- Instalando dependencias Python ---"
cd /var/www/manantiales-invest
python3 -m venv venv
./venv/bin/pip install --upgrade pip -q
./venv/bin/pip install -r backend/requirements.txt -q

echo "✅ Dependencias instaladas"

# 4. Crear servicio systemd
echo "--- Creando servicio systemd ---"
cat > /etc/systemd/system/manantiales-api.service <<SERVICE
[Unit]
Description=Manantiales Invest API
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/var/www/manantiales-invest
ExecStart=/var/www/manantiales-invest/venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3
Environment=PYTHONPATH=/var/www/manantiales-invest

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable manantiales-api
systemctl start manantiales-api

echo "✅ Servicio API iniciado en puerto 8000"

# 5. Configurar nginx como reverse proxy
echo "--- Configurando nginx ---"
cat > /etc/nginx/sites-available/manantiales <<NGINX
server {
    listen 80;
    server_name _;

    # API backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Frontend estático
    root /var/www/manantiales-invest;
    index manantiales-invest.html;

    location / {
        try_files \$uri \$uri/ =404;
    }
}
NGINX

nginx -t && systemctl reload nginx
echo "✅ Nginx configurado con proxy a /api/"

echo ""
echo "=== ¡Todo listo! ==="
echo "API corriendo en: http://localhost:8000/api/docs"
echo "Web corriendo en: http://192.168.100.155"
echo ""
echo "Credenciales admin por defecto:"
echo "  Email:    admin@manantiales.com"
echo "  Password: admin1234"
echo ""
echo "⚠️  Cambiá la contraseña del admin después del primer login."
