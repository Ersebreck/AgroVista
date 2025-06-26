import folium
from utils import evaluar_estado_parcelas
from folium import GeoJson, GeoJsonTooltip

def add_geojson_polygon(grupo, name, coords, color, opacity):
    feature = {
        "type": "Feature",
        "properties": {"name": name},
        "geometry": {"type": "Polygon", "coordinates": [[ [lon, lat] for lat, lon in coords ]]}
    }
    GeoJson(
        feature,
        tooltip=GeoJsonTooltip(fields=["name"], aliases=["Nombre:"], sticky=True),
        style_function=lambda x: {
            "fillColor": color,
            "color": "black",
            "weight": 2,
            "fillOpacity": opacity,
        }
    ).add_to(grupo)

def construir_mapa(df_actividades):
    # Crear mapa base
    m = folium.Map(location=[5.490471, -74.682919], zoom_start=15, tiles='Esri.WorldImagery')
    grupo_terrenos = folium.FeatureGroup(name="Terrenos", show=1)
    grupo_parcelas = folium.FeatureGroup(name="Parcelas", show=1)

    # Terrenos
    add_geojson_polygon(grupo_terrenos, "Terreno 1", [
        [5.490012, -74.689513], [5.491388, -74.686458], [5.493076, -74.686186], 
        [5.494909, -74.687275], [5.495821, -74.687296], [5.495455, -74.689642], 
        [5.492761, -74.690266]
    ], "green", opacity=0.6)

    add_geojson_polygon(grupo_terrenos, "Terreno 2", [
        [5.490012, -74.689513], [5.491388, -74.686458], [5.489541, -74.683064], 
        [5.485220, -74.683948], [5.487558, -74.688777]
    ], "blue", opacity=0.6)

    # Parcelas con polígonos y emojis
    parcelas_coords = {
        "Parcela 1A": [
            [5.490012, -74.689513], [5.490818, -74.687843], 
            [5.493041, -74.688052], [5.492761, -74.690266]
        ],
        "Parcela 1B": [
            [5.493021, -74.688042], [5.493201, -74.686225], 
            [5.494670, -74.687154], [5.495789, -74.687333], 
            [5.495671, -74.688349]
        ],
        "Parcela 2A": [
            [5.488324, -74.685804], [5.486298, -74.686302], 
            [5.485390, -74.683935], [5.487827, -74.683315]
        ],
        "Parcela 2B": [
            [5.488324, -74.685804], [5.487951, -74.683294], 
            [5.489582, -74.683106], [5.490635, -74.685222]
        ]
    }

    estados = evaluar_estado_parcelas(df_actividades)
    emoji_por_estado = {
        "Óptimo": "✅",
        "Atención": "⚠️",
        "Crítico": "🚨 "
    }

    for nombre, coords in parcelas_coords.items():
        add_geojson_polygon(grupo_parcelas, nombre, coords, "lightgreen" if "1" in nombre else "lightblue", opacity=0.3)

        # Obtener centro aproximado del polígono
        centro_lat = sum([p[0] for p in coords]) / len(coords)
        centro_lon = sum([p[1] for p in coords]) / len(coords)

        # Buscar id de parcela
        parcela_id = None
        for key, val in estados.items():
            parcela_id = int(key.split(":")[1])
            if df_actividades[df_actividades["parcela_id"] == parcela_id]["nombre"].iloc[0] == nombre:
                break

        if parcela_id:
            resumen_estado = estados[f"id:{parcela_id}"]
            if "Inactiva" in resumen_estado:
                emoji = emoji_por_estado["Crítico"]
            elif "Pendiente de intervención" in resumen_estado:
                emoji = emoji_por_estado["Atención"]
            elif "Activa" in resumen_estado:
                emoji = emoji_por_estado["Óptimo"]
            else:
                emoji = "❓"

            folium.Marker(
                location=[centro_lat, centro_lon],
                icon=folium.DivIcon(html=f"<div style='font-size:22px'>{emoji}</div>")
            ).add_to(grupo_parcelas)

    grupo_terrenos.add_to(m)
    grupo_parcelas.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    return m
