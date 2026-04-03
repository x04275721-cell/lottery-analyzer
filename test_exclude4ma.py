#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
福彩小条件测试 - 4码≠3
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('福彩小条件测试 - 4码≠3')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 四码排除法
# ============================================================
def get_excluded_4ma(last_nums):
    """
    四码排除法：
    1. 上期号码排序
    2. 取胆码（特定位置）
    3. 排除4个数字
    
    根据示例：
    - 开049 → 排序940 → 排除1348
    - 开332 → 排序332 → 排除0159
    """
    # 排序
    sorted_nums = sorted(last_nums, reverse=True)  # 降序
    
    # 计算胆码（上期号码+0）
    danma = sorted_nums[:2] + [0]
    
    # 计算位置（相邻位置）
    weizhi = []
    for d in sorted_nums:
        weizhi.append((d + 1) % 10)
        weizhi.append((d + 2) % 10)
    
    # 排除的数字 = 不在胆码和位置中的数字
    all_keep = set(danma) | set(weizhi)
    excluded = [d for d in range(10) if d not in all_keep]
    
    return excluded[:4]  # 返回排除的4个数字

def predict_excluded_4ma(df_train):
    """
    四码排除法预测：
    给排除的数字降权
    """
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 2:
        return scores
    
    last = df_train.iloc[-1]
    last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    excluded = get_excluded_4ma(last_nums)
    
    # 给排除的数字降权
    for d in range(10):
        if d in excluded:
            scores[d] -= 3  # 排除的数字减分
        else:
            scores[d] += 2  # 保留的数字加分
    
    return scores

# ============================================================
# 测试四码排除准确率
# ============================================================
print('\n测试四码排除法准确率...')

exclude_correct = 0
exclude_total = 0

for i in range(100, min(400, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    excluded = get_excluded_4ma(last_nums)
    real_set = set(real)
    
    # 检查：开奖号码中至少有1个不在排除的4个数字中
    # 即：3个开奖号码不全在排除的4个数字中
    if not real_set.issubset(set(excluded)):
        exclude_correct += 1
    exclude_total += 1

print('四码排除准确率: %.2f%% (%d/%d)' % (exclude_correct/exclude_total*100, exclude_correct, exclude_total))

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

def predict_11methods_exclude(df_train):
    """10方法 + 四码排除"""
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
    
    # 四码排除
    for d, s in predict_excluded_4ma(df_train).items():
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
r1 = test_predict(predict_10methods, '10种方法', 5000)
print('10种方法: %.2f%%' % r1)

print('\n测试11种方法（+四码排除）...')
r2 = test_predict(predict_11methods_exclude, '+四码排除', 5000)
print('+四码排除: %.2f%%' % r2)

print()
print('='*70)
print('结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 提升 |')
print('|------|--------|------|')
print('| 10种方法 | %.2f%% | - |' % r1)
print('| +四码排除 | %.2f%% | %+.2f%% |' % (r2, r2-r1))
print()
if r2 > r1:
    print('四码排除有效！')
elif r2 < r1:
    print('四码排除效果不佳')
else:
    print('效果相同')
print()
print('='*70)