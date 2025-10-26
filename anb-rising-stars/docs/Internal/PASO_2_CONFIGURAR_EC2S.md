# Paso 2: Configurar las 3 EC2s

## 1️⃣ FILE SERVER (PostgreSQL + NFS)

```bash
ssh -i tu-key.pem ubuntu@<file-server-ip>

# Actualizar
sudo apt update && sudo apt upgrade -y

# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Crear BD y usuario
sudo -u postgres psql << EOF
CREATE DATABASE anb_rising_stars;
CREATE USER anb_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE anb_rising_stars TO anb_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anb_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO anb_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO anb_user;
GRANT CREATE ON SCHEMA public TO anb_user;
EOF

# Permitir conexiones remotas
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" /etc/postgresql/*/main/postgresql.conf
echo "host    all             all             0.0.0.0/0               md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf
sudo systemctl restart postgresql

# Instalar Redis
sudo apt install redis-server redis-tools -y
sudo sed -i 's/bind 127.0.0.1/bind 0.0.0.0/' /etc/redis/redis.conf
sudo redis-cli CONFIG SET protected-mode no
sudo redis-cli CONFIG REWRITE
sudo systemctl restart redis-server

# Instalar NFS
sudo apt install nfs-kernel-server -y

# Crear directorios
sudo mkdir -p /mnt/nfs/{uploads,processed,assets}
sudo chmod 777 /mnt/nfs/{uploads,processed}
sudo chmod 755 /mnt/nfs/assets

# Configurar NFS
echo "/mnt/nfs/uploads    *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
echo "/mnt/nfs/processed  *(rw,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
echo "/mnt/nfs/assets     *(ro,sync,no_subtree_check,no_root_squash)" | sudo tee -a /etc/exports
sudo exportfs -a
sudo systemctl restart nfs-server
```

```bash
### Actualizar redis cuando EC2 se reinicia
sudo systemctl status nfs-server
sudo redis-cli CONFIG SET protected-mode no
sudo redis-cli CONFIG REWRITE
sudo systemctl restart redis-server
sudo systemctl status redis-server
```

---

## 2️⃣ WEB SERVER (FastAPI + Nginx)

```bash
ssh -i tu-key.pem ubuntu@<web-server-ip>

# Actualizar e instalar
sudo apt update && sudo apt upgrade -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip build-essential libpq-dev nginx nfs-common -y

# Clonar repo
cd /home/ubuntu
git clone https://github.com/CatGelvez01/misw4204_SW_CLOUD.git
cd misw4204_SW_CLOUD/anb-rising-stars

# Venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Crear .env

## Crear .env desde el template
cp .env.example .env

## Actualizar valores (reemplaza <FILE_SERVER_IP> y <PASSWORD> con los valores reales)
sed -i 's|postgresql://anb_user:anb_password@postgres|postgresql://anb_user:<PASSWORD>@<FILE_SERVER_IP>|g' .env
sed -i 's|redis://redis|redis://<FILE_SERVER_IP>|g' .env
sed -i 's|UPLOAD_DIR=/app/uploads|UPLOAD_DIR=/mnt/nfs/uploads|g' .env
sed -i 's|PROCESSED_DIR=/app/processed|PROCESSED_DIR=/mnt/nfs/processed|g' .env
sed -i 's|ENVIRONMENT=development|ENVIRONMENT=production|g' .env
sed -i 's|CORS_ORIGINS=\["http://localhost:3000", "http://localhost:8000"\]|CORS_ORIGINS=["http://<WEB_SERVER_IP>", "http://<WEB_SERVER_IP>:8000"]|g' .env

## Verificar que los cambios se aplicaron
cat .env | grep -E "DATABASE_URL|REDIS_URL|UPLOAD_DIR|ENVIRONMENT|CORS_ORIGINS"


# Montar NFS
sudo mkdir -p /mnt/nfs
sudo mount -t nfs <file-server-ip>:/mnt/nfs /mnt/nfs
echo "<file-server-ip>:/mnt/nfs /mnt/nfs nfs defaults 0 0" | sudo tee -a /etc/fstab

# Servicio FastAPI
sudo tee /etc/systemd/system/anb-backend.service > /dev/null << EOF
[Unit]
Description=ANB Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars
Environment="PATH=/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars/venv/bin"
EnvironmentFile=/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars/.env
ExecStart=/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable anb-backend
sudo systemctl start anb-backend

# Configurar Nginx
sudo tee /etc/nginx/sites-available/default > /dev/null << 'EOF'
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80 default_server;
    client_max_body_size 100M;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /uploads/ {
        alias /mnt/nfs/uploads/;
    }

    location /processed/ {
        alias /mnt/nfs/processed/;
    }
}
EOF

sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Actualizar IP cuando EC2 se reinicia
``` bash
cd /home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars
chmod +x scripts/update_ip.sh
./scripts/update_ip.sh 54.158.0.4 54.147.186.0
sudo mount -t nfs 54.158.0.4:/mnt/nfs /mnt/nfs
echo "54.158.0.4:/mnt/nfs /mnt/nfs nfs defaults 0 0" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload
sudo systemctl status anb-backend.service
sudo systemctl restart nginx

```
---

## 3️⃣ WORKER (Celery + FFmpeg)

```bash
ssh -i tu-key.pem ubuntu@<worker-ip>

# Actualizar e instalar
sudo apt update && sudo apt upgrade -y
sudo apt install ffmpeg -y
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip build-essential libpq-dev nginx nfs-common -y

# Clonar repo
cd /home/ubuntu
git clone https://github.com/CatGelvez01/misw4204_SW_CLOUD.git
cd misw4204_SW_CLOUD/anb-rising-stars

# Venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Montar NFS
sudo mkdir -p /mnt/nfs
sudo mount -t nfs <file-server-ip>:/mnt/nfs /mnt/nfs
echo "<file-server-ip>:/mnt/nfs /mnt/nfs nfs defaults 0 0" | sudo tee -a /etc/fstab

# Crear .env

## Crear .env desde el template
cp .env.example .env

## Actualizar valores (reemplaza <FILE_SERVER_IP> y <PASSWORD> con los valores reales)
sed -i 's|postgresql://anb_user:anb_password@postgres|postgresql://anb_user:<PASSWORD>@<FILE_SERVER_IP>|g' .env
sed -i 's|redis://redis|redis://<FILE_SERVER_IP>|g' .env
sed -i 's|UPLOAD_DIR=/app/uploads|UPLOAD_DIR=/mnt/nfs/uploads|g' .env
sed -i 's|PROCESSED_DIR=/app/processed|PROCESSED_DIR=/mnt/nfs/processed|g' .env
sed -i 's|ENVIRONMENT=development|ENVIRONMENT=production|g' .env

## Verificar que los cambios se aplicaron
cat .env | grep -E "DATABASE_URL|REDIS_URL|UPLOAD_DIR|ENVIRONMENT"


# Servicio Celery
sudo tee /etc/systemd/system/anb-celery-worker.service > /dev/null << EOF
[Unit]
Description=ANB Celery Worker
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars
Environment="PATH=/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars/venv/bin"
EnvironmentFile=/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars/.env
ExecStart=/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars/venv/bin/celery -A app.tasks.celery_app worker --loglevel=info --concurrency=1
Restart=always

[Install]
WantedBy=multi-user.target
EOF

export PATH="/usr/bin:$PATH"
/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars/venv/bin/celery -A app.tasks.celery_app worker --loglevel=info

sudo systemctl daemon-reload
sudo systemctl enable anb-celery-worker
sudo systemctl start anb-celery-worker
```

### Actualizar IP cuando EC2 se reinicia
``` bash
cd /home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars
chmod +x scripts/update_ip.sh
./scripts/update_ip.sh 54.158.0.4
sudo mount -t nfs 54.158.0.4:/mnt/nfs /mnt/nfs
echo "54.158.0.4:/mnt/nfs /mnt/nfs nfs defaults 0 0" | sudo tee -a /etc/fstab
sudo systemctl daemon-reload
sudo systemctl status anb-celery-worker.service
sudo systemctl restart anb-celery-worker.service
```


---

## ✅ VALIDACIÓN

```bash
# Desde Web Server
psql -h <file-server-ip> -U anb_user -d anb_rising_stars -c "SELECT 1"
redis-cli -h <redis-ip> ping
ls -la /mnt/nfs/

# Desde tu máquina
curl http://<web-server-ip>/
```
