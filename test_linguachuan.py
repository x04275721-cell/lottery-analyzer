#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邻孤传 + 聪明组六测试
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('邻孤传 + 聪明组六测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 聪明组六31注
# ============================================================
SMART_ZU6 = [
    27, 35, 37, 38, 45, 47, 56, 57, 58, 67, 78,
    126, 129, 136, 138, 156, 167, 236, 238, 239,
    249, 256, 259, 267, 269, 346, 347, 348, 349, 356, 358
]

# 基础方法
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
    counts = [(g1, g1_count), (g2, g2_count), (g3, g3_count)]
    counts.sort(key=lambda x: x[1], reverse=True)
    scores = {d: 0 for d in range(10)}
    for d in counts[0][0]: scores[d] += 14
    for d in counts[1][0]: scores[d] += 10
    for d in counts[2][0]: scores[d] += 2
    return scores

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
    return {d: 9 for d in best_group}

def predict_liangma(df_train):
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    result = [n for n, c in num_count.most_common(3)]
    return {d: 6 for d in result}

def predict_012lu(df_train):
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    hot_nums = []
    for pos in range(3):
        nums = df_train['num%d' % (pos+1)].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums: route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        hot_nums.extend(route_map[hot_route])
    return {d: 6 for d in set(hot_nums)}

def predict_jiou(df_train):
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    scores = {d: 0 for d in range(10)}
    if odd_count > even_count:
        for d in [1,3,5,7,9]: scores[d] += 14
        for d in [0,2,4,6,8]: scores[d] += 2
    else:
        for d in [0,2,4,6,8]: scores[d] += 14
        for d in [1,3,5,7,9]: scores[d] += 2
    return scores

def predict_xingtai(df_train):
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    big_count = sum(1 for n in all_nums if n >= 5)
    small_count = len(all_nums) - big_count
    prime = [2, 3, 5, 7]
    prime_count = sum(1 for n in all_nums if n in prime)
    hot_nums = []
    if big_count > small_count: hot_nums.extend([5, 6, 7, 8, 9])
    else: hot_nums.extend([0, 1, 2, 3, 4])
    if prime_count > len(all_nums) - prime_count: hot_nums.extend(prime)
    else: hot_nums.extend([0, 1, 4, 6, 8, 9])
    return {d: 4 for d in set(hot_nums)}

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
    return {d: 7 for d in list(set(result))[:5]}

def is_banshun(nums):
    n1, n2, n3 = sorted(nums)
    if abs(n1-n2) == 1 or abs(n2-n3) == 1 or abs(n1-n3) == 1:
        return True
    return False

def predict_banshun(df_train):
    recent = df_train.tail(50)
    consecutive_counts = Counter()
    for _, row in recent.iterrows():
        nums = sorted([int(row['num1']), int(row['num2']), int(row['num3'])])
        for i in range(3):
            for j in range(i+1, 3):
                if abs(nums[j] - nums[i]) == 1:
                    consecutive_counts[(min(nums[i], nums[j]), max(nums[i], nums[j]))] += 1
    
    digit_counts = Counter()
    for _, row in recent.iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        if is_banshun(nums):
            for d in nums:
                digit_counts[d] += 1
    
    hot_pairs = [p[0] for p in consecutive_counts.most_common(3)]
    hot_digits = [d[0] for d in digit_counts.most_common(3)]
    
    result = []
    for pair in hot_pairs:
        result.extend(pair)
    result.extend(hot_digits)
    
    return {d: 3 for d in set(result)}

# ============================================================
# 邻孤传分析
# ============================================================
def get_lin_gua_chuan(last_nums):
    """获取上期的邻孤传分类"""
    chuan = set(last_nums)  # 传号
    lin = set()
    for n in last_nums:
        if n > 0: lin.add(n - 1)
        if n < 9: lin.add(n + 1)
    gu = set(range(10)) - chuan - lin
    return chuan, lin, gu

def predict_lin_gua_chuan(df_train):
    """邻孤传分析：优先1邻1孤1传形态"""
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 2:
        return scores
    
    # 获取上期号码
    last = df_train.iloc[-1]
    last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
    chuan, lin, gu = get_lin_gua_chuan(last_nums)
    
    # 1邻1孤1传是最常见形态，给相应号码加分
    # 传号（重复号）
    for d in chuan:
        scores[d] += 3  # 重复号有一定概率
    
    # 邻号（上期±1）
    for d in lin:
        scores[d] += 4  # 邻号概率最高
    
    # 孤号（冷号）
    for d in gu:
        scores[d] += 1  # 孤号概率最低
    
    return scores

# ============================================================
# 聪明组六过滤
# ============================================================
def is_smart_zu6(nums):
    """判断是否为聪明组六"""
    n1, n2, n3 = sorted(nums)
    num_str = ''.join(map(str, [n1, n2, n3]))
    
    # 检查是否在31注列表中
    for s in SMART_ZU6:
        s_str = str(s).zfill(3)
        if sorted([int(c) for c in s_str]) == sorted(nums):
            return True
    return False

def filter_smart_zu6(top5_candidates):
    """从候选中过滤出聪明组六"""
    smart_nums = []
    for nums in top5_candidates:
        if is_smart_zu6(nums):
            smart_nums.append(nums)
    return smart_nums

# ============================================================
# 预测函数
# ============================================================
def predict_8methods(df_train):
    scores = {d: 0 for d in range(10)}
    for d, s in predict_334(df_train).items(): scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): scores[d] += s
    for d, s in predict_liangma(df_train).items(): scores[d] += s
    for d, s in predict_012lu(df_train).items(): scores[d] += s
    for d, s in predict_jiou(df_train).items(): scores[d] += s
    for d, s in predict_xingtai(df_train).items(): scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): scores[d] += s
    for d, s in predict_banshun(df_train).items(): scores[d] += s
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

def predict_9methods(df_train):
    """8方法 + 邻孤传"""
    scores = {d: 0 for d in range(10)}
    for d, s in predict_334(df_train).items(): scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): scores[d] += s
    for d, s in predict_liangma(df_train).items(): scores[d] += s
    for d, s in predict_012lu(df_train).items(): scores[d] += s
    for d, s in predict_jiou(df_train).items(): scores[d] += s
    for d, s in predict_xingtai(df_train).items(): scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): scores[d] += s
    for d, s in predict_banshun(df_train).items(): scores[d] += s
    for d, s in predict_lin_gua_chuan(df_train).items(): scores[d] += s  # +邻孤传
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 测试
# ============================================================
def test_predict(predict_func, name, test_count=5000):
    random.seed(42)
    results = []
    total = min(test_count, len(df) - 600)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_func(df_train))
        hit = len(real_set & top5_set) == len(real_set)
        results.append(hit)
    
    total_hits = sum(results)
    hit_rate = total_hits / len(results) * 100
    
    max_streak, current_streak = 0, 0
    max_miss, current_miss = 0, 0
    for r in results:
        if r:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
            current_miss = 0
        else:
            current_miss += 1
            max_miss = max(max_miss, current_miss)
            current_streak = 0
    
    return {
        'name': name,
        'total': len(results),
        'hits': total_hits,
        'hit_rate': hit_rate,
        'max_streak': max_streak,
        'max_miss': max_miss
    }

print('\n测试聪明组六31注单独命中率...')
def predict_smart_zu6_only(df_train):
    # 随机从31注中选1注作为推荐
    random.seed(hash(str(len(df_train))) % 10000)
    idx = random.randint(0, len(SMART_ZU6) - 1)
    num = str(SMART_ZU6[idx]).zfill(3)
    return [int(num[0]), int(num[1]), int(num[2])]

zu6_hits = 0
zu6_total = 0
zu6_misses = []
current_miss = 0
max_miss_zu6 = 0

for i in range(100, min(5000, len(df) - 600)):
    df_train = df.iloc[max(0, i-500):i]
    if len(df_train) < 100: continue
    
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    pred = predict_smart_zu6_only(df_train)
    
    if set(pred) == set(real):
        zu6_hits += 1
        zu6_misses.append(current_miss)
        max_miss_zu6 = max(max_miss_zu6, current_miss)
        current_miss = 0
    else:
        current_miss += 1
    zu6_total += 1

zu6_rate = zu6_hits / zu6_total * 100
print('聪明组六31注: %.2f%% | 最大不中%d期' % (zu6_rate, max_miss_zu6))

print('\n测试8种方法...')
r1 = test_predict(predict_8methods, '8种方法', 5000)
print('8种方法: %.2f%% | 最大连中%d | 最大不中%d' % (r1['hit_rate'], r1['max_streak'], r1['max_miss']))

print('\n测试9种方法（+邻孤传）...')
r2 = test_predict(predict_9methods, '9种方法', 5000)
print('9种方法: %.2f%% | 最大连中%d | 最大不中%d' % (r2['hit_rate'], r2['max_streak'], r2['max_miss']))

print()
print('='*70)
print('结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 提升 | 最大连中 | 最大不中 |')
print('|------|--------|------|---------|---------|')
print('| 聪明组六31注 | %.2f%% | - | - | %d期 |' % (zu6_rate, max_miss_zu6))
print('| 8种方法 | %.2f%% | - | %d期 | %d期 |' % (r1['hit_rate'], r1['max_streak'], r1['max_miss']))
print('| 9种方法 | %.2f%% | %+.2f%% | %d期 | %d期 |' % (r2['hit_rate'], r2['hit_rate']-r1['hit_rate'], r2['max_streak'], r2['max_miss']))
print()
print('='*70)