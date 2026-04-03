#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双飞神技测试
12789 = 12-17-18-19-27-28-29-78-79-89
03456 = 03-04-05-06-34-35-36-45-46-56
"""

import pandas as pd
from collections import Counter
import random

print('='*70)
print('双飞神技测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 双飞组合定义
# ============================================================
GROUP_UP = [1, 2, 7, 8, 9]  # 上组
GROUP_DOWN = [0, 3, 4, 5, 6]  # 下组

# 上组双飞
SHUANGFEI_UP = [
    (1, 2), (1, 7), (1, 8), (1, 9),
    (2, 7), (2, 8), (2, 9),
    (7, 8), (7, 9), (8, 9)
]

# 下组双飞
SHUANGFEI_DOWN = [
    (0, 3), (0, 4), (0, 5), (0, 6),
    (3, 4), (3, 5), (3, 6),
    (4, 5), (4, 6), (5, 6)
]

def get_shuangfei(nums):
    """获取开奖号码的双飞组合"""
    n1, n2, n3 = nums
    pairs = [
        tuple(sorted([n1, n2])),
        tuple(sorted([n1, n3])),
        tuple(sorted([n2, n3]))
    ]
    return pairs

def is_in_up_group(nums):
    """判断开奖号码是否在上组"""
    return all(n in GROUP_UP for n in nums)

def is_in_down_group(nums):
    """判断开奖号码是否在下组"""
    return all(n in GROUP_DOWN for n in nums)

def get_group_type(nums):
    """获取组类型"""
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
# 测试双飞覆盖率
# ============================================================
print('\n测试双飞覆盖率...')

# 统计每期开奖号码是否包含上组或下组的双飞
up_hit = 0
down_hit = 0
both_hit = 0
total = 0

for i in range(100, min(3100, len(df) - 600)):
    nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    pairs = get_shuangfei(nums)
    
    up_found = any(p in SHUANGFEI_UP for p in pairs)
    down_found = any(p in SHUANGFEI_DOWN for p in pairs)
    
    if up_found:
        up_hit += 1
    if down_found:
        down_hit += 1
    if up_found or down_found:
        both_hit += 1
    
    total += 1

print('上组双飞命中: %.2f%% (%d/%d)' % (up_hit/total*100, up_hit, total))
print('下组双飞命中: %.2f%% (%d/%d)' % (down_hit/total*100, down_hit, total))
print('上下至少一个: %.2f%% (%d/%d)' % (both_hit/total*100, both_hit, total))

# ============================================================
# 测试杀上留下/杀下留上的规律
# ============================================================
print('\n测试杀上留下/杀下留上规律...')

# 统计：如果上期全在上组，下期是否应该杀上留上？
# 根据用户的例子，需要判断杀上还是杀下

# 先统计上期组类型与下期双飞的关系
transition = {
    '全上': {'上': 0, '下': 0},
    '全下': {'上': 0, '下': 0},
    '2上1下': {'上': 0, '下': 0},
    '2下1上': {'上': 0, '下': 0},
}

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    last_type = get_group_type(last_nums)
    curr_pairs = get_shuangfei(curr_nums)
    
    # 判断本期命中哪个组
    hit_up = any(p in SHUANGFEI_UP for p in curr_pairs)
    hit_down = any(p in SHUANGFEI_DOWN for p in curr_pairs)
    
    if hit_up and not hit_down:
        transition[last_type]['上'] += 1
    elif hit_down and not hit_up:
        transition[last_type]['下'] += 1
    elif hit_up and hit_down:
        # 两个都命中，算平
        transition[last_type]['上'] += 0.5
        transition[last_type]['下'] += 0.5

print('\n上期组类型 -> 下期双飞命中:')
for last_type, counts in transition.items():
    total = counts['上'] + counts['下']
    if total > 0:
        print('%s -> 上: %.1f (%.1f%%), 下: %.1f (%.1f%%)' % (
            last_type, 
            counts['上'], counts['上']/total*100,
            counts['下'], counts['下']/total*100
        ))

# ============================================================
# 根据用户例子验证
# ============================================================
print('\n验证用户提供的例子...')

# 用户例子：
# 82期434杀下留上83期开899中双飞89
# 83期899杀下留上84期开219中双飞12
# ...

examples = [
    (434, '杀下留上', 899, 89),
    (899, '杀下留上', 219, 12),
    (219, '杀上留下', 490, 4),  # 用户说04，应该是(0,4)
    (490, '杀上留下', 532, 35),
    (532, '杀下留上', 797, 79),
    (797, '杀下留上', 761, 17),
    (761, '杀上留下', 457, 45),
    (457, '杀上留下', 890, 89),
    (890, '杀上留下', 564, 45),
    (564, '杀下留上', 71, 17),  # 071
]

print('验证用户例子:')
for last, rule, curr, shuangfei in examples:
    last_type = get_group_type([int(d) for d in str(last).zfill(3)])
    print('%s (%s) -> %s -> 双飞%d' % (last, last_type, rule, shuangfei))

# ============================================================
# 寻找杀上杀下的规律
# ============================================================
print('\n寻找杀上杀下的规律...')

# 用户的规律似乎是：
# 如果上期在上组多，就杀上留上（或杀下留上？）

# 让我重新理解用户的例子：
# 82期434（全下）-> 杀下留上 -> 83期899中89（上组）
# 83期899（全上）-> 杀下留上 -> 84期219中12（上组）
# 84期219（2上1下）-> 杀上留下 -> 85期490中04（下组）
# ...

# 让我统计：
# 如果上期全在下，下期命中哪个组？
# 如果上期全在上，下期命中哪个组？

# 重新统计
rule_stats = {
    '全上_杀上': 0, '全上_杀下': 0,
    '全下_杀上': 0, '全下_杀下': 0,
    '2上1下_杀上': 0, '2上1下_杀下': 0,
    '2下1上_杀上': 0, '2下1上_杀下': 0,
}

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    last_type = get_group_type(last_nums)
    curr_pairs = get_shuangfei(curr_nums)
    
    hit_up = any(p in SHUANGFEI_UP for p in curr_pairs)
    hit_down = any(p in SHUANGFEI_DOWN for p in curr_pairs)
    
    if last_type == '全上':
        if hit_up:
            rule_stats['全上_杀下'] += 1
        if hit_down:
            rule_stats['全上_杀上'] += 1
    elif last_type == '全下':
        if hit_up:
            rule_stats['全下_杀下'] += 1
        if hit_down:
            rule_stats['全下_杀上'] += 1
    elif last_type == '2上1下':
        if hit_up:
            rule_stats['2上1下_杀下'] += 1
        if hit_down:
            rule_stats['2上1下_杀上'] += 1
    elif last_type == '2下1上':
        if hit_up:
            rule_stats['2下1上_杀下'] += 1
        if hit_down:
            rule_stats['2下1上_杀上'] += 1

print('\n规律统计:')
for key, count in rule_stats.items():
    print('%s: %d' % (key, count))

# ============================================================
# 总结
# ============================================================
print()
print('='*70)
print('总结')
print('='*70)
print()
print('1. 上下组双飞覆盖率: %.2f%%' % (both_hit/total*100))
print()
print('2. 杀上杀下规律:')
print('   - 上期全在上: 杀下留上 %d次, 杀上留下 %d次' % (rule_stats['全上_杀下'], rule_stats['全上_杀上']))
print('   - 上期全在下: 杀下留上 %d次, 杀上留下 %d次' % (rule_stats['全下_杀下'], rule_stats['全下_杀上']))
print()
print('='*70)