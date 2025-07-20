#!/usr/bin/env python3
"""
Script de prueba para el nuevo endpoint de crear y desplegar tienda automáticamente.
Este script demuestra cómo usar el endpoint POST /stores/ que crea la tienda y la despliega.
"""

import requests
import json
import time
import sys

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

def test_create_and_deploy():
    """Prueba el nuevo endpoint de crear y desplegar tienda."""
    
    print("🚀 Probando el endpoint de crear y desplegar tienda automáticamente")
    print("=" * 70)
    
    # Paso 1: Obtener un country_id válido
    print("\n📍 Paso 1: Obteniendo países disponibles...")
    
    countries_response = requests.get(f"{BASE_URL}/countries")
    if countries_response.status_code != 200:
        print("❌ Error: No se pudieron obtener los países")
        return False
    
    countries = countries_response.json()
    if not countries:
        print("❌ Error: No hay países disponibles")
        return False
    
    # Verificar la estructura de la respuesta
    if isinstance(countries, list) and len(countries) > 0:
        country_data = countries[0]
        country_id = country_data.get("id")
        country_name = country_data.get("nombre", "Desconocido")
        
        if not country_id:
            print("❌ Error: No se pudo obtener country_id")
            return False
            
        print(f"✅ Usando país: {country_name} (ID: {country_id})")
    else:
        print("❌ Error: Respuesta de países inválida")
        return False
    
    # Paso 2: Crear y desplegar tienda con el nuevo endpoint
    print(f"\n🏪 Paso 2: Creando y desplegando tienda...")
    
    store_data = {
        "nombre": f"Mi Tienda Automática {int(time.time())}",
        "country_id": country_id,
        "tokens_disponibles": 500,
        "plan": "enterprise"
    }
    
    print("Datos de la tienda:")
    print(json.dumps(store_data, indent=2, ensure_ascii=False))
    
    create_deploy_response = requests.post(f"{STORES_URL}/deploy", json=store_data)
    print_response(create_deploy_response, "Crear y Desplegar Tienda")
    
    if create_deploy_response.status_code != 201:
        print("❌ Error: No se pudo crear y desplegar la tienda")
        return False
    
    response_data = create_deploy_response.json()
    store_info = response_data.get("store", {})
    deployment_info = response_data.get("deployment", {})
    
    store_id = store_info.get("id")
    back_link = deployment_info.get("back_link")
    
    print(f"✅ Tienda creada y desplegada exitosamente!")
    print(f"   ID: {store_id}")
    print(f"   Nombre: {store_info.get('nombre')}")
    print(f"   Plan: {store_info.get('plan')}")
    print(f"   Tokens: {store_info.get('tokens_disponibles')}")
    print(f"   Backend URL: {back_link}")
    print(f"   Puertos: {deployment_info.get('ports')}")
    
    # Paso 3: Verificar que la tienda fue creada correctamente
    print(f"\n🔍 Paso 3: Verificando tienda creada...")
    
    store_response = requests.get(f"{STORES_URL}/{store_id}")
    print_response(store_response, "Tienda Creada")
    
    if store_response.status_code == 200:
        store_data = store_response.json()
        if store_data.get("back_link"):
            print("✅ La tienda tiene los links de deployment correctos")
        else:
            print("⚠️  Advertencia: La tienda no tiene back_link")
    
    # Paso 4: Verificar estado del deployment
    print(f"\n📊 Paso 4: Verificando estado del deployment...")
    
    time.sleep(5)  # Esperar un poco para que los contenedores se inicien
    
    status_response = requests.get(f"{STORES_URL}/{store_id}/deploy/status")
    print_response(status_response, "Estado del Deployment")
    
    # Paso 5: Probar el backend desplegado
    if back_link:
        print(f"\n🌐 Paso 5: Probando el backend desplegado...")
        try:
            backend_response = requests.get(f"{back_link}/docs", timeout=10)
            if backend_response.status_code == 200:
                print(f"✅ Backend desplegado está funcionando en {back_link}")
                print(f"   Documentación disponible en: {back_link}/docs")
            else:
                print(f"⚠️  Backend retornó status {backend_response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"⚠️  No se pudo conectar al backend desplegado: {e}")
            print("   Esto es normal si los contenedores aún se están iniciando")
    
    # Paso 6: Intentar crear otra tienda con el mismo nombre (debería fallar)
    print(f"\n🔄 Paso 6: Probando validación de nombres duplicados...")
    
    duplicate_data = store_data.copy()
    duplicate_response = requests.post(f"{STORES_URL}/deploy", json=duplicate_data)
    print_response(duplicate_response, "Intento de Tienda Duplicada")
    
    if duplicate_response.status_code != 201:
        print("✅ Validación funcionando correctamente (nombre duplicado rechazado)")
    else:
        print("⚠️  Advertencia: Se permitió crear tienda con nombre duplicado")
    
    # Paso 7: Cleanup - Eliminar el deployment
    print(f"\n🧹 Paso 7: Limpiando deployment...")
    
    undeploy_response = requests.delete(f"{STORES_URL}/{store_id}/deploy")
    print_response(undeploy_response, "Undeploy")
    
    if undeploy_response.status_code == 200:
        print("✅ Undeploy completado exitosamente")
    else:
        print("⚠️  Advertencia: Problemas con el undeploy")
    
    # Paso 8: Eliminar la tienda
    print(f"\n🗑️  Paso 8: Eliminando tienda de prueba...")
    
    delete_response = requests.delete(f"{STORES_URL}/{store_id}")
    if delete_response.status_code == 204:
        print("✅ Tienda eliminada exitosamente")
    else:
        print(f"⚠️  Advertencia: No se pudo eliminar la tienda (status: {delete_response.status_code})")
    
    print("\n" + "="*70)
    print("🎉 Prueba del endpoint crear y desplegar completada!")
    print("="*70)
    
    return True

def test_different_plans():
    """Prueba crear tiendas con diferentes planes."""
    print("\n🎯 Probando diferentes planes de tienda...")
    
    # Obtener country_id
    countries_response = requests.get(f"{BASE_URL}/countries")
    if countries_response.status_code != 200:
        return False
    
    countries = countries_response.json()
    if not countries:
        return False
    
    # Verificar la estructura de la respuesta
    if isinstance(countries, list) and len(countries) > 0:
        country_id = countries[0].get("id")
        if not country_id:
            print("❌ Error: No se pudo obtener country_id")
            return False
    else:
        print("❌ Error: Respuesta de países inválida")
        return False
    
    plans = ["basic", "premium", "enterprise"]
    created_stores = []
    
    for plan in plans:
        print(f"\n📦 Creando tienda con plan: {plan}")
        
        store_data = {
            "nombre": f"Tienda {plan.title()} {int(time.time())}",
            "country_id": country_id,
            "tokens_disponibles": 100 if plan == "basic" else 500 if plan == "premium" else 1000,
            "plan": plan
        }
        
        response = requests.post(f"{STORES_URL}/deploy", json=store_data)
        
        if response.status_code == 201:
            data = response.json()
            store_id = data["store"]["id"]
            created_stores.append(store_id)
            print(f"✅ Tienda {plan} creada: {store_id}")
            print(f"   Backend: {data['deployment']['back_link']}")
        else:
            print(f"❌ Error creando tienda {plan}: {response.status_code}")
    
    # Cleanup
    print(f"\n🧹 Limpiando tiendas de prueba...")
    for store_id in created_stores:
        try:
            requests.delete(f"{STORES_URL}/{store_id}/deploy")
            requests.delete(f"{STORES_URL}/{store_id}")
            print(f"✅ Tienda {store_id} limpiada")
        except:
            print(f"⚠️  Error limpiando tienda {store_id}")

if __name__ == "__main__":
    print("🧪 Script de prueba: Crear y Desplegar Tienda Automáticamente")
    print("=" * 70)
    
    # Verificar que el backend esté corriendo
    try:
        health_response = requests.get(f"{BASE_URL}/countries", timeout=5)
        if health_response.status_code not in [200, 404]:
            print("❌ Error: El backend no está respondiendo correctamente")
            sys.exit(1)
        print("✅ Backend principal está corriendo")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: No se puede conectar al backend: {e}")
        print("Asegúrate de que el backend esté corriendo en http://localhost:8000")
        sys.exit(1)
    
    # Ejecutar pruebas
    if len(sys.argv) > 1 and sys.argv[1] == "--plans":
        test_different_plans()
    else:
        success = test_create_and_deploy()
        if not success:
            print("❌ Las pruebas fallaron")
            sys.exit(1)
        else:
            print("✅ Todas las pruebas pasaron exitosamente")
            
            # Ejecutar prueba adicional de planes
            test_different_plans()
