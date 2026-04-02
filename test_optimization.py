#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多方向优化测试 - 尝试提升五码命中率
1. 不同权重组合
2. 增加历史期数
3. 加入冷热号规律
4. 加入连续性规律
"""

import pandas as pd
import numpy as np
from collections import Counter
import random
import json

print('='*70)
print('多方向优化测试 - 寻找最佳配置')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 基础方法
# ============================================================
def get_334_duanzu(last_nums):
    n1, n2, n3 = last_nums
    sum_tail = (n1 + n2 + n3) % 10
    if sum_tail in [0, 5]: return [0,1,9], [4,5,6], [2,3,7,8]
    elif sum_tail in [1, 6]: return [0,1,2], [5,6,7], [3,4,8,9]
    elif sum_tail in [2, 7]: return [1,2,3], [6,7,8], [0,4,5,9]
    elif sum_tail in [3, 8]: return [2,3,4], [7,8,9], [0,1,5,6]
    else: return [3,4,5], [8,9,0], [1,2,6,7]

def predict_334(df_train):
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    g1, g2, g3 = get_334_duanzu(last_nums)
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    if g1_count <= g2_count and g1_count <= g3_count: return g2 + g3
    elif g2_count <= g1_count and g2_count <= g3_count: return g1 + g3
    else: return g1 + g2

def predict_55fenjie(df_train):
    decompositions = [
        ([0,1,2,3,4], [5,6,7,8,9]),
        ([1,3,5,7,9], [0,2,4,6,8]),
        ([2,3,5,7,0], [1,4,6,8,9]),
        ([0,1,4,5,8], [2,3,6,7,9]),
    ]
    best_group, best_score = None, -1
    for g1, g2 in decompositions:
        all_nums = []
        for _, row in df_train.tail(10).iterrows():
            all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
        g1_count = sum(1 for n in all_nums if n in g1)
        g2_count = sum(1 for n in all_nums if n in g2)
        if g1_count > g2_count: score, group = g1_count, g1
        else: score, group = g2_count, g2
        if score > best_score: best_score, best_group = score, group
    return best_group if best_group else [0,1,2,3,4]

def predict_liangma(df_train):
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    return [n for n, c in num_count.most_common(3)]

def predict_012lu(df_train):
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    hot_nums = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df_train[col].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums: route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        hot_nums.extend(route_map[hot_route])
    return list(set(hot_nums))

def predict_jiou(df_train):
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    if odd_count > even_count: return [1, 3, 5, 7, 9]
    else: return [0, 2, 4, 6, 8]

def predict_xingtai(df_train):
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    big_count = sum(1 for n in all_nums if n >= 5)
    small_count = len(all_nums) - big_count
    prime = [2, 3, 5, 7]
    prime_count = sum(1 for n in all_nums if n in prime)
    composite_count = len(all_nums) - prime_count
    hot_nums = []
    if big_count > small_count: hot_nums.extend([5, 6, 7, 8, 9])
    else: hot_nums.extend([0, 1, 2, 3, 4])
    if prime_count > composite_count: hot_nums.extend(prime)
    else: hot_nums.extend([0, 1, 4, 6, 8, 9])
    return list(set(hot_nums))

# ============================================================
# 新增方法
# ============================================================
def predict_hot_cold(df_train, periods=50):
    """冷热号分析 - 近期热号"""
    all_nums = []
    for _, row in df_train.tail(periods).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    num_count = Counter(all_nums)
    return [n for n, c in num_count.most_common(5)]

def predict_repeat(df_train):
    """重复号分析 - 上期号码大概率重复"""
    last = df_train.iloc[-1]
    return [int(last['num1']), int(last['num2']), int(last['num3'])]

def predict_sum_tail(df_train):
    """和值尾分析"""
    sums = []
    for _, row in df_train.tail(30).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        sums.append(s % 10)
    sum_count = Counter(sums)
    hot_sum = sum_count.most_common(3)
    # 根据热和值尾推荐数字
    result = []
    for tail, _ in hot_sum:
        result.append(tail)
    return result

def predict_span(df_train):
    """跨度分析"""
    spans = []
    for _, row in df_train.tail(30).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        spans.append(max(nums) - min(nums))
    span_count = Counter(spans)
    hot_span = span_count.most_common(3)
    # 根据热跨度推荐数字
    result = []
    for span, _ in hot_span:
        result.append(span)
    return result

# ============================================================
# 综合预测 - 多种配置
# ============================================================
def predict_with_config(df_train, config):
    """根据配置预测"""
    scores = {d: 0 for d in range(10)}
    
    # 原有6种方法
    if config.get('w334', 0) > 0:
        for d in predict_334(df_train): scores[d] += config['w334']
    if config.get('w55', 0) > 0:
        for d in predict_55fenjie(df_train): scores[d] += config['w55']
    if config.get('wliangma', 0) > 0:
        for d in predict_liangma(df_train): scores[d] += config['wliangma']
    if config.get('w012', 0) > 0:
        for d in predict_012lu(df_train): scores[d] += config['w012']
    if config.get('wjiou', 0) > 0:
        for d in predict_jiou(df_train): scores[d] += config['wjiou']
    if config.get('wxingtai', 0) > 0:
        for d in predict_xingtai(df_train): scores[d] += config['wxingtai']
    
    # 新增方法
    if config.get('whot', 0) > 0:
        for d in predict_hot_cold(df_train): scores[d] += config['whot']
    if config.get('wrepeat', 0) > 0:
        for d in predict_repeat(df_train): scores[d] += config['wrepeat']
    if config.get('wsum', 0) > 0:
        for d in predict_sum_tail(df_train): scores[d] += config['wsum']
    if config.get('wspan', 0) > 0:
        for d in predict_span(df_train): scores[d] += config['wspan']
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 测试多种配置
# ============================================================
def test_config(config, name, test_count=5000):
    random.seed(42)
    full_hit, at_least_2, at_least_1 = 0, 0, 0
    total = min(test_count, len(df) - 600)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_with_config(df_train, config))
        hit_count = len(real_set & top5_set)
        
        if hit_count == len(real_set): full_hit += 1
        if hit_count >= 2: at_least_2 += 1
        if hit_count >= 1: at_least_1 += 1
    
    return {
        'name': name,
        'full_hit': full_hit/total*100,
        'at_least_2': at_least_2/total*100,
        'at_least_1': at_least_1/total*100
    }

# ============================================================
# 配置列表
# ============================================================
configs = [
    # 原配置
    {
        'name': '原配置(6种)',
        'w334': 15, 'w55': 10, 'wliangma': 7, 'w012': 7, 'wjiou': 5, 'wxingtai': 5,
        'whot': 0, 'wrepeat': 0, 'wsum': 0, 'wspan': 0
    },
    # 加入冷热号
    {
        'name': '加冷热号',
        'w334': 14, 'w55': 9, 'wliangma': 6, 'w012': 6, 'wjiou': 4, 'wxingtai': 4,
        'whot': 7, 'wrepeat': 0, 'wsum': 0, 'wspan': 0
    },
    # 加入重复号
    {
        'name': '加重复号',
        'w334': 14, 'w55': 9, 'wliangma': 6, 'w012': 6, 'wjiou': 4, 'wxingtai': 4,
        'whot': 0, 'wrepeat': 7, 'wsum': 0, 'wspan': 0
    },
    # 加入和值尾
    {
        'name': '加和值尾',
        'w334': 14, 'w55': 9, 'wliangma': 6, 'w012': 6, 'wjiou': 4, 'wxingtai': 4,
        'whot': 0, 'wrepeat': 0, 'wsum': 7, 'wspan': 0
    },
    # 加入跨度
    {
        'name': '加跨度',
        'w334': 14, 'w55': 9, 'wliangma': 6, 'w012': 6, 'wjiou': 4, 'wxingtai': 4,
        'whot': 0, 'wrepeat': 0, 'wsum': 0, 'wspan': 7
    },
    # 全部方法
    {
        'name': '全部方法(10种)',
        'w334': 12, 'w55': 8, 'wliangma': 5, 'w012': 5, 'wjiou': 3, 'wxingtai': 3,
        'whot': 5, 'wrepeat': 5, 'wsum': 3, 'wspan': 3
    },
    # 冷热号+重复号
    {
        'name': '冷热+重复',
        'w334': 13, 'w55': 8, 'wliangma': 5, 'w012': 5, 'wjiou': 3, 'wxingtai': 3,
        'whot': 6, 'wrepeat': 6, 'wsum': 0, 'wspan': 0
    },
    # 强化334断组
    {
        'name': '强化334',
        'w334': 20, 'w55': 8, 'wliangma': 5, 'w012': 5, 'wjiou': 3, 'wxingtai': 3,
        'whot': 3, 'wrepeat': 3, 'wsum': 0, 'wspan': 0
    },
]

print('\n开始测试多种配置...')
print('测试期数: 5000')
print()

results = []
for config in configs:
    print('测试: %s' % config['name'])
    result = test_config(config, config['name'])
    results.append(result)
    print('  全中: %.2f%% | 至少2: %.2f%% | 至少1: %.2f%%' % (
        result['full_hit'], result['at_least_2'], result['at_least_1']
    ))
    print()

# 排序
results.sort(key=lambda x: x['full_hit'], reverse=True)

print('='*70)
print('测试结果排名')
print('='*70)
print()
for i, r in enumerate(results, 1):
    print('%d. %s' % (i, r['name']))
    print('   全中: %.2f%% | 至少2: %.2f%% | 至少1: %.2f%%' % (
        r['full_hit'], r['at_least_2'], r['at_least_1']
    ))
    print()

# 保存
with open('optimization_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('结果已保存到 optimization_results.json')
