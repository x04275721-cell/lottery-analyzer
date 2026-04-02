#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""历史回测 - 寻找最佳算法权重"""

import pandas as pd
import random
from collections import Counter, defaultdict
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

print('='*60)
print('多算法历史回测 - 寻找最佳比例')
print('='*60)

pl3 = pd.read_csv('pl3_full.csv')
fc3d = pd.read_csv('fc3d_5years.csv')

print('\n排列三：%d期' % len(pl3))
print('3D：%d期' % len(fc3d))

def build_markov3(df):
    matrices = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tolist()
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        for i in range(len(nums) - 3):
            key = (nums[i], nums[i+1], nums[i+2])
            curr = nums[i+3]
            trans[key][curr] += 1
            totals[key] += 1
        matrix = {}
        for key in totals:
            matrix[key] = {d: trans[key].get(d, 0) + 0.01 for d in range(10)}
            total = sum(matrix[key].values())
            for d in matrix[key]:
                matrix[key][d] /= total
        matrices.append(matrix)
    return matrices

def build_first_order(df):
    nums_list = list(zip(df['num1'].astype(int), df['num2'].astype(int), df['num3'].astype(int)))
    matrix = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)
    for i in range(len(nums_list) - 1):
        for p, c in zip(nums_list[i], nums_list[i+1]):
            matrix[p][c] += 1
            totals[p] += 1
    result = {}
    for p in range(10):
        result[p] = {c: (matrix[p][c] / totals[p] if totals[p] > 0 else 0.01) for c in range(10)}
        total = sum(result[p].values())
        for c in result[p]:
            result[p][c] /= total
    return result

def markov_predict(markov3, markov1, history, pos):
    if len(history) >= 3:
        key = (history[-3][pos], history[-2][pos], history[-1][pos])
    elif len(history) >= 2:
        key = (history[-2][pos], history[-1][pos], 5)
    elif len(history) >= 1:
        key = (history[-1][pos], 5, 5)
    else:
        key = (5, 5, 5)
    probs3 = markov3[pos].get(key, {d: 0.1 for d in range(10)})
    if history:
        probs1 = markov1.get(history[-1][pos], {d: 0.1 for d in range(10)})
    else:
        probs1 = {d: 0.1 for d in range(10)}
    combined = {d: probs3.get(d, 0.1) * 0.6 + probs1.get(d, 0.1) * 0.4 for d in range(10)}
    total = sum(combined.values())
    for d in combined:
        combined[d] /= total
    return combined

def backtest(df, weights, test_range=100):
    random.seed(42)
    m1, m2, m3, m4, m5 = [w/100.0 for w in weights]
    
    direct_hit = 0  # 直选命中
    group_hit = 0   # 组选命中
    total = min(test_range, len(df) - 20)
    
    for i in range(10, 10 + total):
        train = df.iloc[max(0, i-500):i]
        
        # 历史（上期）
        if i >= 1:
            h1 = int(df.iloc[i-1]['num1'])
            h2 = int(df.iloc[i-1]['num2'])
            h3 = int(df.iloc[i-1]['num3'])
            history = [(h1, h2, h3)]
        else:
            history = [(5, 5, 5)]
        
        # 真实（本期）
        r1 = int(df.iloc[i]['num1'])
        r2 = int(df.iloc[i]['num2'])
        r3 = int(df.iloc[i]['num3'])
        real = (r1, r2, r3)
        real_sorted = tuple(sorted(real))
        
        # 构建矩阵
        markov3 = build_markov3(train)
        markov1 = build_first_order(train)
        
        # 热号
        hot = []
        for col in ['num1', 'num2', 'num3']:
            counter = Counter(train.head(100)[col].astype(int).tolist())
            hot.append([d for d, c in counter.most_common(8)])
        
        # 和值热号
        sums = Counter(train.head(100)['和值'].astype(int).tolist())
        hot_sums = [s for s, c in sums.most_common(8)]
        
        # 生成候选
        candidates = []
        for _ in range(500):
            nums = []
            for pos in range(3):
                probs = markov_predict(markov3, markov1, history, pos)
                digit = random.choices(range(10), weights=[probs.get(d, 0.1) for d in range(10)])[0]
                nums.append(digit)
            candidates.append(tuple(nums))
        
        for _ in range(200):
            nums = tuple(random.choice(hot[p]) for p in range(3))
            candidates.append(nums)
        
        candidates = list(set(candidates))
        
        # 评分
        def score(nums_tuple):
            s = 0
            for pos in range(3):
                probs = markov_predict(markov3, markov1, history, pos)
                s += probs.get(nums_tuple[pos], 0.01) * m1 * 50
            for pos, d in enumerate(nums_tuple):
                if d in hot[pos][:5]:
                    s += m4 * 5
            if sum(nums_tuple) in hot_sums[:5]:
                s += m2 * 10
            span = max(nums_tuple) - min(nums_tuple)
            if span in [3, 4, 5, 6]:
                s += m5 * 5
            s += m3 * random.random() * 10
            return min(s, 100)
        
        candidates.sort(key=lambda x: score(x), reverse=True)
        top5 = candidates[:5]
        
        # 检查命中
        for nums in top5:
            if nums == real:
                direct_hit += 1
                break
            if tuple(sorted(nums)) == real_sorted:
                group_hit += 1
                break
    
    return direct_hit / total * 100.0, group_hit / total * 100.0

# 测试
print('\n开始回测（请等待）...\n')

test_cases = [
    (30, 25, 20, 15, 15),
    (40, 20, 20, 10, 10),
    (35, 25, 15, 15, 10),
    (25, 30, 20, 15, 10),
    (30, 30, 15, 15, 10),
    (35, 30, 15, 10, 10),
    (40, 25, 15, 10, 10),
    (30, 35, 15, 10, 10),
]

results = []
for weights in test_cases:
    print('测试权重: %s...' % str(weights))
    direct, group = backtest(pl3, weights, 50)
    print('  直选命中率: %.1f%%, 组选命中率: %.1f%%' % (direct, group))
    results.append((weights, direct, group))

results.sort(key=lambda x: x[1] + x[2], reverse=True)

print('\n' + '='*60)
print('回测结果排名（直选+组选）：')
print('='*60)
for i, (weights, direct, group) in enumerate(results, 1):
    print('%d. 权重%s: 直选%.1f%% + 组选%.1f%%' % (i, weights, direct, group))

best = results[0][0]
print('\n推荐最佳权重: %s' % str(best))
print('='*60)

with open('best_weights.json', 'w') as f:
    json.dump({
        'best_weights': list(best), 
        'results': [(list(w), d, g) for w, d, g in results]
    }, f, ensure_ascii=False, indent=2)
print('\n结果已保存到 best_weights.json')
