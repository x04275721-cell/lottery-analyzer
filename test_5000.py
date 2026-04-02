#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
5000期完整测试 - 结合三本书15种方法 + 现有马尔可夫链
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
import json
from book_methods import (
    run_all_analyses, comprehensive_score,
    analyze_danma, analyze_012_route, analyze_sum_value
)

print('='*70)
print('5000期完整测试 - 三本书15种方法 + 马尔可夫链')
print('='*70)

# 加载数据
df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 马尔可夫链（现有系统）
# ============================================================
def build_markov_chain(df, order=3):
    """构建马尔可夫链"""
    matrices = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tolist()
        
        # 构建转移矩阵
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        
        for i in range(len(nums) - order):
            key = tuple(nums[i:i+order])
            next_val = nums[i+order]
            trans[key][next_val] += 1
            totals[key] += 1
        
        # 转换为概率
        matrix = {}
        for key in totals:
            total = totals[key]
            matrix[key] = {d: (trans[key].get(d, 0) + 0.01) / total for d in range(10)}
        
        matrices.append(matrix)
    
    return matrices

def markov_predict(matrices, history, pos):
    """马尔可夫预测"""
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

# ============================================================
# 综合选号函数
# ============================================================
def generate_candidates(df_train, method='combined', top_n=500):
    """生成候选号码"""
    candidates = set()
    
    # 运行所有分析
    analyses = run_all_analyses(df_train)
    
    # 马尔可夫链
    markov = build_markov_chain(df_train)
    history = []
    for _, row in df_train.tail(5).iterrows():
        history.append((int(row['num1']), int(row['num2']), int(row['num3'])))
    
    # 方法1: 马尔可夫生成
    for _ in range(200):
        nums = []
        for pos in range(3):
            probs = markov_predict(markov, history, pos)
            n = random.choices(range(10), weights=[probs.get(d, 0.1) for d in range(10)])[0]
            nums.append(n)
        candidates.add(tuple(nums))
    
    # 方法2: 胆码优先
    danma = analyses['danma']
    gold = danma['gold_dan']
    silver = danma['silver_dan']
    
    for _ in range(150):
        # 必须包含金胆或银胆
        if random.random() < 0.6:
            must_have = gold
        else:
            must_have = random.choice(silver)
        
        nums = [must_have]
        for _ in range(2):
            nums.append(random.randint(0, 9))
        random.shuffle(nums)
        candidates.add(tuple(nums))
    
    # 方法3: 012路优先
    route_012 = analyses['route_012']
    for _ in range(100):
        nums = []
        for pos in range(3):
            # 优先选择热路数字
            hot_nums = route_012[pos]['hot_nums']
            if random.random() < 0.7:
                nums.append(random.choice(hot_nums))
            else:
                nums.append(random.randint(0, 9))
        candidates.add(tuple(nums))
    
    # 方法4: 和值优先
    sum_val = analyses['sum_value']
    hot_sums = sum_val['hot_sums']
    
    for _ in range(100):
        target_sum = random.choice(hot_sums)
        # 生成和值为target_sum的三位数
        n1 = random.randint(0, 9)
        n2 = random.randint(0, 9)
        n3 = target_sum - n1 - n2
        if 0 <= n3 <= 9:
            candidates.add((n1, n2, n3))
    
    # 方法5: 随机补充
    while len(candidates) < top_n:
        candidates.add((random.randint(0, 9), random.randint(0, 9), random.randint(0, 9)))
    
    return list(candidates)[:top_n], analyses

def score_candidate(nums, analyses, markov, history):
    """对候选号码打分"""
    score = 0
    
    # 15种方法综合评分 (权重50%)
    score += comprehensive_score(nums, analyses) * 0.5
    
    # 马尔可夫评分 (权重30%)
    for pos, n in enumerate(nums):
        probs = markov_predict(markov, history, pos)
        score += probs.get(n, 0.01) * 30
    
    # 随机因素 (权重20%)
    score += random.random() * 10
    
    return score

# ============================================================
# 5000期回测
# ============================================================
def backtest_5000(test_count=5000, top_n=10):
    """5000期回测"""
    random.seed(42)
    
    partial_hits = 0  # 至少2个相同
    three_hits = 0    # 组选命中
    
    total = min(test_count, len(df) - 600)
    
    print('\n开始回测...')
    print('测试期数: %d' % total)
    print('推荐注数: %d' % top_n)
    print()
    
    for i in range(100, 100 + total):
        # 训练数据
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100:
            continue
        
        # 实际开奖
        real = (int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3']))
        real_set = set(real)
        
        # 生成候选
        candidates, analyses = generate_candidates(df_train, top_n=500)
        
        # 马尔可夫
        markov = build_markov_chain(df_train)
        history = []
        for _, row in df_train.tail(5).iterrows():
            history.append((int(row['num1']), int(row['num2']), int(row['num3'])))
        
        # 打分排序
        scored = []
        for nums in candidates:
            s = score_candidate(nums, analyses, markov, history)
            scored.append((nums, s))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top = [n for n, s in scored[:top_n]]
        
        # 验证
        if any(set(n) == real_set for n in top):
            three_hits += 1
        
        if any(len(set(n) & real_set) >= 2 for n in top):
            partial_hits += 1
        
        # 进度
        if (i - 100) % 500 == 0:
            progress = (i - 100) / total * 100
            print('进度: %.1f%% (%d/%d) | 2同: %.1f%% | 组选: %.2f%%' % (
                progress, i - 100, total,
                partial_hits / max(1, i - 100) * 100,
                three_hits / max(1, i - 100) * 100
            ))
    
    # 最终结果
    print()
    print('='*70)
    print('5000期回测结果')
    print('='*70)
    print('至少2个相同: %d次 (%.2f%%)' % (partial_hits, partial_hits/total*100))
    print('组选命中: %d次 (%.2f%%)' % (three_hits, three_hits/total*100))
    print()
    print('理论值（随机%d注）：' % top_n)
    print('至少2个相同: ~70%%')
    print('组选命中: ~%.1f%%' % (top_n * 0.5))
    print('='*70)
    
    return {
        'partial': partial_hits / total * 100,
        'three': three_hits / total * 100,
        'total': total
    }

# 运行测试
if __name__ == '__main__':
    result = backtest_5000(test_count=5000, top_n=10)
    
    # 保存结果
    with open('book_methods_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print('\n结果已保存到 book_methods_result.json')