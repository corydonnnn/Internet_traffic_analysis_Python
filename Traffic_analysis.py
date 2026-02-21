import pandas as pd

df = pd.read_csv('internet_traffic_jan_feb_mar.csv')
#health check
print(df.head(), '\n')
print(df.tail(), '\n')
print(df.shape, '\n')
print(df.info(), '\n')
print(df.describe(), '\n') 

#converting to 0
print(df.isnull().sum(), '\n')
#removing corrupt rows
df = df.dropna(subset=['user_id', 'tariff_plan', 'region'])

#converting data
df['plan_limit_gb'] = pd.to_numeric(df['plan_limit_gb'], errors='coerce')
df['traffic_gb_used'] = pd.to_numeric(df['traffic_gb_used'], errors='coerce')

df['traffic_gb_used'] = df['traffic_gb_used'].fillna(0)
print(df.isnull().sum(), '\n')
#creating new column over_limit
df['over_limit'] = df['traffic_gb_used'] > df['plan_limit_gb']
print(df.head())

report1 = df.groupby('region').size().rename('records_count').reset_index() #group
report1 = report1.sort_values('records_count', ascending=False) #sorting values
print("-" * 50)
print("--- Report 1: Number of Subscribers by Region --- \n")
print(report1.to_string(index=False)) 
print("-" * 50)

target_regions = ['Bishkek', 'Osh']
df_r2 = df[df['region'].isin(target_regions)].copy()
report2 = df_r2.groupby('tariff_plan', as_index=False)['traffic_gb_used'].mean().rename(columns={'traffic_gb_used':'avg_traffic_gb_used'})
report2 = report2.sort_values('avg_traffic_gb_used', ascending=False).reset_index(drop=True)

print("--- Report 2: Subscribers from Target Regions --- \n")
print(report2.to_string(index=False))
print("-" * 50)

report3 = df[
    (df['region'] == 'Bishkek') &
    (df['tariff_plan'] == 'Standard') &
    (df['over_limit'] == True)][['user_id', 'traffic_gb_used', 'month']]

print("--- Report 3: Filter of Problematic Users --- \n")
print(report3.to_string(index=False))
print("-" * 50)

report4 = df.groupby('tariff_plan').agg(
    total_traffic = ('traffic_gb_used', 'sum'),
    avg_traffic = ('traffic_gb_used', 'mean'),
    unique_users = ('user_id', 'nunique')
).reset_index()

print("--- Report 4: Overall Summary by Tariff Plans --- \n")
print(report4.to_string(index=False))
print("-" * 50)

report5 = (df.groupby('region')['traffic_gb_used'].mean()
           .sort_values(ascending=False).head(5).reset_index()
           .rename(columns={'traffic_gb_used': 'avg_traffic_gb_used'}))

print(" --- Report 5: Top 5 Regions by Average Traffic --- \n")
print(report5.to_string(index=False))
print("-" * 50)

report6 = df.groupby('tariff_plan').agg(
    min_traffic_gb=('traffic_gb_used', 'min'),
    max_traffic_gb=('traffic_gb_used', 'max')
).reset_index()

print("--- Report 6: Traffic Extremes by Tariff Plans --- \n")
print(report6.to_string(index=False))
print("-" * 50)

df_r7 = df[df['tariff_plan'] != 'Unlimited'].copy()
report7 = df_r7.groupby('tariff_plan').agg(
    total_users=('user_id', 'nunique'),
    overlimit_users=('over_limit', lambda x: df_r7.loc[x.index, 'user_id'][x].nunique())
).reset_index()
report7['percent_overlimit'] = (report7['overlimit_users'] / report7['total_users']) * 100

print(" --- Report 7: Analysis of Limit Exceedances --- \n ")
print(report7.to_string(index=False))
print("-" * 50)

report8 = pd.pivot_table(
    df,
    index='tariff_plan',
    columns='month',
    values='traffic_gb_used',
    aggfunc='sum',
    fill_value=0
)
print("--- Report 8: Monthly Traffic Dynamics --- \n")
print(report8)
print("-" * 50)












