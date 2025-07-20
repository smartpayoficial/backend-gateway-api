#!/usr/bin/env python3
"""
Script de prueba para el sistema de deployment automático de tiendas.
Este script demuestra cómo usar los nuevos endpoints de deployment.
"""

import requests
import json
import time
import sys
from uuid import uuid4

# Configuración
BASE_URL = "http://localhost:8000/api/v1"
STORES_URL = f"{BASE_URL}/stores"

def print_response(response, title="Response"):
    """Imprime una respuesta HTTP de forma legible."""
    print(f"\n{'='*50}")
    print(f"{title}")
    print(f"{'='*50}")
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response Text: {response.text}")

def test_deployment_system():
    """Prueba completa del sistema de deployment."""
    
    print("🚀 Iniciando prueba del sistema de deployment automático")
    print("=" * 60)
    
    # Paso 1: Crear una tienda de prueba
    print("\n📝 Paso 1: Creando tienda de prueba...")
    
    # Primero necesitamos obtener un country_id válido
    countries_response = requests.get(f"{BASE_URL}/countries")
    if countries_response.status_code != 200:
        print("❌ Error: No se pudieron obtener los países")
        return False
    
    countries = countries_response.json()
    if not countries:
        print("❌ Error: No hay países disponibles")
        return False
    
    country_id = countries[0]["id"]
    print(f"✅ Usando país: {countries[0]['nombre']} (ID: {country_id})")
    
    # Crear la tienda
    store_data = {
        "nombre": f"Tienda Test Deployment {int(time.time())}",
        "country_id": country_id,
        "tokens_disponibles": 100,
        "plan": "premium"
    }
    
    create_response = requests.post(STORES_URL, json=store_data)
    print_response(create_response, "Creación de tienda")
    
    if create_response.status_code != 201:
        print("❌ Error: No se pudo crear la tienda de prueba")
        return False
    
    store = create_response.json()
    store_id = store["id"]
    print(f"✅ Tienda creada exitosamente con ID: {store_id}")
    
    # Paso 2: Verificar estado inicial del deployment
    print(f"\n🔍 Paso 2: Verificando estado inicial del deployment...")
    
    status_response = requests.get(f"{STORES_URL}/{store_id}/deploy/status")
    print_response(status_response, "Estado inicial del deployment")
    
    # Paso 3: Realizar el deployment
    print(f"\n🚀 Paso 3: Realizando deployment de la tienda...")
    
    deploy_response = requests.post(f"{STORES_URL}/{store_id}/deploy")
    print_response(deploy_response, "Deployment de tienda")
    
    if deploy_response.status_code != 200:
        print("❌ Error: Falló el deployment")
        return False
    
    deployment_info = deploy_response.json()
    print(f"✅ Deployment completado exitosamente!")
    print(f"   Backend URL: {deployment_info.get('back_link')}")
    print(f"   DB URL: {deployment_info.get('db_link')}")
    print(f"   Puertos asignados: {deployment_info.get('ports')}")
    
    # Paso 4: Verificar estado después del deployment
    print(f"\n🔍 Paso 4: Verificando estado después del deployment...")
    
    time.sleep(5)  # Esperar un poco para que los contenedores se inicien
    
    status_response = requests.get(f"{STORES_URL}/{store_id}/deploy/status")
    print_response(status_response, "Estado después del deployment")
    
    # Paso 5: Verificar que la tienda fue actualizada con los links
    print(f"\n🔍 Paso 5: Verificando que la tienda fue actualizada...")
    
    store_response = requests.get(f"{STORES_URL}/{store_id}")
    print_response(store_response, "Tienda actualizada")
    
    if store_response.status_code == 200:
        updated_store = store_response.json()
        if updated_store.get("back_link"):
            print("✅ La tienda fue actualizada correctamente con los links")
        else:
            print("⚠️  Advertencia: La tienda no tiene back_link actualizado")
    
    # Paso 6: Intentar deployment duplicado (debería fallar o retornar info existente)
    print(f"\n🔄 Paso 6: Intentando deployment duplicado...")
    
    duplicate_response = requests.post(f"{STORES_URL}/{store_id}/deploy")
    print_response(duplicate_response, "Deployment duplicado")
    
    # Paso 7: Probar el backend desplegado (opcional)
    if deployment_info.get('back_link'):
        print(f"\n🌐 Paso 7: Probando el backend desplegado...")
        try:
            backend_url = deployment_info['back_link']
            health_response = requests.get(f"{backend_url}/docs", timeout=10)
            if health_response.status_code == 200:
                print(f"✅ Backend desplegado está respondiendo en {backend_url}")
            else:
                print(f"⚠️  Backend desplegado retornó status {health_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  No se pudo conectar al backend desplegado: {e}")
    
    # Paso 8: Cleanup - Eliminar el deployment
    print(f"\n🧹 Paso 8: Limpiando deployment...")
    
    undeploy_response = requests.delete(f"{STORES_URL}/{store_id}/deploy")
    print_response(undeploy_response, "Undeploy")
    
    if undeploy_response.status_code == 200:
        print("✅ Undeploy completado exitosamente")
    else:
        print("⚠️  Advertencia: Problemas con el undeploy")
    
    # Paso 9: Verificar estado final
    print(f"\n🔍 Paso 9: Verificando estado final...")
    
    final_status_response = requests.get(f"{STORES_URL}/{store_id}/deploy/status")
    print_response(final_status_response, "Estado final")
    
    # Paso 10: Eliminar la tienda de prueba
    print(f"\n🗑️  Paso 10: Eliminando tienda de prueba...")
    
    delete_response = requests.delete(f"{STORES_URL}/{store_id}")
    if delete_response.status_code == 204:
        print("✅ Tienda de prueba eliminada exitosamente")
    else:
        print(f"⚠️  Advertencia: No se pudo eliminar la tienda de prueba (status: {delete_response.status_code})")
    
    print("\n" + "="*60)
    print("🎉 Prueba del sistema de deployment completada!")
    print("="*60)
    
    return True

def test_deployment_status_only():
    """Prueba rápida solo del endpoint de estado."""
    print("🔍 Probando endpoint de estado con UUID aleatorio...")
    
    random_uuid = str(uuid4())
    status_response = requests.get(f"{STORES_URL}/{random_uuid}/deploy/status")
    
    if status_response.status_code == 404:
        print("✅ Endpoint de estado funciona correctamente (tienda no encontrada)")
    else:
        print_response(status_response, "Estado de UUID aleatorio")

if __name__ == "__main__":
    print("🧪 Script de prueba del sistema de deployment automático")
    print("=" * 60)
    
    # Verificar que el backend esté corriendo
    try:
        # Usar el endpoint de países como health check
        health_response = requests.get(f"{BASE_URL}/countries", timeout=5)
        if health_response.status_code not in [200, 404]:  # 404 es OK si no hay países
            print("❌ Error: El backend no está respondiendo correctamente")
            sys.exit(1)
        print("✅ Backend principal está corriendo")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: No se puede conectar al backend: {e}")
        print("Asegúrate de que el backend esté corriendo en http://localhost:8000")
        sys.exit(1)
    
    # Ejecutar pruebas
    if len(sys.argv) > 1 and sys.argv[1] == "--status-only":
        test_deployment_status_only()
    else:
        success = test_deployment_system()
        if not success:
            print("❌ Las pruebas fallaron")
            sys.exit(1)
        else:
            print("✅ Todas las pruebas pasaron exitosamente")
