import pandas as pd
from collections import Counter
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('='*60)
print('振幅权重优化测试（简化版）')
print('='*60)

df = pd.read_csv('pl3_full.csv')
print(f'数据: {len(df)}期')

# 简化版振幅
def zhengfu(df_train):
    if len(df_train) < 5: return []
    recent_amps = []
    for i in range(1, min(11, len(df_train))):
        prev = df_train.iloc[i-1]
        curr = df_train.iloc[i]
        for pos in range(3):
            col = ['num1','num2','num3'][pos]
            amp = abs(int(curr[col]) - int(prev[col]))
            recent_amps.append(amp)
    
    last = df_train.iloc[-1]
    last_digits = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    amp_count = Counter(recent_amps)
    hot_amp = amp_count.most_common(1)[0][0]
    
    result = []
    for d in last_digits:
        result.append((d + hot_amp) % 10)
        result.append((d - hot_amp) % 10)
    
    return list(set(result))[:5]

# 快速测试
test_start = 1000  # 从第1000期开始，减少测试量
weights = [0, 2, 4, 6, 8]

print()
print('振幅权重测试:')
print('-'*40)

for weight in weights:
    hits = 0
    total = len(df) - test_start
    
    for i in range(test_start, len(df)):
        df_train = df.iloc[:i].copy()
        actual = df.iloc[i]
        actual_digits = set([int(actual['num1']), int(actual['num2']), int(actual['num3'])])
        
        # 计算分数
        scores = {d: 0 for d in range(10)}
        
        # 334断组
        last = df_train.iloc[-1]
        n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
        sum_tail = (n1 + n2 + n3) % 10
        if sum_tail in [0, 5]: g = [0,1,9,4,5,6,2,3,7,8]
        elif sum_tail in [1, 6]: g = [0,1,2,5,6,7,3,4,8,9]
        elif sum_tail in [2, 7]: g = [1,2,3,6,7,8,0,4,5,9]
        elif sum_tail in [3, 8]: g = [2,3,4,7,8,9,0,1,5,6]
        else: g = [3,4,5,8,9,0,1,2,6,7]
        for d in g[:7]: scores[d] += 14
        
        # 振幅
        zf = zhengfu(df_train)
        for d in zf: scores[d] += weight
        
        top5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_set = set([x[0] for x in top5])
        
        if actual_digits.issubset(top5_set):
            hits += 1
    
    rate = hits / total * 100
    label = '无' if weight == 0 else f'{weight}%'
    print(f'权重={label}: {rate:.2f}% ({hits}/{total})')

print('='*60)
