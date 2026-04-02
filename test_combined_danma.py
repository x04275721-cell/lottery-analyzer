#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整组合测试 - 单胆码 + 双胆码
马尔可夫50% + 书本方法10% + 随机40%
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
from book_methods import run_all_analyses, comprehensive_score

print('='*70)
print('完整组合测试 - 单胆码 & 双胆码')
print('马尔可夫50% + 书本方法10% + 随机40%')
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

def predict_danma_combined(df_train):
    """完整组合预测胆码"""
    analyses = run_all_analyses(df_train)
    markov = build_markov(df_train)
    
    history = []
    for _, row in df_train.tail(5).iterrows():
        history.append((int(row['num1']), int(row['num2']), int(row['num3'])))
    
    # 每个数字的综合得分
    scores = {d: 0 for d in range(10)}
    
    # 1. 马尔可夫得分 (50%)
    markov_probs = {}
    for pos in range(3):
        probs = markov_predict(markov, history, pos)
        for d, p in probs.items():
            markov_probs[d] = markov_probs.get(d, 0) + p
    
    max_markov = max(markov_probs.values()) if markov_probs else 1
    for d in range(10):
        scores[d] += (markov_probs.get(d, 0) / max_markov) * 50
    
    # 2. 书本方法得分 (10%)
    # 热号
    danma = analyses['danma']
    scores[danma['gold_dan']] += 5
    for sd in danma['silver_dan']:
        scores[sd] += 2
    
    # 012路热号
    route_012 = analyses['route_012']
    for pos in range(3):
        for n in route_012[pos]['hot_nums']:
            scores[n] += 1
    
    # 和值热号
    sum_val = analyses['sum_value']
    for s in sum_val['hot_sums'][:3]:
        scores[s % 10] += 1
    
    # 3. 随机得分 (40%)
    for d in range(10):
        scores[d] += random.random() * 40
    
    # 排序得到胆码
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # 单胆码：得分最高的
    single_dan = sorted_nums[0][0]
    
    # 双胆码：得分最高的2个
    double_dan = [sorted_nums[0][0], sorted_nums[1][0]]
    
    return single_dan, double_dan, scores

# 测试
def test_combined_danma(test_count=5000):
    """测试完整组合"""
    random.seed(42)
    
    single_hits = 0
    double_hits = 0
    double_exact = 0  # 双胆全中
    
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
        single_dan, double_dan, scores = predict_danma_combined(df_train)
        
        # 验证单胆码
        if single_dan in real:
            single_hits += 1
        
        # 验证双胆码
        hit_count = sum(1 for d in double_dan if d in real)
        if hit_count >= 1:
            double_hits += 1
        if hit_count == 2:
            double_exact += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d | 单胆: %.1f%% | 双胆至少1中: %.1f%% | 双胆全中: %.1f%%' % (
                i - 100, total,
                single_hits / max(1, i - 100) * 100,
                double_hits / max(1, i - 100) * 100,
                double_exact / max(1, i - 100) * 100
            ))
    
    # 输出结果
    print()
    print('='*70)
    print('完整组合测试结果 (5000期)')
    print('马尔可夫50% + 书本方法10% + 随机40%')
    print('='*70)
    print()
    print('【单胆码】')
    print('  命中: %d次 (%.2f%%)' % (single_hits, single_hits/total*100))
    print('  理论值: 30.00%%')
    print('  对比: %+.2f%%' % (single_hits/total*100 - 30))
    print()
    print('【双胆码】')
    print('  至少中1个: %d次 (%.2f%%)' % (double_hits, double_hits/total*100))
    print('  双胆全中: %d次 (%.2f%%)' % (double_exact, double_exact/total*100))
    print('  理论值: 至少中1个约51%%, 全中约3%%')
    print()
    print('='*70)
    
    return {
        'single_rate': single_hits/total*100,
        'double_at_least_one': double_hits/total*100,
        'double_both': double_exact/total*100
    }

# 运行测试
result = test_combined_danma(5000)

# 保存
import json
with open('combined_danma_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 combined_danma_result.json')
