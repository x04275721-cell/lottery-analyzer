#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
和值判断三大原则测试
原则一：平均间隔期
原则二：相邻和数值是否开出
原则三：同尾和数值是否开出
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('和值判断三大原则测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 基础方法（当前系统）
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
    counts = [(g1, g1_count), (g2, g2_count), (g3, g3_count)]
    counts.sort(key=lambda x: x[1], reverse=True)
    scores = {d: 0 for d in range(10)}
    for d in counts[0][0]: scores[d] += 14
    for d in counts[1][0]: scores[d] += 10
    for d in counts[2][0]: scores[d] += 2
    return scores

def predict_jiou(df_train):
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    scores = {d: 0 for d in range(10)}
    if odd_count > even_count:
        for d in [1,3,5,7,9]: scores[d] += 14
        for d in [0,2,4,6,8]: scores[d] += 2
    else:
        for d in [0,2,4,6,8]: scores[d] += 14
        for d in [1,3,5,7,9]: scores[d] += 2
    return scores

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
    return {d: 9 for d in best_group}

def predict_liangma(df_train):
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    result = [n for n, c in num_count.most_common(3)]
    return {d: 6 for d in result}

def predict_012lu(df_train):
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    hot_nums = []
    for pos in range(3):
        nums = df_train['num%d' % (pos+1)].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums: route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        hot_nums.extend(route_map[hot_route])
    return {d: 6 for d in set(hot_nums)}

def predict_xingtai(df_train):
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    big_count = sum(1 for n in all_nums if n >= 5)
    small_count = len(all_nums) - big_count
    prime = [2, 3, 5, 7]
    prime_count = sum(1 for n in all_nums if n in prime)
    hot_nums = []
    if big_count > small_count: hot_nums.extend([5, 6, 7, 8, 9])
    else: hot_nums.extend([0, 1, 2, 3, 4])
    if prime_count > len(all_nums) - prime_count: hot_nums.extend(prime)
    else: hot_nums.extend([0, 1, 4, 6, 8, 9])
    return {d: 4 for d in set(hot_nums)}

def predict_sum_tail(df_train):
    sums = []
    for _, row in df_train.tail(30).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        sums.append(s % 10)
    sum_count = Counter(sums)
    hot_sums = [n for n, c in sum_count.most_common(3)]
    result = []
    for tail in hot_sums:
        result.append(tail)
        result.append((tail + 5) % 10)
    return {d: 7 for d in list(set(result))[:5]}

def predict_base(df_train, df_all=None, current_idx=None):
    """基础7方法"""
    scores = {d: 0 for d in range(10)}
    for d, s in predict_334(df_train).items(): scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): scores[d] += s
    for d, s in predict_liangma(df_train).items(): scores[d] += s
    for d, s in predict_012lu(df_train).items(): scores[d] += s
    for d, s in predict_jiou(df_train).items(): scores[d] += s
    for d, s in predict_xingtai(df_train).items(): scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): scores[d] += s
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 和值三大原则
# ============================================================
def analyze_sum_rules(df_train, df_all, current_idx):
    """和值判断三大原则分析"""
    
    # 计算当前所有和值
    sums = []
    for i in range(max(0, current_idx-500), current_idx+1):
        if i < len(df_all):
            row = df_all.iloc[i]
            s = int(row['num1']) + int(row['num2']) + int(row['num3'])
            sums.append(s)
    
    # 统计各和值出现次数和遗漏
    sum_stats = {}
    for s in range(0, 28):
        count = sums.count(s)
        # 计算遗漏（从后往前找）
        missing = 0
        found = False
        for x in reversed(sums):
            if x == s:
                found = True
                break
            missing += 1
        sum_stats[s] = {'count': count, 'missing': missing}
    
    # 原则一：平均间隔期
    # 计算高频和值的平均间隔
    hot_sums = []
    for s in range(0, 28):
        if sum_stats[s]['count'] >= 50:  # 高频和值
            hot_sums.append(s)
    
    # 原则二：相邻和值是否开出
    # 对于高频和值，观察相邻和值12、14的开出状态
    
    # 原则三：同尾和值是否开出
    # 和值13的同尾是3、23
    
    return sum_stats, hot_sums

def predict_sum_with_rules(df_train, df_all, current_idx):
    """结合和值三大原则的预测"""
    
    # 获取基础预测
    base_scores = {d: 0 for d in range(10)}
    for d, s in predict_334(df_train).items(): base_scores[d] += s
    for d, s in predict_55fenjie(df_train).items(): base_scores[d] += s
    for d, s in predict_liangma(df_train).items(): base_scores[d] += s
    for d, s in predict_012lu(df_train).items(): base_scores[d] += s
    for d, s in predict_jiou(df_train).items(): base_scores[d] += s
    for d, s in predict_xingtai(df_train).items(): base_scores[d] += s
    for d, s in predict_sum_tail(df_train).items(): base_scores[d] += s
    
    # 分析和值三大原则
    sum_stats, hot_sums = analyze_sum_rules(df_train, df_all, current_idx)
    
    # 获取推荐和值
    recommended_sums = []
    
    for target_sum in [12, 13, 14, 10, 11, 15]:  # 中高频和值
        if target_sum not in sum_stats:
            continue
            
        # 原则一：平均间隔（简化版：遗漏超过平均值）
        avg_interval = 7  # 默认平均间隔
        p1_pass = sum_stats[target_sum]['missing'] >= avg_interval
        
        # 原则二：相邻和值开出
        adj1, adj2 = target_sum - 1, target_sum + 1
        if adj1 < 0: adj1 = 27
        if adj2 > 27: adj2 = 0
        adj1_recent = sum_stats[adj1]['missing'] <= 3  # 3期内开过
        adj2_recent = sum_stats[adj2]['missing'] <= 3
        p2_pass = adj1_recent or adj2_recent  # 至少一个相邻和值近期开出
        
        # 原则三：同尾和值铺垫
        tail1 = target_sum % 10
        tail2 = (target_sum + 10) % 20
        if tail2 > 27: tail2 = target_sum - 10
        tail1_recent = sum_stats.get(tail1, {}).get('missing', 999) <= 5
        tail2_recent = sum_stats.get(tail2, {}).get('missing', 999) <= 5
        p3_pass = tail1_recent or tail2_recent
        
        # 三重信号共振
        if p1_pass and p2_pass and p3_pass:
            recommended_sums.append(target_sum)
    
    # 根据推荐和值调整分数
    if recommended_sums:
        for s in recommended_sums:
            for d in range(10):
                # 检查哪些数字组合能得出这个和值
                for d2 in range(10):
                    for d3 in range(10):
                        if (d + d2 + d3) == s:
                            base_scores[d] += 5
                            base_scores[d2] += 5
                            base_scores[d3] += 5
    
    sorted_nums = sorted(base_scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 测试
# ============================================================
def test_predict(predict_func, name, test_count=5000):
    random.seed(42)
    results = []
    total = min(test_count, len(df) - 600)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_func(df_train, df, i))
        hit = len(real_set & top5_set) == len(real_set)
        results.append(hit)
    
    total_hits = sum(results)
    hit_rate = total_hits / len(results) * 100
    
    return {
        'name': name,
        'total': len(results),
        'hits': total_hits,
        'hit_rate': hit_rate
    }

print('\n测试基础7方法...')
base_result = test_predict(predict_base, '基础7方法', 5000)
print('基础7方法命中率: %.2f%%' % base_result['hit_rate'])

print('\n测试+和值三大原则...')
enhanced_result = test_predict(predict_sum_with_rules, '+和值三大原则', 5000)
print('+和值三大原则命中率: %.2f%%' % enhanced_result['hit_rate'])

print()
print('='*70)
print('测试结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 提升 |')
print('|------|--------|------|')
print('| 基础7方法 | %.2f%% | - |' % base_result['hit_rate'])
print('| +和值三大原则 | %.2f%% | +%.2f%% |' % (enhanced_result['hit_rate'], enhanced_result['hit_rate'] - base_result['hit_rate']))
print()
print('='*70)