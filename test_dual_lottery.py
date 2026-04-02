#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双彩测试 - 排列三 + 3D
V4.0最佳配置：7种方法
"""

import pandas as pd
import numpy as np
from collections import Counter
import random
import json

print('='*70)
print('双彩测试 - 排列三 + 3D')
print('='*70)

# 加载数据
pl3_df = pd.read_csv('pl3_full.csv')
print('排列三数据: %d期' % len(pl3_df))

# 尝试加载3D数据
try:
    d3_df = pd.read_csv('3d_full.csv')
    print('3D数据: %d期' % len(d3_df))
    has_3d = True
except:
    print('3D数据未找到，尝试下载...')
    has_3d = False

# ============================================================
# 方法实现
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
    return list(set(result))[:5]

def predict_5ma(df_train):
    scores = {d: 0 for d in range(10)}
    for d in predict_334(df_train): scores[d] += 14
    for d in predict_55fenjie(df_train): scores[d] += 9
    for d in predict_liangma(df_train): scores[d] += 6
    for d in predict_012lu(df_train): scores[d] += 6
    for d in predict_jiou(df_train): scores[d] += 4
    for d in predict_xingtai(df_train): scores[d] += 4
    for d in predict_sum_tail(df_train): scores[d] += 7
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [n for n, s in sorted_nums[:5]]

# ============================================================
# 测试函数
# ============================================================
def test_lottery(df, name, test_count=5000):
    random.seed(42)
    full_hit, at_least_2, at_least_1 = 0, 0, 0
    total = min(test_count, len(df) - 600)
    
    print('\n测试 %s...' % name)
    print('测试期数: %d' % total)
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_5ma(df_train))
        hit_count = len(real_set & top5_set)
        
        if hit_count == len(real_set): full_hit += 1
        if hit_count >= 2: at_least_2 += 1
        if hit_count >= 1: at_least_1 += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d | 全中: %.1f%%' % (i - 100, total, full_hit / max(1, i - 100) * 100))
    
    result = {
        'name': name,
        'total': total,
        'full_hit': full_hit,
        'full_hit_rate': full_hit/total*100,
        'at_least_2': at_least_2/total*100,
        'at_least_1': at_least_1/total*100
    }
    
    print()
    print('='*70)
    print('%s 测试结果' % name)
    print('='*70)
    print('开奖号全在五码中: %d次 (%.2f%%) 理论8.33%%' % (full_hit, full_hit/total*100))
    print('至少2个在五码中: %d次 (%.2f%%) 理论50%%' % (at_least_2, at_least_2/total*100))
    print('至少1个在五码中: %d次 (%.2f%%) 理论65%%' % (at_least_1, at_least_1/total*100))
    print('='*70)
    
    return result

# ============================================================
# 测试排列三
# ============================================================
pl3_result = test_lottery(pl3_df, '排列三', 5000)

# ============================================================
# 测试3D
# ============================================================
if has_3d:
    d3_result = test_lottery(d3_df, '3D', 5000)
else:
    # 下载3D数据
    print('\n下载3D数据...')
    import urllib.request
    try:
        url = 'http://data.17500.cn/3d_asc.txt'
        urllib.request.urlretrieve(url, '3d_data.txt')
        print('下载完成')
        
        # 解析数据
        with open('3d_data.txt', 'r', encoding='gbk') as f:
            lines = f.readlines()
        
        data = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 2:
                issue = parts[0]
                num = parts[1]
                if len(num) == 3:
                    data.append({
                        'issue': issue,
                        'num1': int(num[0]),
                        'num2': int(num[1]),
                        'num3': int(num[2])
                    })
        
        d3_df = pd.DataFrame(data)
        d3_df.to_csv('3d_full.csv', index=False)
        print('3D数据解析完成: %d期' % len(d3_df))
        
        d3_result = test_lottery(d3_df, '3D', 5000)
    except Exception as e:
        print('下载失败: %s' % e)
        d3_result = None

# ============================================================
# 汇总结果
# ============================================================
print()
print('='*70)
print('双彩测试结果汇总')
print('='*70)
print()
print('【排列三】')
print('  全中命中率: %.2f%% (理论8.33%%)' % pl3_result['full_hit_rate'])
print('  至少2个: %.2f%%' % pl3_result['at_least_2'])
print('  至少1个: %.2f%%' % pl3_result['at_least_1'])
print()

if d3_result:
    print('【3D】')
    print('  全中命中率: %.2f%% (理论8.33%%)' % d3_result['full_hit_rate'])
    print('  至少2个: %.2f%%' % d3_result['at_least_2'])
    print('  至少1个: %.2f%%' % d3_result['at_least_1'])
    print()
    
    # 对比
    print('【对比】')
    if pl3_result['full_hit_rate'] > d3_result['full_hit_rate']:
        print('  排列三命中率更高: %.2f%% vs %.2f%%' % (pl3_result['full_hit_rate'], d3_result['full_hit_rate']))
    else:
        print('  3D命中率更高: %.2f%% vs %.2f%%' % (d3_result['full_hit_rate'], pl3_result['full_hit_rate']))

print('='*70)

# 保存
results = {'pl3': pl3_result}
if d3_result:
    results['d3'] = d3_result

with open('dual_lottery_result.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 dual_lottery_result.json')
