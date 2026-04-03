#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连续命中测试 - 5700期
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('连续命中测试 - 5700期')
print('='*70)

# 加载数据
df_pl3 = pd.read_csv('pl3_full.csv')
df_3d = pd.read_csv('fc3d_5years.csv')
print('排列三数据: %d期' % len(df_pl3))
print('3D数据: %d期' % len(df_3d))

# 方法函数
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

def predict_5ma(df_train):
    scores = {d: 0 for d in range(10)}
    
    for d, s in predict_334(df_train).items(): scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): scores[d] += s
    for d, s in predict_liangma(df_train).items(): scores[d] += s
    for d, s in predict_012lu(df_train).items(): scores[d] += s
    for d, s in predict_jiou(df_train).items(): scores[d] += s
    for d, s in predict_xingtai(df_train).items(): scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): scores[d] += s
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

def test_consecutive(df, name, test_count=5700):
    random.seed(42)
    results = []
    total = min(test_count, len(df) - 100)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_5ma(df_train))
        hit = len(real_set & top5_set) == len(real_set)
        results.append(hit)
    
    # 统计
    total_hits = sum(results)
    hit_rate = total_hits / len(results) * 100
    
    # 最大连中
    max_streak = 0
    current_streak = 0
    for r in results:
        if r:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    # 最大不中
    max_miss = 0
    current_miss = 0
    for r in results:
        if not r:
            current_miss += 1
            max_miss = max(max_miss, current_miss)
        else:
            current_miss = 0
    
    return {
        'name': name,
        'total': len(results),
        'hits': total_hits,
        'hit_rate': hit_rate,
        'max_streak': max_streak,
        'max_miss': max_miss
    }

print('\n测试排列三...')
pl3_result = test_consecutive(df_pl3, '排列三', 5700)

print('测试3D...')
d3_result = test_consecutive(df_3d, '福彩3D', 5700)

# 双彩综合
total_all = pl3_result['total'] + d3_result['total']
hits_all = pl3_result['hits'] + d3_result['hits']
rate_all = hits_all / total_all * 100

print()
print('='*70)
print('测试结果')
print('='*70)
print()
print('| 彩种 | 测试期数 | 命中次数 | 命中率 | 最大连中 | 最大不中 |')
print('|------|---------|---------|--------|---------|---------|')
print('| %s | %d | %d | %.2f%% | %d期 | %d期 |' % (pl3_result['name'], pl3_result['total'], pl3_result['hits'], pl3_result['hit_rate'], pl3_result['max_streak'], pl3_result['max_miss']))
print('| %s | %d | %d | %.2f%% | %d期 | %d期 |' % (d3_result['name'], d3_result['total'], d3_result['hits'], d3_result['hit_rate'], d3_result['max_streak'], d3_result['max_miss']))
print('| **双彩综合** | %d | %d | **%.2f%%** | - | - |' % (total_all, hits_all, rate_all))
print()
print('='*70)