import streamlit as st

# Examples
#create_page = st.Page("create.py", title="Create entry", icon=":material/add_circle:")
#delete_page = st.Page("delete.py", title="Delete entry", icon=":material/delete:")
#pg = st.navigation([create_page, delete_page])
#st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
#pg.run()
# Build with "Dashboard", "Map & Parcels", "Activities & Inventory", "Economy", "AI Assistant"

principal = st.set_page_config(page_title="AgroVista", page_icon="🌱")
dashboard = st.Page("pages/_1_Dashboard.py", title="Dashboard", icon="📊")
dashmap = st.Page("pages/DashMap.py", title="Terrains Management", icon="🗺️")
map_page = st.Page("pages/_2_Map.py", title="Map", icon="🌍")
activities = st.Page("pages/_3_Activities_Inventory.py", title="Activities", icon="🌱")
economy = st.Page("pages/_4_Economy.py", title="Economy", icon="💰")
assistant = st.Page("pages/_5_AI_Assistant.py", title="Assistant", icon="🤖")

pg = st.navigation([dashmap, dashboard, map_page, activities, economy, assistant])
pg.run()
