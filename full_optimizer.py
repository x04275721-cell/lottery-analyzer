#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整算法比例优化器 - 测试所有组合"""

import pandas as pd
import random
from collections import Counter, defaultdict
import itertools
import json
from datetime import datetime

print('='*60)
print('完整算法比例优化器')
print('系统性测试所有权重组合')
print('='*60)

pl3 = pd.read_csv('pl3_full.csv')
fc3d = pd.read_csv('fc3d_5years.csv')

# 基础函数
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
        matrix = {k: {d: (trans[k].get(d, 0) + 0.01) / totals[k] for d in range(10)} for k in totals}
        default = {d: 0.1 for d in range(10)}
        matrices.append((matrix, default))
    return matrices

def markov_predict(markov3, history, pos):
    matrix, default = markov3[pos]
    if len(history) >= 3:
        key = (history[-3][pos], history[-2][pos], history[-1][pos])
    elif len(history) >= 2:
        key = (history[-2][pos], history[-1][pos], 5)
    elif len(history) >= 1:
        key = (history[-1][pos], 5, 5)
    else:
        key = (5, 5, 5)
    return matrix.get(key, default)

def get_missing_score(df, nums_tuple):
    score = 0
    for i, d in enumerate(nums_tuple):
        col = ['num1', 'num2', 'num3'][i]
        nums = df[col].astype(int).tolist()
        if d in nums:
            idx = len(nums) - 1 - nums[::-1].index(d)
            missing = len(nums) - idx - 1
        else:
            missing = len(nums)
        if 5 <= missing <= 20:
            score += 0.8
        elif missing < 5:
            score += 0.5
        else:
            score += 0.6
    return score / 3

def get_span_score(df, nums_tuple):
    spans = df['跨度'].astype(int).tolist()[-50:] if '跨度' in df.columns else [4] * 50
    avg_span = sum(spans) / len(spans) if spans else 4
    current_span = max(nums_tuple) - min(nums_tuple)
    diff = abs(current_span - avg_span)
    return max(0, 0.8 - diff * 0.2)

def get_hot_score(df, nums_tuple):
    score = 0
    for i, d in enumerate(nums_tuple):
        col = ['num1', 'num2', 'num3'][i]
        counter = Counter(df[col].astype(int).tolist()[-30:])
        total = sum(counter.values())
        freq = counter.get(d, 0) / total if total > 0 else 0
        score += freq
    return score / 3

def get_bayes_score(df, nums_tuple):
    score = 0
    for i, col in enumerate(['num1', 'num2', 'num3']):
        counter = Counter(df[col].astype(int).tolist())
        total = sum(counter.values())
        score += counter.get(nums_tuple[i], 0) / total if total > 0 else 0.01
    return score / 3

def backtest(df, weights, top_n=10, test_count=1000):
    """回测函数"""
    random.seed(42)
    
    markov_w = weights.get('markov', 30) / 100
    random_w = weights.get('random', 40) / 100
    missing_w = weights.get('missing', 10) / 100
    span_w = weights.get('span', 10) / 100
    hot_w = weights.get('hot', 10) / 100
    bayes_w = weights.get('bayes', 0) / 100
    
    # 归一化
    total_w = markov_w + random_w + missing_w + span_w + hot_w + bayes_w
    if total_w > 0:
        markov_w /= total_w
        random_w /= total_w
        missing_w /= total_w
        span_w /= total_w
        hot_w /= total_w
        bayes_w /= total_w
    
    partial_hits = 0  # 至少2个相同
    three_hits = 0    # 组选命中
    total = min(test_count, len(df) - 600)
    
    for i in range(100, 100 + total):
        train = df.iloc[max(0,i-500):i]
        if len(train) < 100:
            continue
        
        history = [(int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3']))]
        real = (int(df.iloc[i+1]['num1']), int(df.iloc[i+1]['num2']), int(df.iloc[i+1]['num3']))
        real_set = set(real)
        
        markov3 = build_markov3(train)
        
        # 生成候选
        candidates = set()
        for _ in range(int(500 * (markov_w + bayes_w))):
            nums = tuple(random.choices(range(10), weights=[markov3[pos][1].get(d,0.1) for d in range(10)])[0] for pos in range(3))
            candidates.add(nums)
        
        for _ in range(int(500 * random_w)):
            candidates.add(tuple(random.randint(0, 9) for _ in range(3)))
        
        # 评分
        def score(nums_tuple):
            s = 0
            # 马尔可夫
            if markov_w > 0:
                for pos in range(3):
                    probs = markov_predict(markov3, history, pos)
                    s += probs.get(nums_tuple[pos], 0.01) * markov_w * 50
            # 遗漏值
            if missing_w > 0:
                s += get_missing_score(train, nums_tuple) * missing_w * 50
            # 跨度
            if span_w > 0:
                s += get_span_score(train, nums_tuple) * span_w * 30
            # 热号
            if hot_w > 0:
                s += get_hot_score(train, nums_tuple) * hot_w * 30
            # 贝叶斯
            if bayes_w > 0:
                s += get_bayes_score(train, nums_tuple) * bayes_w * 20
            # 随机
            s += random.random() * random_w * 20
            return s
        
        scored = [(n, score(n)) for n in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        top = [n for n, s in scored[:top_n]]
        
        # 检查命中
        if any(set(n) == real_set for n in top):
            three_hits += 1
        if any(len(set(n) & real_set) >= 2 for n in top):
            partial_hits += 1
    
    return {
        'partial': partial_hits / total * 100,
        'three': three_hits / total * 100
    }

# ========== 测试配置 ==========
print('\n开始系统测试...\n')

results = []

# 测试组合1: 马尔可夫 vs 随机
print('[阶段1] 测试马尔可夫+随机比例')
for markov in [20, 30, 40, 50, 60, 70]:
    for random_pct in [30, 40, 50, 60, 70, 80]:
        missing = max(0, 100 - markov - random_pct)
        if missing < 0:
            continue
        weights = {
            'markov': markov,
            'random': random_pct,
            'missing': missing,
            'span': 0,
            'hot': 0,
            'bayes': 0
        }
        r = backtest(pl3, weights, 10, 500)
        results.append({
            'weights': weights,
            'partial': r['partial'],
            'three': r['three']
        })
        print('M%d R%d -> 2同:%.1f%% 组:%.2f%%' % (markov, random_pct, r['partial'], r['three']))

# 排序找最佳
results.sort(key=lambda x: (x['partial'] + x['three'] * 5), reverse=True)

print('\n' + '='*60)
print('TOP 10 最佳组合')
print('='*60)
for i, r in enumerate(results[:10], 1):
    w = r['weights']
    print('%d. M%d R%d Miss%d -> 2同:%.1f%% 组:%.2f%%' % (
        i, w['markov'], w['random'], w['missing'], r['partial'], r['three']))

best = results[0]
print('\n' + '='*60)
print('最佳配置:')
print(best['weights'])
print('2个相同: %.1f%%' % best['partial'])
print('组选命中: %.2f%%' % best['three'])
print('='*60)

# 保存结果
with open('optimizer_results.json', 'w') as f:
    json.dump(results[:50], f, indent=2)

print('\n结果已保存到 optimizer_results.json')
