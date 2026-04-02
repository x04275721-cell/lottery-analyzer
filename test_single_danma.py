#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单胆码测试 - 每期推荐1个胆码
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
from book_methods import run_all_analyses

print('='*70)
print('单胆码测试 - 每期推荐1个胆码')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# 马尔可夫链
def build_markov(df, order=3):
    matrices = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tolist()
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        for i in range(len(nums) - order):
            key = tuple(nums[i:i+order])
            trans[key][nums[i+order]] += 1
            totals[key] += 1
        matrix = {}
        for key in totals:
            matrix[key] = {d: (trans[key].get(d, 0) + 0.01) / totals[key] for d in range(10)}
        matrices.append(matrix)
    return matrices

def markov_predict(matrices, history, pos):
    matrix = matrices[pos]
    if len(history) >= 3:
        key = (history[-3][pos], history[-2][pos], history[-1][pos])
    elif len(history) >= 2:
        key = (history[-2][pos], history[-1][pos], 5)
    else:
        key = (5, 5, 5)
    return matrix.get(key, {d: 0.1 for d in range(10)})

def predict_single_danma(df_train, method='combined'):
    """预测单个胆码"""
    analyses = run_all_analyses(df_train)
    markov = build_markov(df_train)
    
    history = []
    for _, row in df_train.tail(5).iterrows():
        history.append((int(row['num1']), int(row['num2']), int(row['num3'])))
    
    # 方法1: 纯热号
    danma = analyses['danma']
    hot_dan = danma['gold_dan']
    
    # 方法2: 马尔可夫预测
    markov_probs = {}
    for pos in range(3):
        probs = markov_predict(markov, history, pos)
        for d, p in probs.items():
            markov_probs[d] = markov_probs.get(d, 0) + p
    
    markov_dan = max(markov_probs, key=markov_probs.get)
    
    # 方法3: 012路热号
    route_012 = analyses['route_012']
    route_counts = Counter()
    for pos in range(3):
        for n in route_012[pos]['hot_nums']:
            route_counts[n] += 1
    route_dan = route_counts.most_common(1)[0][0]
    
    # 方法4: 和值热号
    sum_val = analyses['sum_value']
    # 根据热和值推算胆码
    sum_dan = sum_val['hot_sums'][0] % 10
    
    # 综合投票
    votes = Counter()
    votes[hot_dan] += 3      # 热号权重3
    votes[markov_dan] += 3   # 马尔可夫权重3
    votes[route_dan] += 2    # 012路权重2
    votes[sum_dan] += 1      # 和值权重1
    
    final_dan = votes.most_common(1)[0][0]
    
    return {
        'hot_dan': hot_dan,
        'markov_dan': markov_dan,
        'route_dan': route_dan,
        'sum_dan': sum_dan,
        'final_dan': final_dan
    }

# 测试
def test_single_danma(test_count=5000):
    """测试单胆码准确率"""
    random.seed(42)
    
    results = {
        'hot_dan': 0,
        'markov_dan': 0,
        'route_dan': 0,
        'sum_dan': 0,
        'final_dan': 0
    }
    
    total = min(test_count, len(df) - 600)
    
    print('\n开始测试...')
    print('测试期数: %d' % total)
    print()
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100:
            continue
        
        # 实际开奖
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        
        # 预测
        pred = predict_single_danma(df_train)
        
        # 验证
        if pred['hot_dan'] in real:
            results['hot_dan'] += 1
        if pred['markov_dan'] in real:
            results['markov_dan'] += 1
        if pred['route_dan'] in real:
            results['route_dan'] += 1
        if pred['sum_dan'] in real:
            results['sum_dan'] += 1
        if pred['final_dan'] in real:
            results['final_dan'] += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d' % (i - 100, total))
    
    # 输出结果
    print()
    print('='*70)
    print('单胆码测试结果 (5000期)')
    print('='*70)
    print('理论命中率: 30% (随机选1个数字，3个位置)')
    print()
    print('各方法命中率:')
    print('-'*70)
    
    for method, hits in sorted(results.items(), key=lambda x: x[1], reverse=True):
        rate = hits / total * 100
        vs_theory = rate - 30
        symbol = '[+]' if vs_theory > 0 else '[-]'
        print('%s: %d次 (%.2f%%) %s 理论%.1f%%' % (
            method.ljust(12), hits, rate, symbol, vs_theory
        ))
    
    print('='*70)
    
    return {k: v / total * 100 for k, v in results.items()}

# 运行测试
result = test_single_danma(5000)

# 保存
import json
with open('single_danma_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 single_danma_result.json')
