#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双彩测试 - 使用本地数据
"""

import pandas as pd
import numpy as np
from collections import Counter
import random
import json

print('='*70)
print('双彩测试 - 排列三 + 3D')
print('='*70)

# 加载数据
pl3_df = pd.read_csv('pl3_full.csv')
print('排列三数据: %d期' % len(pl3_df))

# 加载3D数据
d3_df = pd.read_csv('fc3d_5years.csv')
print('3D数据: %d期' % len(d3_df))

# 检查列名
print('3D列名:', d3_df.columns.tolist())

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

def predict_334(df_train, cols):
    last = df_train.iloc[-1]
    last_nums = (int(last[cols[0]]), int(last[cols[1]]), int(last[cols[2]]))
    g1, g2, g3 = get_334_duanzu(last_nums)
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row[cols[0]]), int(row[cols[1]]), int(row[cols[2]])])
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    if g1_count <= g2_count and g1_count <= g3_count: return g2 + g3
    elif g2_count <= g1_count and g2_count <= g3_count: return g1 + g3
    else: return g1 + g2

def predict_55fenjie(df_train, cols):
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
            all_nums.extend([int(row[cols[0]]), int(row[cols[1]]), int(row[cols[2]])])
        g1_count = sum(1 for n in all_nums if n in g1)
        g2_count = sum(1 for n in all_nums if n in g2)
        if g1_count > g2_count: score, group = g1_count, g1
        else: score, group = g2_count, g2
        if score > best_score: best_score, best_group = score, group
    return best_group if best_group else [0,1,2,3,4]

def predict_liangma(df_train, cols):
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last[cols[0]]), int(last[cols[1]]), int(last[cols[2]])
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    return [n for n, c in num_count.most_common(3)]

def predict_012lu(df_train, cols):
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    hot_nums = []
    for pos in range(3):
        nums = df_train[cols[pos]].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums: route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        hot_nums.extend(route_map[hot_route])
    return list(set(hot_nums))

def predict_jiou(df_train, cols):
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in cols:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    if odd_count > even_count: return [1, 3, 5, 7, 9]
    else: return [0, 2, 4, 6, 8]

def predict_xingtai(df_train, cols):
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row[cols[0]]), int(row[cols[1]]), int(row[cols[2]])])
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

def predict_sum_tail(df_train, cols):
    sums = []
    for _, row in df_train.tail(30).iterrows():
        s = int(row[cols[0]]) + int(row[cols[1]]) + int(row[cols[2]])
        sums.append(s % 10)
    sum_count = Counter(sums)
    hot_sums = [n for n, c in sum_count.most_common(3)]
    result = []
    for tail in hot_sums:
        result.append(tail)
        result.append((tail + 5) % 10)
    return list(set(result))[:5]

def predict_5ma(df_train, cols):
    scores = {d: 0 for d in range(10)}
    for d in predict_334(df_train, cols): scores[d] += 14
    for d in predict_55fenjie(df_train, cols): scores[d] += 9
    for d in predict_liangma(df_train, cols): scores[d] += 6
    for d in predict_012lu(df_train, cols): scores[d] += 6
    for d in predict_jiou(df_train, cols): scores[d] += 4
    for d in predict_xingtai(df_train, cols): scores[d] += 4
    for d in predict_sum_tail(df_train, cols): scores[d] += 7
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 测试函数
# ============================================================
def test_lottery(df, name, cols, test_count=5000):
    random.seed(42)
    full_hit, at_least_2, at_least_1 = 0, 0, 0
    total = min(test_count, len(df) - 600)
    
    print('\n测试 %s...' % name)
    print('测试期数: %d' % total)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i][cols[0]]), int(df.iloc[i][cols[1]]), int(df.iloc[i][cols[2]])]
        real_set = set(real)
        top5_set = set(predict_5ma(df_train, cols))
        hit_count = len(real_set & top5_set)
        
        if hit_count == len(real_set): full_hit += 1
        if hit_count >= 2: at_least_2 += 1
        if hit_count >= 1: at_least_1 += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d | 全中: %.1f%%' % (i - 100, total, full_hit / max(1, i - 100) * 100))
    
    result = {
        'name': name,
        'total': total,
        'full_hit': full_hit,
        'full_hit_rate': full_hit/total*100,
        'at_least_2': at_least_2/total*100,
        'at_least_1': at_least_1/total*100
    }
    
    print()
    print('='*70)
    print('%s 测试结果' % name)
    print('='*70)
    print('开奖号全在五码中: %d次 (%.2f%%) 理论8.33%%' % (full_hit, full_hit/total*100))
    print('至少2个在五码中: %d次 (%.2f%%) 理论50%%' % (at_least_2, at_least_2/total*100))
    print('至少1个在五码中: %d次 (%.2f%%) 理论65%%' % (at_least_1, at_least_1/total*100))
    print('='*70)
    
    return result

# ============================================================
# 测试排列三
# ============================================================
pl3_cols = ['num1', 'num2', 'num3']
pl3_result = test_lottery(pl3_df, '排列三', pl3_cols, 5000)

# ============================================================
# 测试3D
# ============================================================
# 确定列名
if 'num1' in d3_df.columns:
    d3_cols = ['num1', 'num2', 'num3']
elif '百位' in d3_df.columns:
    d3_cols = ['百位', '十位', '个位']
else:
    # 尝试解析
    print('3D数据列名:', d3_df.columns.tolist())
    d3_cols = d3_df.columns.tolist()[:3]

d3_result = test_lottery(d3_df, '3D', d3_cols, min(5000, len(d3_df)-600))

# ============================================================
# 汇总结果
# ============================================================
print()
print('='*70)
print('双彩测试结果汇总')
print('='*70)
print()
print('【排列三】')
print('  测试期数: %d' % pl3_result['total'])
print('  全中命中率: %.2f%% (理论8.33%%)' % pl3_result['full_hit_rate'])
print('  至少2个: %.2f%%' % pl3_result['at_least_2'])
print('  至少1个: %.2f%%' % pl3_result['at_least_1'])
print()

print('【3D】')
print('  测试期数: %d' % d3_result['total'])
print('  全中命中率: %.2f%% (理论8.33%%)' % d3_result['full_hit_rate'])
print('  至少2个: %.2f%%' % d3_result['at_least_2'])
print('  至少1个: %.2f%%' % d3_result['at_least_1'])
print()

print('【对比】')
print('  排列三: %.2f%%' % pl3_result['full_hit_rate'])
print('  3D: %.2f%%' % d3_result['full_hit_rate'])
if pl3_result['full_hit_rate'] > d3_result['full_hit_rate']:
    print('  排列三命中率更高')
else:
    print('  3D命中率更高')

print('='*70)

# 保存
results = {
    'pl3': pl3_result,
    'd3': d3_result
}

with open('dual_lottery_result.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 dual_lottery_result.json')
