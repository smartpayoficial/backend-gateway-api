# Configuración de Traefik para SmartPay

Este directorio contiene la configuración necesaria para ejecutar Traefik como proxy inverso para el sistema SmartPay, permitiendo el acceso a los subdominios de cada tienda.

## Archivos incluidos

- `docker-compose.yml`: Configuración de Traefik para Docker Compose
- `acme.json`: Archivo para almacenar certificados SSL (debe tener permisos 600)

## Requisitos

- Docker y Docker Compose instalados
- Red `traefik-public` creada en Docker
- Certificados SSL en `/etc/ssl/smartpay/`

## Instalación en VPS

1. Clonar este repositorio en la VPS:
   ```bash
   git clone <repositorio> /home/smartpayvps/backend-gateway-api
   ```

2. Crear la red de Docker si no existe:
   ```bash
   docker network create traefik-public || echo "La red ya existe"
   ```

3. Asegurar que el archivo acme.json tenga los permisos correctos:
   ```bash
   chmod 600 /home/smartpayvps/backend-gateway-api/traefik/acme.json
   ```

4. Iniciar Traefik:
   ```bash
   cd /home/smartpayvps/backend-gateway-api/traefik
   docker-compose up -d
   ```

## Verificación

Para verificar que Traefik está funcionando correctamente:

1. Comprobar que el contenedor está en ejecución:
   ```bash
   docker ps | grep traefik
   ```

2. Acceder al dashboard de Traefik:
   ```
   http://[IP-VPS]:8080/dashboard/
   ```

3. Verificar que los subdominios están funcionando:
   ```
   https://[nombre-tienda].smartpay-oficial.com/docs
   ```

## Configuración DNS

Para que los subdominios funcionen correctamente, es necesario configurar un registro DNS wildcard:

- Tipo: `A` o `CNAME`
- Nombre: `*.smartpay-oficial.com`
- Valor: IP de la VPS o dominio principal

## Integración con deployments

Este sistema de Traefik se integra automáticamente con los deployments de tiendas gracias a las etiquetas de Docker configuradas en el servicio de deployment.
