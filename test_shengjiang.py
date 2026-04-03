#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
升降号形态分析测试
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('升降号形态分析测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 升降号形态分析
# ============================================================
def get_pattern_type(nums):
    """
    获取升降号形态：
    - 升号组合：n1 < n2 < n3
    - 降号组合：n1 > n2 > n3
    - V型组合：n2 < n1 and n2 < n3
    - 倒V型组合：n2 > n1 and n2 > n3
    - 其他：无规律
    """
    n1, n2, n3 = nums
    
    if n1 < n2 < n3:
        return '升号'
    elif n1 > n2 > n3:
        return '降号'
    elif n2 < n1 and n2 < n3:
        return 'V型'
    elif n2 > n1 and n2 > n3:
        return '倒V型'
    else:
        return '其他'

def predict_shengjiang(df_train):
    """
    升降号形态分析：
    1. 统计近期形态分布
    2. 根据形态规律选号
    """
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 20:
        return scores
    
    # 统计近20期形态
    patterns = []
    for _, row in df_train.tail(20).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        pattern = get_pattern_type(nums)
        patterns.append(pattern)
    
    pattern_count = Counter(patterns)
    
    # 找出最热形态
    hot_pattern = pattern_count.most_common(1)[0][0]
    
    # 根据形态给数字加分
    last = df_train.iloc[-1]
    last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    if hot_pattern == '升号':
        # 升号：优先小号
        for d in range(0, 6):
            scores[d] += 3
    
    elif hot_pattern == '降号':
        # 降号：优先大号
        for d in range(4, 10):
            scores[d] += 3
    
    elif hot_pattern == 'V型':
        # V型：中间位最小，给中间区域加分
        for d in range(0, 6):
            scores[d] += 2
        # 给十位小号加分
        for d in range(0, 5):
            scores[d] += 1
    
    elif hot_pattern == '倒V型':
        # 倒V型：中间位最大，给中间区域加分
        for d in range(4, 10):
            scores[d] += 2
        # 给十位大号加分
        for d in range(5, 10):
            scores[d] += 1
    
    return scores

# ============================================================
# 测试升降号形态统计
# ============================================================
print('\n统计升降号形态分布（近3000期）...')
pattern_stats = Counter()
for i in range(100, min(3100, len(df))):
    nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    pattern = get_pattern_type(nums)
    pattern_stats[pattern] += 1

total = sum(pattern_stats.values())
print()
print('| 形态 | 出现次数 | 占比 |')
print('|------|---------|------|')
for pattern, count in pattern_stats.most_common():
    print('| %s | %d | %.2f%% |' % (pattern, count, count/total*100))

# ============================================================
# 基础方法
# ============================================================
def get_334(last_nums):
    n1, n2, n3 = last_nums
    st = (n1+n2+n3)%10
    if st in [0,5]: g1,g2,g3=[0,1,9],[4,5,6],[2,3,7,8]
    elif st in [1,6]: g1,g2,g3=[0,1,2],[5,6,7],[3,4,8,9]
    elif st in [2,7]: g1,g2,g3=[1,2,3],[6,7,8],[0,4,5,9]
    elif st in [3,8]: g1,g2,g3=[2,3,4],[7,8,9],[0,1,5,6]
    else: g1,g2,g3=[3,4,5],[8,9,0],[1,2,6,7]
    return g1,g2,g3

def predict_10methods(df_train):
    """10种方法"""
    scores = {d: 0 for d in range(10)}
    
    last = df_train.iloc[-1]
    last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    # 334断组
    g1,g2,g3 = get_334(tuple(last_nums))
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    g1c = sum(1 for n in all_nums if n in g1)
    g2c = sum(1 for n in all_nums if n in g2)
    g3c = sum(1 for n in all_nums if n in g3)
    c = sorted([(g1,g1c),(g2,g2c),(g3,g3c)], key=lambda x:x[1], reverse=True)
    for d in c[0][0]: scores[d] += 14
    for d in c[1][0]: scores[d] += 10
    for d in c[2][0]: scores[d] += 2
    
    counter = Counter(all_nums)
    for d, ct in counter.items():
        scores[d] += ct * 0.3
    
    ch = set(last_nums)
    li = set()
    for n in last_nums:
        if n > 0: li.add(n-1)
        if n < 9: li.add(n+1)
    for d in ch: scores[d] += 3
    for d in li: scores[d] += 4
    
    def is_b(nums):
        n1,n2,n3 = sorted(nums)
        return abs(n1-n2)==1 or abs(n2-n3)==1 or abs(n1-n3)==1
    for _, row in df_train.tail(50).iterrows():
        ns = [int(row['num1']), int(row['num2']), int(row['num3'])]
        if is_b(ns):
            for d in ns: scores[d] += 0.5
    
    WAN_NENG_6 = [
        [0,1,2,3,4,5],[0,1,2,3,6,7],[0,1,2,3,8,9],[0,1,4,5,6,7],[0,1,4,5,8,9],
        [0,1,6,7,8,9],[2,3,4,5,6,7],[2,3,4,5,8,9],[2,3,6,7,8,9],[4,5,6,7,8,9],
    ]
    hot = [d for d, ct in counter.items() if ct >= 3]
    if not hot: hot = [d for d, ct in counter.most_common(2)]
    best_g, best_s = None, -1
    for g in WAN_NENG_6:
        m = sum(1 for h in hot if h in g)
        if m > best_s: best_s, best_g = m, g
    if best_g:
        for d in best_g: scores[d] += 5
    
    n1, n2, n3 = last_nums
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    lm_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    lm_count = Counter(lm_nums)
    for d, ct in lm_count.items():
        scores[d] += ct * 2
    
    return [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:5]]

def predict_11methods_shengjiang(df_train):
    """10方法 + 升降号形态"""
    scores = {d: 0 for d in range(10)}
    
    last = df_train.iloc[-1]
    last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    # 334断组
    g1,g2,g3 = get_334(tuple(last_nums))
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    g1c = sum(1 for n in all_nums if n in g1)
    g2c = sum(1 for n in all_nums if n in g2)
    g3c = sum(1 for n in all_nums if n in g3)
    c = sorted([(g1,g1c),(g2,g2c),(g3,g3c)], key=lambda x:x[1], reverse=True)
    for d in c[0][0]: scores[d] += 14
    for d in c[1][0]: scores[d] += 10
    for d in c[2][0]: scores[d] += 2
    
    counter = Counter(all_nums)
    for d, ct in counter.items():
        scores[d] += ct * 0.3
    
    ch = set(last_nums)
    li = set()
    for n in last_nums:
        if n > 0: li.add(n-1)
        if n < 9: li.add(n+1)
    for d in ch: scores[d] += 3
    for d in li: scores[d] += 4
    
    def is_b(nums):
        n1,n2,n3 = sorted(nums)
        return abs(n1-n2)==1 or abs(n2-n3)==1 or abs(n1-n3)==1
    for _, row in df_train.tail(50).iterrows():
        ns = [int(row['num1']), int(row['num2']), int(row['num3'])]
        if is_b(ns):
            for d in ns: scores[d] += 0.5
    
    WAN_NENG_6 = [
        [0,1,2,3,4,5],[0,1,2,3,6,7],[0,1,2,3,8,9],[0,1,4,5,6,7],[0,1,4,5,8,9],
        [0,1,6,7,8,9],[2,3,4,5,6,7],[2,3,4,5,8,9],[2,3,6,7,8,9],[4,5,6,7,8,9],
    ]
    hot = [d for d, ct in counter.items() if ct >= 3]
    if not hot: hot = [d for d, ct in counter.most_common(2)]
    best_g, best_s = None, -1
    for g in WAN_NENG_6:
        m = sum(1 for h in hot if h in g)
        if m > best_s: best_s, best_g = m, g
    if best_g:
        for d in best_g: scores[d] += 5
    
    n1, n2, n3 = last_nums
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    lm_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    lm_count = Counter(lm_nums)
    for d, ct in lm_count.items():
        scores[d] += ct * 2
    
    # 升降号形态
    for d, s in predict_shengjiang(df_train).items():
        scores[d] += s
    
    return [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:5]]

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
    return hit_rate

print('\n测试10种方法...')
r1 = test_predict(predict_10methods, '10种方法', 3000)
print('10种方法: %.2f%%' % r1)

print('\n测试11种方法（+升降号形态）...')
r2 = test_predict(predict_11methods_shengjiang, '+升降号形态', 3000)
print('+升降号形态: %.2f%%' % r2)

print()
print('='*70)
print('结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 提升 |')
print('|------|--------|------|')
print('| 10种方法 | %.2f%% | - |' % r1)
print('| +升降号形态 | %.2f%% | %+.2f%% |' % (r2, r2-r1))
print()
if r2 > r1:
    print('升降号形态有效！')
elif r2 < r1:
    print('升降号形态效果不佳')
else:
    print('效果相同')
print()
print('='*70)