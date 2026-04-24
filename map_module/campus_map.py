#############################################################################
# campus_map.py
#
# Interactive campus map using Folium + streamlit-folium.
# Buildings are defined here as static data; swap in a BigQuery fetch
# (similar to get_active_polls in data_fetcher.py) whenever the DB table
# is ready.
#############################################################################

import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# ---------------------------------------------------------------------------
# Duke University campus center  (~36.0015° N, 78.9391° W)
# Use West Campus / Chapel coordinates as a central anchor.
# ---------------------------------------------------------------------------
CAMPUS_CENTER = [36.0016639, -78.9398111]


# ---------------------------------------------------------------------------
# Building data — Duke University West Campus landmarks
# (coordinates updated to higher-precision values where available)
# ---------------------------------------------------------------------------
BUILDINGS = [
    {
        "id": 1,
        "name": "Perkins & Bostock Libraries",
        # 36°00′07.65″ N, 78°56′19″ W
        "lat": 36.002125,
        "lon": -78.938611,
        "type": "study",
    },
    {
        "id": 2,
        "name": "Bryan Center",
        # Mapcarta: 36.001° N, -78.9412° W
        "lat": 36.001000,
        "lon": -78.941200,
        "type": "dining",
    },
    {
        "id": 3,
        "name": "Wilson Recreation Center",
        # No better published GPS than the approximate value you had.
        "lat": 36.0005,
        "lon": -78.9440,
        "type": "recreation",
    },
    {
        "id": 4,
        "name": "Fitzpatrick Center (CIEMAS)",
        # Wikipedia: 36.003520° N, 78.939599° W
        "lat": 36.003520,
        "lon": -78.939599,
        "type": "academic",
    },
    {
        "id": 5,
        "name": "Duke Chapel",
        # Wikipedia: 36.0016639° N, 78.9398111° W
        "lat": 36.0016639,
        "lon": -78.9398111,
        "type": "academic",
    },
    {
        "id": 6,
        "name": "Allen Building",
        # Commons camera point: 36°00′03.96″ N, 78°56′16.57″ W
        "lat": 36.001100,
        "lon": -78.937936,
        "type": "admin",
    },
    {
        "id": 7,
        "name": "Bryan Center Parking Garage",
        # LatLong.net: 36.0015839, -78.9421350
        "lat": 36.0015839,
        "lon": -78.9421350,
        "type": "parking",
    },
    {
        "id": 8,
        "name": "Cameron Indoor Stadium",
        # CoordinatesFinder: 35.997174, -78.9424182
        "lat": 35.997174,
        "lon": -78.9424182,
        "type": "recreation",
    },
    {
        "id": 9,
        "name": "Nasher Museum of Art",
        # Wikipedia: 35.9990639° N, 78.9290528° W
        "lat": 35.9990639,
        "lon": -78.9290528,
        "type": "academic",
    },
    {
        "id": 10,
        "name": "Sarah P. Duke Gardens",
        # Wikipedia: 36.0018028° N, 78.9334833° W
        "lat": 36.0018028,
        "lon": -78.9334833,
        "type": "recreation",
    },
]

TYPE_COLORS = {
    "study":      "blue",
    "dining":     "orange",
    "recreation": "green",
    "academic":   "purple",
    "admin":      "gray",
    "parking":    "lightgray",
}

st.title("🗺️ Campus Map")
st.markdown("Browse Duke University buildings. Use the sidebar to filter by type or jump to a specific building.")

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
all_types = sorted({b["type"] for b in BUILDINGS})
selected_types = st.sidebar.multiselect(
    "Filter by type",
    options=all_types,
    default=all_types,
    format_func=str.capitalize,
)

building_names = ["— none —"] + [b["name"] for b in BUILDINGS if b["type"] in selected_types]
selected_name = st.sidebar.selectbox("Jump to building", building_names)
selected_building = next((b for b in BUILDINGS if b["name"] == selected_name), None)

filtered = [b for b in BUILDINGS if b["type"] in selected_types]

# ---------------------------------------------------------------------------
# Build the Folium map
# ---------------------------------------------------------------------------
m = folium.Map(location=CAMPUS_CENTER, zoom_start=16, tiles="OpenStreetMap")
cluster = MarkerCluster().add_to(m)

for b in filtered:
    is_selected = selected_building and b["id"] == selected_building["id"]
    color = "red" if is_selected else TYPE_COLORS.get(b["type"], "blue")
    folium.Marker(
        location=[b["lat"], b["lon"]],
        popup=folium.Popup(f"<b>{b['name']}</b><br>Type: {b['type'].capitalize()}", max_width=200),
        tooltip=b["name"],
        icon=folium.Icon(color=color, icon="info-sign"),
    ).add_to(cluster)

# Zoom to selected building
if selected_building:
    m.location = [selected_building["lat"], selected_building["lon"]]
    m.zoom_start = 18

# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
st_folium(m, width="100%", height=520)

if selected_building:
    st.success(f"📍 **{selected_building['name']}** — {selected_building['type'].capitalize()}")
else:
    st.info("Select a building from the sidebar to highlight it on the map.")

# ---------------------------------------------------------------------------
# Legend
# ---------------------------------------------------------------------------
st.markdown("**Map legend**")
cols = st.columns(len(TYPE_COLORS))
for col, (btype, color) in zip(cols, TYPE_COLORS.items()):
    col.markdown(f"🔵 {btype.capitalize()}" if color == "blue" else
                 f"🟠 {btype.capitalize()}" if color == "orange" else
                 f"🟢 {btype.capitalize()}" if color == "green" else
                 f"🟣 {btype.capitalize()}" if color == "purple" else
                 f"⚫ {btype.capitalize()}")
