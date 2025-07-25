# Implementación de Traefik para SmartPay VPS

Esta guía explica cómo implementar Traefik como reverse proxy para gestionar automáticamente los deployments de tiendas en SmartPay.

## Beneficios de esta implementación

1. **URLs limpias y profesionales**: Cada tienda tendrá su propio subdominio (`tienda1.smartpay-oficial.com`)
2. **Gestión automática de SSL/TLS**: Traefik obtiene y renueva certificados automáticamente
3. **Enrutamiento dinámico**: No es necesario modificar configuraciones al añadir nuevas tiendas
4. **Escalabilidad**: Fácil de escalar a cientos de tiendas sin cambios en la infraestructura
5. **Seguridad mejorada**: No es necesario exponer múltiples puertos

## Requisitos previos

- Acceso root al VPS
- Docker y Docker Compose instalados
- Dominio configurado (smartpay-oficial.com)
- Registro DNS wildcard (*.smartpay-oficial.com) apuntando a la IP del VPS

## Pasos de implementación

### 1. Configurar Traefik

1. Ejecutar el script de configuración:

```bash
chmod +x setup_traefik_vps.sh
./setup_traefik_vps.sh
```

Este script:
- Crea los directorios necesarios
- Configura los archivos de Traefik
- Crea la red Docker `traefik-public`
- Inicia el contenedor de Traefik

### 2. Verificar la instalación de Traefik

1. Acceder al dashboard: https://traefik.smartpay-oficial.com:8080
   - Usuario: admin
   - Contraseña: smartpay

2. Comprobar que Traefik está funcionando correctamente:

```bash
docker ps | grep traefik
```

### 3. Configuración DNS

Asegúrese de que tiene configurados los siguientes registros DNS:

1. Registro A wildcard para `*.smartpay-oficial.com` → IP del VPS
2. Registro A específico para `traefik.smartpay-oficial.com` → IP del VPS

### 4. Prueba de despliegue

Los cambios ya están implementados en el sistema de deployment. Para probar:

1. Desplegar una nueva tienda:

```bash
curl -X POST "https://smartpay-oficial.com/api/v1/stores/deploy" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "tiendaprueba",
    "country_id": "123e4567-e89b-12d3-a456-426614174000",
    "plan": "basic",
    "tokens_disponibles": 100
  }'
```

2. Verificar que la tienda es accesible en: `https://tiendaprueba.smartpay-oficial.com`

### 5. Migración de tiendas existentes

Para migrar tiendas existentes al nuevo sistema:

1. Obtener la lista de tiendas desplegadas
2. Para cada tienda, realizar un redeployment:

```bash
curl -X DELETE "https://smartpay-oficial.com/api/v1/stores/{store_id}/deploy"
curl -X POST "https://smartpay-oficial.com/api/v1/stores/{store_id}/deploy"
```

## Estructura de archivos

```
/home/smartpayvps/traefik/
├── docker-compose.yml
└── data/
    ├── traefik.yml
    ├── config.yml
    └── acme.json
```

## Solución de problemas

### Certificados SSL

Si hay problemas con los certificados:

```bash
docker logs traefik
```

### Problemas de conectividad

Verificar que los contenedores están en la red `traefik-public`:

```bash
docker network inspect traefik-public
```

### Reiniciar Traefik

```bash
cd /home/smartpayvps/traefik
docker-compose restart
```

## Mantenimiento

- Los certificados se renuevan automáticamente
- Actualizar Traefik:

```bash
cd /home/smartpayvps/traefik
docker-compose pull
docker-compose up -d
```

## Seguridad

- El dashboard está protegido con autenticación básica
- Considerar cambiar la contraseña del dashboard en producción
- Los certificados SSL se gestionan automáticamente

## Próximos pasos recomendados

1. Implementar monitoreo con Prometheus/Grafana
2. Configurar rate limiting para prevenir abusos
3. Implementar middleware para seguridad adicional (headers, WAF)
