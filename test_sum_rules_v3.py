#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
和值三大原则 - 作为过滤条件
核心思想：不是直接改变选号，而是判断是否应该下注
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('和值三大原则 - 过滤条件版')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

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
# 和值三大原则 - 判断是否下注
# ============================================================
def should_bet(df_train):
    """
    和值三大原则 - 判断是否应该下注
    返回：True=下注，False=观望
    """
    # 计算近50期和值
    recent_sums = []
    for _, row in df_train.tail(50).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        recent_sums.append(s)
    
    sum_count = Counter(recent_sums)
    
    # 计算每个和值的遗漏
    sum_missing = {}
    for s in range(0, 28):
        if s in sum_count:
            for i, rs in enumerate(reversed(recent_sums)):
                if rs == s:
                    sum_missing[s] = i
                    break
        else:
            sum_missing[s] = 50
    
    # 获取最热的3个和值
    hot_sums = [s for s, c in sum_count.most_common(3)]
    
    signals = 0  # 信号计数
    
    for target_sum in hot_sums:
        if target_sum < 9 or target_sum > 16:
            continue
            
        # 原则一：平均间隔（简化：遗漏>=5期）
        miss = sum_missing.get(target_sum, 50)
        if miss >= 5:
            signals += 1
        
        # 原则二：相邻和值近期开出
        adj1, adj2 = target_sum - 1, target_sum + 1
        if adj1 < 0: adj1 = 0
        if adj2 > 27: adj2 = 27
        if sum_missing.get(adj1, 999) <= 5 or sum_missing.get(adj2, 999) <= 5:
            signals += 1
        
        # 原则三：同尾和值近期铺垫
        tail1 = target_sum % 10
        tail2 = (tail1 + 10) % 20
        if sum_missing.get(tail1, 999) <= 5 or sum_missing.get(tail2, 999) <= 5:
            signals += 1
        
        # 三重信号共振
        if signals >= 2:  # 至少2个信号
            return True
    
    return False  # 信号不足，观望

# ============================================================
# 测试
# ============================================================
def test_predict(predict_func, should_bet_func=None, name='基础7方法', test_count=5000, use_filter=False):
    random.seed(42)
    results = []
    skip_count = 0
    
    total = min(test_count, len(df) - 600)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        # 如果使用过滤条件
        if use_filter and should_bet_func:
            if not should_bet_func(df_train):
                skip_count += 1
                continue  # 跳过这期
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_func(df_train))
        hit = len(real_set & top5_set) == len(real_set)
        results.append(hit)
    
    total_hits = sum(results)
    hit_rate = total_hits / len(results) * 100 if results else 0
    
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
        'skipped': skip_count,
        'hits': total_hits,
        'hit_rate': hit_rate,
        'max_streak': max_streak,
        'max_miss': max_miss
    }

print('\n测试1: 基础7方法（每期都下）')
r1 = test_predict(predict_base, name='每期下注', test_count=5000, use_filter=False)
print('命中率: %.2f%% | 投注%d期 | 最大连中%d | 最大不中%d' % (r1['hit_rate'], r1['total'], r1['max_streak'], r1['max_miss']))

print('\n测试2: 基础7方法 + 和值原则（信号过滤）')
r2 = test_predict(predict_base, should_bet_func=should_bet, name='信号过滤', test_count=5000, use_filter=True)
print('命中率: %.2f%% | 投注%d期(跳过%d期) | 最大连中%d | 最大不中%d' % (r2['hit_rate'], r2['total'], r2['skipped'], r2['max_streak'], r2['max_miss']))

print()
print('='*70)
print('结果对比')
print('='*70)
print()
print('| 策略 | 投注期数 | 命中率 | 提升 | 最大连中 | 最大不中 |')
print('|------|---------|--------|------|---------|---------|')
print('| 每期下注 | %d期 | %.2f%% | - | %d期 | %d期 |' % (r1['total'], r1['hit_rate'], r1['max_streak'], r1['max_miss']))
print('| 信号过滤 | %d期 | %.2f%% | %+.2f%% | %d期 | %d期 |' % (
    r2['total'], r2['hit_rate'], 
    r2['hit_rate'] - r1['hit_rate'],
    r2['max_streak'], r2['max_miss']
))
print()
print('='*70)