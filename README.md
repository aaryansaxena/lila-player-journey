# LILA BLACK Player Journey Visualization Tool

A web-based visualization tool for analyzing player movement, combat, and loot behavior across 5 days of production gameplay data from LILA BLACK extraction shooter.

## 🚀 **[View Live App](https://lila-player-journey-game.streamlit.app)**

**Try it now:** https://lila-player-journey-game.streamlit.app

---

## Features

- **Player Journey Visualization**: See human and bot movement paths on the actual in-game minimap
- **Event Filtering**: Isolate kills, deaths, looting, and storm casualties by event type
- **Temporal Playback**: Use the timeline slider to watch matches unfold in real-time
- **Heatmap Overlays**: Visualize kill zones, death zones, and high-traffic areas with semi-transparent overlays
- **Multi-map Support**: Analyze behavior across AmbroseValley, GrandRift, and Lockdown maps
- **5 Days of Data**: 89,104 events across 5 days of gameplay (Feb 10-14, 2025)

## ⚡ Quick Test

Try these match IDs in the live app to see different gameplay patterns:

| Match ID | Map | Date | Events | Use Case |
|----------|-----|------|--------|----------|
| `d3a3297e-2cdf-4a49-8450-09119b91a779` | AmbroseValley | Feb_10 | 1,097 | High-volume test |
| `de5aa1ae-6246-4cfb-9941-adf5996ef678` | AmbroseValley | Feb_12 | 1,124 | Balanced events |
| `d0a38c30-d476-4305-857d-ece9e65f72e6` | Lockdown | Feb_12 | 1,216 | Cross-map test |

## Tech Stack

- **Frontend**: Streamlit (Python web framework)
- **Data Processing**: pandas, pyarrow (Apache Parquet)
- **Visualization**: Plotly Express
- **Language**: Python 3.10+

## Setup

### Local Development

```bash
# 1. Clone the repository
git clone <repo-url>
cd lila-player-journey

# 2. Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# or: source .venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Process raw data (one-time)
python scripts/process_data.py

# 5. Run the app
streamlit run src/app.py
```

The app will open at `http://localhost:8502`

### Environment Variables

No environment variables required for local development.

For cloud deployment, ensure the `data/processed/master_data.parquet` file is available in the deployment environment.

## Usage

1. **Select Match**: Use the sidebar to choose a map, date, and match ID
2. **Adjust Timeline**: Drag the timeline slider to reveal events progressively
3. **Choose View**: Select between scatter view (all events) or heatmap overlays
4. **Filter Events**: Toggle event categories (Movement, Loot, Kill, Death, Storm Death)
5. **Show Paths**: Optional: render player movement paths as lines

### Visual Key

- **Blue Circle**: Human player
- **Red Diamond**: Bot
- **Sizes**: Kills/Deaths are 3x larger than movement events
- **Colors** (scatter view):
  - Gray: Movement
  - Green: Loot
  - Red: Kill
  - Black: Death
  - Blue: Storm Death

## File Structure

```
lila-player-journey/
├── src/
│   └── app.py              # Main Streamlit application
├── scripts/
│   ├── process_data.py     # Data pipeline: raw parquet → master dataset
│   └── test_script.py      # Utility script for data exploration
├── data/
│   ├── raw/                # Raw parquet files (not in repo)
│   ├── processed/          # master_data.parquet (generated)
│   └── minimaps/           # AmbroseValley, GrandRift, Lockdown minimaps
├── requirements.txt        # Python dependencies
├── ARCHITECTURE.md         # System design & coordinate mapping
├── INSIGHTS.md            # Gameplay insights & findings
└── README.md              # This file
```

## Data Processing Pipeline

1. **Ingest**: `process_data.py` recursively reads all `.nakama-0` parquet files from `data/raw/player_data/player data/`
2. **Decode**: Converts `event` field from bytes to UTF-8 strings
3. **Classify**: Identifies bots (numeric user_id < 10 chars) vs humans (UUID)
4. **Transform**: Applies world-to-pixel coordinate mapping for each map
5. **Consolidate**: Merges 50+ raw files into single `master_data.parquet` (89,104 rows)
6. **Optimize**: Compresses with snappy codec for fast I/O

## Coordinate Mapping

Game world coordinates (x, z) are converted to 2D pixel positions (0-1024 pixels) on the minimap:

```
Step 1: World → UV (normalized 0-1)
  u = (world_x - origin_x) / scale
  v = (world_z - origin_z) / scale

Step 2: UV → Pixel (1024x1024 image)
  pixel_x = u * 1024
  pixel_y = (1 - v) * 1024    # Y flipped for image origin at top-left

Map Constants (from README):
- AmbroseValley: scale=900, origin=(-370, -473)
- GrandRift: scale=581, origin=(-290, -290)
- Lockdown: scale=1000, origin=(-500, -500)
```

See ARCHITECTURE.md for detailed coordinate validation.

## Deployment

### Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Sign in with GitHub
4. Select your repo → branch → `src/app.py`
5. Streamlit Cloud automatically handles dependencies and runs the app

### Other Platforms

- **Vercel**: Deploy Python ASGI app (requires different setup)
- **Railway**: Supports Streamlit natively via Procfile
- **Render**: Similar to Railway

For Streamlit Cloud, data files must be committed to git or downloaded at runtime.

## Validation Checklist

- ✅ Player paths render correctly on minimap
- ✅ Humans (blue circles) vs bots (red diamonds) visually distinct
- ✅ Event types marked distinctly (kill, death, loot, storm)
- ✅ Filtering by map, date, match works
- ✅ Timeline slider shows match progression (0.0-0.8s range)
- ✅ Heatmap overlays (kill/death/traffic) with semi-transparency
- ✅ Coordinates validated via pixel range (0-1024)

## Test Data

Recommended match IDs for verification:

| ID | Map | Date | Duration | Events | Use Case |
|----|-----|------|----------|--------|----------|
| `d3a3297e-2cdf-4a49-8450-09119b91a779` | AmbroseValley | Feb_10 | 0.8s | 1,097 | High-volume test |
| `de5aa1ae-6246-4cfb-9941-adf5996ef678` | AmbroseValley | Feb_12 | 0.76s | 1,124 | Balanced events |
| `d0a38c30-d476-4305-857d-ece9e65f72e6` | Lockdown | Feb_12 | 0.73s | 1,216 | Cross-map test |

## Notes

- Timeline slider is optimized for matches 0.3-1.0s in duration
- Matches with single timestamp show "This match has only one timestamp" message
- Heatmaps use 50x50 density bins for ~20px resolution
- Bot vs human classification: bots have numeric IDs < 10 chars; humans are UUIDs

## License

Internal use only - LILA Games
