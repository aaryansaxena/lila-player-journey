import pandas as pd
import pyarrow.parquet as pq
import os
from pathlib import Path

# 1. Map Configurations from the README
MAP_CONFIGS = {
    'AmbroseValley': {'scale': 900, 'origin_x': -370, 'origin_z': -473},
    'GrandRift': {'scale': 581, 'origin_x': -290, 'origin_z': -290},
    'Lockdown': {'scale': 1000, 'origin_x': -500, 'origin_z': -500}
}

def world_to_pixel(row):
    """Converts game (x, z) to 1024x1024 pixel (u, v) coordinates."""
    config = MAP_CONFIGS.get(row['map_id'])
    if not config or pd.isna(row['x']) or pd.isna(row['z']):
        return pd.Series([None, None])
    
    # Step 1: Convert world coords to UV (0-1 range)
    u = (row['x'] - config['origin_x']) / config['scale']
    v = (row['z'] - config['origin_z']) / config['scale']
    
    # Step 2: Convert UV to pixel coords (1024x1024 image)
    pixel_x = u * 1024
    pixel_y = (1 - v) * 1024  # Y is flipped because image origin is top-left
    
    return pd.Series([pixel_x, pixel_y])

def process_all_data(input_dir, output_file):
    all_frames = []
    input_path = Path(input_dir)
    
    print(f"Scanning directory: {input_path}")
    
    # rglob('*') finds everything recursively through nested folders
    for file_path in input_path.rglob('*'):
        
        # SKIP: directories, hidden files, and IMAGES
        if not file_path.is_file() or file_path.name.startswith('.'):
            continue
        
        # Skip known non-parquet extensions
        if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.ds_store', '.md']:
            continue

        try:
            # Load the Parquet data
            df = pd.read_parquet(file_path)
            
            # A. Decode 'event' from bytes to string
            df['event'] = df['event'].apply(
                lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
            )
            
            # B. Identify bots vs humans (Bot IDs are short numeric strings)
            df['is_bot'] = df['user_id'].str.len() < 10
            
            # C. Store the date folder name (e.g., February_10)
            df['day'] = file_path.parent.name 
            
            all_frames.append(df)
        except Exception:
            # If a file isn't actually a parquet file, skip it
            continue

    if not all_frames:
        print("Error: No data found. Please double-check your RAW_DATA_DIR path!")
        return

    # Combine all individual player files
    print(f"Merging {len(all_frames)} files...")
    master_df = pd.concat(all_frames, ignore_index=True)
    
    # D. Clean Match IDs (remove the .nakama-0 suffix)
    master_df['match_id'] = master_df['match_id'].str.replace('.nakama-0', '', regex=False)
    
    # E. Apply the coordinate transform
    print("Calculating pixel coordinates for the maps...")
    master_df[['pixel_x', 'pixel_y']] = master_df.apply(world_to_pixel, axis=1)
    
    # F. Save as one optimized master file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # We use 'fastparquet' or 'pyarrow' to save. index=False keeps it clean.
    master_df.to_parquet(output_path, index=False, compression='snappy')
    
    print("-" * 30)
    print(f"SUCCESS!")
    print(f"Total Rows Processed: {len(master_df)}")
    print(f"Master File Created: {output_file}")
    print("-" * 30)

if __name__ == "__main__":
    # Update these paths to match your local setup exactly
    RAW_DATA_DIR = r'C:\Users\rj\OneDrive\Desktop\lila-player-journey\data\raw\player_data\player data'
    OUTPUT_FILE = r'data\processed\master_data.parquet'
    
    process_all_data(RAW_DATA_DIR, OUTPUT_FILE)