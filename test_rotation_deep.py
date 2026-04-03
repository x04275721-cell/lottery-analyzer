#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旋转矩阵 - 深度破解标识选择规律
"""

import pandas as pd
from collections import Counter

print('='*70)
print('旋转矩阵 - 深度破解标识选择规律')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 旋转矩阵定义
# ============================================================
rotation_matrix = {
    '05': [[2,3,7,8], [0,1,5,6], [0,4,5,9], [0,4,6], [2,4,6,8]],
    '21': [[3,4,8,9], [0,1,5,6], [1,2,6,7], [0,2,6], [0,2,4,8]],
    '47': [[0,4,5,9], [2,3,7,8], [1,2,6,7], [2,6,8], [0,4,6,8]],
    '63': [[0,1,5,6], [2,3,7,8], [3,4,8,9], [2,4,8], [0,2,4,6]],
    '89': [[1,2,6,7], [3,4,8,9], [0,4,5,9], [0,4,8], [0,2,6,8]],
}

# 对码
DUI_MA = {0:5, 5:0, 1:6, 6:1, 2:7, 7:2, 3:8, 8:3, 4:9, 9:4}

# ============================================================
# 分析标识的含义
# ============================================================
print('\n分析标识含义...')
print()

# 标识: 05, 21, 47, 63, 89
# 可能规律:
# 1. 对码: 05, 16, 27, 38, 49 (不是)
# 2. 两码差: |0-5|=5, |2-1|=1, |4-7|=3, |6-3|=3, |8-9|=1
# 3. 两码和: 0+5=5, 2+1=3, 4+7=11, 6+3=9, 8+9=17

# 检查标识与上期号码的关系
print('检查标识与上期号码的关系...')

# 统计：上期号码通过某种运算得到标识
key_from_last = Counter()

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    # 找到命中的标识
    hit_key = None
    for key, values in rotation_matrix.items():
        for v in values:
            if curr_set.issubset(set(v)):
                hit_key = key
                break
        if hit_key:
            break
    
    if hit_key:
        # 检查上期号码与标识的关系
        # 规则1: 标识的第一个数字在上期号码中
        key_first = int(hit_key[0])
        key_second = int(hit_key[1])
        
        if key_first in last_nums:
            key_from_last['标识首字在上期'] += 1
        if key_second in last_nums:
            key_from_last['标识次字在上期'] += 1
        if key_first in last_nums or key_second in last_nums:
            key_from_last['标识任一字在上期'] += 1

print('\n标识与上期号码关系:')
for rule, count in key_from_last.items():
    print('%s: %d次' % (rule, count))

# ============================================================
# 验证：标识=上期号码的对码组合
# ============================================================
print('\n验证：标识=上期号码的对码组合...')

duima_match = 0
total_match = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    # 找到命中的标识
    hit_key = None
    for key, values in rotation_matrix.items():
        for v in values:
            if curr_set.issubset(set(v)):
                hit_key = key
                break
        if hit_key:
            break
    
    if hit_key:
        total_match += 1
        
        # 计算上期号码的对码
        last_duima = sorted([DUI_MA[n] for n in last_nums])
        
        # 检查标识是否在对码中
        key_first = int(hit_key[0])
        key_second = int(hit_key[1])
        
        if key_first in last_duima or key_second in last_duima:
            duima_match += 1

print('标识在对码中: %.2f%% (%d/%d)' % (duima_match/total_match*100 if total_match > 0 else 0, duima_match, total_match))

# ============================================================
# 新思路：标识=上期某两位的差或和
# ============================================================
print('\n验证：标识=上期某两位的差...')

diff_match = 0
total_match = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    hit_key = None
    for key, values in rotation_matrix.items():
        for v in values:
            if curr_set.issubset(set(v)):
                hit_key = key
                break
        if hit_key:
            break
    
    if hit_key:
        total_match += 1
        
        # 计算上期号码的差
        diffs = [
            abs(last_nums[0] - last_nums[1]),
            abs(last_nums[0] - last_nums[2]),
            abs(last_nums[1] - last_nums[2]),
        ]
        
        key_first = int(hit_key[0])
        key_second = int(hit_key[1])
        
        if key_first in diffs or key_second in diffs:
            diff_match += 1

print('标识在差值中: %.2f%% (%d/%d)' % (diff_match/total_match*100 if total_match > 0 else 0, diff_match, total_match))

# ============================================================
# 统计每个标识对应的最佳上期特征
# ============================================================
print('\n统计每个标识对应的最佳上期特征...')

key_features = {k: Counter() for k in rotation_matrix.keys()}

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    hit_key = None
    for key, values in rotation_matrix.items():
        for v in values:
            if curr_set.issubset(set(v)):
                hit_key = key
                break
        if hit_key:
            break
    
    if hit_key:
        # 记录上期特征
        feature = '最大数%d' % max(last_nums)
        key_features[hit_key][feature] += 1

print('\n各标识对应的上期最大数:')
for key, features in key_features.items():
    print('%s: %s' % (key, features.most_common(3)))

# ============================================================
# 总结
# ============================================================
print()
print('='*70)
print('总结')
print('='*70)
print()
print('1. 标识与上期号码的关系不明显')
print('2. 需要更多数据或更复杂的规则')
print('3. 可能是动态计算而非固定规则')
print()
print('='*70)