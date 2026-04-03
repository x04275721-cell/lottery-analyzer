#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
半顺（连号）细分技巧测试
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('半顺（连号）细分技巧测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 基础方法
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

def predict_base(df_train):
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

# ============================================================
# 半顺细分技巧
# ============================================================
def is_banshun(nums):
    """判断是否为半顺（任意两个数字相邻）"""
    n1, n2, n3 = sorted(nums)
    # 检查任意两个是否相邻
    if abs(n1-n2) == 1 or abs(n2-n3) == 1 or abs(n1-n3) == 1:
        return True
    return False

def get_hot_consecutive_type(df_train, lookback=50):
    """获取热门的二连码类型"""
    consecutive_counts = Counter()
    
    for _, row in df_train.tail(lookback).iterrows():
        nums = sorted([int(row['num1']), int(row['num2']), int(row['num3'])])
        # 检查所有两两组合
        for i in range(3):
            for j in range(i+1, 3):
                diff = nums[j] - nums[i]
                if diff == 1:  # 差1就是相邻
                    consecutive_counts[(nums[i], nums[j])] += 1
    
    return consecutive_counts.most_common(5)

def get_hot_single_digit(df_train, lookback=50):
    """获取含热门数字的半顺"""
    digit_counts = Counter()
    
    for _, row in df_train.tail(lookback).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        if is_banshun(nums):
            for d in nums:
                digit_counts[d] += 1
    
    return digit_counts.most_common(5)

def predict_banshun(df_train):
    """
    半顺细分技巧：
    1. 优先选择热态二连码（89、90、01最热）
    2. 优先选择含热门数字（8、9、0最热）
    3. 半顺开出率60.7%，平均1.6期1次
    """
    scores = {d: 0 for d in range(10)}
    
    # 获取热门二连码
    hot_types = get_hot_consecutive_type(df_train, 50)
    
    # 获取热门单码
    hot_digits = get_hot_single_digit(df_train, 50)
    
    # 二连码加分
    hot_pairs = [p[0] for p in hot_types[:3]]  # 最热的3种
    for pair in hot_pairs:
        for d in pair:
            scores[d] += 5
    
    # 单码加分
    hot_ds = [d[0] for d in hot_digits[:3]]  # 最热的3个数字
    for d in hot_ds:
        scores[d] += 4
    
    # 半顺特征：数字尽量相邻
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    # 统计相邻数字出现次数
    for i in range(10):
        count = all_nums.count(i)
        if count >= 15:  # 高频数字加分
            scores[i] += 3
    
    return scores

def predict_enhanced_banshun(df_train):
    """增强版：基础7方法 + 半顺技巧"""
    scores = {d: 0 for d in range(10)}
    
    # 基础7方法
    for d, s in predict_334(df_train).items(): scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): scores[d] += s
    for d, s in predict_liangma(df_train).items(): scores[d] += s
    for d, s in predict_012lu(df_train).items(): scores[d] += s
    for d, s in predict_jiou(df_train).items(): scores[d] += s
    for d, s in predict_xingtai(df_train).items(): scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): scores[d] += s
    
    # 半顺技巧（中等权重）
    for d, s in predict_banshun(df_train).items(): scores[d] += s
    
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

print('\n测试基础7方法...')
r1 = test_predict(predict_base, '基础7方法', 5000)
print('基础7方法: %.2f%% | 最大连中%d | 最大不中%d' % (r1['hit_rate'], r1['max_streak'], r1['max_miss']))

print('\n测试+半顺细分技巧...')
r2 = test_predict(predict_enhanced_banshun, '+半顺技巧', 5000)
print('+半顺技巧: %.2f%% | 最大连中%d | 最大不中%d' % (r2['hit_rate'], r2['max_streak'], r2['max_miss']))

# 测试半顺单独命中率
print('\n测试纯半顺技巧（只用半顺选号）...')
def predict_only_banshun(df_train):
    scores = predict_banshun(df_train)
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]
r3 = test_predict(predict_only_banshun, '纯半顺', 5000)
print('纯半顺: %.2f%% | 最大连中%d | 最大不中%d' % (r3['hit_rate'], r3['max_streak'], r3['max_miss']))

print()
print('='*70)
print('测试结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 提升 | 最大连中 | 最大不中 |')
print('|------|--------|------|---------|---------|')
print('| 基础7方法 | %.2f%% | - | %d期 | %d期 |' % (r1['hit_rate'], r1['max_streak'], r1['max_miss']))
print('| +半顺技巧 | %.2f%% | %+.2f%% | %d期 | %d期 |' % (r2['hit_rate'], r2['hit_rate']-r1['hit_rate'], r2['max_streak'], r2['max_miss']))
print('| 纯半顺 | %.2f%% | - | %d期 | %d期 |' % (r3['hit_rate'], r3['max_streak'], r3['max_miss']))
print()
print('='*70)