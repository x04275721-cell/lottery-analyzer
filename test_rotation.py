#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旋转矩阵破解分析
"""

import pandas as pd
from collections import Counter
import itertools

print('='*70)
print('旋转矩阵破解分析')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 旋转矩阵数据（从用户提供的数据解析）
# ============================================================
# 格式：{标识: [组合1, 组合2, ...]}
# 每行第一个数字对是标识，后面是组合

ROTATION_MATRIX = {
    # 第一组
    (0,5): [[2,3,7,8], [0,1,5,6], [0,4,5,9], [0,4,6], [2,4,6,8]],
    (2,1): [[3,4,8,9], [0,1,5,6], [1,2,6,7], [0,2,6], [0,2,4,8]],
    (4,7): [[0,4,5,9], [2,3,7,8], [1,2,6,7], [2,6,8], [0,4,6,8]],
    (6,3): [[0,1,5,6], [2,3,7,8], [3,4,8,9], [2,4,8], [0,2,4,6]],
    (8,9): [[1,2,6,7], [3,4,8,9], [0,4,5,9], [0,4,8], [0,2,6,8]],
    
    # 第二组
    (0,5): [[1,4,6,9], [0,2,5,7], [0,3,5,8], [0,2,8], [2,4,6,8]],
    (2,1): [[0,2,5,7], [1,4,6,9], [1,3,6,8], [4,6,8], [0,2,4,8]],
    (4,7): [[1,3,6,8], [0,2,5,7], [2,4,7,9], [0,2,4], [0,4,6,8]],
    (6,3): [[2,4,7,9], [1,3,6,8], [0,3,5,8], [0,6,8], [0,2,4,6]],
    (8,9): [[0,3,5,8], [1,4,6,9], [2,4,7,9], [2,4,6], [0,2,6,8]],
}

# 重新整理
# 用户提供的格式：
# 05一2378一0156一0459一046一2468
# 标识:05, 组合:2378, 0156, 0459, 046, 2468

# 解析用户数据
matrix_data = """
05一2378一0156一0459一046一2468
21一3489一0156一1267一026一0248
47一0459一2378一1267一268一0468
63一0156一2378一3489一248一0246
89一1267一3489一0459一048一0268

05一1469一0257一0358一028一2468
21一0257一1469一1368一468一0248
47一1368一0257一2479一024一0468
63一2479一1368一0358一068一0246
89一0358一1469一2479一246一0268
"""

# 解析矩阵
rotation_matrix = {}
for line in matrix_data.strip().split('\n'):
    parts = line.split('一')
    key = parts[0]
    values = []
    for v in parts[1:]:
        # 转换为数字列表
        nums = [int(d) for d in v]
        values.append(nums)
    rotation_matrix[key] = values

print('\n旋转矩阵结构:')
for key, values in rotation_matrix.items():
    print('%s: %s' % (key, values))

# ============================================================
# 分析标识含义
# ============================================================
print('\n分析标识含义...')

# 标识: 05, 21, 47, 63, 89
# 可能的含义：
# 1. 对码：05, 16, 27, 38, 49
# 2. 差值：|0-5|=5, |2-1|=1, |4-7|=3, |6-3|=3, |8-9|=1
# 3. 和值：0+5=5, 2+1=3, 4+7=11, 6+3=9, 8+9=17

# 检查标识与开奖号码的关系
print('\n检查标识与上期开奖号码的关系...')

# 统计：标识是否与上期开奖号码有关
key_match_count = 0
total_count = 0

for i in range(100, min(1100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    # 检查所有可能的标识
    for key, values in rotation_matrix.items():
        key_nums = [int(d) for d in key]
        
        # 检查标识是否在上期号码中
        # 可能规则：标识的第一个数字在上期号码中？
        if key_nums[0] in last_nums or key_nums[1] in last_nums:
            key_match_count += 1
            break
    
    total_count += 1

print('标识匹配率: %.2f%% (%d/%d)' % (key_match_count/total_count*100, key_match_count, total_count))

# ============================================================
# 测试覆盖率
# ============================================================
print('\n测试旋转矩阵覆盖率...')

# 统计：开奖号码是否在某个组合中
coverage_count = 0
total_count = 0

for i in range(100, min(3100, len(df) - 600)):
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    # 检查所有组合
    found = False
    for key, values in rotation_matrix.items():
        for v in values:
            if curr_set.issubset(set(v)):
                found = True
                break
        if found:
            break
    
    if found:
        coverage_count += 1
    total_count += 1

print('旋转矩阵覆盖率: %.2f%% (%d/%d)' % (coverage_count/total_count*100, coverage_count, total_count))

# ============================================================
# 分析标识与组合的关系
# ============================================================
print('\n分析标识与组合的关系...')

# 统计每个标识的命中次数
key_hits = Counter()

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    # 找到命中的组合
    for key, values in rotation_matrix.items():
        for v in values:
            if curr_set.issubset(set(v)):
                key_hits[key] += 1
                break

print('\n各标识命中次数:')
for key, count in key_hits.most_common():
    print('%s: %d次' % (key, count))

# ============================================================
# 寻找选择标识的规律
# ============================================================
print('\n寻找选择标识的规律...')

# 检查：上期号码与标识的关系
# 规则1：上期最大数？
# 规则2：上期最小数？
# 规则3：上期和值？

rule_stats = {
    'max_num': Counter(),
    'min_num': Counter(),
    'sum_mod10': Counter(),
}

for i in range(100, min(1100, len(df) - 600)):
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
        max_num = max(last_nums)
        min_num = min(last_nums)
        sum_mod10 = sum(last_nums) % 10
        
        rule_stats['max_num'][max_num] += 1
        rule_stats['min_num'][min_num] += 1
        rule_stats['sum_mod10'][sum_mod10] += 1

print('\n上期最大数与命中关系:')
for num, count in sorted(rule_stats['max_num'].items()):
    print('最大数=%d: 命中%d次' % (num, count))

print('\n上期最小数与命中关系:')
for num, count in sorted(rule_stats['min_num'].items()):
    print('最小数=%d: 命中%d次' % (num, count))

print('\n上期和值尾与命中关系:')
for num, count in sorted(rule_stats['sum_mod10'].items()):
    print('和值尾=%d: 命中%d次' % (num, count))

# ============================================================
# 总结
# ============================================================
print()
print('='*70)
print('总结')
print('='*70)
print()
print('1. 旋转矩阵覆盖率: %.2f%%' % (coverage_count/total_count*100))
print()
print('2. 标识命中统计:')
for key, count in key_hits.most_common(5):
    print('   %s: %d次' % (key, count))
print()
print('3. 需要进一步研究选择标识的规律')
print()
print('='*70)