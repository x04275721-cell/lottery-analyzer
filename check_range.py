import pandas as pd

df = pd.read_csv('pl3_full.csv')
print(f'数据: {len(df)}期')

# 计算3000期的范围
test_start = len(df) - 3000
print(f'测试起点: 第{test_start}期')
print(f'测试范围: 第{test_start}期 ~ 第{len(df)}期 (共{len(df)-test_start}期)')
