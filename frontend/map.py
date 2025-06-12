import folium
from utils import add_geojson_polygon

def construir_mapa():
    # Crear mapa base
    m = folium.Map(location=[5.490471, -74.682925], zoom_start=15, tiles='Esri.WorldImagery')
    grupo_terrenos = folium.FeatureGroup(name="Terrenos", show=1)
    grupo_parcelas = folium.FeatureGroup(name="Parcelas", show=1)

    # Terrenos (más opacos)
    add_geojson_polygon(grupo_terrenos, "Terreno 1", [
        [5.490012, -74.689513], [5.491388, -74.686458], [5.493076, -74.686186], 
        [5.494909, -74.687275], [5.495821, -74.687296], [5.495455, -74.689642], 
        [5.492761, -74.690266]
    ], "green", opacity=0.6)

    add_geojson_polygon(grupo_terrenos, "Terreno 2", [
        [5.490012, -74.689513], [5.491388, -74.686458], [5.489541, -74.683064], 
        [5.485220, -74.683948], [5.487558, -74.688777]
    ], "blue", opacity=0.6)

    # Parcelas (menos opacas)
    add_geojson_polygon(grupo_parcelas, "Parcela 1A", [
        [5.490012, -74.689513], [5.490818, -74.687843], 
        [5.493041, -74.688052], [5.492761, -74.690266]
    ], "lightgreen", opacity=0.3)

    add_geojson_polygon(grupo_parcelas, "Parcela 1B", [
        [5.493021, -74.688042], [5.493201, -74.686225], 
        [5.494670, -74.687154], [5.495789, -74.687333], 
        [5.495671, -74.688349]
    ], "lightgreen", opacity=0.3)

    add_geojson_polygon(grupo_parcelas, "Parcela 2A", [
        [5.488324, -74.685804], [5.486298, -74.686302], 
        [5.485390, -74.683935], [5.487827, -74.683315]
    ], "lightblue", opacity=0.3)

    add_geojson_polygon(grupo_parcelas, "Parcela 2B", [
        [5.488324, -74.685804], [5.487951, -74.683294], 
        [5.489582, -74.683106], [5.490635, -74.685222]
    ], "lightblue", opacity=0.3)

    # Añadir grupos al mapa
    grupo_terrenos.add_to(m)
    grupo_parcelas.add_to(m)

    # Añadir control de capas
    folium.LayerControl(collapsed=False).add_to(m)
    return m