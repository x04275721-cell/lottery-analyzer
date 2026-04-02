#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重调整测试 - 前三种方法各加5%
334断组 30%→35%, 五五分解 20%→25%, 两码进位和差 15%→20%
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('权重调整测试 - 前三种方法各加5%')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# 方法实现（同test_6methods.py）
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

# ============================================================
# 综合预测 - 调整权重
# ============================================================
def predict_5ma_adjusted(df_train):
    """调整权重后的预测"""
    scores = {d: 0 for d in range(10)}
    
    # 1. 334断组 (35%) - 原30%
    duanzu = predict_334(df_train)
    for d in duanzu: scores[d] += 17.5
    
    # 2. 五五分解 (25%) - 原20%
    fenjie = predict_55fenjie(df_train)
    for d in fenjie: scores[d] += 12.5
    
    # 3. 两码进位和差 (20%) - 原15%
    liangma = predict_liangma(df_train)
    for d in liangma: scores[d] += 10
    
    # 4. 012路 (10%) - 原15%
    route = predict_012lu(df_train)
    for d in route: scores[d] += 5
    
    # 5. 奇偶 (5%) - 原10%
    jiou = predict_jiou(df_train)
    for d in jiou: scores[d] += 2.5
    
    # 6. 形态 (5%) - 原10%
    xingtai = predict_xingtai(df_train)
    for d in xingtai: scores[d] += 2.5
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 测试
# ============================================================
def test_adjusted(test_count=5000):
    random.seed(42)
    full_hit, at_least_2, at_least_1 = 0, 0, 0
    total = min(test_count, len(df) - 600)
    
    print('\n开始测试...')
    print('测试期数: %d' % total)
    print()
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_5ma_adjusted(df_train))
        hit_count = len(real_set & top5_set)
        
        if hit_count == len(real_set): full_hit += 1
        if hit_count >= 2: at_least_2 += 1
        if hit_count >= 1: at_least_1 += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d | 全中: %.1f%% | 至少2: %.1f%% | 至少1: %.1f%%' % (
                i - 100, total, full_hit / max(1, i - 100) * 100,
                at_least_2 / max(1, i - 100) * 100, at_least_1 / max(1, i - 100) * 100
            ))
    
    print()
    print('='*70)
    print('调整权重后测试结果 (5000期)')
    print('='*70)
    print()
    print('权重配置:')
    print('  1. 334断组法: 35% (原30%)')
    print('  2. 五五分解法: 25% (原20%)')
    print('  3. 两码进位和差: 20% (原15%)')
    print('  4. 012路分析法: 10% (原15%)')
    print('  5. 奇偶分析法: 5% (原10%)')
    print('  6. 形态分析法: 5% (原10%)')
    print()
    print('【结果】')
    print('-'*70)
    print('开奖号全在五码中: %d次 (%.2f%%) 理论8.33%%' % (full_hit, full_hit/total*100))
    print('至少2个在五码中: %d次 (%.2f%%) 理论50%%' % (at_least_2, at_least_2/total*100))
    print('至少1个在五码中: %d次 (%.2f%%) 理论65%%' % (at_least_1, at_least_1/total*100))
    print('='*70)
    
    return {'full_hit': full_hit/total*100, 'at_least_2': at_least_2/total*100, 'at_least_1': at_least_1/total*100}

result = test_adjusted(5000)

import json
with open('adjusted_weight_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 adjusted_weight_result.json')
