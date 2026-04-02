#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
组选五码测试 - 推荐5个数字，看开奖号是否全在其中
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
from book_methods import run_all_analyses

print('='*70)
print('组选五码测试 - 推荐5个数字')
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

def predict_5ma(df_train):
    """预测组选五码"""
    analyses = run_all_analyses(df_train)
    markov = build_markov(df_train)
    
    history = []
    for _, row in df_train.tail(5).iterrows():
        history.append((int(row['num1']), int(row['num2']), int(row['num3'])))
    
    # 每个数字的综合得分
    scores = {d: 0 for d in range(10)}
    
    # 1. 马尔可夫得分 (50%)
    for pos in range(3):
        probs = markov_predict(markov, history, pos)
        max_p = max(probs.values()) if probs else 1
        for d in range(10):
            scores[d] += (probs.get(d, 0) / max_p) * 50
    
    # 2. 书本方法得分 (10%)
    danma = analyses['danma']
    scores[danma['gold_dan']] += 5
    for sd in danma['silver_dan']:
        scores[sd] += 2
    
    route_012 = analyses['route_012']
    for pos in range(3):
        for n in route_012[pos]['hot_nums']:
            scores[n] += 1
    
    # 3. 随机得分 (40%)
    for d in range(10):
        scores[d] += random.random() * 40
    
    # 排序取前5
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top5 = [n for n, s in sorted_nums[:5]]
    
    return top5, scores

# 测试
def test_zuxuan_5ma(test_count=5000):
    """测试组选五码"""
    random.seed(42)
    
    full_hit = 0      # 开奖号3个数字全在5码中
    at_least_2 = 0    # 至少2个在5码中
    at_least_1 = 0    # 至少1个在5码中
    
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
        real_set = set(real)
        
        # 预测五码
        top5, scores = predict_5ma(df_train)
        top5_set = set(top5)
        
        # 验证
        hit_count = len(real_set & top5_set)
        
        if hit_count == len(real_set):  # 全中
            full_hit += 1
        if hit_count >= 2:
            at_least_2 += 1
        if hit_count >= 1:
            at_least_1 += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d | 全中: %.1f%% | 至少2: %.1f%% | 至少1: %.1f%%' % (
                i - 100, total,
                full_hit / max(1, i - 100) * 100,
                at_least_2 / max(1, i - 100) * 100,
                at_least_1 / max(1, i - 100) * 100
            ))
    
    # 输出结果
    print()
    print('='*70)
    print('组选五码测试结果 (5000期)')
    print('='*70)
    print()
    print('【理论值】')
    print('  组选五码全中: C(5,3)/C(10,3) = 10/120 = 8.33%%')
    print('  至少2个在五码中: 约50%%')
    print('  至少1个在五码中: 约65%%')
    print()
    print('【测试结果】')
    print('-'*70)
    print('开奖号全在五码中: %d次 (%.2f%%) 理论8.33%%' % (full_hit, full_hit/total*100))
    print('至少2个在五码中: %d次 (%.2f%%) 理论50%%' % (at_least_2, at_least_2/total*100))
    print('至少1个在五码中: %d次 (%.2f%%) 理论65%%' % (at_least_1, at_least_1/total*100))
    print('='*70)
    
    return {
        'full_hit': full_hit/total*100,
        'at_least_2': at_least_2/total*100,
        'at_least_1': at_least_1/total*100
    }

# 运行测试
result = test_zuxuan_5ma(5000)

# 保存
import json
with open('zuxuan_5ma_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 zuxuan_5ma_result.json')
