import pandas as pd
df = pd.read_parquet('data/processed/master_data.parquet')

# This looks for matches that have more than 50 events (a full game)
match_counts = df['match_id'].value_counts()
busy_matches = match_counts[match_counts > 50].index.tolist()

print("COPY ONE OF THESE IDs:")
for m_id in busy_matches[:5]:
    print(m_id)
python -c "import pandas as pd; df=pd.read_parquet('data/processed/master_data.parquet'); print(df['match_id'].value_counts().head(5))"