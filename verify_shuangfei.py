#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证双飞神技规律：和值大杀上留下
"""

import pandas as pd
from collections import Counter

print('='*70)
print('验证双飞神技规律：和值大杀上留下')
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

# ============================================================
# 验证规律
# ============================================================
print('\n验证规律：和值大(19-27)杀上留下\n')

# 统计
correct = 0
total = 0

for i in range(100, min(5100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    # 检查上期和值是否大(19-27)
    last_sum = sum(last_nums)
    
    if last_sum >= 19:  # 和值大
        # 获取本期双飞
        curr_pairs = get_shuangfei(curr_nums)
        hit_up = any(p in SHUANGFEI_UP for p in curr_pairs)
        hit_down = any(p in SHUANGFEI_DOWN for p in curr_pairs)
        
        # 验证：杀上留下 = 命中下组
        if hit_down:
            correct += 1
        total += 1

print('规律验证（和值大杀上留下）:')
print('命中次数: %d / %d' % (correct, total))
print('准确率: %.2f%%' % (correct/total*100 if total > 0 else 0))
print()

# 对比：不按规律（杀下留上）的准确率
reverse_correct = total - correct
print('反向策略（和值大杀下留上）:')
print('准确率: %.2f%%' % (reverse_correct/total*100 if total > 0 else 0))
print()

# ============================================================
# 验证其他规律
# ============================================================
print('='*70)
print('验证其他规律')
print('='*70)

# 规律1：和值小(0-9)杀下留上
print('\n规律1：和值小(0-9)杀下留上\n')

correct1 = 0
total1 = 0

for i in range(100, min(5100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    last_sum = sum(last_nums)
    
    if last_sum <= 9:  # 和值小
        curr_pairs = get_shuangfei(curr_nums)
        hit_up = any(p in SHUANGFEI_UP for p in curr_pairs)
        
        if hit_up:
            correct1 += 1
        total1 += 1

print('准确率: %.2f%% (%d/%d)' % (correct1/total1*100 if total1 > 0 else 0, correct1, total1))

# 规律2：和值中(10-18)杀下留上
print('\n规律2：和值中(10-18)杀下留上\n')

correct2 = 0
total2 = 0

for i in range(100, min(5100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    last_sum = sum(last_nums)
    
    if 10 <= last_sum <= 18:  # 和值中
        curr_pairs = get_shuangfei(curr_nums)
        hit_up = any(p in SHUANGFEI_UP for p in curr_pairs)
        
        if hit_up:
            correct2 += 1
        total2 += 1

print('准确率: %.2f%% (%d/%d)' % (correct2/total2*100 if total2 > 0 else 0, correct2, total2))

# ============================================================
# 综合验证
# ============================================================
print()
print('='*70)
print('综合验证')
print('='*70)

all_correct = 0
all_total = 0

for i in range(100, min(5100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    last_sum = sum(last_nums)
    curr_pairs = get_shuangfei(curr_nums)
    hit_up = any(p in SHUANGFEI_UP for p in curr_pairs)
    hit_down = any(p in SHUANGFEI_DOWN for p in curr_pairs)
    
    # 根据规律判断
    if last_sum >= 19:  # 和值大，杀上留下
        if hit_down:
            all_correct += 1
    elif last_sum <= 9:  # 和值小，杀下留上
        if hit_up:
            all_correct += 1
    else:  # 和值中，杀下留上
        if hit_up:
            all_correct += 1
    
    all_total += 1

print('\n综合规律准确率: %.2f%% (%d/%d)' % (all_correct/all_total*100, all_correct, all_total))

# 对比：随机选择
random_rate = 50  # 随机选择的理论准确率
improve = all_correct/all_total*100 - random_rate

print('对比随机选择: %.2f%%' % improve)
print()

# ============================================================
# 最优策略验证
# ============================================================
print('='*70)
print('最优策略验证')
print('='*70)
print()

# 统计每种情况的最佳策略
print('| 和值范围 | 样本数 | 杀上留下准确率 | 杀下留上准确率 | 最佳策略 |')
print('|----------|--------|---------------|---------------|----------|')

for sum_range in [(0, 9), (10, 18), (19, 27)]:
    kill_up_correct = 0
    kill_down_correct = 0
    total_count = 0
    
    for i in range(100, min(5100, len(df) - 600)):
        last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
        curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        
        last_sum = sum(last_nums)
        
        if sum_range[0] <= last_sum <= sum_range[1]:
            curr_pairs = get_shuangfei(curr_nums)
            hit_up = any(p in SHUANGFEI_UP for p in curr_pairs)
            hit_down = any(p in SHUANGFEI_DOWN for p in curr_pairs)
            
            if hit_up:
                kill_down_correct += 1
            if hit_down:
                kill_up_correct += 1
            
            total_count += 1
    
    kill_up_rate = kill_up_correct / total_count * 100 if total_count > 0 else 0
    kill_down_rate = kill_down_correct / total_count * 100 if total_count > 0 else 0
    
    if kill_up_rate > kill_down_rate:
        best = '杀上留下'
        best_rate = kill_up_rate
    else:
        best = '杀下留上'
        best_rate = kill_down_rate
    
    print('| %d-%d | %d | %.2f%% | %.2f%% | %s (%.2f%%) |' % (
        sum_range[0], sum_range[1], total_count,
        kill_up_rate, kill_down_rate,
        best, best_rate
    ))

print()
print('='*70)