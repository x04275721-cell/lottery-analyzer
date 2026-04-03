import pandas as pd
from collections import Counter
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('='*70)
print('优化后的振幅分析方法测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print(f'数据加载完成：共{len(df)}期')

# ============================================================
# 优化后的振幅分析方法
# ============================================================
def predict_zhengfu_optimized(df_train):
    """
    优化版振幅分析 - 精简推荐数字
    核心思路：
    1. 只关注振幅为0-4的情况（高频区域）
    2. 限制推荐数字数量（最多5个）
    3. 结合近期热振幅和上期号码
    """
    if len(df_train) < 5:
        return [0, 1, 2, 3, 4]
    
    # 计算振幅
    recent_amps = {0: [], 1: [], 2: []}
    for i in range(1, min(21, len(df_train))):  # 只看近20期
        prev = df_train.iloc[i-1]
        curr = df_train.iloc[i]
        for pos in range(3):
            col = ['num1', 'num2', 'num3'][pos]
            amp = abs(int(curr[col]) - int(prev[col]))
            recent_amps[pos].append(amp)
    
    # 获取上期号码
    last = df_train.iloc[-1]
    last_digits = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    # 统计每个位置最热的振幅
    result = []
    for pos in range(3):
        if recent_amps[pos]:
            amp_count = Counter(recent_amps[pos])
            hot_amp = amp_count.most_common(1)[0][0]
            
            # 只推荐振幅0-4的情况（高频）
            if hot_amp <= 4:
                c1 = (last_digits[pos] + hot_amp) % 10
                c2 = (last_digits[pos] - hot_amp) % 10
                result.extend([c1, c2])
    
    # 去重并限制数量
    result = list(set(result))[:5]
    
    # 如果结果少于3个，补充冷号
    if len(result) < 3:
        all_digits = [d for d in range(10) if d not in result]
        result.extend(all_digits[:3-len(result)])
    
    return result

# ============================================================
# 测试不同权重
# ============================================================
def predict_5ma_v1(df_train, weight):
    """权重测试版"""
    scores = {d: 0 for d in range(10)}
    
    # 334断组 (14%)
    def get_334_duanzu(last_nums):
        n1, n2, n3 = last_nums
        sum_tail = (n1 + n2 + n3) % 10
        if sum_tail in [0, 5]: return [0,1,9], [4,5,6], [2,3,7,8]
        elif sum_tail in [1, 6]: return [0,1,2], [5,6,7], [3,4,8,9]
        elif sum_tail in [2, 7]: return [1,2,3], [6,7,8], [0,4,5,9]
        elif sum_tail in [3, 8]: return [2,3,4], [7,8,9], [0,1,5,6]
        else: return [3,4,5], [8,9,0], [1,2,6,7]
    
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    g1, g2, g3 = get_334_duanzu(last_nums)
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    if g1_count <= g2_count and g1_count <= g3_count: top334 = g2 + g3
    elif g2_count <= g1_count and g2_count <= g3_count: top334 = g1 + g3
    else: top334 = g1 + g2
    for d in top334: scores[d] += 14
    
    # 五五分解 (9%)
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
    for d in (best_group if best_group else [0,1,2,3,4]): scores[d] += 9
    
    # 两码进位和差 (6%)
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    all_nums2 = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums2)
    for d, c in num_count.most_common(3): scores[d] += 6
    
    # 012路 (6%)
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df_train[col].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums: route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        for d in route_map[hot_route]: scores[d] += 6
    
    # 奇偶 (4%)
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    for d in ([1, 3, 5, 7, 9] if odd_count > even_count else [0, 2, 4, 6, 8]): scores[d] += 4
    
    # 形态 (4%)
    all_nums3 = []
    for _, row in df_train.tail(30).iterrows():
        all_nums3.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    big_count = sum(1 for n in all_nums3 if n >= 5)
    small_count = len(all_nums3) - big_count
    prime = [2, 3, 5, 7]
    prime_count = sum(1 for n in all_nums3 if n in prime)
    if big_count > small_count: hot_nums = [5, 6, 7, 8, 9]
    else: hot_nums = [0, 1, 2, 3, 4]
    if prime_count > (len(all_nums3) - prime_count): hot_nums.extend(prime)
    else: hot_nums.extend([0, 1, 4, 6, 8, 9])
    for d in set(hot_nums): scores[d] += 4
    
    # 和值尾 (7%)
    sums = []
    for _, row in df_train.tail(30).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        sums.append(s % 10)
    sum_count = Counter(sums)
    hot_sums = [n for n, c in sum_count.most_common(3)]
    for tail in hot_sums:
        scores[tail] += 7
        scores[(tail + 5) % 10] += 7
    
    # 大小单双 (3%)
    big_small = ['大' if n >= 5 else '小' for n in [n1, n2, n3]]
    odd_even = ['单' if n % 2 == 1 else '双' for n in [n1, n2, n3]]
    big_dan = sum(1 for i in range(3) if big_small[i] == '大' and odd_even[i] == '单')
    small_shuang = sum(1 for i in range(3) if big_small[i] == '小' and odd_even[i] == '双')
    for d in ([0, 2, 4] if big_dan > small_shuang else [5, 7, 9]): scores[d] += 3
    
    # 振幅分析（优化版）- 可调权重
    zhengfu = predict_zhengfu_optimized(df_train)
    for d in zhengfu: scores[d] += weight
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 测试不同权重
# ============================================================
print()
print('='*70)
print('测试不同振幅权重')
print('='*70)

test_start = 100
weights = [0, 1, 2, 3, 4, 5]

for weight in weights:
    total_tests = len(df) - test_start
    hits = 0
    
    for i in range(test_start, len(df)):
        df_train = df.iloc[:i].copy()
        actual = df.iloc[i]
        actual_digits = set([int(actual['num1']), int(actual['num2']), int(actual['num3'])])
        
        top5 = predict_5ma_v1(df_train, weight)
        
        if actual_digits.issubset(set(top5)):
            hits += 1
    
    hit_rate = hits / total_tests * 100
    label = '无振幅' if weight == 0 else f'{weight}%'
    print(f'振幅权重={label}: 命中率 {hit_rate:.2f}%')

print()
print('='*70)
print('结论：选择命中率最高的权重作为最终配置')
print('='*70)
