#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
和值判断三大原则测试 - 优化版
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('和值判断三大原则测试 - 优化版')
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
# 和值三大原则 - 简化版
# ============================================================
def predict_sum_rules(df_train):
    """
    和值三大原则简化版：
    1. 选择热和值（9-16）
    2. 优先选择遗漏接近平均值的和值
    3. 参考相邻和值状态
    """
    scores = {d: 0 for d in range(10)}
    
    # 计算近50期和值统计
    recent_sums = []
    for _, row in df_train.tail(50).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        recent_sums.append(s)
    
    sum_count = Counter(recent_sums)
    
    # 计算每个和值的遗漏
    sum_missing = {}
    for s in range(0, 28):
        if s in sum_count:
            # 找最近一次出现的位置
            for i, rs in enumerate(reversed(recent_sums)):
                if rs == s:
                    sum_missing[s] = i
                    break
        else:
            sum_missing[s] = 50  # 50期都没出现
    
    # 优先热和值（9-16区间的）
    hot_sums = [s for s, c in sum_count.most_common(5)]
    
    # 根据和值推荐数字组合
    recommended_sums = []
    for target_sum in hot_sums:
        if 9 <= target_sum <= 16:  # 中区
            # 检查遗漏是否合理（不要太长也不要太短）
            miss = sum_missing.get(target_sum, 50)
            if miss <= 15:  # 遗漏不超过15期
                recommended_sums.append(target_sum)
    
    # 如果没有合适的，返回空
    if not recommended_sums:
        return scores
    
    # 根据推荐和值，为对应数字加分
    for target_sum in recommended_sums[:3]:  # 最多3个和值
        # 找出所有和为target_sum的数字组合
        for d1 in range(10):
            for d2 in range(d1, 10):
                d3 = target_sum - d1 - d2
                if 0 <= d3 <= 9 and d3 >= d2:  # 排序组合
                    scores[d1] += 3
                    scores[d2] += 3
                    scores[d3] += 3
    
    return scores

def predict_enhanced(df_train):
    """增强版：基础7方法 + 和值原则"""
    scores = {d: 0 for d in range(10)}
    
    # 基础7方法
    for d, s in predict_334(df_train).items(): scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): scores[d] += s
    for d, s in predict_liangma(df_train).items(): scores[d] += s
    for d, s in predict_012lu(df_train).items(): scores[d] += s
    for d, s in predict_jiou(df_train).items(): scores[d] += s
    for d, s in predict_xingtai(df_train).items(): scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): scores[d] += s
    
    # 和值三大原则（低权重）
    for d, s in predict_sum_rules(df_train).items(): scores[d] += s
    
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
    
    # 最大连中/不中
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
base_result = test_predict(predict_base, '基础7方法', 5000)
print('基础7方法: %.2f%% | 最大连中%d | 最大不中%d' % (base_result['hit_rate'], base_result['max_streak'], base_result['max_miss']))

print('\n测试+和值三大原则...')
enhanced_result = test_predict(predict_enhanced, '+和值三大原则', 5000)
print('+和值三大原则: %.2f%% | 最大连中%d | 最大不中%d' % (enhanced_result['hit_rate'], enhanced_result['max_streak'], enhanced_result['max_miss']))

print()
print('='*70)
print('测试结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 最大连中 | 最大不中 | 提升 |')
print('|------|--------|---------|---------|------|')
print('| 基础7方法 | %.2f%% | %d期 | %d期 | - |' % (base_result['hit_rate'], base_result['max_streak'], base_result['max_miss']))
print('| +和值三大原则 | %.2f%% | %d期 | %d期 | %+.2f%% |' % (
    enhanced_result['hit_rate'], 
    enhanced_result['max_streak'], 
    enhanced_result['max_miss'],
    enhanced_result['hit_rate'] - base_result['hit_rate']
))
print()
print('='*70)