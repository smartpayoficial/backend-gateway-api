import os
import shutil
import subprocess
import hashlib
from typing import Dict, Optional
from uuid import UUID
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)

# ---- Configuración dinámica de rutas ----
# Directorio donde se encuentra este archivo (…/backend-gateway-api/app/services)
PROJECT_ROOT = Path(__file__).resolve().parent.parent  # …/backend-gateway-api

# Permitir sobre-escritura vía variables de entorno para flexibilidad
BASE_BACKEND_PATH: Path = Path(os.getenv("SMARTPAY_BACKEND_PATH", PROJECT_ROOT))
BASE_DB_PATH: Path = Path(os.getenv("SMARTPAY_DB_PATH", PROJECT_ROOT.parent / "db-smartpay"))

# Colocamos los deployments fuera del árbol del código por defecto
DEPLOYMENT_BASE_PATH: Path = Path(
    os.getenv("SMARTPAY_DEPLOY_PATH", PROJECT_ROOT.parent / "deployments")
)

# Aseguramos que las rutas existan o las creamos cuando sea necesario




class DeploymentService:
    """Servicio para manejar el deployment automático de tiendas."""
    
    def __init__(self):
        self.ensure_deployment_directory()
    
    def ensure_deployment_directory(self):
        """Asegura que el directorio base de deployments existe."""
        Path(DEPLOYMENT_BASE_PATH).mkdir(parents=True, exist_ok=True)
    
    def generate_ports(self, store_id: UUID) -> Dict[str, int]:
        """Genera puertos únicos basados en el store_id."""
        # Usar hash del store_id para generar puertos únicos
        store_hash = int(hashlib.md5(str(store_id).encode()).hexdigest()[:8], 16)
        base_port = 9000 + (store_hash % 1000)
        
        return {
            "backend_port": base_port,
            "websocket_port": base_port + 1,
            "db_port": base_port + 2
        }
    
    async def get_store_name(self, store_id: UUID) -> str:
        """Obtiene el nombre de la tienda para usarlo en las rutas de deployment."""
        try:
            from app.services import store as store_service
            logger.info(f"Obteniendo tienda con ID: {store_id}")
            store = await store_service.get_store(store_id)
            logger.info(f"Tienda obtenida: {store}")
            logger.info(f"Tipo de tienda: {type(store)}")
            
            if store:
                # Manejar tanto objetos como diccionarios
                if hasattr(store, 'nombre'):
                    # Es un objeto con atributos
                    logger.info("La tienda es un objeto con atributos")
                    nombre = store.nombre
                    logger.info(f"Nombre obtenido: {nombre}")
                elif isinstance(store, dict) and 'nombre' in store:
                    # Es un diccionario
                    logger.info("La tienda es un diccionario")
                    nombre = store['nombre']
                    logger.info(f"Nombre obtenido: {nombre}")
                else:
                    # No se pudo obtener el nombre
                    logger.warning(f"No se pudo obtener el nombre de la tienda {store_id}")
                    logger.info(f"Contenido de la tienda: {store}")
                    return str(store_id)
                
                # Normalizar el nombre para usarlo como directorio
                store_name = nombre.lower().replace(' ', '-')
                logger.info(f"Nombre normalizado: {store_name}")
                return store_name
            logger.warning(f"No se encontró la tienda con ID: {store_id}")
            return str(store_id)
        except Exception as e:
            logger.error(f"Error obteniendo nombre de tienda {store_id}: {str(e)}", exc_info=True)
            return str(store_id)
    
    async def get_deployment_paths(self, store_id: UUID) -> Dict[str, str]:
        """Obtiene las rutas de deployment para una tienda."""
        store_name = await self.get_store_name(store_id)
        return {
            "backend_path": f"{DEPLOYMENT_BASE_PATH}/{store_name}/backend-gateway-api-{store_id}",
            "db_path": f"{DEPLOYMENT_BASE_PATH}/{store_name}/db-smartpay-{store_id}"
        }
    
    def copy_backend_files(self, store_id: UUID, backend_path: str) -> bool:
        """Copia los archivos del backend a la ruta de deployment."""
        try:
            backend_dir = Path(backend_path)
            if backend_dir.exists():
                shutil.rmtree(backend_dir)
            backend_dir.mkdir(parents=True, exist_ok=True)

            # Copiar contenido excluyendo el directorio de deployments
            for item in BASE_BACKEND_PATH.iterdir():
                if item.name == "deployments":
                    continue  # evitar recursión infinita
                dest = backend_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, dest, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, dest)
            logger.info(f"Backend copiado exitosamente para store {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error copiando backend para store {store_id}: {str(e)}")
            return False
    
    def copy_db_files(self, store_id: UUID, db_path: str) -> bool:
        """Copia los archivos de la DB a la ruta de deployment."""
        try:
            base_db_dir = Path(BASE_DB_PATH)
            target_db_dir = Path(db_path)
            if not base_db_dir.exists():
                logger.warning(f"Ruta base de DB no encontrada: {base_db_dir}")
                return False

            if target_db_dir.exists():
                shutil.rmtree(target_db_dir)

            shutil.copytree(base_db_dir, target_db_dir)
            logger.info(f"DB copiada exitosamente para store {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error copiando DB para store {store_id}: {str(e)}")
            return False
    
    async def create_docker_compose(self, store_id: UUID, backend_path: str, ports: Dict[str, int]) -> bool:
        """Crea un docker-compose personalizado para la tienda con integración Traefik."""
        try:
            # Obtener el nombre de la tienda para usar en las rutas
            store_name = await self.get_store_name(store_id)
            
            docker_compose_content = f"""services:
  api-{store_id}:
    image: docker-api
    # No build context needed as we're using the existing image
    container_name: backend-api-{store_id}
    expose:
      - "8000"
      - "8001"
    environment:
      HOST: 0.0.0.0
      PORT: 8000
      PYTHONUNBUFFERED: 1
      PYTHONPATH: /app
      SOCKETIO_ASYNC_MODE: asgi
      DB_API: http://smartpay-db-api-{store_id}:8002
      USER_SVC_URL: http://smartpay-db-api-{store_id}:8002
      REDIRECT_URI: https://{store_name}.smartpay-oficial.com/api/v1/google/auth/callback
      CLIENT_SECRET: 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
      CLIENT_ID: 631597337466-dt7qitq7tg2022rhje5ib5sk0eua6t79.apps.googleusercontent.com
      SMTP_SERVER: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USERNAME: smartpay.noreply@gmail.com
      SMTP_PASSWORD: 'jgiz oqck snoj icwz'
      EMAIL_FROM: smartpay.noreply@gmail.com
      RESET_PASSWORD_BASE_URL: https://{store_name}.smartpay-oficial.com/reset-password
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.{store_name}.rule=Host(`{store_name}.smartpay-oficial.com`)"
      - "traefik.http.routers.{store_name}.entrypoints=https"
      - "traefik.http.routers.{store_name}.tls=true"
      - "traefik.http.routers.{store_name}.tls.certresolver=letsencrypt"
      - "traefik.http.services.{store_name}.loadbalancer.server.port=8000"
      # WebSocket configuration
      - "traefik.http.routers.{store_name}-ws.rule=Host(`{store_name}.smartpay-oficial.com`) && PathPrefix(`/ws`)"
      - "traefik.http.routers.{store_name}-ws.entrypoints=https"
      - "traefik.http.routers.{store_name}-ws.tls=true"
      - "traefik.http.routers.{store_name}-ws.tls.certresolver=letsencrypt"
      - "traefik.http.services.{store_name}-ws.loadbalancer.server.port=8001"
    # No need to mount volumes as we're using the existing image
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-use-colors"]
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"
    sysctls:
      - net.core.somaxconn=65535
    ulimits:
      nofile:
        soft: 65535
        hard: 65535
    networks:
      - smartpay-{store_id}
      - traefik-public

  smartpay-db-api-{store_id}:
    image: smartpay-db-api
    container_name: smartpay-db-api-{store_id}
    expose:
      - "8002"
    environment:
      HOST: 0.0.0.0
      PORT: 8002
      PYTHONUNBUFFERED: 1
      PYTHONPATH: /app
      WEB_APP_VERSION: "0.1.0"
      WEP_APP_TITLE: smartpay-db
      WEP_APP_DESCRIPTION: Database service for SmartPay
      ENVIRONMENT: prod
      POSTGRES_DATABASE_URL: postgres://postgres:postgres@postgres-{store_id}:5432/smartpay
      DEFAULT_DATA: "False"
      DB_HOST: postgres-{store_id}
      DB_PORT: "5432"
      DB_NAME: smartpay
      DB_USER: postgres
      DB_PASSWORD: postgres
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.db-{store_name}.rule=Host(`db-{store_name}.smartpay-oficial.com`)"
      - "traefik.http.routers.db-{store_name}.entrypoints=https"
      - "traefik.http.routers.db-{store_name}.tls=true"
      - "traefik.http.routers.db-{store_name}.tls.certresolver=letsencrypt"
      - "traefik.http.services.db-{store_name}.loadbalancer.server.port=8002"
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002", "--no-use-colors"]
    restart: unless-stopped
    networks:
      - smartpay-{store_id}
      - traefik-public
      - database_network

  postgres-{store_id}:
    image: postgres:12
    container_name: postgres-{store_id}
    environment:
      POSTGRES_DB: smartpay
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data_{store_id}:/var/lib/postgresql/data
    ports:
      - "{db_port}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - database_network
      - smartpay-{store_id}

networks:
  smartpay-{store_id}:
    driver: bridge
  traefik-public:
    external: true
  database_network:
    driver: bridge
"""
            
            docker_compose_path = os.path.join(backend_path, "docker-compose.yml")
            with open(docker_compose_path, "w") as f:
                f.write(docker_compose_content)
            
            logger.info(f"Docker compose creado para store {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando docker-compose para store {store_id}: {str(e)}")
            return False
    
    def start_services(self, store_id: UUID, backend_path: str) -> bool:
        """Inicia los servicios Docker para la tienda."""
        try:
            # Registrar información detallada para depuración
            logger.info(f"Iniciando servicios para store_id: {store_id}, tipo: {type(store_id)}")
            logger.info(f"Backend path: {backend_path}")
            
            # Verificar que el directorio existe
            if not os.path.exists(backend_path):
                logger.error(f"El directorio {backend_path} no existe")
                return False
                
            # Verificar que el docker-compose.yml existe
            docker_compose_path = os.path.join(backend_path, "docker-compose.yml")
            if not os.path.exists(docker_compose_path):
                logger.error(f"El archivo docker-compose.yml no existe en {backend_path}")
                return False
            
            # Cambiar al directorio del backend
            original_cwd = os.getcwd()
            logger.info(f"Directorio actual antes de cambiar: {original_cwd}")
            os.chdir(backend_path)
            logger.info(f"Cambiado al directorio: {backend_path}")
            
            # Intentar con docker-compose primero, luego con docker compose
            commands_to_try = [
                ["docker-compose", "up", "-d"],
                ["docker", "compose", "up", "-d"]
            ]
            
            result = None
            for cmd in commands_to_try:
                try:
                    logger.info(f"Intentando ejecutar comando: {' '.join(cmd)}")
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=300  # 5 minutos timeout
                    )
                    logger.info(f"Resultado del comando: código {result.returncode}")
                    if result.returncode == 0:
                        logger.info(f"Comando ejecutado exitosamente: {' '.join(cmd)}")
                        break
                    else:
                        logger.warning(f"Comando {' '.join(cmd)} falló: {result.stderr}")
                except FileNotFoundError:
                    logger.warning(f"Comando {cmd[0]} no encontrado")
                    continue
            
            os.chdir(original_cwd)
            
            if result and result.returncode == 0:
                logger.info(f"Servicios iniciados exitosamente para store {store_id}")
                return True
            else:
                error_msg = result.stderr if result else "Ningún comando docker disponible"
                logger.error(f"Error iniciando servicios para store {store_id}: {error_msg}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout iniciando servicios para store {store_id}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado iniciando servicios para store {store_id}: {str(e)}")
            return False
        finally:
            # Asegurar que volvemos al directorio original
            try:
                os.chdir(original_cwd)
            except:
                pass
    
    async def cleanup_deployment(self, store_id: UUID):
        """Limpia los archivos de deployment en caso de error."""
        try:
            paths = await self.get_deployment_paths(store_id)
            for path in paths.values():
                if os.path.exists(path):
                    shutil.rmtree(path)
            logger.info(f"Cleanup completado para store {store_id}")
        except Exception as e:
            logger.error(f"Error en cleanup para store {store_id}: {str(e)}")
    
    async def deploy_store(self, store_id: UUID) -> Optional[Dict[str, any]]:
        """
        Despliega una tienda completa con backend y DB.
        
        Args:
            store_id: ID de la tienda a desplegar
            
        Returns:
            Dict con información del deployment o None si falla
        """
        try:
            logger.info(f"Iniciando deployment para store {store_id}")
            
            # Añadir registro detallado para depuración
            logger.info(f"Tipo de store_id: {type(store_id)}")
            
            # Generar puertos y rutas
            logger.info("Generando puertos para la tienda")
            ports = self.generate_ports(store_id)
            logger.info(f"Puertos generados: {ports}")
            
            logger.info("Obteniendo rutas de deployment")
            paths = await self.get_deployment_paths(store_id)
            logger.info(f"Rutas de deployment: {paths}")
            
            # Crear directorio base con el nombre de la tienda si no existe
            store_name = await self.get_store_name(store_id)
            store_dir = f"{DEPLOYMENT_BASE_PATH}/{store_name}"
            Path(store_dir).mkdir(parents=True, exist_ok=True)
            
            # Copiar archivos del backend
            if not self.copy_backend_files(store_id, paths["backend_path"]):
                raise Exception("Error copiando archivos del backend")
            
            # Copiar archivos de la DB (opcional, puede no existir aún)
            db_copied = self.copy_db_files(store_id, paths["db_path"])
            if not db_copied:
                logger.warning(f"No se pudo copiar la DB para store {store_id}, continuando sin ella")
            
            # Crear docker-compose personalizado
            if not await self.create_docker_compose(store_id, paths["backend_path"], ports):
                raise Exception("Error creando docker-compose")
            
            # Iniciar servicios
            if not self.start_services(store_id, paths["backend_path"]):
                raise Exception("Error iniciando servicios")
            
            # Generar links con subdominio para Traefik
            store_name = await self.get_store_name(store_id)
            back_link = f"https://{store_name}.smartpay-oficial.com"
            db_link = f"https://db-{store_name}.smartpay-oficial.com" if db_copied else None
            
            deployment_info = {
                "store_id": str(store_id),
                "back_link": back_link,
                "db_link": db_link,
                "ports": ports,
                "paths": paths,
                "status": "deployed"
            }
            
            logger.info(f"Deployment completado exitosamente para store {store_id}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Error en deployment para store {store_id}: {str(e)}")
            # Cleanup en caso de error
            await self.cleanup_deployment(store_id)
            return None


    async def stop_services(self, store_id: UUID) -> bool:
        """Detiene los servicios Docker para una tienda."""
        try:
            paths = await self.get_deployment_paths(store_id)
            backend_path = paths["backend_path"]
            
            if not os.path.exists(backend_path):
                logger.warning(f"No existe deployment para store {store_id}")
                return True
            
            # Cambiar al directorio del backend
            original_cwd = os.getcwd()
            os.chdir(backend_path)
            
            # Ejecutar docker compose down
            result = subprocess.run(
                ["docker", "compose", "down", "-v"],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutos timeout
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                logger.info(f"Servicios detenidos exitosamente para store {store_id}")
                return True
            else:
                logger.error(f"Error deteniendo servicios para store {store_id}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout deteniendo servicios para store {store_id}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado deteniendo servicios para store {store_id}: {str(e)}")
            return False
        finally:
            try:
                os.chdir(original_cwd)
            except:
                pass
    
    async def get_deployment_status(self, store_id: UUID) -> Dict[str, any]:
        """Obtiene el estado actual del deployment de una tienda."""
        try:
            paths = await self.get_deployment_paths(store_id)
            ports = self.generate_ports(store_id)
            
            backend_exists = os.path.exists(paths["backend_path"])
            db_exists = os.path.exists(paths["db_path"])
            
            # Verificar si los contenedores están corriendo
            containers_running = False
            if backend_exists:
                try:
                    result = subprocess.run(
                        ["docker", "ps", "--filter", f"name=backend-api-{store_id}", "--format", "{{.Names}}"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    containers_running = bool(result.stdout.strip())
                except:
                    pass
            
            status = "not_deployed"
            if backend_exists and containers_running:
                status = "running"
            elif backend_exists:
                status = "stopped"
            
            return {
                "store_id": str(store_id),
                "status": status,
                "backend_exists": backend_exists,
                "db_exists": db_exists,
                "containers_running": containers_running,
                "ports": ports,
                "paths": paths,
                "back_link": f"https://{await self.get_store_name(store_id)}.smartpay-oficial.com" if containers_running else None,
                "db_link": f"https://db-{await self.get_store_name(store_id)}.smartpay-oficial.com" if containers_running and db_exists else None
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado para store {store_id}: {str(e)}")
            return {
                "store_id": str(store_id),
                "status": "error",
                "error": str(e)
            }
    
    async def undeploy_store(self, store_id: UUID) -> bool:
        """Detiene y limpia completamente el deployment de una tienda."""
        try:
            logger.info(f"Iniciando undeploy para store {store_id}")
            
            # Detener servicios
            services_stopped = await self.stop_services(store_id)
            if not services_stopped:
                logger.warning(f"No se pudieron detener todos los servicios para store {store_id}")
            
            # Limpiar archivos
            await self.cleanup_deployment(store_id)
            
            logger.info(f"Undeploy completado para store {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error en undeploy para store {store_id}: {str(e)}")
            return False


# Instancia global del servicio
deployment_service = DeploymentService()
