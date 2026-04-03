import pandas as pd

df = pd.read_csv('pl3_full.csv')
print('数据样例：')
print(df.tail(10))
print()

# 计算和值尾分布
df['sum_tail'] = (df['num1'].astype(int) + df['num2'].astype(int) + df['num3'].astype(int)) % 10
print('和值尾分布（近100期）：')
print(df['sum_tail'].tail(100).value_counts().sort_index())
