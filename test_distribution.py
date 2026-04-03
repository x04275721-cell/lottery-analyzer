#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分布图规律测试 - 分位分析 + 钟摆理论 + 热号优先
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('分布图规律测试 - 分位分析 + 钟摆理论')
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
# 新增：分布图规律 - 分位分析 + 钟摆理论
# ============================================================
def predict_position_analysis(df_train):
    """
    分布图规律：
    1. 分位分析：每个位置单独计算热号
    2. 钟摆理论：近5期摆幅超3时，下期回摆
    3. 热号优先：全局热号加权
    """
    scores = {d: 0 for d in range(10)}
    
    # 1. 分位热号分析（近30期）
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df_train[col].astype(int).tail(30).tolist()
        counter = Counter(nums)
        top_nums = [d for d, c in counter.most_common(3)]
        for d in top_nums:
            scores[d] += 4  # 每个位置热号+4分
    
    # 2. 钟摆理论 - 检测近5期摆幅
    recent5 = df_train.tail(5)
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = recent5[col].astype(int).tolist()
        if len(nums) >= 5:
            max_num = max(nums)
            min_num = min(nums)
            swing = max_num - min_num
            
            # 摆幅超过3，回摆预测
            if swing > 3:
                # 预测回摆到中间区域（3-7）
                for d in range(3, 8):
                    scores[d] += 3
    
    # 3. 全局热号（近50期）
    all_nums = []
    for _, row in df_train.tail(50).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    counter = Counter(all_nums)
    hot_nums = [d for d, c in counter.most_common(3)]
    for d in hot_nums:
        scores[d] += 2  # 最热3个+2分
    
    return scores

def predict_hot_priority(df_train):
    """
    热号优先策略：
    - 热号5、7、8持续热出概率达68%
    - 冷号解冻后3期内重复概率仅12%
    """
    scores = {d: 0 for d in range(10)}
    
    # 统计各数字出现次数
    all_nums = []
    for _, row in df_train.tail(50).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    counter = Counter(all_nums)
    total = sum(counter.values())
    avg = total / 10  # 平均值
    
    # 热号加分（高于平均值）
    for d, c in counter.items():
        if c > avg * 1.1:  # 高于平均10%
            scores[d] += 5
        elif c > avg * 1.2:  # 高于平均20%
            scores[d] += 3
    
    # 冷号降权（低于平均值）
    for d in range(10):
        if d not in counter or counter[d] < avg * 0.8:
            scores[d] -= 1
    
    return scores

def predict_7methods(df_train):
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

def predict_enhanced_v1(df_train):
    """增强版1：+分位分析"""
    scores = {d: 0 for d in range(10)}
    for d, s in predict_334(df_train).items(): scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): scores[d] += s
    for d, s in predict_liangma(df_train).items(): scores[d] += s
    for d, s in predict_012lu(df_train).items(): scores[d] += s
    for d, s in predict_jiou(df_train).items(): scores[d] += s
    for d, s in predict_xingtai(df_train).items(): scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): scores[d] += s
    for d, s in predict_banshun(df_train).items(): scores[d] += s
    for d, s in predict_position_analysis(df_train).items(): scores[d] += s  # +分位分析
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

def predict_enhanced_v2(df_train):
    """增强版2：+热号优先"""
    scores = {d: 0 for d in range(10)}
    for d, s in predict_334(df_train).items(): scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): scores[d] += s
    for d, s in predict_liangma(df_train).items(): scores[d] += s
    for d, s in predict_012lu(df_train).items(): scores[d] += s
    for d, s in predict_jiou(df_train).items(): scores[d] += s
    for d, s in predict_xingtai(df_train).items(): scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): scores[d] += s
    for d, s in predict_banshun(df_train).items(): scores[d] += s
    for d, s in predict_position_analysis(df_train).items(): scores[d] += s
    for d, s in predict_hot_priority(df_train).items(): scores[d] += s  # +热号优先
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

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

print('\n测试各种配置...')
r1 = test_predict(predict_7methods, '7种方法', 3000)
print('7种方法: %.2f%% | 最大不中%d' % (r1['hit_rate'], r1['max_miss']))

r2 = test_predict(predict_8methods, '8种方法', 3000)
print('8种方法: %.2f%% | 最大不中%d' % (r2['hit_rate'], r2['max_miss']))

r3 = test_predict(predict_enhanced_v1, '+分位分析', 3000)
print('+分位分析: %.2f%% | 最大不中%d' % (r3['hit_rate'], r3['max_miss']))

r4 = test_predict(predict_enhanced_v2, '+热号优先', 3000)
print('+热号优先: %.2f%% | 最大不中%d' % (r4['hit_rate'], r4['max_miss']))

print()
print('='*70)
print('结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 提升 | 最大不中 |')
print('|------|--------|------|---------|')
print('| 7种方法 | %.2f%% | - | %d期 |' % (r1['hit_rate'], r1['max_miss']))
print('| 8种方法 | %.2f%% | %+.2f%% | %d期 |' % (r2['hit_rate'], r2['hit_rate']-r1['hit_rate'], r2['max_miss']))
print('| +分位分析 | %.2f%% | %+.2f%% | %d期 |' % (r3['hit_rate'], r3['hit_rate']-r1['hit_rate'], r3['max_miss']))
print('| +热号优先 | %.2f%% | %+.2f%% | %d期 |' % (r4['hit_rate'], r4['hit_rate']-r1['hit_rate'], r4['max_miss']))
print()
print('='*70)