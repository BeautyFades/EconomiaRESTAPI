import pandas as pd

df = pd.read_parquet('latest_selic.parquet')
json = df.iloc[0].to_json(orient='columns').replace('\\','')
print(json)