import os
from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx
from app.auth.dependencies import get_current_user
from app.models.user import User
import io

router = APIRouter()

class AnalyticsResponse(BaseModel):
    customers: int
    devices: int
    payments: float
    vendors: int

@router.get("/date-range", response_model=AnalyticsResponse)
async def get_analytics_by_date_range(
    start_date: date = Query(..., description="Fecha inicial (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Fecha final (YYYY-MM-DD). Si no se proporciona, se usa la fecha actual")
):
    """
    Obtiene analytics por rango de fechas desde el servicio smartpay-db-api
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
        db_api_url = f"{DB_API_URL}/api/v1/analytics/date-range"
        
        # Parámetros para el servicio de DB
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        # Hacer la petición al servicio smartpay-db-api
        async with httpx.AsyncClient() as client:
            response = await client.get(db_api_url, params=params, timeout=30.0)
            
            if response.status_code == 200:
                data = response.json()
                return AnalyticsResponse(**data)
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
