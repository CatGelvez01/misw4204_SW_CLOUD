#!/bin/bash

# Script para actualizar IPs en .env
# Uso: ./update_ip.sh <file-server-ip> <web-server-ip>

if [ $# -ne 2 ]; then
    echo "Uso: $0 <file-server-ip> <web-server-ip>"
    echo "Ejemplo: $0 98.93.73.106 18.234.60.223"
    exit 1
fi

FILE_SERVER_IP=$1
WEB_SERVER_IP=$2

echo "Actualizando IPs..."
echo "File Server: $FILE_SERVER_IP"
echo "Web Server: $WEB_SERVER_IP"

# Ruta del repositorio
REPO_PATH="/home/ubuntu/misw4204_SW_CLOUD/anb-rising-stars"

# Actualizar .env
if [ -f "$REPO_PATH/.env" ]; then
    echo "Actualizando .env..."

    # Actualizar DATABASE_URL
    sed -i "s|postgresql://anb_user:\([^@]*\)@[^:]*:5432|postgresql://anb_user:\1@$FILE_SERVER_IP:5432|g" "$REPO_PATH/.env"

    # Actualizar REDIS_URL
    sed -i "s|redis://[^:]*:6379/0|redis://$FILE_SERVER_IP:6379/0|g" "$REPO_PATH/.env"

    # Actualizar CELERY_BROKER_URL
    sed -i "s|redis://[^:]*:6379/1|redis://$FILE_SERVER_IP:6379/1|g" "$REPO_PATH/.env"

    # Actualizar CELERY_RESULT_BACKEND
    sed -i "s|redis://[^:]*:6379/2|redis://$FILE_SERVER_IP:6379/2|g" "$REPO_PATH/.env"

    # Actualizar SERVER_URL (solo en Web Server)
    if grep -q "SERVER_URL" "$REPO_PATH/.env"; then
        sed -i "s|SERVER_URL=.*|SERVER_URL=http://$WEB_SERVER_IP|g" "$REPO_PATH/.env"
    else
        echo "SERVER_URL=http://$WEB_SERVER_IP" >> "$REPO_PATH/.env"
    fi

    echo "✓ .env actualizado"
else
    echo "✗ No se encontró .env en $REPO_PATH"
    exit 1
fi

# Mostrar cambios
echo ""
echo "Configuración actualizada:"
grep -E "DATABASE_URL|REDIS_URL|CELERY_BROKER_URL|CELERY_RESULT_BACKEND|SERVER_URL" "$REPO_PATH/.env"

echo ""
echo "✓ IPs actualizadas correctamente"

# Remount NFS
echo ""
echo "Remontando NFS..."
sudo umount /mnt/nfs 2>/dev/null || true
sudo mount -t nfs $FILE_SERVER_IP:/mnt/nfs /mnt/nfs
echo "$FILE_SERVER_IP:/mnt/nfs /mnt/nfs nfs defaults 0 0" | sudo tee -a /etc/fstab > /dev/null

echo "✓ NFS remontado"
echo ""
