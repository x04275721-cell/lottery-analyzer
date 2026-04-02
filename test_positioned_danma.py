#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单胆码定位测试 - 预测胆码+位置
例如：预测胆码5出现在百位
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
from book_methods import run_all_analyses

print('='*70)
print('单胆码定位测试 - 预测胆码+位置')
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

def predict_positioned_danma(df_train):
    """预测定位胆码：胆码+位置"""
    analyses = run_all_analyses(df_train)
    markov = build_markov(df_train)
    
    history = []
    for _, row in df_train.tail(5).iterrows():
        history.append((int(row['num1']), int(row['num2']), int(row['num3'])))
    
    # 每个位置每个数字的得分
    pos_scores = [{d: 0 for d in range(10)} for _ in range(3)]
    
    for pos in range(3):
        # 1. 马尔可夫得分 (50%)
        probs = markov_predict(markov, history, pos)
        max_p = max(probs.values()) if probs else 1
        for d in range(10):
            pos_scores[pos][d] += (probs.get(d, 0) / max_p) * 50
        
        # 2. 书本方法得分 (10%)
        # 热号
        danma = analyses['danma']
        pos_scores[pos][danma['gold_dan']] += 5
        
        # 012路热号
        route_012 = analyses['route_012']
        for n in route_012[pos]['hot_nums']:
            pos_scores[pos][n] += 2
        
        # 3. 随机得分 (40%)
        for d in range(10):
            pos_scores[pos][d] += random.random() * 40
    
    # 找出每个位置的最佳胆码
    best_per_pos = []
    for pos in range(3):
        sorted_nums = sorted(pos_scores[pos].items(), key=lambda x: x[1], reverse=True)
        best_per_pos.append(sorted_nums[0][0])
    
    # 找出全局最佳定位胆码（得分最高的位置+数字）
    all_scores = []
    for pos in range(3):
        for d in range(10):
            all_scores.append((pos, d, pos_scores[pos][d]))
    
    all_scores.sort(key=lambda x: x[2], reverse=True)
    best_pos, best_dan = all_scores[0][0], all_scores[0][1]
    
    return {
        'best_pos_dan': (best_pos, best_dan),  # 最佳定位胆码
        'pos1_dan': best_per_pos[0],  # 百位胆码
        'pos2_dan': best_per_pos[1],  # 十位胆码
        'pos3_dan': best_per_pos[2],  # 个位胆码
        'pos_scores': pos_scores
    }

# 测试
def test_positioned_danma(test_count=5000):
    """测试定位胆码"""
    random.seed(42)
    
    results = {
        'best_pos_dan': 0,      # 最佳定位胆码命中
        'pos1_dan': 0,          # 百位胆码命中
        'pos2_dan': 0,          # 十位胆码命中
        'pos3_dan': 0,          # 个位胆码命中
        'any_pos_dan': 0,       # 任一位置胆码命中
        'all_pos_dan': 0,       # 三个位置全中
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
        pred = predict_positioned_danma(df_train)
        
        # 验证最佳定位胆码
        best_pos, best_dan = pred['best_pos_dan']
        if real[best_pos] == best_dan:
            results['best_pos_dan'] += 1
        
        # 验证各位置胆码
        if real[0] == pred['pos1_dan']:
            results['pos1_dan'] += 1
        if real[1] == pred['pos2_dan']:
            results['pos2_dan'] += 1
        if real[2] == pred['pos3_dan']:
            results['pos3_dan'] += 1
        
        # 验证任一位置命中
        if pred['pos1_dan'] in real or pred['pos2_dan'] in real or pred['pos3_dan'] in real:
            results['any_pos_dan'] += 1
        
        # 验证三个位置全中
        if real[0] == pred['pos1_dan'] and real[1] == pred['pos2_dan'] and real[2] == pred['pos3_dan']:
            results['all_pos_dan'] += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d' % (i - 100, total))
    
    # 输出结果
    print()
    print('='*70)
    print('定位胆码测试结果 (5000期)')
    print('='*70)
    print()
    print('【理论值】')
    print('  单位置单胆码: 10% (预测1个数字在1个位置)')
    print('  三位置各1胆码任中: 约27% (1-(0.9)^3)')
    print('  三位置各1胆码全中: 0.1% (0.1^3)')
    print()
    print('【测试结果】')
    print('-'*70)
    print('最佳定位胆码(位置+数字): %d次 (%.2f%%) 理论10%%' % (
        results['best_pos_dan'], results['best_pos_dan']/total*100
    ))
    print('百位胆码命中: %d次 (%.2f%%) 理论10%%' % (
        results['pos1_dan'], results['pos1_dan']/total*100
    ))
    print('十位胆码命中: %d次 (%.2f%%) 理论10%%' % (
        results['pos2_dan'], results['pos2_dan']/total*100
    ))
    print('个位胆码命中: %d次 (%.2f%%) 理论10%%' % (
        results['pos3_dan'], results['pos3_dan']/total*100
    ))
    print('-'*70)
    print('三位置胆码任中1个: %d次 (%.2f%%) 理论27%%' % (
        results['any_pos_dan'], results['any_pos_dan']/total*100
    ))
    print('三位置胆码全中: %d次 (%.2f%%) 理论0.1%%' % (
        results['all_pos_dan'], results['all_pos_dan']/total*100
    ))
    print('='*70)
    
    return {k: v/total*100 for k, v in results.items()}

# 运行测试
result = test_positioned_danma(5000)

# 保存
import json
with open('positioned_danma_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 positioned_danma_result.json')
