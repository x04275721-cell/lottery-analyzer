import pandas as pd
from collections import Counter
import random
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('='*70)
print('命中率验证测试')
print('='*70)

# 读取数据
df = pd.read_csv('pl3_full.csv')
print(f'数据加载完成：共{len(df)}期')

# ============================================================
# 方法定义（与V5.1相同）
# ============================================================
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
    big_small = ['大' if n >= 5 else '小' for n in [n1, n2, n3]]
    odd_even = ['单' if n % 2 == 1 else '双' for n in [n1, n2, n3]]
    big_dan = sum(1 for i in range(3) if big_small[i] == '大' and odd_even[i] == '单')
    small_shuang = sum(1 for i in range(3) if big_small[i] == '小' and odd_even[i] == '双')
    if big_dan > small_shuang:
        return [0, 2, 4]
    else:
        return [5, 7, 9]

def predict_zhengfu(df_train):
    if len(df_train) < 2:
        return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    amplitudes = {0: [], 1: [], 2: []}
    for i in range(1, min(31, len(df_train))):
        prev = df_train.iloc[i-1]
        curr = df_train.iloc[i]
        for pos in range(3):
            col = ['num1', 'num2', 'num3'][pos]
            amp = abs(int(curr[col]) - int(prev[col]))
            amplitudes[pos].append(amp)
    hot_amplitudes = {}
    for pos in range(3):
        amp_count = Counter(amplitudes[pos])
        hot_amp = [amp for amp, count in amp_count.most_common(2)]
        hot_amplitudes[pos] = hot_amp
    last = df_train.iloc[-1]
    last_digits = [int(last['num1']), int(last['num2']), int(last['num3'])]
    result = []
    for pos in range(3):
        for amp in hot_amplitudes[pos]:
            candidate1 = (last_digits[pos] + amp) % 10
            candidate2 = (last_digits[pos] - amp) % 10
            result.extend([candidate1, candidate2])
    return list(set(result))

def predict_5ma(df_train):
    scores = {d: 0 for d in range(10)}
    for d in predict_334(df_train): scores[d] += 14
    for d in predict_55fenjie(df_train): scores[d] += 9
    for d in predict_liangma(df_train): scores[d] += 6
    for d in predict_012lu(df_train): scores[d] += 6
    for d in predict_jiou(df_train): scores[d] += 4
    for d in predict_xingtai(df_train): scores[d] += 4
    for d in predict_sum_tail(df_train): scores[d] += 7
    for d in predict_daxiao(df_train): scores[d] += 3
    for d in predict_zhengfu(df_train): scores[d] += 5
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top5 = [n for n, s in sorted_nums[:5]]
    return top5

# ============================================================
# 验证测试
# ============================================================
print()
print('='*70)
print('测试：组选五码命中率')
print('='*70)

# 从第100期开始测试（确保有足够的历史数据）
test_start = 100
total_tests = len(df) - test_start
hits = 0

for i in range(test_start, len(df)):
    # 训练数据
    df_train = df.iloc[:i].copy()
    # 测试数据
    actual = df.iloc[i]
    actual_num = str(actual['num1']) + str(actual['num2']) + str(actual['num3'])
    actual_digits = set([int(actual['num1']), int(actual['num2']), int(actual['num3'])])
    
    # 预测
    top5 = predict_5ma(df_train)
    top5_set = set(top5)
    
    # 命中判定：五码中是否包含开奖号码的三个数字
    if actual_digits.issubset(top5_set):
        hits += 1

hit_rate = hits / total_tests * 100
print(f'测试范围：第{test_start}期 ~ 第{len(df)}期')
print(f'总测试次数：{total_tests}')
print(f'命中次数：{hits}')
print(f'命中率：{hit_rate:.2f}%')
print(f'理论概率：8.33%')
print(f'提升幅度：+{(hit_rate - 8.33):.2f}%')

print()
print('='*70)
