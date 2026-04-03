#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比测试：完全排除 vs 综合加权
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('对比测试：完全排除 vs 综合加权')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 方法实现
# ============================================================

def get_334_duanzu(last_nums):
    n1, n2, n3 = last_nums
    sum_tail = (n1 + n2 + n3) % 10
    if sum_tail in [0, 5]: return [0,1,9], [4,5,6], [2,3,7,8]
    elif sum_tail in [1, 6]: return [0,1,2], [5,6,7], [3,4,8,9]
    elif sum_tail in [2, 7]: return [1,2,3], [6,7,8], [0,4,5,9]
    elif sum_tail in [3, 8]: return [2,3,4], [7,8,9], [0,1,5,6]
    else: return [3,4,5], [8,9,0], [1,2,6,7]

def predict_334_old(df_train):
    """完全排除模式"""
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    g1, g2, g3 = get_334_duanzu(last_nums)
    
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    
    # 完全排除最冷的组
    if g1_count <= g2_count and g1_count <= g3_count:
        return g2 + g3
    elif g2_count <= g1_count and g2_count <= g3_count:
        return g1 + g3
    else:
        return g1 + g2

def predict_334_new(df_train):
    """综合加权模式"""
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    g1, g2, g3 = get_334_duanzu(last_nums)
    
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    
    # 综合加权
    counts = [(g1, g1_count), (g2, g2_count), (g3, g3_count)]
    counts.sort(key=lambda x: x[1], reverse=True)
    
    scores = {d: 0 for d in range(10)}
    for d in counts[0][0]: scores[d] += 14  # 热
    for d in counts[1][0]: scores[d] += 9   # 中
    for d in counts[2][0]: scores[d] += 3   # 冷
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:7]]

def predict_jiou_old(df_train):
    """完全排除模式"""
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    
    if odd_count > even_count:
        return [1, 3, 5, 7, 9]
    else:
        return [0, 2, 4, 6, 8]

def predict_jiou_new(df_train):
    """综合加权模式"""
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    
    scores = {d: 0 for d in range(10)}
    if odd_count > even_count:
        for d in [1,3,5,7,9]: scores[d] += 8
        for d in [0,2,4,6,8]: scores[d] += 3
    else:
        for d in [0,2,4,6,8]: scores[d] += 8
        for d in [1,3,5,7,9]: scores[d] += 3
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:7]]

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

# ============================================================
# 综合预测
# ============================================================
def predict_5ma_old(df_train):
    """完全排除模式"""
    scores = {d: 0 for d in range(10)}
    for d in predict_334_old(df_train): scores[d] += 14
    for d in predict_55fenjie(df_train): scores[d] += 9
    for d in predict_liangma(df_train): scores[d] += 6
    for d in predict_012lu(df_train): scores[d] += 6
    for d in predict_jiou_old(df_train): scores[d] += 4
    for d in predict_xingtai(df_train): scores[d] += 4
    for d in predict_sum_tail(df_train): scores[d] += 7
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

def predict_5ma_new(df_train):
    """综合加权模式"""
    scores = {d: 0 for d in range(10)}
    
    # 334断组 - 综合加权
    result_334 = predict_334_new(df_train)
    for d in result_334:
        scores[d] += 14
    
    # 其他方法
    for d in predict_55fenjie(df_train): scores[d] += 9
    for d in predict_liangma(df_train): scores[d] += 6
    for d in predict_012lu(df_train): scores[d] += 6
    
    # 奇偶 - 综合加权
    result_jiou = predict_jiou_new(df_train)
    for d in result_jiou:
        scores[d] += 4
    
    for d in predict_xingtai(df_train): scores[d] += 4
    for d in predict_sum_tail(df_train): scores[d] += 7
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 测试
# ============================================================
def test_mode(predict_func, name, test_count=5000):
    random.seed(42)
    full_hit, at_least_2, at_least_1 = 0, 0, 0
    total = min(test_count, len(df) - 600)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_func(df_train))
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

print('\n测试完全排除模式...')
old_result = test_mode(predict_5ma_old, '完全排除模式', 5000)

print('测试综合加权模式...')
new_result = test_mode(predict_5ma_new, '综合加权模式', 5000)

print()
print('='*70)
print('对比测试结果 (5000期)')
print('='*70)
print()
print('| 模式 | 全中命中率 | 至少2个 | 至少1个 |')
print('|------|-----------|---------|---------|')
print('| %s | %.2f%% | %.2f%% | %.2f%% |' % (old_result['name'], old_result['full_hit'], old_result['at_least_2'], old_result['at_least_1']))
print('| %s | %.2f%% | %.2f%% | %.2f%% |' % (new_result['name'], new_result['full_hit'], new_result['at_least_2'], new_result['at_least_1']))
print()

# 对比
diff = new_result['full_hit'] - old_result['full_hit']
if diff > 0:
    print('✅ 综合加权模式命中率更高！提升 %.2f%%' % diff)
elif diff < 0:
    print('❌ 完全排除模式命中率更高！高出 %.2f%%' % abs(diff))
else:
    print('≈ 两种模式命中率相同')

print()
print('='*70)