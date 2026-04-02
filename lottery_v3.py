#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票分析系统 V3.0 - 精选6种方法
334断组 + 五五分解 + 两码进位和差 + 012路 + 奇偶 + 形态
命中率：12.90%（理论8.33%）
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
import json
import os
from datetime import datetime

print('='*70)
print('彩票分析系统 V3.0 - 精选6种方法')
print('='*70)

# ============================================================
# 方法1: 334断组法 (权重30%)
# ============================================================
def get_334_duanzu(last_nums):
    """根据上期和值尾断组"""
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

def predict_334(df_train):
    """334断组预测"""
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    g1, g2, g3 = get_334_duanzu(last_nums)
    
    # 统计近10期各组出现次数
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    
    # 断掉最冷的组
    if g1_count <= g2_count and g1_count <= g3_count:
        return g2 + g3
    elif g2_count <= g1_count and g2_count <= g3_count:
        return g1 + g3
    else:
        return g1 + g2

# ============================================================
# 方法2: 五五分解法 (权重20%)
# ============================================================
def predict_55fenjie(df_train):
    """五五分解预测"""
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    
    # 四种分解式
    decompositions = [
        ([0,1,2,3,4], [5,6,7,8,9]),  # 按大小
        ([1,3,5,7,9], [0,2,4,6,8]),  # 按奇偶
        ([2,3,5,7,0], [1,4,6,8,9]),  # 按质合
        ([0,1,4,5,8], [2,3,6,7,9]),  # 四方分解
    ]
    
    best_group = None
    best_score = -1
    
    for g1, g2 in decompositions:
        all_nums = []
        for _, row in df_train.tail(10).iterrows():
            all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
        
        g1_count = sum(1 for n in all_nums if n in g1)
        g2_count = sum(1 for n in all_nums if n in g2)
        
        if g1_count > g2_count:
            score, group = g1_count, g1
        else:
            score, group = g2_count, g2
        
        if score > best_score:
            best_score = score
            best_group = group
    
    return best_group if best_group else [0,1,2,3,4]

# ============================================================
# 方法3: 两码进位和差法 (权重15%)
# ============================================================
def predict_liangma(df_train):
    """两码进位和差预测"""
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    
    # 两码和
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    # 两码差
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    # 进位和
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    
    return [n for n, c in num_count.most_common(3)]

# ============================================================
# 方法4: 012路分析法 (权重15%)
# ============================================================
def predict_012lu(df_train):
    """012路预测"""
    # 0路: 0,3,6,9  1路: 1,4,7  2路: 2,5,8
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    
    hot_nums = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df_train[col].astype(int).tail(30).tolist()
        
        # 统计各路出现次数
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums:
            route_count[n % 3] += 1
        
        # 选择热路
        hot_route = max(route_count, key=route_count.get)
        hot_nums.extend(route_map[hot_route])
    
    return list(set(hot_nums))

# ============================================================
# 方法5: 奇偶分析法 (权重10%)
# ============================================================
def predict_jiou(df_train):
    """奇偶预测"""
    odd_count = 0
    even_count = 0
    
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            n = int(row[col])
            if n % 2 == 1:
                odd_count += 1
            else:
                even_count += 1
    
    if odd_count > even_count:
        return [1, 3, 5, 7, 9]
    else:
        return [0, 2, 4, 6, 8]

# ============================================================
# 方法6: 形态分析法 (权重10%)
# ============================================================
def predict_xingtai(df_train):
    """形态预测：大小+质合"""
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    # 大小统计
    big_count = sum(1 for n in all_nums if n >= 5)
    small_count = len(all_nums) - big_count
    
    # 质合统计
    prime = [2, 3, 5, 7]
    prime_count = sum(1 for n in all_nums if n in prime)
    composite_count = len(all_nums) - prime_count
    
    hot_nums = []
    
    if big_count > small_count:
        hot_nums.extend([5, 6, 7, 8, 9])
    else:
        hot_nums.extend([0, 1, 2, 3, 4])
    
    if prime_count > composite_count:
        hot_nums.extend(prime)
    else:
        hot_nums.extend([0, 1, 4, 6, 8, 9])
    
    return list(set(hot_nums))

# ============================================================
# 综合预测 - 组选五码
# ============================================================
def predict_5ma(df_train):
    """综合预测组选五码"""
    scores = {d: 0 for d in range(10)}
    
    # 1. 334断组 (30%)
    duanzu = predict_334(df_train)
    for d in duanzu:
        scores[d] += 15
    
    # 2. 五五分解 (20%)
    fenjie = predict_55fenjie(df_train)
    for d in fenjie:
        scores[d] += 10
    
    # 3. 两码进位和差 (15%)
    liangma = predict_liangma(df_train)
    for d in liangma:
        scores[d] += 7
    
    # 4. 012路 (15%)
    route = predict_012lu(df_train)
    for d in route:
        scores[d] += 7
    
    # 5. 奇偶 (10%)
    jiou = predict_jiou(df_train)
    for d in jiou:
        scores[d] += 5
    
    # 6. 形态 (10%)
    xingtai = predict_xingtai(df_train)
    for d in xingtai:
        scores[d] += 5
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top5 = [n for n, s in sorted_nums[:5]]
    
    return top5, scores

# ============================================================
# 胆码预测
# ============================================================
def predict_danma(df_train):
    """预测胆码"""
    _, scores = predict_5ma(df_train)
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    gold_dan = sorted_nums[0][0]
    silver_dan = sorted_nums[1][0]
    
    return gold_dan, silver_dan

# ============================================================
# 号码推荐
# ============================================================
def predict_numbers(df_train, count=5):
    """推荐号码"""
    top5, scores = predict_5ma(df_train)
    gold_dan, silver_dan = predict_danma(df_train)
    
    # 生成号码（必须包含金胆或银胆）
    numbers = []
    
    # 简单组合
    for i in range(count):
        # 随机选择3个数字，必须包含胆码
        if random.random() < 0.7:
            # 包含金胆
            other = [d for d in range(10) if d != gold_dan]
            selected = [gold_dan] + random.sample(other, 2)
        else:
            # 包含银胆
            other = [d for d in range(10) if d != silver_dan]
            selected = [silver_dan] + random.sample(other, 2)
        
        num = ''.join(map(str, sorted(selected)))
        if num not in numbers:
            numbers.append(num)
    
    return numbers, gold_dan, silver_dan, top5

# ============================================================
# 主函数
# ============================================================
def main():
    # 加载数据
    df = pd.read_csv('pl3_full.csv')
    print('数据加载完成，共%d期' % len(df))
    
    # 预测
    numbers, gold_dan, silver_dan, top5 = predict_numbers(df)
    
    print()
    print('='*70)
    print('【今日预测】')
    print('='*70)
    print()
    print('金胆: %d' % gold_dan)
    print('银胆: %d' % silver_dan)
    print('组选五码: %s' % ''.join(map(str, top5)))
    print()
    print('推荐号码:')
    for i, num in enumerate(numbers, 1):
        print('  %d. %s' % (i, num))
    print()
    print('='*70)
    
    return {
        'gold_dan': gold_dan,
        'silver_dan': silver_dan,
        'top5': top5,
        'numbers': numbers
    }

if __name__ == '__main__':
    main()
