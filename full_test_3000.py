#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""3000期完整测试"""

import pandas as pd
import random
from collections import Counter, defaultdict
import json

print('='*60)
print('3000期完整测试')
print('='*60)

pl3 = pd.read_csv('pl3_full.csv')

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
        else:
            score += 0.6
    return score / 3

def backtest(weights, top_n=10, test_count=3000):
    random.seed(42)
    
    m = weights.get('markov', 50) / 100
    r = weights.get('random', 50) / 100
    miss = weights.get('missing', 0) / 100
    
    partial_hits = 0
    three_hits = 0
    total = min(test_count, len(pl3) - 600)
    
    for i in range(100, 100 + total):
        train = pl3.iloc[max(0,i-500):i]
        if len(train) < 100:
            continue
        
        history = [(int(pl3.iloc[i]['num1']), int(pl3.iloc[i]['num2']), int(pl3.iloc[i]['num3']))]
        real = (int(pl3.iloc[i+1]['num1']), int(pl3.iloc[i+1]['num2']), int(pl3.iloc[i+1]['num3']))
        real_set = set(real)
        
        markov3 = build_markov3(train)
        
        candidates = set()
        for _ in range(int(500 * m)):
            nums = tuple(random.choices(range(10), weights=[markov3[pos][1].get(d,0.1) for d in range(10)])[0] for pos in range(3))
            candidates.add(nums)
        
        for _ in range(int(500 * r)):
            candidates.add(tuple(random.randint(0, 9) for _ in range(3)))
        
        def score(nums_tuple):
            s = 0
            for pos in range(3):
                probs = markov_predict(markov3, history, pos)
                s += probs.get(nums_tuple[pos], 0.01) * m * 50
            s += get_missing_score(train, nums_tuple) * miss * 50
            s += random.random() * r * 20
            return s
        
        scored = [(n, score(n)) for n in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)
        top = [n for n, s in scored[:top_n]]
        
        if any(set(n) == real_set for n in top):
            three_hits += 1
        if any(len(set(n) & real_set) >= 2 for n in top):
            partial_hits += 1
    
    return {
        'partial': partial_hits / total * 100,
        'three': three_hits / total * 100
    }

# 测试关键组合
test_configs = [
    {'markov': 60, 'random': 30, 'missing': 10},
    {'markov': 40, 'random': 60, 'missing': 0},
    {'markov': 50, 'random': 50, 'missing': 0},
    {'markov': 70, 'random': 30, 'missing': 0},
    {'markov': 30, 'random': 70, 'missing': 0},
    {'markov': 60, 'random': 40, 'missing': 0},
    {'markov': 50, 'random': 40, 'missing': 10},
    {'markov': 40, 'random': 50, 'missing': 10},
    {'markov': 60, 'random': 35, 'missing': 5},
    {'markov': 55, 'random': 40, 'missing': 5},
]

print('\n3000期测试中，请等待...\n')

results = []
for cfg in test_configs:
    print('测试 M%d R%d Miss%d ...' % (cfg['markov'], cfg['random'], cfg['missing']))
    r = backtest(cfg, 10, 3000)
    results.append({**cfg, **r})
    print('  -> 2同:%.1f%% 组:%.2f%%' % (r['partial'], r['three']))

# 排序
results.sort(key=lambda x: (x['partial'], x['three']), reverse=True)

print('\n' + '='*60)
print('3000期测试结果')
print('='*60)

for i, r in enumerate(results, 1):
    print('%d. M%d R%d Miss%d -> 2同:%.1f%% 组:%.2f%%' % (
        i, r['markov'], r['random'], r['missing'], r['partial'], r['three']))

print('\n' + '='*60)
print('理论值（随机10注）：')
print('2个相同: ~70%')
print('组选命中: ~5%')
print('='*60)

best = results[0]
print('\n最佳: M%d R%d Miss%d' % (best['markov'], best['random'], best['missing']))
print('2个相同: %.1f%%' % best['partial'])
print('组选命中: %.2f%%' % best['three'])
