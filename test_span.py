#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
跨度分析方法测试
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

print('='*70)
print('跨度分析方法测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 跨度分析方法
# ============================================================
def get_span(nums):
    """获取跨度"""
    return max(nums) - min(nums)

def get_position_span(n1, n2):
    """获取两位置跨度"""
    return abs(n1 - n2)

def predict_span(df_train):
    """
    跨度分析：
    1. 十个跨度余数：避免连续3期相同
    2. 百十、百个跨度：大跨度区域定胆
    3. 百十跨7：平均遗漏约16期
    4. 百个0跨：组三信号
    """
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 10:
        return scores
    
    # 近10期跨度统计
    recent_spans = []
    for _, row in df_train.tail(10).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        span = get_span(nums)
        recent_spans.append(span)
    
    # 统计近10期跨度出现情况
    span_count = Counter(recent_spans)
    
    # 避免连续3期相同的跨度
    last3_spans = recent_spans[-3:]
    if len(set(last3_spans)) == 1:
        # 如果连续3期相同，杀同跨度
        same_span = last3_spans[0]
        # 给不同跨度的数字加分
        for d in range(10):
            for s in range(10):
                if s != same_span:
                    scores[d] += 0.5
    
    # 百十、百个跨度统计
    bai_shi_spans = []
    bai_ge_spans = []
    
    for _, row in df_train.tail(10).iterrows():
        bai, shi, ge = int(row['num1']), int(row['num2']), int(row['num3'])
        bai_shi_spans.append(get_position_span(bai, shi))
        bai_ge_spans.append(get_position_span(bai, ge))
    
    # 百十跨度大跨度（5-9）加分
    bai_shi_big = sum(1 for s in bai_shi_spans if s >= 5)
    if bai_shi_big <= 2:  # 近10期大跨度少
        # 给大跨度数字加分
        for d in [5, 6, 7, 8, 9]:
            scores[d] += 2
    
    # 百十跨7遗漏
    span7_missing = 0
    for s in reversed(bai_shi_spans):
        if s == 7:
            break
        span7_missing += 1
    
    if span7_missing >= 15:  # 遗漏超过平均（约16期）
        # 给能形成跨7的数字组合加分
        for d in range(10):
            for d2 in range(10):
                if abs(d - d2) == 7:
                    scores[d] += 1
    
    # 百个0跨遗漏（组三信号）
    span0_missing = 0
    for s in reversed(bai_ge_spans):
        if s == 0:
            break
        span0_missing += 1
    
    if span0_missing >= 5:  # 遗漏5期以上
        # 组三概率增加，给重复号加分
        last = df_train.iloc[-1]
        last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
        for d in set(last_nums):
            scores[d] += 2
    
    return scores

# ============================================================
# 基础方法
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

def predict_10methods(df_train):
    """10种方法"""
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
    
    # 其他方法
    counter = Counter(all_nums)
    for d, ct in counter.items():
        scores[d] += ct * 0.3
    
    # 邻孤传
    ch = set(last_nums)
    li = set()
    for n in last_nums:
        if n > 0: li.add(n-1)
        if n < 9: li.add(n+1)
    for d in ch: scores[d] += 3
    for d in li: scores[d] += 4
    
    # 半顺
    def is_b(nums):
        n1,n2,n3 = sorted(nums)
        return abs(n1-n2)==1 or abs(n2-n3)==1 or abs(n1-n3)==1
    for _, row in df_train.tail(50).iterrows():
        ns = [int(row['num1']), int(row['num2']), int(row['num3'])]
        if is_b(ns):
            for d in ns: scores[d] += 0.5
    
    # 万能六码
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
    
    # 两码和差
    n1, n2, n3 = last_nums
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    lm_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    lm_count = Counter(lm_nums)
    for d, ct in lm_count.items():
        scores[d] += ct * 2
    
    return [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:5]]

def predict_11methods_span(df_train):
    """10方法 + 跨度分析"""
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
        scores[d] += ct * 0.3
    
    ch = set(last_nums)
    li = set()
    for n in last_nums:
        if n > 0: li.add(n-1)
        if n < 9: li.add(n+1)
    for d in ch: scores[d] += 3
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
        scores[d] += ct * 2
    
    # 跨度分析
    for d, s in predict_span(df_train).items():
        scores[d] += s
    
    return [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:5]]

# ============================================================
# 测试
# ============================================================
def test_predict(predict_func, name, test_count=5000):
    random.seed(42)
    results = []
    total = min(test_count, len(df) - 600)
    for i in range(100, 100 + total):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        top5_set = set(predict_func(df_train))
        hit = len(real_set & top5_set) == len(real_set)
        results.append(hit)
    
    total_hits = sum(results)
    hit_rate = total_hits / len(results) * 100
    return hit_rate

print('\n测试10种方法...')
r1 = test_predict(predict_10methods, '10种方法', 3000)
print('10种方法: %.2f%%' % r1)

print('\n测试11种方法（+跨度分析）...')
r2 = test_predict(predict_11methods_span, '+跨度分析', 3000)
print('+跨度分析: %.2f%%' % r2)

print()
print('='*70)
print('结果对比')
print('='*70)
print()
print('| 方法 | 命中率 | 提升 |')
print('|------|--------|------|')
print('| 10种方法 | %.2f%% | - |' % r1)
print('| +跨度分析 | %.2f%% | %+.2f%% |' % (r2, r2-r1))
print()
if r2 > r1:
    print('跨度分析有效！')
else:
    print('跨度分析效果不佳')
print()
print('='*70)