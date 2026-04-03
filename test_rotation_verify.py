#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旋转矩阵 - 验证标识=差值规律
"""

import pandas as pd
from collections import Counter

print('='*70)
print('旋转矩阵 - 验证标识=差值规律')
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

# 标识对应的差值
KEY_DIFF_MAP = {
    '05': [5],
    '21': [1, 2],
    '47': [3, 4, 7],
    '63': [3, 6],
    '89': [1, 8, 9],
}

# ============================================================
# 验证规律：标识=差值
# ============================================================
print('\n验证规律：标识=上期差值\n')

correct = 0
total = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    # 计算上期差值
    diffs = [
        abs(last_nums[0] - last_nums[1]),
        abs(last_nums[0] - last_nums[2]),
        abs(last_nums[1] - last_nums[2]),
    ]
    
    # 根据差值选择标识
    selected_key = None
    for key, diff_list in KEY_DIFF_MAP.items():
        if any(d in diff_list for d in diffs):
            selected_key = key
            break
    
    # 如果找到标识，检查是否命中
    if selected_key:
        for v in rotation_matrix[selected_key]:
            if curr_set.issubset(set(v)):
                correct += 1
                break
        total += 1

print('规律验证: %.2f%% (%d/%d)' % (correct/total*100 if total > 0 else 0, correct, total))

# ============================================================
# 优化：根据差值组合选择标识
# ============================================================
print('\n优化：根据差值组合选择标识\n')

# 统计每个差值组合对应的最佳标识
diff_key_stats = Counter()

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    diffs = tuple(sorted([
        abs(last_nums[0] - last_nums[1]),
        abs(last_nums[0] - last_nums[2]),
        abs(last_nums[1] - last_nums[2]),
    ]))
    
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
        diff_key_stats[(diffs, hit_key)] += 1

# 统计每个差值组合的最佳标识
diff_best_key = {}
diff_counter = Counter()

for (diffs, key), count in diff_key_stats.items():
    if count > diff_counter.get(diffs, 0):
        diff_counter[diffs] = count
        diff_best_key[diffs] = (key, count)

print('差值组合 -> 最佳标识（出现次数>10）:')
for diffs, (key, count) in sorted(diff_best_key.items(), key=lambda x: x[1][1], reverse=True)[:20]:
    if count > 10:
        print('差值%s -> 标识%s (%d次)' % (diffs, key, count))

# ============================================================
# 使用最佳标识进行预测
# ============================================================
print('\n使用最佳标识进行预测...\n')

# 根据差值选择最佳标识
predict_correct = 0
predict_total = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    curr_set = set(curr_nums)
    
    diffs = tuple(sorted([
        abs(last_nums[0] - last_nums[1]),
        abs(last_nums[0] - last_nums[2]),
        abs(last_nums[1] - last_nums[2]),
    ]))
    
    # 选择最佳标识
    if diffs in diff_best_key:
        key, _ = diff_best_key[diffs]
        
        # 检查是否命中
        for v in rotation_matrix[key]:
            if curr_set.issubset(set(v)):
                predict_correct += 1
                break
        predict_total += 1

print('使用最佳标识预测: %.2f%% (%d/%d)' % (predict_correct/predict_total*100 if predict_total > 0 else 0, predict_correct, predict_total))

# ============================================================
# 总结
# ============================================================
print()
print('='*70)
print('总结')
print('='*70)
print()
print('1. 标识与差值有关，但关系复杂')
print('2. 需要根据差值组合动态选择标识')
print('3. 覆盖率仍需提升')
print()
print('='*70)