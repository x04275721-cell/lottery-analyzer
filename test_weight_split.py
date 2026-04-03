#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重测试：热号14，中号和冷号平分
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('权重测试：热号14，中号冷号平分')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

def get_334_duanzu(last_nums):
    n1, n2, n3 = last_nums
    sum_tail = (n1 + n2 + n3) % 10
    if sum_tail in [0, 5]: return [0,1,9], [4,5,6], [2,3,7,8]
    elif sum_tail in [1, 6]: return [0,1,2], [5,6,7], [3,4,8,9]
    elif sum_tail in [2, 7]: return [1,2,3], [6,7,8], [0,4,5,9]
    elif sum_tail in [3, 8]: return [2,3,4], [7,8,9], [0,1,5,6]
    else: return [3,4,5], [8,9,0], [1,2,6,7]

def predict_334_weighted(df_train, hot_w, mid_w, cold_w):
    """334断组 - 可调权重"""
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
    for d in counts[0][0]: scores[d] += hot_w
    for d in counts[1][0]: scores[d] += mid_w
    for d in counts[2][0]: scores[d] += cold_w
    
    return scores

def predict_jiou_weighted(df_train, hot_w, cold_w):
    """奇偶 - 可调权重"""
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    
    scores = {d: 0 for d in range(10)}
    if odd_count > even_count:
        for d in [1,3,5,7,9]: scores[d] += hot_w
        for d in [0,2,4,6,8]: scores[d] += cold_w
    else:
        for d in [0,2,4,6,8]: scores[d] += hot_w
        for d in [1,3,5,7,9]: scores[d] += cold_w
    
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
    return best_group

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
        nums = df_train['num%d' % (pos+1)].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums: route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        hot_nums.extend(route_map[hot_route])
    return list(set(hot_nums))

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

def predict_5ma_weighted(df_train, hot_w, mid_w, cold_w):
    """综合预测 - 可调权重"""
    scores = {d: 0 for d in range(10)}
    
    # 334断组
    s334 = predict_334_weighted(df_train, hot_w, mid_w, cold_w)
    for d, s in s334.items(): scores[d] += s * 14 / hot_w
    
    # 其他方法
    for d in predict_55fenjie(df_train): scores[d] += 9
    for d in predict_liangma(df_train): scores[d] += 6
    for d in predict_012lu(df_train): scores[d] += 6
    
    # 奇偶
    sjiou = predict_jiou_weighted(df_train, 8, cold_w)
    for d, s in sjiou.items(): scores[d] += s * 4 / 8
    
    for d in predict_xingtai(df_train): scores[d] += 4
    for d in predict_sum_tail(df_train): scores[d] += 7
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

def test_weight(hot_w, mid_w, cold_w, name, test_count=5000):
    random.seed(42)
    full_hit, at_least_2, at_least_1 = 0, 0, 0
    total = min(test_count, len(df) - 600)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_5ma_weighted(df_train, hot_w, mid_w, cold_w))
        hit_count = len(real_set & top5_set)
        
        if hit_count == len(real_set): full_hit += 1
        if hit_count >= 2: at_least_2 += 1
        if hit_count >= 1: at_least_1 += 1
    
    return {
        'name': name,
        'full_hit': full_hit/total*100,
        'at_least_2': at_least_2/total*100,
        'at_least_1': at_least_1/total*100
    }

# 测试多种权重配置
print('\n测试多种权重配置...\n')

configs = [
    (14, 9, 3, '热14-中9-冷3 (当前)'),
    (14, 6, 6, '热14-中6-冷6 (平分)'),
    (14, 7, 7, '热14-中7-冷7 (平分)'),
    (14, 8, 8, '热14-中8-冷8 (平分)'),
    (14, 5, 5, '热14-中5-冷5 (平分)'),
    (14, 4, 4, '热14-中4-冷4 (平分)'),
    (14, 10, 2, '热14-中10-冷2'),
    (14, 12, 1, '热14-中12-冷1'),
]

results = []
for hot_w, mid_w, cold_w, name in configs:
    print('测试: %s' % name)
    r = test_weight(hot_w, mid_w, cold_w, name, 5000)
    results.append(r)
    print('  全中: %.2f%% | 至少2: %.2f%% | 至少1: %.2f%%' % (r['full_hit'], r['at_least_2'], r['at_least_1']))

print()
print('='*70)
print('权重测试结果排名')
print('='*70)
print()

# 按命中率排序
results.sort(key=lambda x: x['full_hit'], reverse=True)

print('| 排名 | 配置 | 全中命中率 | 至少2个 | 至少1个 |')
print('|------|------|-----------|---------|---------|')
for i, r in enumerate(results, 1):
    print('| %d | %s | %.2f%% | %.2f%% | %.2f%% |' % (i, r['name'], r['full_hit'], r['at_least_2'], r['at_least_1']))

print()
print('='*70)