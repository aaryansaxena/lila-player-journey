import pandas as pd
df = pd.read_parquet('data/processed/master_data.parquet')

# 1. Find a match with BOTH Humans and Bots (to see Circles & Diamonds)
mixed_matches = df.groupby('match_id').filter(lambda x: x['is_bot'].nunique() > 1)
print("--- IDs with both Humans & Bots ---")
print(mixed_matches['match_id'].unique()[:3])

# 2. Find a match with Kills (to see the Heatmap)
combat_matches = df[df['event'].str.contains('Kill|Killed', case=False)]
print("\n--- IDs with Kills (Heatmap will work here) ---")
print(combat_matches['match_id'].unique()[:3])