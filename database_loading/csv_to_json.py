import pandas as pd
df = pd.read_csv (r'./rate_my_professor.csv')
df.to_json (r'./rate_my_professor.json')