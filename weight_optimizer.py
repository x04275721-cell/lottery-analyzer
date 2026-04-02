#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重调优测试 - 找出最佳配置
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
import json
from book_methods import run_all_analyses, comprehensive_score

print('='*70)
print('权重调优测试 - 找出最佳配置')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# 马尔可夫链
def build_markov_chain(df, order=3):
    matrices = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tolist()
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        for i in range(len(nums) - order):
            key = tuple(nums[i:i+order])
            next_val = nums[i+order]
            trans[key][next_val] += 1
            totals[key] += 1
        matrix = {}
        for key in totals:
            total = totals[key]
            matrix[key] = {d: (trans[key].get(d, 0) + 0.01) / total for d in range(10)}
        matrices.append(matrix)
    return matrices

def markov_predict(matrices, history, pos):
    matrix = matrices[pos]
    if len(history) >= 3:
        key = (history[-3][pos], history[-2][pos], history[-1][pos])
    elif len(history) >= 2:
        key = (history[-2][pos], history[-1][pos], 5)
    elif len(history) >= 1:
        key = (history[-1][pos], 5, 5)
    else:
        key = (5, 5, 5)
    return matrix.get(key, {d: 0.1 for d in range(10)})

def generate_candidates_v2(df_train, markov_weight=0.3, book_weight=0.5, random_weight=0.2):
    """生成候选号码 - 可调权重"""
    candidates = set()
    analyses = run_all_analyses(df_train)
    markov = build_markov_chain(df_train)
    history = []
    for _, row in df_train.tail(5).iterrows():
        history.append((int(row['num1']), int(row['num2']), int(row['num3'])))
    
    # 马尔可夫生成
    markov_count = int(300 * markov_weight)
    for _ in range(markov_count):
        nums = []
        for pos in range(3):
            probs = markov_predict(markov, history, pos)
            n = random.choices(range(10), weights=[probs.get(d, 0.1) for d in range(10)])[0]
            nums.append(n)
        candidates.add(tuple(nums))
    
    # 胆码优先
    danma = analyses['danma']
    gold = danma['gold_dan']
    silver = danma['silver_dan']
    
    book_count = int(300 * book_weight)
    for _ in range(book_count):
        if random.random() < 0.6:
            must_have = gold
        else:
            must_have = random.choice(silver)
        nums = [must_have]
        for _ in range(2):
            nums.append(random.randint(0, 9))
        random.shuffle(nums)
        candidates.add(tuple(nums))
    
    # 随机生成
    random_count = int(300 * random_weight)
    for _ in range(random_count):
        candidates.add((random.randint(0, 9), random.randint(0, 9), random.randint(0, 9)))
    
    return list(candidates)[:500], analyses, markov, history

def score_candidate_v2(nums, analyses, markov, history, markov_w=0.3, book_w=0.5, random_w=0.2):
    """打分 - 可调权重"""
    score = 0
    
    # 书本方法评分
    score += comprehensive_score(nums, analyses) * book_w
    
    # 马尔可夫评分
    for pos, n in enumerate(nums):
        probs = markov_predict(markov, history, pos)
        score += probs.get(n, 0.01) * 30 * markov_w
    
    # 随机因素
    score += random.random() * 10 * random_w
    
    return score

def backtest_config(markov_w, book_w, random_w, test_count=2000, top_n=10):
    """回测特定配置"""
    random.seed(42)
    
    partial_hits = 0
    three_hits = 0
    total = min(test_count, len(df) - 600)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100:
            continue
        
        real = (int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3']))
        real_set = set(real)
        
        candidates, analyses, markov, history = generate_candidates_v2(
            df_train, markov_w, book_w, random_w
        )
        
        scored = []
        for nums in candidates:
            s = score_candidate_v2(nums, analyses, markov, history, markov_w, book_w, random_w)
            scored.append((nums, s))
        
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

# 测试不同配置
configs = [
    {'markov': 0.5, 'book': 0.3, 'random': 0.2, 'name': 'M50 B30 R20'},
    {'markov': 0.4, 'book': 0.4, 'random': 0.2, 'name': 'M40 B40 R20'},
    {'markov': 0.3, 'book': 0.5, 'random': 0.2, 'name': 'M30 B50 R20'},
    {'markov': 0.2, 'book': 0.6, 'random': 0.2, 'name': 'M20 B60 R20'},
    {'markov': 0.6, 'book': 0.2, 'random': 0.2, 'name': 'M60 B20 R20'},
    {'markov': 0.3, 'book': 0.3, 'random': 0.4, 'name': 'M30 B30 R40'},
    {'markov': 0.2, 'book': 0.4, 'random': 0.4, 'name': 'M20 B40 R40'},
    {'markov': 0.4, 'book': 0.2, 'random': 0.4, 'name': 'M40 B20 R40'},
    {'markov': 0.1, 'book': 0.5, 'random': 0.4, 'name': 'M10 B50 R40'},
    {'markov': 0.5, 'book': 0.1, 'random': 0.4, 'name': 'M50 B10 R40'},
]

print('\n测试不同权重配置...')
print('='*70)

results = []
for cfg in configs:
    print('测试 %s ...' % cfg['name'])
    r = backtest_config(cfg['markov'], cfg['book'], cfg['random'], test_count=2000, top_n=10)
    results.append({
        'name': cfg['name'],
        'markov': cfg['markov'],
        'book': cfg['book'],
        'random': cfg['random'],
        'partial': r['partial'],
        'three': r['three']
    })
    print('  -> 2同: %.1f%% 组选: %.2f%%' % (r['partial'], r['three']))

# 排序
results.sort(key=lambda x: (x['partial'], x['three']), reverse=True)

print()
print('='*70)
print('2000期测试结果排名')
print('='*70)

for i, r in enumerate(results, 1):
    print('%d. %s -> 2同: %.1f%% 组选: %.2f%%' % (
        i, r['name'], r['partial'], r['three']
    ))

print()
print('='*70)
print('最佳配置: %s' % results[0]['name'])
print('='*70)

# 用最佳配置跑5000期
best = results[0]
print('\n用最佳配置跑5000期...')
print('='*70)

random.seed(42)
partial_hits = 0
three_hits = 0
total = 5000

for i in range(100, 100 + total):
    df_train = df.iloc[max(0, i-500):i]
    if len(df_train) < 100:
        continue
    
    real = (int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3']))
    real_set = set(real)
    
    candidates, analyses, markov, history = generate_candidates_v2(
        df_train, best['markov'], best['book'], best['random']
    )
    
    scored = []
    for nums in candidates:
        s = score_candidate_v2(nums, analyses, markov, history, best['markov'], best['book'], best['random'])
        scored.append((nums, s))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    top = [n for n, s in scored[:10]]
    
    if any(set(n) == real_set for n in top):
        three_hits += 1
    if any(len(set(n) & real_set) >= 2 for n in top):
        partial_hits += 1
    
    if (i - 100) % 1000 == 0:
        print('进度: %d/5000 | 2同: %.1f%% | 组选: %.2f%%' % (
            i - 100, partial_hits / max(1, i - 100) * 100, three_hits / max(1, i - 100) * 100
        ))

print()
print('='*70)
print('最终结果 (5000期)')
print('='*70)
print('配置: %s' % best['name'])
print('至少2个相同: %d次 (%.2f%%)' % (partial_hits, partial_hits/total*100))
print('组选命中: %d次 (%.2f%%)' % (three_hits, three_hits/total*100))
print('='*70)

# 保存结果
with open('weight_optimization_result.json', 'w', encoding='utf-8') as f:
    json.dump({
        'best_config': best,
        'all_results': results,
        'final_5000': {
            'partial': partial_hits / total * 100,
            'three': three_hits / total * 100
        }
    }, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 weight_optimization_result.json')
