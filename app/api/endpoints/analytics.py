import os
from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from app.auth.dependencies import get_current_user
from app.models.user import User
import io
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

class DailyAnalytics(BaseModel):
    date: date
    customers: int
    devices: int
    payments: float
    vendors: int

class AnalyticsResponse(BaseModel):
    total_customers: int
    total_devices: int
    total_payments: float
    total_vendors: int
    daily_data: List[DailyAnalytics]

@router.get("/date-range", response_model=AnalyticsResponse)
async def get_analytics_by_date_range(
    start_date: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha final (YYYY-MM-DD). Si no se proporciona, se usa la fecha actual")
):
    """
    Obtiene analytics por rango de fechas desde el servicio smartpay-db-api
    """
    try:
        logger.info(f"Iniciando solicitud de analytics para fechas: {start_date} a {end_date}")
        
        # Si no se proporciona end_date, usar la fecha actual
        if end_date is None:
            end_date = datetime.now().date()
        
        # Validar que start_date no sea mayor que end_date
        if start_date > end_date:
            error_msg = "La fecha de inicio no puede ser mayor que la fecha final"
            logger.error(error_msg)
            raise HTTPException(status_code=400, detail=error_msg)
            
        db_api = os.getenv('DB_API', 'http://smartpay-db-api:8002')
        if not db_api.startswith(('http://', 'https://')):
            error_msg = f"URL de DB API inválida: {db_api}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
            
        db_api_url = f"{db_api}/api/v1/analytics/date-range"
        params = {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()}
        
        logger.info(f"Conectando a DB API en: {db_api_url}")
        logger.info(f"Parámetros: {params}")
        
        # Configuración robusta del cliente HTTP
        timeout = httpx.Timeout(30.0, connect=60.0)
        transport = httpx.AsyncHTTPTransport(retries=3)
        
        async with httpx.AsyncClient(timeout=timeout, transport=transport) as client:
            try:
                response = await client.get(db_api_url, params=params)
                logger.info(f"Respuesta recibida - Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_msg = f"El servicio de analytics respondió con error: {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    raise HTTPException(status_code=502, detail=error_msg)
                
                data = response.json()
                logger.debug(f"Datos recibidos: {data}")
                
                # Validación estricta de la respuesta
                if 'daily_data' not in data or not isinstance(data['daily_data'], list):
                    error_msg = "La respuesta no contiene el array daily_data"
                    logger.error(f"{error_msg}. Respuesta: {data}")
                    raise HTTPException(status_code=502, detail=error_msg)
                    
                if not data['daily_data']:
                    return {
                        "total_customers": 0,
                        "total_devices": 0,
                        "total_payments": 0.0,
                        "total_vendors": 0,
                        "daily_data": []
                    }
                
                # Tomamos los datos del primer elemento de daily_data
                first_day = data['daily_data'][0]
                required_fields = ['customers', 'devices', 'payments', 'vendors']
                if not all(field in first_day for field in required_fields):
                    missing = [f for f in required_fields if f not in first_day]
                    error_msg = f"Faltan campos requeridos en daily_data: {missing}"
                    logger.error(f"{error_msg}. Primer día: {first_day}")
                    raise HTTPException(status_code=502, detail=error_msg)
                
                # Transformación a la estructura esperada
                return {
                    "total_customers": sum(day.get('customers', 0) for day in data['daily_data']),
                    "total_devices": sum(day.get('devices', 0) for day in data['daily_data']),
                    "total_payments": sum(day.get('payments', 0.0) for day in data['daily_data']),
                    "total_vendors": sum(day.get('vendors', 0) for day in data['daily_data']),
                    "daily_data": data['daily_data']
                }
                
            except httpx.RequestError as e:
                error_msg = f"Error de conexión con el servicio de analytics: {str(e)}"
                logger.error(error_msg)
                raise HTTPException(status_code=503, detail=error_msg)
            except ValueError as e:
                error_msg = f"Error procesando la respuesta JSON: {str(e)}"
                logger.error(f"{error_msg}. Response text: {response.text if 'response' in locals() else 'N/A'}")
                raise HTTPException(status_code=502, detail=error_msg)
            except Exception as e:
                error_msg = f"Error inesperado: {str(e)}"
                logger.error(error_msg, exc_info=True)
                raise HTTPException(status_code=500, detail=error_msg)
            
    except httpx.RequestError as e:
        error_msg = f"Error de conexión: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg)
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error inesperado: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/excel")
async def get_analytics_excel(
    start_date: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha final (YYYY-MM-DD). Si no se proporciona, se usa la fecha actual"),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene analytics en formato Excel desde el servicio smartpay-db-api
    """
    try:
        # Si no se proporciona end_date, usar la fecha actual
        if end_date is None:
            end_date = datetime.now().date()
        
        # Validar que start_date no sea mayor que end_date
        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="La fecha inicial no puede ser mayor que la fecha final"
            )
        
        # Construir la URL del servicio smartpay-db-api
        DB_API_URL = os.getenv("DB_API", "http://smartpay-db-api:8002")
        db_api_url = f"{DB_API_URL}/api/v1/analytics/excel"
        
        # Parámetros para el servicio de DB
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        # Hacer la petición al servicio smartpay-db-api
        async with httpx.AsyncClient() as client:
            response = await client.get(db_api_url, params=params, timeout=30.0)
            
            if response.status_code == 200:
                # Crear un nombre de archivo con las fechas
                filename = f"analytics_{start_date.isoformat()}_{end_date.isoformat()}.xlsx"
                
                # Retornar el archivo Excel como StreamingResponse
                return StreamingResponse(
                    io.BytesIO(response.content),
                    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f"attachment; filename={filename}"}
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error en el servicio de base de datos: {response.text}"
                )
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error de conexión con el servicio de base de datos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )
