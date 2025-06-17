import requests

API_URL = "http://localhost:8000"  # Ajusta si corres desde Docker o con dominio

def obtener_actividades_por_parcela(parcela_id):
    try:
        res = requests.get(f"{API_URL}/actividades/por-parcela/{parcela_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener actividades: {e}")
        return []

def obtener_terrenos():
    try:
        res = requests.get(f"{API_URL}/terrenos")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener terrenos: {e}")
        return []

def obtener_parcelas_por_terreno(terreno_id):
    try:
        res = requests.get(f"{API_URL}/parcelas/por-terreno/{terreno_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener parcelas: {e}")
        return []

def obtener_parcela(parcela_id):
    try:
        res = requests.get(f"{API_URL}/parcelas/{parcela_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener parcela: {e}")
        return {}

def obtener_ubicacion(ubicacion_id):
    try:
        res = requests.get(f"{API_URL}/ubicaciones/{ubicacion_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener ubicación: {e}")
        return {}

def registrar_actividad(data):
    try:
        res = requests.post(f"{API_URL}/actividades/", json=data)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al registrar actividad: {e}")
        return None
