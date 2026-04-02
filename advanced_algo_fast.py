#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简化版混沌分形 + 机器学习"""

import pandas as pd
import random
from collections import Counter, defaultdict
import sys

sys.stdout.reconfigure(encoding='utf-8')

print('='*60)
print('简化版混沌分形 + 机器学习')
print('='*60)

pl3 = pd.read_csv('pl3_full.csv')
print('排列三: %d期' % len(pl3))

# 基础数据
pl3['和值'] = pl3['num1'] + pl3['num2'] + pl3['num3']
pl3['跨度'] = pl3.apply(lambda x: max(x['num1'], x['num2'], x['num3']) - min(x['num1'], x['num2'], x['num3']), axis=1)

# ========== 算法1: 奇怪吸引子 ==========
def attractor_score(df, nums_tuple):
    """奇怪吸引子分析"""
    score = 0
    for i, d in enumerate(nums_tuple):
        col = ['num1', 'num2', 'num3'][i]
        nums = df[col].astype(int).tolist()[-50:]
        mean = sum(nums) / len(nums)
        variance = sum((x - mean) ** 2 for x in nums) / len(nums)
        std = variance ** 0.5
        distance = abs(d - mean) / max(std, 1)
        score += max(0, 0.8 - distance * 0.3)
    return score / 3

# ========== 算法2: 分形维度 ==========
def fractal_score(df, nums_tuple):
    """分形维度简化"""
    sums = df['和值'].astype(int).tolist()[-30:]
    current_sum = sum(nums_tuple)
    sum_mean = sum(sums) / len(sums)
    deviation = abs(current_sum - sum_mean)
    return max(0, 0.8 - deviation / 20)

# ========== 算法3: 机器学习 - 决策树 ==========
def ml_score(df, nums_tuple):
    """简化决策树"""
    score = 0
    for i, d in enumerate(nums_tuple):
        col = ['num1', 'num2', 'num3'][i]
        nums = df[col].astype(int).tolist()[-100:]
        counter = Counter(nums)
        freq = counter.get(d, 0) / 100
        score += freq
    return score / 3

# ========== 算法4: 遗漏回补 ==========
def missing_score(df, nums_tuple):
    """遗漏回补理论"""
    score = 0
    for i, d in enumerate(nums_tuple):
        col = ['num1', 'num2', 'num3'][i]
        nums = df[col].astype(int).tolist()
        if d in nums:
            idx = len(nums) - 1 - nums[::-1].index(d)
            missing = len(nums) - idx - 1
        else:
            missing = len(nums)
        # 遗漏10-20期回补概率高
        if 5 <= missing <= 25:
            score += 0.7
        elif missing < 5:
            score += 0.3
        else:
            score += 0.5
    return score / 3

# ========== 综合评分 ==========
def total_score(nums_tuple, df):
    score = 0
    score += ml_score(df, nums_tuple) * 0.30  # 机器学习 30%
    score += attractor_score(df, nums_tuple) * 0.25  # 奇怪吸引子 25%
    score += fractal_score(df, nums_tuple) * 0.20  # 分形 20%
    score += missing_score(df, nums_tuple) * 0.25  # 遗漏回补 25%
    return score

# ========== 回测 ==========
def backtest(test_count=200):
    random.seed(42)
    group_hits = 0
    partial_hits = 0
    direct_hits = 0
    total = min(test_count, len(pl3) - 300)
    
    for i in range(100, 100 + total):
        train = pl3.iloc[:i]
        
        real = (int(pl3.iloc[i]['num1']), int(pl3.iloc[i]['num2']), int(pl3.iloc[i]['num3']))
        real_set = set(real)
        
        # 生成候选
        candidates = []
        for _ in range(1000):
            nums = tuple(random.randint(0, 9) for _ in range(3))
            candidates.append(nums)
        
        # 评分
        scored = [(n, total_score(n, train)) for n in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        top5 = [n for n, s in scored[:5]]
        
        # 检查命中
        if any(set(n) == real_set for n in top5):
            group_hits += 1
        if any(n == real for n in top5):
            direct_hits += 1
        if any(len(set(n) & real_set) >= 2 for n in top5):
            partial_hits += 1
    
    return {
        'direct': direct_hits / total * 100,
        'group': group_hits / total * 100,
        'partial': partial_hits / total * 100
    }

# ========== 运行 ==========
print('\n测试中...')
r = backtest(300)

print('\n' + '='*60)
print('测试结果：')
print('='*60)
print('直选命中: %.1f%%' % r['direct'])
print('组选命中: %.1f%%' % r['group'])
print('2个相同: %.1f%%' % r['partial'])

print('\n对比：')
print('原算法: 直选1.0%% 组选3.6%% 2同45.2%%')
print('理论值: 直选0.5%% 组选2.4%% 2同~60%%')
