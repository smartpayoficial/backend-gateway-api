import os
import shutil
import subprocess
import hashlib
from typing import Dict, Optional
from uuid import UUID
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Rutas base para el deployment
# Detectar si estamos en contenedor (con volumen montado) o en host
if os.path.exists('/host/smart-pay'):
    # Estamos en el contenedor con volumen montado
    BASE_BACKEND_PATH = "/host/smart-pay/backend-gateway-api"
    BASE_DB_PATH = "/host/smart-pay/db-smartpay"
    DEPLOYMENT_BASE_PATH = "/host/smart-pay/deployments"
else:
    # Estamos en el host
    BASE_BACKEND_PATH = "/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/backend-gateway-api"
    BASE_DB_PATH = "/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/db-smartpay"
    DEPLOYMENT_BASE_PATH = "/home/danielamg/Escritorio/trabajo/olimpo/smart-pay/deployments"


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
            store = await store_service.get_store(store_id)
            if store and store.nombre:
                # Normalizar el nombre para usarlo como directorio
                store_name = store.nombre.lower().replace(' ', '-')
                return store_name
            return str(store_id)
        except Exception as e:
            logger.error(f"Error obteniendo nombre de tienda {store_id}: {str(e)}")
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
            if os.path.exists(backend_path):
                shutil.rmtree(backend_path)
            
            # Copiar todo el directorio del backend
            shutil.copytree(BASE_BACKEND_PATH, backend_path)
            logger.info(f"Backend copiado exitosamente para store {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error copiando backend para store {store_id}: {str(e)}")
            return False
    
    def copy_db_files(self, store_id: UUID, db_path: str) -> bool:
        """Copia los archivos de la DB a la ruta de deployment."""
        try:
            if not os.path.exists(BASE_DB_PATH):
                logger.warning(f"Ruta base de DB no encontrada: {BASE_DB_PATH}")
                return False
                
            if os.path.exists(db_path):
                shutil.rmtree(db_path)
            
            # Copiar todo el directorio de la DB
            shutil.copytree(BASE_DB_PATH, db_path)
            logger.info(f"DB copiada exitosamente para store {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error copiando DB para store {store_id}: {str(e)}")
            return False
    
    def create_docker_compose(self, store_id: UUID, backend_path: str, ports: Dict[str, int]) -> bool:
        """Crea un docker-compose personalizado para la tienda."""
        try:
            docker_compose_content = f"""services:
  api-{store_id}:
    build:
      context: .
      dockerfile: docker/Dockerfile
    container_name: backend-api-{store_id}
    ports:
      - "{ports['backend_port']}:8000"
      - "{ports['websocket_port']}:8001"
    environment:
      HOST: 0.0.0.0
      PORT: 8000
      PYTHONUNBUFFERED: 1
      PYTHONPATH: /app
      SOCKETIO_ASYNC_MODE: asgi
      DB_API: http://smartpay-db-api-{store_id}:{ports['db_port']}
      USER_SVC_URL: http://smartpay-db-api-{store_id}:{ports['db_port']}
      REDIRECT_URI: https://smartpay-oficial.com:{ports['backend_port']}/api/v1/google/auth/callback
      CLIENT_SECRET: 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
      CLIENT_ID: 631597337466-dt7qitq7tg2022rhje5ib5sk0eua6t79.apps.googleusercontent.com
      SMTP_SERVER: smtp.gmail.com
      SMTP_PORT: 587
      SMTP_USERNAME: smartpay.noreply@gmail.com
      SMTP_PASSWORD: 'jgiz oqck snoj icwz'
      EMAIL_FROM: smartpay.noreply@gmail.com
      RESET_PASSWORD_BASE_URL: https://smartpay-oficial.com/reset-password
    volumes:
      - .:/app
      - ./logs:/app/logs
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

networks:
  smartpay-{store_id}:
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
            # Cambiar al directorio del backend
            original_cwd = os.getcwd()
            os.chdir(backend_path)
            
            # Ejecutar docker compose up -d
            result = subprocess.run(
                ["docker", "compose", "up", "-d"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            os.chdir(original_cwd)
            
            if result.returncode == 0:
                logger.info(f"Servicios iniciados exitosamente para store {store_id}")
                return True
            else:
                logger.error(f"Error iniciando servicios para store {store_id}: {result.stderr}")
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
            
            # Generar puertos y rutas
            ports = self.generate_ports(store_id)
            paths = await self.get_deployment_paths(store_id)
            
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
            if not self.create_docker_compose(store_id, paths["backend_path"], ports):
                raise Exception("Error creando docker-compose")
            
            # Iniciar servicios
            if not self.start_services(store_id, paths["backend_path"]):
                raise Exception("Error iniciando servicios")
            
            # Generar links con dominio smartpay-oficial.com en lugar de localhost
            back_link = f"https://smartpay-oficial.com:{ports['backend_port']}"
            db_link = f"https://smartpay-oficial.com:{ports['db_port']}" if db_copied else None
            
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
            self.cleanup_deployment(store_id)
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
                "back_link": f"https://smartpay-oficial.com:{ports['backend_port']}" if containers_running else None,
                "db_link": f"https://smartpay-oficial.com:{ports['db_port']}" if containers_running and db_exists else None
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
