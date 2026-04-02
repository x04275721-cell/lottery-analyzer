#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整方法组合测试
包含：马尔可夫 + 书本15种方法 + 334断组 + 更多
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
from book_methods import run_all_analyses, comprehensive_score

print('='*70)
print('完整方法组合测试 - 提升命中率')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 新方法1: 334断组法
# ============================================================
def get_334_duanzu(last_nums):
    """334断组：根据上期和值尾断组"""
    n1, n2, n3 = last_nums
    sum_tail = (n1 + n2 + n3) % 10
    
    # 根据和值尾断组
    if sum_tail in [0, 5]:
        # 断组019~456~2378
        group1 = [0,1,9]
        group2 = [4,5,6]
        group3 = [2,3,7,8]
    elif sum_tail in [1, 6]:
        # 断组012~567~3489
        group1 = [0,1,2]
        group2 = [5,6,7]
        group3 = [3,4,8,9]
    elif sum_tail in [2, 7]:
        # 断组123~678~0459
        group1 = [1,2,3]
        group2 = [6,7,8]
        group3 = [0,4,5,9]
    elif sum_tail in [3, 8]:
        # 断组234~789~0156
        group1 = [2,3,4]
        group2 = [7,8,9]
        group3 = [0,1,5,6]
    else:  # 4, 9
        # 断组345~890~1267
        group1 = [3,4,5]
        group2 = [8,9,0]
        group3 = [1,2,6,7]
    
    return group1, group2, group3

def predict_334_duanzu(df_train):
    """预测334断组"""
    last = df.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    
    g1, g2, g3 = get_334_duanzu(last_nums)
    
    # 判断哪组可能断掉（近期未出）
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    
    # 断掉出现最少的组
    if g1_count <= g2_count and g1_count <= g3_count:
        return g2 + g3  # 保留g2和g3
    elif g2_count <= g1_count and g2_count <= g3_count:
        return g1 + g3  # 保留g1和g3
    else:
        return g1 + g2  # 保留g1和g2

# ============================================================
# 新方法2: 万三万六法
# ============================================================
def get_wansan_wanliu(last_nums):
    """万三万六法"""
    n1, n2, n3 = last_nums
    
    # 万三：每个数字对应的3个数字
    wansan_map = {
        0: [0,4,8], 1: [1,5,9], 2: [2,6,0], 3: [3,7,1],
        4: [4,8,2], 5: [5,9,3], 6: [6,0,4], 7: [7,1,5],
        8: [8,2,6], 9: [9,3,7]
    }
    
    # 取个位对应的万三
    wansan = wansan_map[n3]
    
    return wansan

# ============================================================
# 新方法3: 余温断组
# ============================================================
def get_yuwen_duanzu(df_train):
    """余温断组：根据近期热号分组"""
    all_nums = []
    for _, row in df_train.tail(20).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    num_count = Counter(all_nums)
    
    # 热号组（前3）
    hot = [n for n, c in num_count.most_common(3)]
    
    # 温号组（中间3）
    middle = [n for n, c in num_count.most_common(6)[3:]]
    
    # 冷号组（剩余4）
    cold = [n for n in range(10) if n not in hot and n not in middle]
    
    return hot, middle, cold

# ============================================================
# 综合预测
# ============================================================
def predict_5ma_enhanced(df_train):
    """增强版组选五码预测"""
    analyses = run_all_analyses(df_train)
    
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    
    # 每个数字得分
    scores = {d: 0 for d in range(10)}
    
    # 1. 书本方法 (20%)
    danma = analyses['danma']
    scores[danma['gold_dan']] += 10
    for sd in danma['silver_dan']:
        scores[sd] += 5
    
    # 2. 334断组 (30%)
    duanzu_6ma = predict_334_duanzu(df_train)
    for d in duanzu_6ma:
        scores[d] += 15
    
    # 3. 万三万六 (10%)
    wansan = get_wansan_wanliu(last_nums)
    for d in wansan:
        scores[d] += 5
    
    # 4. 余温断组 (20%)
    hot, middle, cold = get_yuwen_duanzu(df_train)
    for d in hot:
        scores[d] += 10
    for d in middle:
        scores[d] += 5
    
    # 5. 马尔可夫 (10%)
    # 简化版：直接用热号
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df_train[col].astype(int).tail(30).tolist()
        num_count = Counter(nums)
        for n, c in num_count.most_common(3):
            scores[n] += 2
    
    # 6. 随机 (10%)
    for d in range(10):
        scores[d] += random.random() * 5
    
    # 排序取前5
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top5 = [n for n, s in sorted_nums[:5]]
    
    return top5, scores

# ============================================================
# 测试
# ============================================================
def test_enhanced_5ma(test_count=5000):
    """测试增强版组选五码"""
    random.seed(42)
    
    full_hit = 0
    at_least_2 = 0
    at_least_1 = 0
    
    total = min(test_count, len(df) - 600)
    
    print('\n开始测试...')
    print('测试期数: %d' % total)
    print()
    
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100:
            continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        
        top5, scores = predict_5ma_enhanced(df_train)
        top5_set = set(top5)
        
        hit_count = len(real_set & top5_set)
        
        if hit_count == len(real_set):
            full_hit += 1
        if hit_count >= 2:
            at_least_2 += 1
        if hit_count >= 1:
            at_least_1 += 1
        
        if (i - 100) % 1000 == 0:
            print('进度: %d/%d | 全中: %.1f%% | 至少2: %.1f%% | 至少1: %.1f%%' % (
                i - 100, total,
                full_hit / max(1, i - 100) * 100,
                at_least_2 / max(1, i - 100) * 100,
                at_least_1 / max(1, i - 100) * 100
            ))
    
    print()
    print('='*70)
    print('增强版组选五码测试结果 (5000期)')
    print('='*70)
    print()
    print('包含方法:')
    print('  1. 书本15种方法 (20%)')
    print('  2. 334断组法 (30%)')
    print('  3. 万三万六法 (10%)')
    print('  4. 余温断组 (20%)')
    print('  5. 马尔可夫 (10%)')
    print('  6. 随机 (10%)')
    print()
    print('【结果】')
    print('-'*70)
    print('开奖号全在五码中: %d次 (%.2f%%) 理论8.33%%' % (full_hit, full_hit/total*100))
    print('至少2个在五码中: %d次 (%.2f%%) 理论50%%' % (at_least_2, at_least_2/total*100))
    print('至少1个在五码中: %d次 (%.2f%%) 理论65%%' % (at_least_1, at_least_1/total*100))
    print('='*70)
    
    return {
        'full_hit': full_hit/total*100,
        'at_least_2': at_least_2/total*100,
        'at_least_1': at_least_1/total*100
    }

# 运行测试
result = test_enhanced_5ma(5000)

# 保存
import json
with open('enhanced_5ma_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 enhanced_5ma_result.json')
