#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""综合多算法系统 V8"""

import pandas as pd
import random
from collections import Counter, defaultdict
import sys

sys.stdout.reconfigure(encoding='utf-8')

print('='*60)
print('综合多算法系统 V8 - 整合多种算法')
print('='*60)

pl3 = pd.read_csv('pl3_full.csv')
print('排列三总共: %d期' % len(pl3))

# ========== 算法1: 三阶马尔可夫链 ==========
def build_markov3(df):
    matrices = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tolist()
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        for i in range(len(nums) - 3):
            key = (nums[i], nums[i+1], nums[i+2])
            trans[key][nums[i+3]] += 1
            totals[key] += 1
        matrix = {}
        for k in totals:
            matrix[k] = {d: (trans[k].get(d, 0) + 0.01) / totals[k] for d in range(10)}
        default = {d: 0.1 for d in range(10)}
        matrices.append((matrix, default))
    return matrices

def markov_score(markov3, history, nums_tuple):
    score = 0
    for pos in range(3):
        matrix, default = markov3[pos]
        if len(history) >= 3:
            key = (history[-3][pos], history[-2][pos], history[-1][pos])
        elif len(history) >= 2:
            key = (history[-2][pos], history[-1][pos], 5)
        elif len(history) >= 1:
            key = (history[-1][pos], 5, 5)
        else:
            key = (5, 5, 5)
        probs = matrix.get(key, default)
        score += probs.get(nums_tuple[pos], 0.01)
    return score

# ========== 算法2: 贝叶斯概率 ==========
def bayes_score(df, nums_tuple):
    score = 0
    for i, col in enumerate(['num1', 'num2', 'num3']):
        counter = Counter(df[col].astype(int).tolist())
        total = sum(counter.values())
        # 先验概率 + 平滑
        prior = counter.get(nums_tuple[i], 0) / total if total > 0 else 0.1
        score += prior
    return score / 3

# ========== 算法3: 移动平均（时间序列） ==========
def moving_avg_score(df, nums_tuple, window=20):
    score = 0
    recent = df.head(window)
    for i, col in enumerate(['num1', 'num2', 'num3']):
        counter = Counter(recent[col].astype(int).tolist())
        total = sum(counter.values())
        # 最近期出现次数作为分数
        count = counter.get(nums_tuple[i], 0)
        score += count / total if total > 0 else 0.1
    return score / 3

# ========== 算法4: 遗漏值分析 ==========
def missing_score(df, nums_tuple):
    """遗漏值：数字越久没出现，分数越高"""
    score = 0
    for i, col in enumerate(['num1', 'num2', 'num3']):
        nums = df[col].astype(int).tolist()
        d = nums_tuple[i]
        # 找到最近出现位置
        if d in nums:
            idx = nums.index(d)
            missing = len(nums) - idx
        else:
            missing = len(nums) + 1
        # 遗漏值越大，分数越高（回补理论）
        score += min(missing / 50, 1.0)
    return score / 3

# ========== 算法5: 位置关系分析 ==========
def position_score(nums_tuple, history):
    """分析号码与历史的位置关系"""
    score = 0
    if not history:
        return 0.5
    
    last = history[-1]
    # 号码与上期相同位置重复
    for pos in range(3):
        if nums_tuple[pos] == last[pos]:
            score += 0.1  # 位置重复加分
        # 相邻数字
        diff = abs(nums_tuple[pos] - last[pos])
        if diff <= 2:
            score += 0.05  # 相邻加分
    
    # 跨度分析
    span = max(nums_tuple) - min(nums_tuple)
    if span in [3, 4, 5, 6]:  # 适中跨度
        score += 0.2
    
    return min(score, 1.0)

# ========== 算法6: 邻号分析 ==========
def neighbor_score(nums_tuple, df):
    """邻号：一个数字相邻的数字出现概率"""
    score = 0
    for i, col in enumerate(['num1', 'num2', 'num3']):
        nums = df[col].astype(int).tolist()[:50]
        counter = Counter(nums)
        total = sum(counter.values())
        for d in nums_tuple:
            # 邻号出现次数
            neighbor_count = counter.get((d-1)%10, 0) + counter.get((d+1)%10, 0)
            score += neighbor_count / total if total > 0 else 0.1
    return score / 3

# ========== 算法7: 奇偶/大小分析 ==========
def pattern_score(nums_tuple):
    """奇偶比例分析"""
    odd = sum(1 for d in nums_tuple if d % 2 == 1)
    if odd == 1 or odd == 2:  # 1:2 或 2:1 最常见
        return 0.8
    elif odd == 0 or odd == 3:  # 全奇/全偶较少
        return 0.3
    return 0.5

# ========== 综合评分 ==========
def total_score(nums_tuple, df, markov3, history, weights):
    """
    权重可调的综合评分
    weights: dict of algorithm weights
    """
    score = 0
    
    # 算法1: 马尔可夫 30%
    score += markov_score(markov3, history, nums_tuple) * weights.get('markov', 0.3)
    
    # 算法2: 贝叶斯 15%
    score += bayes_score(df, nums_tuple) * weights.get('bayes', 0.15)
    
    # 算法3: 移动平均 15%
    score += moving_avg_score(df, nums_tuple) * weights.get('moving_avg', 0.15)
    
    # 算法4: 遗漏值 10%
    score += missing_score(df, nums_tuple) * weights.get('missing', 0.10)
    
    # 算法5: 位置关系 10%
    score += position_score(nums_tuple, history) * weights.get('position', 0.10)
    
    # 算法6: 邻号 10%
    score += neighbor_score(nums_tuple, df) * weights.get('neighbor', 0.10)
    
    # 算法7: 模式 10%
    score += pattern_score(nums_tuple) * weights.get('pattern', 0.10)
    
    return score

# ========== 回测函数 ==========
def backtest(weights, test_count=500):
    random.seed(42)
    group_hits = 0
    partial_hits = 0
    direct_hits = 0
    total = min(test_count, len(pl3) - 700)
    
    for i in range(100, 100 + total):
        train = pl3.iloc[:i]
        
        history = [(int(pl3.iloc[i]['num1']), int(pl3.iloc[i]['num2']), int(pl3.iloc[i]['num3']))]
        real = (int(pl3.iloc[i+1]['num1']), int(pl3.iloc[i+1]['num2']), int(pl3.iloc[i+1]['num3']))
        real_set = set(real)
        
        markov3 = build_markov3(train)
        
        # 生成候选
        candidates = set()
        for _ in range(1000):
            nums = tuple(random.randint(0, 9) for _ in range(3))
            candidates.add(nums)
        
        # 评分排序
        scored = []
        for nums in candidates:
            s = total_score(nums, train, markov3, history, weights)
            scored.append((nums, s))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top5 = [n for n, s in scored[:5]]
        
        # 检查命中
        if any(set(nums) == real_set for nums in top5):
            group_hits += 1
        if any(nums == real for nums in top5):
            direct_hits += 1
        if any(len(set(nums) & real_set) >= 2 for nums in top5):
            partial_hits += 1
    
    return {
        'direct': direct_hits / total * 100,
        'group': group_hits / total * 100,
        'partial': partial_hits / total * 100
    }

# ========== 测试不同的权重组合 ==========
print('\n' + '='*60)
print('多算法综合测试')
print('='*60)

# 测试默认权重
default_weights = {
    'markov': 0.30,
    'bayes': 0.15,
    'moving_avg': 0.15,
    'missing': 0.10,
    'position': 0.10,
    'neighbor': 0.10,
    'pattern': 0.10
}

print('\n[默认权重] 500期测试：')
r = backtest(default_weights, 500)
print('直选: %.1f%%  组选: %.1f%%  2个相同: %.1f%%' % (r['direct'], r['group'], r['partial']))

# 测试不同组合
print('\n' + '-'*60)
print('测试不同权重组合：')
print('-'*60)

test_configs = [
    # 侧重马尔可夫
    {'name': '马尔可夫为主', 'markov': 0.50, 'bayes': 0.10, 'moving_avg': 0.10, 'missing': 0.10, 'position': 0.10, 'neighbor': 0.05, 'pattern': 0.05},
    # 侧重遗漏值
    {'name': '遗漏值为主', 'markov': 0.20, 'bayes': 0.10, 'moving_avg': 0.10, 'missing': 0.40, 'position': 0.10, 'neighbor': 0.05, 'pattern': 0.05},
    # 侧重位置关系
    {'name': '位置关系为主', 'markov': 0.25, 'bayes': 0.10, 'moving_avg': 0.10, 'missing': 0.10, 'position': 0.30, 'neighbor': 0.10, 'pattern': 0.05},
    # 均匀分布
    {'name': '均匀分布', 'markov': 0.20, 'bayes': 0.15, 'moving_avg': 0.15, 'missing': 0.15, 'position': 0.15, 'neighbor': 0.10, 'pattern': 0.10},
    # 侧重邻号
    {'name': '邻号为主', 'markov': 0.25, 'bayes': 0.10, 'moving_avg': 0.10, 'missing': 0.10, 'position': 0.10, 'neighbor': 0.30, 'pattern': 0.05},
    # 无马尔可夫
    {'name': '无马尔可夫', 'markov': 0.00, 'bayes': 0.20, 'moving_avg': 0.20, 'missing': 0.20, 'position': 0.20, 'neighbor': 0.15, 'pattern': 0.05},
]

best = None
best_rate = 0

for cfg in test_configs:
    name = cfg.pop('name')
    r = backtest(cfg, 300)
    mark = ' >>>' if r['partial'] >= 50 else ''
    print('%s: 直选%.1f%% 组选%.1f%% 2同%.1f%%%s' % (name, r['direct'], r['group'], r['partial'], mark))
    if r['partial'] > best_rate:
        best_rate = r['partial']
        best = cfg.copy()
        best['name'] = name

print('-'*60)
print('最佳配置: %s (2个相同%.1f%%)' % (best['name'], best_rate))
