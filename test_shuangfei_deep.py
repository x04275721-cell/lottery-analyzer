#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双飞神技 - 反推杀上杀下规律
"""

import pandas as pd
from collections import Counter
import numpy as np

print('='*70)
print('双飞神技 - 反推杀上杀下规律')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 双飞组合定义
# ============================================================
GROUP_UP = [1, 2, 7, 8, 9]
GROUP_DOWN = [0, 3, 4, 5, 6]

SHUANGFEI_UP = [
    (1, 2), (1, 7), (1, 8), (1, 9),
    (2, 7), (2, 8), (2, 9),
    (7, 8), (7, 9), (8, 9)
]

SHUANGFEI_DOWN = [
    (0, 3), (0, 4), (0, 5), (0, 6),
    (3, 4), (3, 5), (3, 6),
    (4, 5), (4, 6), (5, 6)
]

def get_shuangfei(nums):
    n1, n2, n3 = nums
    pairs = [
        tuple(sorted([n1, n2])),
        tuple(sorted([n1, n3])),
        tuple(sorted([n2, n3]))
    ]
    return pairs

def get_group_type(nums):
    up_count = sum(1 for n in nums if n in GROUP_UP)
    down_count = sum(1 for n in nums if n in GROUP_DOWN)
    
    if up_count == 3:
        return '全上'
    elif down_count == 3:
        return '全下'
    elif up_count == 2:
        return '2上1下'
    elif down_count == 2:
        return '2下1上'
    else:
        return '其他'

# ============================================================
# 多维度分析
# ============================================================
print('\n多维度分析杀上杀下规律...\n')

# 创建特征矩阵
features = []
labels = []

for i in range(100, min(5100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    # 特征1：上期组类型
    last_type = get_group_type(last_nums)
    
    # 特征2：上期号码的和值
    last_sum = sum(last_nums)
    
    # 特征3：上期号码的跨度
    last_span = max(last_nums) - min(last_nums)
    
    # 特征4：上期在上组的数字个数
    last_up_count = sum(1 for n in last_nums if n in GROUP_UP)
    
    # 特征5：上期和值的奇偶
    last_sum_odd = last_sum % 2
    
    # 特征6：上期最大数在上组还是下组
    last_max = max(last_nums)
    last_max_in_up = 1 if last_max in GROUP_UP else 0
    
    # 特征7：上期最小数在上组还是下组
    last_min = min(last_nums)
    last_min_in_up = 1 if last_min in GROUP_UP else 0
    
    # 标签：本期命中哪个组
    curr_pairs = get_shuangfei(curr_nums)
    hit_up = any(p in SHUANGFEI_UP for p in curr_pairs)
    hit_down = any(p in SHUANGFEI_DOWN for p in curr_pairs)
    
    if hit_up and not hit_down:
        label = '上'
    elif hit_down and not hit_up:
        label = '下'
    else:
        label = '平'
    
    features.append({
        'type': last_type,
        'sum': last_sum,
        'span': last_span,
        'up_count': last_up_count,
        'sum_odd': last_sum_odd,
        'max_in_up': last_max_in_up,
        'min_in_up': last_min_in_up,
        'label': label
    })

# 转为DataFrame
df_features = pd.DataFrame(features)

# ============================================================
# 分析每个特征的规律
# ============================================================
print('特征1：上期组类型\n')
type_stats = df_features.groupby(['type', 'label']).size().unstack(fill_value=0)
print(type_stats)
print()

# 计算每种类型下，上下组的比例
for t in ['全上', '全下', '2上1下', '2下1上']:
    if t in type_stats.index:
        row = type_stats.loc[t]
        total = row['上'] + row['下'] + row.get('平', 0)
        if total > 0:
            print('%s -> 上: %.1f%%, 下: %.1f%%' % (t, row['上']/total*100, row['下']/total*100))

print('\n' + '='*70)
print('特征2：上期和值大小\n')
df_features['sum_type'] = df_features['sum'].apply(lambda x: '小(0-9)' if x <= 9 else ('中(10-18)' if x <= 18 else '大(19-27)'))
sum_stats = df_features.groupby(['sum_type', 'label']).size().unstack(fill_value=0)
print(sum_stats)
print()

for t in ['小(0-9)', '中(10-18)', '大(19-27)']:
    if t in sum_stats.index:
        row = sum_stats.loc[t]
        total = row['上'] + row['下'] + row.get('平', 0)
        if total > 0:
            print('%s -> 上: %.1f%%, 下: %.1f%%' % (t, row['上']/total*100, row['下']/total*100))

print('\n' + '='*70)
print('特征3：上期跨度大小\n')
df_features['span_type'] = df_features['span'].apply(lambda x: '小(0-3)' if x <= 3 else ('中(4-6)' if x <= 6 else '大(7-9)'))
span_stats = df_features.groupby(['span_type', 'label']).size().unstack(fill_value=0)
print(span_stats)
print()

for t in ['小(0-3)', '中(4-6)', '大(7-9)']:
    if t in span_stats.index:
        row = span_stats.loc[t]
        total = row['上'] + row['下'] + row.get('平', 0)
        if total > 0:
            print('%s -> 上: %.1f%%, 下: %.1f%%' % (t, row['上']/total*100, row['下']/total*100))

print('\n' + '='*70)
print('特征4：上期在上组的数字个数\n')
up_stats = df_features.groupby(['up_count', 'label']).size().unstack(fill_value=0)
print(up_stats)
print()

for c in [0, 1, 2, 3]:
    if c in up_stats.index:
        row = up_stats.loc[c]
        total = row['上'] + row['下'] + row.get('平', 0)
        if total > 0:
            print('%d个在上组 -> 上: %.1f%%, 下: %.1f%%' % (c, row['上']/total*100, row['下']/total*100))

print('\n' + '='*70)
print('特征5：上期最大数在上组还是下组\n')
max_stats = df_features.groupby(['max_in_up', 'label']).size().unstack(fill_value=0)
print(max_stats)
print()

for c in [0, 1]:
    row = max_stats.loc[c]
    total = row['上'] + row['下'] + row.get('平', 0)
    if total > 0:
        print('最大数在%s -> 上: %.1f%%, 下: %.1f%%' % ('上组' if c == 1 else '下组', row['上']/total*100, row['下']/total*100))

print('\n' + '='*70)
print('特征6：上期最小数在上组还是下组\n')
min_stats = df_features.groupby(['min_in_up', 'label']).size().unstack(fill_value=0)
print(min_stats)
print()

for c in [0, 1]:
    row = min_stats.loc[c]
    total = row['上'] + row['下'] + row.get('平', 0)
    if total > 0:
        print('最小数在%s -> 上: %.1f%%, 下: %.1f%%' % ('上组' if c == 1 else '下组', row['上']/total*100, row['下']/total*100))

# ============================================================
# 组合规律分析
# ============================================================
print('\n' + '='*70)
print('组合规律分析')
print('='*70)

# 最优组合：上期类型 + 最大数位置
print('\n上期组类型 + 最大数位置:\n')
combo_stats = df_features.groupby(['type', 'max_in_up', 'label']).size().unstack(fill_value=0)

best_rules = []
for t in ['全上', '全下', '2上1下', '2下1上']:
    for m in [0, 1]:
        key = (t, m)
        if key in combo_stats.index:
            row = combo_stats.loc[key]
            total = row['上'] + row['下'] + row.get('平', 0)
            if total >= 50:  # 样本量至少50
                up_rate = row['上'] / total * 100
                down_rate = row['下'] / total * 100
                
                if up_rate > 55:
                    best_rules.append(('%s + 最大数在%s -> 杀下留上' % (t, '上组' if m == 1 else '下组'), up_rate, total))
                elif down_rate > 55:
                    best_rules.append(('%s + 最大数在%s -> 杀上留下' % (t, '上组' if m == 1 else '下组'), down_rate, total))

print('有效规律（准确率>55%，样本量>=50）:')
for rule, rate, total in sorted(best_rules, key=lambda x: x[1], reverse=True):
    print('%s: %.1f%% (%d期)' % (rule, rate, total))

print('\n' + '='*70)
print('总结')
print('='*70)
print()
print('1. 单独特征规律不明显，准确率都在50%左右')
print('2. 需要组合多个特征才能提高准确率')
print('3. 用户可能掌握了更复杂的规律，或者这只是概率统计')
print()
print('='*70)