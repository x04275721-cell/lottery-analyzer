#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整方法组合测试 V2
包含：马尔可夫 + 书本15种方法 + 334断组 + 五五分解 + 两码进位和差
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
from book_methods import run_all_analyses

print('='*70)
print('完整方法组合测试 V2 - 更多方法融合')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 方法1: 334断组法
# ============================================================
def get_334_duanzu(last_nums):
    """334断组：根据上期和值尾断组"""
    n1, n2, n3 = last_nums
    sum_tail = (n1 + n2 + n3) % 10
    
    if sum_tail in [0, 5]:
        return [0,1,9], [4,5,6], [2,3,7,8]
    elif sum_tail in [1, 6]:
        return [0,1,2], [5,6,7], [3,4,8,9]
    elif sum_tail in [2, 7]:
        return [1,2,3], [6,7,8], [0,4,5,9]
    elif sum_tail in [3, 8]:
        return [2,3,4], [7,8,9], [0,1,5,6]
    else:
        return [3,4,5], [8,9,0], [1,2,6,7]

def predict_334_duanzu(df_train):
    """预测334断组"""
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    g1, g2, g3 = get_334_duanzu(last_nums)
    
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    
    if g1_count <= g2_count and g1_count <= g3_count:
        return g2 + g3
    elif g2_count <= g1_count and g2_count <= g3_count:
        return g1 + g3
    else:
        return g1 + g2

# ============================================================
# 方法2: 五五分解法
# ============================================================
def get_55_fenjie(last_nums):
    """五五分解：将0-9分成两组各5个数字"""
    n1, n2, n3 = last_nums
    all_nums = set([n1, n2, n3])
    
    # 常用分解式
    # 1. 按大小分
    group1_small = [0,1,2,3,4]
    group2_big = [5,6,7,8,9]
    
    # 2. 按奇偶分
    group1_odd = [1,3,5,7,9]
    group2_even = [0,2,4,6,8]
    
    # 3. 按质合分
    group1_prime = [2,3,5,7] + [0]  # 质数+0
    group2_composite = [1,4,6,8,9]
    
    # 4. 四方分解
    group1_4f = [0,1,4,5,8]
    group2_4f = [2,3,6,7,9]
    
    return [
        (group1_small, group2_big),
        (group1_odd, group2_even),
        (group1_prime, group2_composite),
        (group1_4f, group2_4f)
    ]

def predict_55_fenjie(df_train):
    """预测五五分解"""
    decompositions = None
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    
    decompositions = get_55_fenjie(last_nums)
    
    # 统计近期各分解式的表现
    best_group = None
    best_score = -1
    
    for g1, g2 in decompositions:
        # 统计近10期哪组更热
        all_nums = []
        for _, row in df_train.tail(10).iterrows():
            all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
        
        g1_count = sum(1 for n in all_nums if n in g1)
        g2_count = sum(1 for n in all_nums if n in g2)
        
        # 选择更热的组
        if g1_count > g2_count:
            score = g1_count
            group = g1
        else:
            score = g2_count
            group = g2
        
        if score > best_score:
            best_score = score
            best_group = group
    
    return best_group if best_group else [0,1,2,3,4]

# ============================================================
# 方法3: 两码进位和差法
# ============================================================
def get_liangma_jinwei_hecha(last_nums):
    """两码进位和差"""
    n1, n2, n3 = last_nums
    
    # 两码和（取个位）
    he12 = (n1 + n2) % 10
    he13 = (n1 + n3) % 10
    he23 = (n2 + n3) % 10
    
    # 两码差（绝对值）
    cha12 = abs(n1 - n2)
    cha13 = abs(n1 - n3)
    cha23 = abs(n2 - n3)
    
    # 进位和
    jinwei12 = (n1 + n2) // 10
    jinwei13 = (n1 + n3) // 10
    jinwei23 = (n2 + n3) // 10
    
    return {
        'he': [he12, he13, he23],
        'cha': [cha12, cha13, cha23],
        'jinwei': [jinwei12, jinwei13, jinwei23]
    }

def predict_liangma(df_train):
    """预测两码进位和差"""
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    
    result = get_liangma_jinwei_hecha(last_nums)
    
    # 根据两码和差推荐数字
    # 两码和可能出现的数字
    he_nums = result['he']
    cha_nums = result['cha']
    jinwei_nums = result['jinwei']
    
    # 综合推荐
    all_nums = he_nums + cha_nums + jinwei_nums
    num_count = Counter(all_nums)
    
    # 返回出现次数最多的数字
    return [n for n, c in num_count.most_common(3)]

# ============================================================
# 综合预测
# ============================================================
def predict_5ma_v2(df_train):
    """增强版V2组选五码预测"""
    analyses = run_all_analyses(df_train)
    
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    
    scores = {d: 0 for d in range(10)}
    
    # 1. 书本方法 (15%)
    danma = analyses['danma']
    scores[danma['gold_dan']] += 8
    for sd in danma['silver_dan']:
        scores[sd] += 4
    
    # 2. 334断组 (25%)
    duanzu_6ma = predict_334_duanzu(df_train)
    for d in duanzu_6ma:
        scores[d] += 12
    
    # 3. 五五分解 (20%)
    fenjie_5ma = predict_55_fenjie(df_train)
    for d in fenjie_5ma:
        scores[d] += 10
    
    # 4. 两码进位和差 (15%)
    liangma_3ma = predict_liangma(df_train)
    for d in liangma_3ma:
        scores[d] += 8
    
    # 5. 马尔可夫/热号 (15%)
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df_train[col].astype(int).tail(30).tolist()
        num_count = Counter(nums)
        for n, c in num_count.most_common(3):
            scores[n] += 3
    
    # 6. 随机 (10%)
    for d in range(10):
        scores[d] += random.random() * 5
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top5 = [n for n, s in sorted_nums[:5]]
    
    return top5, scores

# ============================================================
# 测试
# ============================================================
def test_5ma_v2(test_count=5000):
    """测试V2版组选五码"""
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
        
        top5, scores = predict_5ma_v2(df_train)
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
    print('V2版组选五码测试结果 (5000期)')
    print('='*70)
    print()
    print('包含方法:')
    print('  1. 书本15种方法 (15%)')
    print('  2. 334断组法 (25%)')
    print('  3. 五五分解法 (20%)')
    print('  4. 两码进位和差 (15%)')
    print('  5. 马尔可夫/热号 (15%)')
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
result = test_5ma_v2(5000)

# 保存
import json
with open('5ma_v2_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n结果已保存到 5ma_v2_result.json')
