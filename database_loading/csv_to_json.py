import pandas as pd
df = pd.read_csv (r'./ManualColumnPicking.csv')
df.to_json (r'./ManualColumnPicking.json')