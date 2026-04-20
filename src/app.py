import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

# --- PAGE CONFIGURATION ---
st.set_page_config(
    layout="wide",
    page_title="LILA BLACK - Player Journey Visualizer",
    page_icon="🎮"
)

EVENT_CATEGORY_MAP = {
    'Position': 'Movement',
    'BotPosition': 'Movement',
    'Loot': 'Loot',
    'Kill': 'Kill',
    'BotKill': 'Kill',
    'Killed': 'Death',
    'BotKilled': 'Death',
    'KilledByStorm': 'Storm Death'
}

EVENT_COLOR_MAP = {
    'Movement': 'gray',
    'Loot': 'green',
    'Kill': 'red',
    'Death': 'black',
    'Storm Death': 'blue'
}

EVENT_SIZE_MAP = {
    'Movement': 6,
    'Loot': 12,
    'Kill': 18,
    'Death': 18,
    'Storm Death': 20
}

HEATMAP_CATEGORY_MAP = {
    'Kill Zones': ['Kill'],
    'Death Zones': ['Death', 'Storm Death'],
    'Traffic': ['Movement']
}

@st.cache_data
def load_data():
    df = pd.read_parquet('data/processed/master_data.parquet')
    df['ts'] = pd.to_datetime(df['ts'])
    df['user_type'] = df['is_bot'].map({True: 'Bot', False: 'Human'})
    df['event_category'] = df['event'].map(EVENT_CATEGORY_MAP).fillna('Other')
    df['marker_size'] = df['event_category'].map(EVENT_SIZE_MAP).fillna(8)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load master data. Error: {e}")
    st.stop()

st.sidebar.title("🎮 Match Explorer")
selected_map = st.sidebar.selectbox("🗺️ Select Map", sorted(df['map_id'].unique()))
selected_day = st.sidebar.selectbox(
    "📅 Select Date",
    sorted(df[df['map_id'] == selected_map]['day'].unique())
)

match_filter = df[(df['map_id'] == selected_map) & (df['day'] == selected_day)]
selected_match = st.sidebar.selectbox(
    "🆔 Select Match ID",
    sorted(match_filter['match_id'].unique())
)

match_df = df[df['match_id'] == selected_match].sort_values('ts').copy()
match_df['elapsed_sec'] = (match_df['ts'] - match_df['ts'].min()).dt.total_seconds()
max_duration = float(max(0.01, round(match_df['elapsed_sec'].max(), 2)))

st.sidebar.markdown("---")
if max_duration <= 0.01:
    st.sidebar.info("This match has only one timestamp.")
    time_filter = 0.0
else:
    time_filter = st.sidebar.slider(
        "⏳ Timeline (Seconds)", 0.0, max_duration, max_duration, step=0.01
    )

st.sidebar.subheader("🎨 View Settings")
show_bots = st.sidebar.checkbox("🤖 Include Bots", value=True)
show_paths = st.sidebar.checkbox("🛣️ Show Player Paths", value=True)
heatmap_type = st.sidebar.selectbox(
    "🔥 Heatmap Overlay",
    ["None", "Kill Zones", "Death Zones", "Traffic"]
)
all_categories = sorted(match_df['event_category'].unique())

required_categories = set(HEATMAP_CATEGORY_MAP.get(heatmap_type, []))
available_required = required_categories.intersection(set(all_categories))
default_categories = sorted(set(all_categories).union(available_required))

selected_event_categories = st.sidebar.multiselect(
    "📌 Event Categories",
    all_categories,
    default=default_categories,
    key=f"event_categories_{selected_match}"
)

display_df = match_df[match_df['elapsed_sec'] <= time_filter].copy()
if not show_bots:
    display_df = display_df[display_df['is_bot'] == False]
if selected_event_categories:
    display_df = display_df[display_df['event_category'].isin(selected_event_categories)]

display_df = display_df.dropna(subset=['pixel_x', 'pixel_y'])

st.title(f"📍 Match Journey: {selected_match}")
st.caption(f"Map: {selected_map} | Date: {selected_day}")

col_map, col_stats = st.columns([4, 1])

with col_map:
    possible_paths = [
        f"data/minimaps/{selected_map}_Minimap.png",
        f"data/minimaps/{selected_map}_Minimap.jpg",
        f"data/minimaps/{selected_map}.png",
        f"data/minimaps/{selected_map}.jpg"
    ]
    map_image_path = next((p for p in possible_paths if os.path.exists(p)), None)

    if map_image_path:
        img = Image.open(map_image_path)
        fig = None

        if heatmap_type != "None":
            if heatmap_type == "Kill Zones":
                heatmap_df = display_df[display_df['event_category'] == 'Kill']
                color_scale = 'Hot'
            elif heatmap_type == "Death Zones":
                heatmap_df = display_df[display_df['event_category'].isin(['Death', 'Storm Death'])]
                color_scale = 'YlOrRd'
            else:
                heatmap_df = display_df[display_df['event_category'] == 'Movement']
                color_scale = 'Viridis'

            if heatmap_df.empty:
                st.info(
                    f"No available '{heatmap_type}' events in this match. "
                    f"This match contains: {display_df['event_category'].value_counts().to_dict()}"
                )
            else:
                fig = px.density_heatmap(
                    heatmap_df,
                    x='pixel_x',
                    y='pixel_y',
                    nbinsx=50,
                    nbinsy=50,
                    color_continuous_scale=color_scale,
                    range_x=[0, 1024],
                    range_y=[1024, 0],
                    title=f"{heatmap_type}"
                )
                fig.update_traces(opacity=0.6)
        else:
            if display_df.empty:
                st.warning("No events match the current filters.")
                fig = go.Figure()
            else:
                fig = px.scatter(
                    display_df,
                    x='pixel_x',
                    y='pixel_y',
                    color='user_type',
                    symbol='user_type',
                    symbol_map={'Human': 'circle', 'Bot': 'diamond'},
                    color_discrete_map={'Human': '#1f77b4', 'Bot': '#E63946'},
                    size='marker_size',
                    size_max=18,
                    hover_data=['user_id', 'event', 'elapsed_sec', 'event_category'],
                    title="Player Journey Events",
                    range_x=[0, 1024],
                    range_y=[1024, 0]
                )

                if show_paths:
                    movement_df = display_df[display_df['event_category'] == 'Movement']
                    for user_id, user_df in movement_df.groupby('user_id'):
                        sorted_user_df = user_df.sort_values('elapsed_sec')
                        fig.add_trace(
                            go.Scatter(
                                x=sorted_user_df['pixel_x'],
                                y=sorted_user_df['pixel_y'],
                                mode='lines',
                                line=dict(
                                    color='lightgray' if sorted_user_df['is_bot'].iloc[0] else 'white',
                                    width=1,
                                    dash='solid'
                                ),
                                opacity=0.5,
                                showlegend=False,
                                hoverinfo='skip'
                            )
                        )

        if fig is not None:
            fig.add_layout_image(
                dict(
                    source=img,
                    xref="x",
                    yref="y",
                    x=0,
                    y=0,
                    sizex=1024,
                    sizey=1024,
                    sizing="stretch",
                    layer="below"
                )
            )

            fig.update_layout(
                width=880,
                height=880,
                margin=dict(l=0, r=0, t=30, b=0),
                legend_title_text='Event category / player type',
                xaxis=dict(visible=False, range=[0, 1024]),
                yaxis=dict(visible=False, range=[1024, 0])
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"Minimap not found. Checked: {possible_paths}")

with col_stats:
    st.subheader("📊 Match Stats")
    humans = display_df[display_df['is_bot'] == False]['user_id'].nunique()
    bots = display_df[display_df['is_bot'] == True]['user_id'].nunique()
    st.metric("Humans", humans)
    st.metric("Bots", bots)
    st.markdown("---")
    st.subheader("📝 Event Breakdown")
    st.write(display_df['event_category'].value_counts())
    st.write(display_df['event'].value_counts().head(20))
    st.markdown("---")
    st.subheader("🔍 Coordinate Accuracy")
    st.caption(f"Map: {selected_map}")
    if len(display_df) > 0:
        st.caption(f"Pixel X range: [{display_df['pixel_x'].min():.1f}, {display_df['pixel_x'].max():.1f}]")
        st.caption(f"Pixel Y range: [{display_df['pixel_y'].min():.1f}, {display_df['pixel_y'].max():.1f}]")
        st.caption(f"Events plotted: {len(display_df)}")
    else:
        st.caption("No events in current filter range")
    if st.button("Reset Timeline"):
        st.rerun()

st.markdown("---")
st.markdown("Built for LILA Games Level Design Team | Player Journey Visualization Tool")