import pandas as pd
from collections import Counter
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('='*60)
print('完整系统命中率测试')
print('='*60)

df = pd.read_csv('pl3_full.csv')
print(f'数据: {len(df)}期')

# 完整方法
def get_334_duanzu(last_nums):
    n1, n2, n3 = last_nums
    sum_tail = (n1 + n2 + n3) % 10
    if sum_tail in [0, 5]: return [0,1,9], [4,5,6], [2,3,7,8]
    elif sum_tail in [1, 6]: return [0,1,2], [5,6,7], [3,4,8,9]
    elif sum_tail in [2, 7]: return [1,2,3], [6,7,8], [0,4,5,9]
    elif sum_tail in [3, 8]: return [2,3,4], [7,8,9], [0,1,5,6]
    else: return [3,4,5], [8,9,0], [1,2,6,7]

def predict_334(df_train):
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    g1, g2, g3 = get_334_duanzu(last_nums)
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    if g1_count <= g2_count and g1_count <= g3_count: return g2 + g3
    elif g2_count <= g1_count and g2_count <= g3_count: return g1 + g3
    else: return g1 + g2

def predict_55fenjie(df_train):
    decompositions = [
        ([0,1,2,3,4], [5,6,7,8,9]),
        ([1,3,5,7,9], [0,2,4,6,8]),
        ([2,3,5,7,0], [1,4,6,8,9]),
        ([0,1,4,5,8], [2,3,6,7,9]),
    ]
    best_group, best_score = None, -1
    for g1, g2 in decompositions:
        all_nums = []
        for _, row in df_train.tail(10).iterrows():
            all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
        g1_count = sum(1 for n in all_nums if n in g1)
        g2_count = sum(1 for n in all_nums if n in g2)
        if g1_count > g2_count: score, group = g1_count, g1
        else: score, group = g2_count, g2
        if score > best_score: best_score, best_group = score, group
    return best_group if best_group else [0,1,2,3,4]

def predict_liangma(df_train):
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    return [n for n, c in num_count.most_common(3)]

def predict_012lu(df_train):
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    hot_nums = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df_train[col].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums: route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        hot_nums.extend(route_map[hot_route])
    return list(set(hot_nums))

def predict_jiou(df_train):
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    if odd_count > even_count: return [1, 3, 5, 7, 9]
    else: return [0, 2, 4, 6, 8]

def predict_xingtai(df_train):
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    big_count = sum(1 for n in all_nums if n >= 5)
    small_count = len(all_nums) - big_count
    prime = [2, 3, 5, 7]
    prime_count = sum(1 for n in all_nums if n in prime)
    composite_count = len(all_nums) - prime_count
    hot_nums = []
    if big_count > small_count: hot_nums.extend([5, 6, 7, 8, 9])
    else: hot_nums.extend([0, 1, 2, 3, 4])
    if prime_count > composite_count: hot_nums.extend(prime)
    else: hot_nums.extend([0, 1, 4, 6, 8, 9])
    return list(set(hot_nums))

def predict_sum_tail(df_train):
    sums = []
    for _, row in df_train.tail(30).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        sums.append(s % 10)
    sum_count = Counter(sums)
    hot_sums = [n for n, c in sum_count.most_common(3)]
    result = []
    for tail in hot_sums:
        result.append(tail)
        result.append((tail + 5) % 10)
    return list(set(result))[:5]

def predict_daxiao(df_train):
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    big_dan = sum(1 for i, n in enumerate([n1,n2,n3]) if n >= 5 and n % 2 == 1)
    small_shuang = sum(1 for i, n in enumerate([n1,n2,n3]) if n < 5 and n % 2 == 0)
    return [0, 2, 4] if big_dan > small_shuang else [5, 7, 9]

def predict_zhengfu(df_train):
    """振幅分析"""
    if len(df_train) < 2: return [0, 1, 2, 3, 4]
    amplitudes = {0: [], 1: [], 2: []}
    for i in range(1, min(21, len(df_train))):
        prev = df_train.iloc[i-1]
        curr = df_train.iloc[i]
        for pos in range(3):
            col = ['num1', 'num2', 'num3'][pos]
            amp = abs(int(curr[col]) - int(prev[col]))
            amplitudes[pos].append(amp)
    last = df_train.iloc[-1]
    last_digits = [int(last['num1']), int(last['num2']), int(last['num3'])]
    result = []
    for pos in range(3):
        if amplitudes[pos]:
            amp_count = Counter(amplitudes[pos])
            hot_amp = amp_count.most_common(1)[0][0]
            if hot_amp <= 4:
                result.append((last_digits[pos] + hot_amp) % 10)
                result.append((last_digits[pos] - hot_amp) % 10)
    return list(set(result))[:5]

def predict_5ma(df_train, use_zhengfu=True):
    scores = {d: 0 for d in range(10)}
    for d in predict_334(df_train): scores[d] += 14
    for d in predict_55fenjie(df_train): scores[d] += 9
    for d in predict_liangma(df_train): scores[d] += 6
    for d in predict_012lu(df_train): scores[d] += 6
    for d in predict_jiou(df_train): scores[d] += 4
    for d in predict_xingtai(df_train): scores[d] += 4
    for d in predict_sum_tail(df_train): scores[d] += 7
    for d in predict_daxiao(df_train): scores[d] += 3
    if use_zhengfu:
        for d in predict_zhengfu(df_train): scores[d] += 5
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# 测试
test_start = 100

print()
print('='*60)
print('测试结果')
print('='*60)

# 版本1：无振幅
hits1, hits2 = 0, 0
total = len(df) - test_start

for i in range(test_start, len(df)):
    df_train = df.iloc[:i].copy()
    actual = df.iloc[i]
    actual_digits = set([int(actual['num1']), int(actual['num2']), int(actual['num3'])])
    
    top5_v1 = predict_5ma(df_train, use_zhengfu=False)
    top5_v2 = predict_5ma(df_train, use_zhengfu=True)
    
    if actual_digits.issubset(set(top5_v1)): hits1 += 1
    if actual_digits.issubset(set(top5_v2)): hits2 += 1

print()
print(f'V5.0 (无振幅): {(hits1/total*100):.2f}% ({hits1}/{total})')
print(f'V5.1 (有振幅): {(hits2/total*100):.2f}% ({hits2}/{total})')
print()
print(f'理论概率: 8.33%')
print(f'提升: +{(hits1/total*100-8.33):.2f}% (V5.0) / +{(hits2/total*100-8.33):.2f}% (V5.1)')
print()
if hits1 > hits2:
    print('结论: V5.0 无振幅版本效果更好')
else:
    print('结论: V5.1 有振幅版本效果更好')
print('='*60)
