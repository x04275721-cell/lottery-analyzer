#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两码和实战 vs 两码和差 对比测试
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('两码和实战 vs 两码和差 对比测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 方法1：两码和差（现有）
# ============================================================
def predict_liangma_old(df_train):
    """现有方法：两码和差"""
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    
    # 和
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    # 差
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    # 进位
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    result = [n for n, c in num_count.most_common(3)]
    
    return {d: 6 for d in result}

# ============================================================
# 方法2：两码和实战（新）
# ============================================================
def predict_liangma_new(df_train):
    """新方法：两码和实战"""
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 2:
        return scores
    
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    
    # 排序两码和
    sorted_nums = sorted([n1, n2, n3])
    xiao_he = sorted_nums[0] + sorted_nums[1]  # 小数和
    zhong_he = sorted_nums[0] + sorted_nums[2]  # 中数和
    da_he = sorted_nums[1] + sorted_nums[2]  # 大数和
    
    # 和尾
    xiao_tail = xiao_he % 10
    zhong_tail = zhong_he % 10
    da_tail = da_he % 10
    
    # 按和尾分类
    # 第一类：2,3,7,8 - 多出现在小数和、大数和
    # 第二类：9,0,1 - 多出现在中数和
    # 第三类：4,5,6 - 警示和尾
    
    # 给和尾对应的数字加分
    if xiao_tail in [2, 3, 7, 8]:
        for d in sorted_nums[:2]:
            scores[d] += 3
    
    if da_tail in [2, 3, 7, 8]:
        for d in sorted_nums[1:]:
            scores[d] += 3
    
    if zhong_tail in [9, 0, 1]:
        for d in [sorted_nums[0], sorted_nums[2]]:
            scores[d] += 3
    
    # 五选二法则：奇偶组合形态
    # 两码和中出现奇数和（1,3,5,7,9），对应奇偶组合形态
    odd_sums = []
    if xiao_he % 2 == 1: odd_sums.append(xiao_tail)
    if zhong_he % 2 == 1: odd_sums.append(zhong_tail)
    if da_he % 2 == 1: odd_sums.append(da_tail)
    
    # 如果有奇数和，优先从奇数中选
    if len(odd_sums) >= 2:
        for d in [1, 3, 5, 7, 9]:
            scores[d] += 2
    
    return scores

# ============================================================
# 综合预测
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

def predict_10methods_old(df_train):
    """10种方法（使用旧两码和差）"""
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
    
    # 其他方法
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
    
    # 旧两码和差
    for d, s in predict_liangma_old(df_train).items():
        scores[d] += s
    
    return [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:5]]

def predict_10methods_new(df_train):
    """10种方法（使用新两码和实战）"""
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
    
    # 新两码和实战
    for d, s in predict_liangma_new(df_train).items():
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

print('\n测试旧两码和差...')
r1 = test_predict(predict_10methods_old, '旧两码和差', 3000)
print('旧两码和差: %.2f%%' % r1)

print('\n测试新两码和实战...')
r2 = test_predict(predict_10methods_new, '新两码和实战', 3000)
print('新两码和实战: %.2f%%' % r2)

print()
print('='*70)
print('结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 对比 |')
print('|------|--------|------|')
print('| 旧两码和差 | %.2f%% | 基准 |' % r1)
print('| 新两码和实战 | %.2f%% | %+.2f%% |' % (r2, r2-r1))
print()
if r2 > r1:
    print('✅ 新方法更好！')
elif r2 < r1:
    print('✅ 旧方法更好！')
else:
    print('≈ 两种方法效果相同')
print()
print('='*70)