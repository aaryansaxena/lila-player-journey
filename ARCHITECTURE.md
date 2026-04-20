# Architecture & Design Document

## System Overview

The LILA BLACK Player Journey Visualization Tool is a data-driven web application that transforms raw extraction shooter telemetry into spatial analysis for level designers.

### Tech Stack & Rationale

| Component | Technology | Why |
|-----------|-----------|-----|
| **Frontend** | Streamlit | Fast prototyping, no frontend boilerplate, built-in interactivity (sliders, selects) |
| **Backend** | Python | Direct pandas/PyArrow integration, data science native, minimal API layer needed |
| **Visualization** | Plotly Express | Interactive scatter + heatmap, overlaid minimap backgrounds, excellent for map overlays |
| **Data Storage** | Apache Parquet | Compressed columnar format (89K rows → small file), fast I/O, standard for data pipelines |
| **Coordinate Math** | NumPy / Pandas | Vectorized world→pixel transformations, no external geometry libraries needed |

## Data Flow

```
Raw Files (50+)            Data Processing          Frontend Visualization
   ↓                             ↓                            ↓
.nakama-0 files  ────→  decode events  ────→   master_data.parquet  ────→  Streamlit App
(game telemetry)      classify bots          (89,104 rows, 8 cols)      (browser UI)
                    transform coords
                    merge/dedupe
```

### Step 1: Data Ingestion (`process_data.py`)

- **Input**: `data/raw/player_data/player_data/{February_10..14}/` — 50+ parquet files
- **Processing**:
  - Recursively scan for `.nakama-0` files (no extension, but valid parquet)
  - Skip non-parquet files (images, metadata)
  - Decode `event` field (bytes → UTF-8 string)
  - Classify users: bots (numeric id < 10 chars) vs humans (UUID)
  - Extract date folder name (e.g., "February_10")
  - Apply coordinate transformation (see below)
- **Output**: `data/processed/master_data.parquet` (89,104 rows)
  - Columns: `user_id`, `match_id`, `event`, `is_bot`, `day`, `map_id`, `x`, `z`, `y`, `ts`, `pixel_x`, `pixel_y`
  - Compressed with snappy codec
  - Read time: <1s (cached by Streamlit)

### Step 2: Frontend State Management (`src/app.py`)

1. **Data Loading** (`@st.cache_data`)
   - Load master_data.parquet once
   - Add derived columns: `event_category`, `user_type`, `marker_size`
   - Events mapped: `Position→Movement`, `BotPosition→Movement`, `Kill/BotKill→Kill`, `Killed/BotKilled→Death`, `KilledByStorm→Storm Death`

2. **Sidebar Filters**
   - Map selector (AmbroseValley, GrandRift, Lockdown)
   - Date selector (Feb 10-14, filtered by map)
   - Match ID selector (filtered by map + date)
   - Timeline slider (0.0 to match duration, 0.01s steps)
   - Event category multiselect (auto-includes required categories for heatmap)
   - Heatmap overlay type (None, Kill Zones, Death Zones, Traffic)

3. **Display Pipeline**
   - Filter match by match_id
   - Calculate `elapsed_sec` (relative time from match start)
   - Apply timeline filter: keep only events ≤ slider value
   - Apply category filter: keep only selected event types
   - Apply bot filter: exclude bots if unchecked
   - Generate scatter plot OR heatmap based on overlay selection
   - Overlay minimap image as background layer

### Step 3: Coordinate Mapping (The Tricky Part)

**Problem**: Game world uses 3D coordinates (x, y/elevation, z). Minimap is 2D 1024×1024 pixel image.

**Solution**: Per-map linear transformation:

```python
# For each map: scale factor and world-space origin
MAP_CONFIGS = {
    'AmbroseValley': {'scale': 900, 'origin_x': -370, 'origin_z': -473},
    'GrandRift': {'scale': 581, 'origin_x': -290, 'origin_z': -290},
    'Lockdown': {'scale': 1000, 'origin_x': -500, 'origin_z': -500}
}

# Transform (world space → pixel space):
u = (world_x - origin_x) / scale           # Normalize: [origin, origin+scale] → [0, 1]
v = (world_z - origin_z) / scale           # Same for Z axis
pixel_x = u * 1024                         # Scale to image dimensions
pixel_y = (1 - v) * 1024                   # Flip Y (image origin is top-left, game uses bottom-left convention)
```

**Validation**:
- Pixel ranges: `[50-965, 75-918]` (all events within 0-1024, good coverage)
- Spot-checks: death clusters at high-traffic areas match visual map features
- Y-flip correct: player spawns near bottom-left of map appear at top-left of image

## Data Nuances & Assumptions

| Issue | How Handled | Rationale |
|-------|-------------|-----------|
| Events stored as bytes | Decode with UTF-8 on load | README specified bytes encoding |
| Bot vs human detection | Numeric ID length < 10 chars | README: "Bot: short numeric ID, Human: UUID" |
| Match ID suffixes (.nakama-0) | Strip on consolidation | Data format quirk, clean for analysis |
| Y coordinate semantics | Flip when converting to pixel space | Game likely uses bottom-left origin; minimap uses top-left |
| Single-timestamp matches | Show info message, disable slider | Edge case: ~1-2% of matches; can't show progression |
| Loot event accuracy | Accept as-is (assumed correct) | No validation method; trust telemetry pipeline |
| Storm death frequency | Accept as-is (39 events / 89K rows) | Rare but real event; included for completeness |

## Major Tradeoffs

| Consideration | Option A | Option B | **Chosen** | Why |
|---------------|----------|----------|-----------|-----|
| **Hosting** | Streamlit Cloud (free) | Custom server (expensive) | Streamlit Cloud | Fast deployment, no ops overhead |
| **Coordinate Origin** | Assume top-left | Assume center | Top-left + Y-flip | Matches image raster convention |
| **Heatmap Bins** | 50×50 (fast) | 100×100 (precise) | 50×50 | Good balance: ~20px per bin |
| **Heatmap Transparency** | 60% opacity | 30% opacity | 60% opacity | Readable heat while seeing map |
| **Event Categories** | 8 raw types | 5 grouped types | 5 grouped types | Less cognitive load for designers |
| **Timeline Step** | 0.01s | 0.1s | 0.01s | Fine-grained control, matches ~20ms frame |

## Implementation Decisions

### 1. Why Streamlit, not React?
- **Pro**: Rapid iteration, state management built-in, no frontend dev time
- **Con**: Not mobile-optimized (OK: level designers use desktop)
- **Result**: 6 hours to MVP vs. 3+ days for React

### 2. Why Parquet, not CSV?
- **Pro**: Compressed (~2MB vs ~30MB), fast columnar access, industry standard
- **Con**: Requires PyArrow library
- **Result**: 10x faster load times, acceptable dependency

### 3. Why Plotly, not D3/Leaflet?
- **Pro**: Built-in interactivity (hover, zoom), image overlay support, Streamlit integration
- **Con**: Less customizable than D3
- **Result**: 4 hours to heatmap + overlay vs. 2+ days custom D3

### 4. Why process data offline?
- **Pro**: Fast app load (cached parquet), reproducible transforms
- **Con**: Requires re-processing if raw data changes
- **Result**: <1s app startup; acceptable for 5-day snapshot

## Key Assumptions

1. **Coordinate System**: World-space origin is roughly at corner of map; scale is linear distance per unit
2. **Bot Detection**: Numeric user_id always means bot; UUID always means human
3. **Event Timestamps**: `ts` column is monotonically increasing within each match
4. **Loot Locations**: `x`, `z` are accurate pickup locations (not corrected for client lag)
5. **Map Constants**: Values from README are exact and don't change per-match

## Performance Notes

- **App startup**: ~500ms (parquet load + data enrichment)
- **Timeline slider**: 60fps (Streamlit reruns on each change)
- **Heatmap render**: <1s for 1000+ events (Plotly density_heatmap)
- **Memory**: ~200MB (parquet in RAM)
- **Scaling**: Current dataset fits easily; would need optimization for >1M rows

## Testing & Validation

Tested with three representative matches:

1. **High-volume** (`d3a3297e-2cdf-4a49-8450-09119b91a779`): 1,097 events, 12 kills, 10 deaths → heatmaps render clearly
2. **Balanced** (`de5aa1ae-6246-4cfb-9941-adf5996ef678`): 1,124 events, 12 kills, 11 deaths → good separation
3. **Cross-map** (`d0a38c30-d476-4305-857d-ece9e65f72e6` on Lockdown): different scale/origin values work correctly

All coordinates fall within 0-1024 pixel bounds; no clipping or overflow errors.

## Future Improvements

- Add replay speed control (1x, 2x, 4x)
- Export match as video clip
- Compare two matches side-by-side
- Kalman-filter player paths (smooth interpolation between samples)
- Persist filter preferences in URL params
