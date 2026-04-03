#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四平法测试 - 判断组三/组六形态
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('四平法测试 - 判断组三/组六形态')
print('='*70)

# 使用排列三数据（没有排列五数据，用排列三模拟）
df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 四平法判断组三/组六
# ============================================================
def is_zu3(nums):
    """判断是否为组三"""
    n1, n2, n3 = nums
    return n1 == n2 or n1 == n3 or n2 == n3

def get_zu3_zu6_type(nums):
    """获取形态类型：组三=1, 组六=0"""
    return 1 if is_zu3(nums) else 0

def check_siping(last_nums):
    """
    四平法（简化版，用排列三模拟）：
    1. 计算和值
    2. 检查是否能被2整除
    3. 结合统计规律判断
    
    原版需要排列五数据，这里用排列三简化
    """
    n1, n2, n3 = last_nums
    
    # 方法1：和值判断
    he = n1 + n2 + n3
    
    # 方法2：两两相加
    he12 = n1 + n2
    he13 = n1 + n3
    he23 = n2 + n3
    
    # 检查是否"平"（相等或接近）
    ping_count = 0
    
    # 检查和值能否被2整除
    if he % 2 == 0:
        ping_count += 1
    
    # 检查两两和是否接近
    if abs(he12 - he23) <= 2:
        ping_count += 1
    
    if abs(he12 - he13) <= 2:
        ping_count += 1
    
    if abs(he13 - he23) <= 2:
        ping_count += 1
    
    # 四平迹象：ping_count >= 3
    # 判断为组三
    return ping_count >= 3

def predict_siping(df_train):
    """
    四平法预测：
    如果四平迹象，增加组三概率的号码组合
    否则增加组六概率的号码组合
    """
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 2:
        return scores
    
    # 上期号码
    last = df_train.iloc[-1]
    last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    # 判断形态
    siping = check_siping(last_nums)
    
    if siping:
        # 预测组三：增加重复号概率
        for d in set(last_nums):
            scores[d] += 5
        # 增加上期号码本身
        for d in last_nums:
            scores[d] += 3
    else:
        # 预测组六：增加不同号概率
        for d in range(10):
            if d not in last_nums:
                scores[d] += 2
    
    return scores

# ============================================================
# 测试四平法准确率
# ============================================================
print('\n测试四平法判断组三/组六准确率...')

zu3_correct = 0
zu3_total = 0
zu6_correct = 0
zu6_total = 0

for i in range(100, min(3000, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    # 四平判断
    predict_zu3 = check_siping(last_nums)
    
    # 实际形态
    actual_zu3 = is_zu3(real)
    
    # 统计
    if predict_zu3:
        zu3_total += 1
        if actual_zu3:
            zu3_correct += 1
    else:
        zu6_total += 1
        if not actual_zu3:
            zu6_correct += 1

zu3_rate = zu3_correct / zu3_total * 100 if zu3_total > 0 else 0
zu6_rate = zu6_correct / zu6_total * 100 if zu6_total > 0 else 0

print('预测组三准确率: %.2f%% (%d/%d)' % (zu3_rate, zu3_correct, zu3_total))
print('预测组六准确率: %.2f%% (%d/%d)' % (zu6_rate, zu6_correct, zu6_total))

# 组三/组六实际比例
actual_zu3_count = 0
actual_zu6_count = 0
for i in range(100, min(3000, len(df) - 600)):
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    if is_zu3(real):
        actual_zu3_count += 1
    else:
        actual_zu6_count += 1

print('\n实际组三占比: %.2f%%' % (actual_zu3_count / (actual_zu3_count + actual_zu6_count) * 100))
print('实际组六占比: %.2f%%' % (actual_zu6_count / (actual_zu3_count + actual_zu6_count) * 100))

# ============================================================
# 基础方法（简化版）
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
    """10种方法（简化版）"""
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
    
    # 其他方法简化：热号加权
    counter = Counter(all_nums)
    for d, ct in counter.items():
        scores[d] += ct * 0.5
    
    # 邻孤传
    ch = set(last_nums)
    li = set()
    for n in last_nums:
        if n > 0: li.add(n-1)
        if n < 9: li.add(n+1)
    for d in ch: scores[d] += 3
    for d in li: scores[d] += 4
    
    # 半顺
    def is_b(nums):
        n1,n2,n3 = sorted(nums)
        return abs(n1-n2)==1 or abs(n2-n3)==1 or abs(n1-n3)==1
    for _, row in df_train.tail(50).iterrows():
        ns = [int(row['num1']), int(row['num2']), int(row['num3'])]
        if is_b(ns):
            for d in ns: scores[d] += 0.5
    
    # 万能六码
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
    
    return [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:5]]

def predict_11methods_siping(df_train):
    """10方法 + 四平法"""
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
        scores[d] += ct * 0.5
    
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
    
    # 四平法
    for d, s in predict_siping(df_train).items():
        scores[d] += s
    
    return [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:5]]

# ============================================================
# 测试综合
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

print('\n测试综合方法...')
r1 = test_predict(predict_10methods, '10种方法', 3000)
print('10种方法: %.2f%%' % r1)

r2 = test_predict(predict_11methods_siping, '+四平法', 3000)
print('+四平法: %.2f%%' % r2)

print()
print('='*70)
print('结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 提升 |')
print('|------|--------|------|')
print('| 10种方法 | %.2f%% | - |' % r1)
print('| +四平法 | %.2f%% | %+.2f%% |' % (r2, r2-r1))
print()
print('='*70)