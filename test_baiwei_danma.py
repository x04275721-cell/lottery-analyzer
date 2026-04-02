#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百位胆码深度分析
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
from book_methods import run_all_analyses

print('='*70)
print('百位胆码深度分析')
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

def predict_baiwei_danma(df_train):
    """预测百位胆码"""
    analyses = run_all_analyses(df_train)
    markov = build_markov(df_train)
    
    history = []
    for _, row in df_train.tail(5).iterrows():
        history.append((int(row['num1']), int(row['num2']), int(row['num3'])))
    
    # 百位各数字得分
    scores = {d: 0 for d in range(10)}
    
    # 1. 马尔可夫得分 (50%)
    probs = markov_predict(markov, history, 0)
    max_p = max(probs.values()) if probs else 1
    for d in range(10):
        scores[d] += (probs.get(d, 0) / max_p) * 50
    
    # 2. 书本方法得分 (10%)
    danma = analyses['danma']
    scores[danma['gold_dan']] += 5
    for sd in danma['silver_dan']:
        scores[sd] += 2
    
    route_012 = analyses['route_012']
    for n in route_012[0]['hot_nums']:
        scores[n] += 2
    
    # 3. 随机得分 (40%)
    for d in range(10):
        scores[d] += random.random() * 40
    
    # 排序
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'top1': sorted_nums[0][0],  # 最佳胆码
        'top2': sorted_nums[1][0],  # 次佳胆码
        'top3': [sorted_nums[0][0], sorted_nums[1][0], sorted_nums[2][0]],  # 前3胆码
        'scores': scores
    }

# 测试
def test_baiwei_danma(test_count=5000):
    """测试百位胆码"""
    random.seed(42)
    
    results = {
        'top1_hit': 0,      # 最佳胆码命中
        'top2_hit': 0,      # 次佳胆码命中
        'top3_hit': 0,      # 前3胆码任中
        'top1_or_top2': 0,  # 最佳或次佳命中
    }
    
    # 各数字命中统计
    digit_hits = {d: 0 for d in range(10)}
    digit_total = {d: 0 for d in range(10)}
    
    total = min(test_count, len(df) - 600)
    
    print('\n开始测试...')
    print('测试期数: %d' % total)
    print()
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100:
            continue
        
        # 实际开奖百位
        real_bai = int(df.iloc[i]['num1'])
        
        # 预测
        pred = predict_baiwei_danma(df_train)
        
        # 验证
        if real_bai == pred['top1']:
            results['top1_hit'] += 1
        if real_bai == pred['top2']:
            results['top2_hit'] += 1
        if real_bai in pred['top3']:
            results['top3_hit'] += 1
        if real_bai in [pred['top1'], pred['top2']]:
            results['top1_or_top2'] += 1
        
        # 统计各数字
        digit_total[pred['top1']] += 1
        if real_bai == pred['top1']:
            digit_hits[pred['top1']] += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d | Top1: %.1f%% | Top2: %.1f%% | Top3: %.1f%%' % (
                i - 100, total,
                results['top1_hit'] / max(1, i - 100) * 100,
                results['top2_hit'] / max(1, i - 100) * 100,
                results['top3_hit'] / max(1, i - 100) * 100
            ))
    
    # 输出结果
    print()
    print('='*70)
    print('百位胆码测试结果 (5000期)')
    print('='*70)
    print()
    print('【理论值】')
    print('  单胆码: 10%')
    print('  双胆码: 20%')
    print('  三胆码: 30%')
    print()
    print('【测试结果】')
    print('-'*70)
    print('Top1胆码命中: %d次 (%.2f%%) 理论10%%' % (results['top1_hit'], results['top1_hit']/total*100))
    print('Top2胆码命中: %d次 (%.2f%%) 理论10%%' % (results['top2_hit'], results['top2_hit']/total*100))
    print('Top1或Top2命中: %d次 (%.2f%%) 理论20%%' % (results['top1_or_top2'], results['top1_or_top2']/total*100))
    print('Top3任中: %d次 (%.2f%%) 理论30%%' % (results['top3_hit'], results['top3_hit']/total*100))
    print('-'*70)
    print()
    print('【各数字作为胆码的命中率】')
    print('-'*70)
    for d in range(10):
        if digit_total[d] > 0:
            rate = digit_hits[d] / digit_total[d] * 100
            print('数字%d: 推荐%d次, 命中%d次 (%.1f%%)' % (d, digit_total[d], digit_hits[d], rate))
    print('='*70)
    
    return {k: v/total*100 for k, v in results.items()}

# 运行测试
result = test_baiwei_danma(5000)

# 保存
import json
with open('baiwei_danma_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 baiwei_danma_result.json')
