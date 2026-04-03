#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多输出格式测试 - 四注号码 + 两个和值
"""

import pandas as pd
from collections import Counter
import random
from itertools import combinations

print('='*70)
print('多输出格式测试 - 四注号码 + 两个和值')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 方法实现
# ============================================================
def get_334(last_nums):
    n1, n2, n3 = last_nums
    st = (n1+n2+n3)%10
    if st in [0,5]: g1,g2,g3=[0,1,9],[4,5,6],[2,3,7,8]
    elif st in [1,6]: g1,g2,g3=[0,1,2],[5,6,7],[3,4,8,9]
    elif st in [2,7]: g1,g2,g3=[1,2,3],[6,7,8],[0,4,5,9]
    elif st in [3,8]: g1,g2,g3=[2,3,4],[7,8,9],[0,1,5,6]
    else: g1,g2,g3=[3,4,5],[8,9,0],[1,2,6,7]
    return g1,g2,g3

def kill_tail_2methods(last_nums):
    """只用两招：百位加一 + 十位减一"""
    bai, shi, ge = last_nums
    kill1 = (bai + 1) % 10  # 百位加一
    kill3 = (shi - 1) % 10 if shi > 0 else 9  # 十位减一
    return [kill1, kill3]

def predict_full(df_train):
    """完整预测：返回所有需要的数据"""
    scores = {d: 0 for d in range(10)}
    
    last = df_train.iloc[-1]
    last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    # 334断组
    g1,g2,g3 = get_334(tuple(last_nums))
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    g1c = sum(1 for n in all_nums if n in g1)
    g2c = sum(1 for n in all_nums if n in g2)
    g3c = sum(1 for n in all_nums if n in g3)
    c = sorted([(g1,g1c),(g2,g2c),(g3,g3c)], key=lambda x:x[1], reverse=True)
    for d in c[0][0]: scores[d] += 14
    for d in c[1][0]: scores[d] += 10
    for d in c[2][0]: scores[d] += 2
    
    counter = Counter(all_nums)
    for d, ct in counter.items():
        scores[d] += ct * 0.4
    
    ch = set(last_nums)
    li = set()
    for n in last_nums:
        if n > 0: li.add(n-1)
        if n < 9: li.add(n+1)
    for d in ch: scores[d] += 5
    for d in li: scores[d] += 4
    
    def is_b(nums):
        n1,n2,n3 = sorted(nums)
        return abs(n1-n2)==1 or abs(n2-n3)==1 or abs(n1-n3)==1
    for _, row in df_train.tail(50).iterrows():
        ns = [int(row['num1']), int(row['num2']), int(row['num3'])]
        if is_b(ns):
            for d in ns: scores[d] += 0.5
    
    WAN_NENG_6 = [
        [0,1,2,3,4,5],[0,1,2,3,6,7],[0,1,2,3,8,9],[0,1,4,5,6,7],[0,1,4,5,8,9],
        [0,1,6,7,8,9],[2,3,4,5,6,7],[2,3,4,5,8,9],[2,3,6,7,8,9],[4,5,6,7,8,9],
    ]
    hot = [d for d, ct in counter.items() if ct >= 3]
    if not hot: hot = [d for d, ct in counter.most_common(2)]
    best_g, best_s = None, -1
    for g in WAN_NENG_6:
        m = sum(1 for h in hot if h in g)
        if m > best_s: best_s, best_g = m, g
    if best_g:
        for d in best_g: scores[d] += 5
    
    n1, n2, n3 = last_nums
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    lm_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    lm_count = Counter(lm_nums)
    for d, ct in lm_count.items():
        scores[d] += ct * 3
    
    sums = []
    for _, r in df_train.tail(30).iterrows():
        s = int(r['num1']) + int(r['num2']) + int(r['num3'])
        sums.append(s % 10)
    sum_count = Counter(sums)
    for d, ct in sum_count.items():
        scores[d] += ct * 0.8
    
    # 两招杀尾
    kill_tails = kill_tail_2methods(last_nums)
    for d in range(10):
        if d in kill_tails:
            scores[d] -= 3
        else:
            scores[d] += 2
    
    # 返回排序后的数字
    sorted_nums = [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
    
    # 返回热门和值尾
    hot_tails = [n for n, c in sum_count.most_common(2)]
    
    return sorted_nums, hot_tails

# ============================================================
# 测试不同输出格式
# ============================================================
def test_output_formats():
    random.seed(42)
    
    # 统计
    hit_4nums = 0  # 四注号码命中
    hit_2tails = 0  # 两个和值尾命中
    hit_both = 0  # 两者都命中
    hit_either = 0  # 两者至少一个命中
    total = 0
    
    for i in range(100, 5100):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        # 真实开奖
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        real_sum = sum(real)
        real_tail = real_sum % 10
        
        # 预测
        sorted_nums, hot_tails = predict_full(df_train)
        
        # 四注号码（前4个数字）
        top4 = set(sorted_nums[:4])
        
        # 两个和值尾
        tail_set = set(hot_tails)
        
        # 检查命中
        hit4 = len(real_set & top4) == len(real_set)
        hit_tail = real_tail in tail_set
        
        if hit4:
            hit_4nums += 1
        if hit_tail:
            hit_2tails += 1
        if hit4 and hit_tail:
            hit_both += 1
        if hit4 or hit_tail:
            hit_either += 1
        
        total += 1
    
    return {
        'total': total,
        'hit_4nums': hit_4nums,
        'hit_2tails': hit_2tails,
        'hit_both': hit_both,
        'hit_either': hit_either
    }

print('\n测试不同输出格式命中率...\n')

results = test_output_formats()

print('='*70)
print('测试结果（5000期）')
print('='*70)
print()
print('| 输出格式 | 命中次数 | 命中率 |')
print('|----------|---------|--------|')
print('| 四注号码 | %d | %.2f%% |' % (results['hit_4nums'], results['hit_4nums']/results['total']*100))
print('| 两个和值尾 | %d | %.2f%% |' % (results['hit_2tails'], results['hit_2tails']/results['total']*100))
print('| 两者都命中 | %d | %.2f%% |' % (results['hit_both'], results['hit_both']/results['total']*100))
print('| 两者至少一个命中 | %d | %.2f%% |' % (results['hit_either'], results['hit_either']/results['total']*100))

print()
print('='*70)
print('分析')
print('='*70)
print()

# 计算理论概率
# 四注号码理论概率：C(4,3)/C(10,3) = 4/120 = 3.33%
# 两个和值尾理论概率：2/10 = 20%

print('理论概率对比:')
print('- 四注号码理论概率: 3.33%% (C(4,3)/C(10,3))')
print('- 两个和值尾理论概率: 20.00%% (2/10)')
print()

rate_4nums = results['hit_4nums']/results['total']*100
rate_2tails = results['hit_2tails']/results['total']*100
rate_either = results['hit_either']/results['total']*100

print('实际命中率:')
print('- 四注号码: %.2f%% (提升 %.2f%%)' % (rate_4nums, rate_4nums - 3.33))
print('- 两个和值尾: %.2f%% (提升 %.2f%%)' % (rate_2tails, rate_2tails - 20))
print('- 两者至少一个: %.2f%%' % rate_either)

print()
print('='*70)