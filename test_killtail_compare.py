#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
和值尾杀号法对比测试
方法1：四招杀尾（百位加一 + 十位减一）
方法2：两期和值相加杀尾
"""

import pandas as pd
from collections import Counter
import random

print('='*70)
print('和值尾杀号法对比测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 方法1：四招杀尾（只用两招）
# ============================================================
def kill_tail_2methods(last_nums):
    """百位加一 + 十位减一"""
    bai, shi, ge = last_nums
    kill1 = (bai + 1) % 10
    kill3 = (shi - 1) % 10 if shi > 0 else 9
    return [kill1, kill3]

# ============================================================
# 方法2：两期和值相加杀尾
# ============================================================
def kill_tail_sum(df_train):
    """
    两期和值相加杀尾：
    上期和值 + 上上期和值，取尾数
    """
    if len(df_train) < 2:
        return None
    
    last = df_train.iloc[-1]
    last2 = df_train.iloc[-2]
    
    sum1 = int(last['num1']) + int(last['num2']) + int(last['num3'])
    sum2 = int(last2['num1']) + int(last2['num2']) + int(last2['num3'])
    
    kill_tail = (sum1 + sum2) % 10
    
    return kill_tail

# ============================================================
# 测试准确率
# ============================================================
print('\n测试准确率...\n')

# 方法1：四招杀尾（两招版）
correct1 = 0
for i in range(100, min(5100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real_sum = int(df.iloc[i]['num1']) + int(df.iloc[i]['num2']) + int(df.iloc[i]['num3'])
    real_tail = real_sum % 10
    
    kill_tails = kill_tail_2methods(last_nums)
    
    if real_tail not in kill_tails:
        correct1 += 1

rate1 = correct1 / 5000 * 100
print('方法1（百位加一 + 十位减一）准确率: %.2f%%' % rate1)

# 方法2：两期和值相加杀尾
correct2 = 0
for i in range(100, min(5100, len(df) - 600)):
    df_train = df.iloc[max(0, i-500):i]
    real_sum = int(df.iloc[i]['num1']) + int(df.iloc[i]['num2']) + int(df.iloc[i]['num3'])
    real_tail = real_sum % 10
    
    kill_tail = kill_tail_sum(df_train)
    
    if kill_tail is not None and real_tail != kill_tail:
        correct2 += 1

rate2 = correct2 / 5000 * 100
print('方法2（两期和值相加）准确率: %.2f%%' % rate2)

# ============================================================
# 测试对选号命中率的影响
# ============================================================
print('\n测试对选号命中率的影响...\n')

def get_334(last_nums):
    n1, n2, n3 = last_nums
    st = (n1+n2+n3)%10
    if st in [0,5]: g1,g2,g3=[0,1,9],[4,5,6],[2,3,7,8]
    elif st in [1,6]: g1,g2,g3=[0,1,2],[5,6,7],[3,4,8,9]
    elif st in [2,7]: g1,g2,g3=[1,2,3],[6,7,8],[0,4,5,9]
    elif st in [3,8]: g1,g2,g3=[2,3,4],[7,8,9],[0,1,5,6]
    else: g1,g2,g3=[3,4,5],[8,9,0],[1,2,6,7]
    return g1,g2,g3

def predict_with_kill1(df_train):
    """方法1：百位加一 + 十位减一"""
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
    
    # 方法1杀尾
    kill_tails = kill_tail_2methods(last_nums)
    for d in range(10):
        if d in kill_tails:
            scores[d] -= 3
        else:
            scores[d] += 2
    
    sorted_nums = [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
    hot_tails = [n for n, c in sum_count.most_common(2)]
    
    return sorted_nums, hot_tails

def predict_with_kill2(df_train):
    """方法2：两期和值相加杀尾"""
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
    
    # 方法2杀尾
    kill_tail = kill_tail_sum(df_train)
    if kill_tail is not None:
        for d in range(10):
            if d == kill_tail:
                scores[d] -= 3
            else:
                scores[d] += 2
    
    sorted_nums = [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
    hot_tails = [n for n, c in sum_count.most_common(2)]
    
    return sorted_nums, hot_tails

# ============================================================
# 测试函数
# ============================================================
def test_predict(predict_func, test_count=5000):
    random.seed(42)
    
    hit_5nums = 0
    hit_4nums = 0
    hit_2tails = 0
    hit_either = 0
    total = 0
    
    for i in range(100, min(test_count + 100, len(df) - 600)):
        df_train = df.iloc[max(0, i-500):i]
        if len(df_train) < 100: continue
        
        real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        real_set = set(real)
        real_sum = sum(real)
        real_tail = real_sum % 10
        
        sorted_nums, hot_tails = predict_func(df_train)
        
        top5 = set(sorted_nums[:5])
        top4 = set(sorted_nums[:4])
        tail_set = set(hot_tails)
        
        hit5 = len(real_set & top5) == len(real_set)
        hit4 = len(real_set & top4) == len(real_set)
        hit_tail = real_tail in tail_set
        
        if hit5:
            hit_5nums += 1
        if hit4:
            hit_4nums += 1
        if hit_tail:
            hit_2tails += 1
        if hit4 or hit_tail:
            hit_either += 1
        
        total += 1
    
    return {
        'hit_5nums': hit_5nums,
        'hit_4nums': hit_4nums,
        'hit_2tails': hit_2tails,
        'hit_either': hit_either,
        'total': total
    }

print('测试方法1（百位加一 + 十位减一）...')
r1 = test_predict(predict_with_kill1)
print('完成')

print('测试方法2（两期和值相加）...')
r2 = test_predict(predict_with_kill2)
print('完成')

print()
print('='*70)
print('对比结果')
print('='*70)
print()
print('| 指标 | 方法1 | 方法2 | 差异 |')
print('|------|-------|-------|------|')
print('| 杀尾准确率 | %.2f%% | %.2f%% | %+.2f%% |' % (rate1, rate2, rate1-rate2))
print('| 五码命中率 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_5nums']/r1['total']*100, r2['hit_5nums']/r2['total']*100, r1['hit_5nums']/r1['total']*100 - r2['hit_5nums']/r2['total']*100))
print('| 四注号码 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_4nums']/r1['total']*100, r2['hit_4nums']/r2['total']*100, r1['hit_4nums']/r1['total']*100 - r2['hit_4nums']/r2['total']*100))
print('| 两个和值尾 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_2tails']/r1['total']*100, r2['hit_2tails']/r2['total']*100, r1['hit_2tails']/r1['total']*100 - r2['hit_2tails']/r2['total']*100))
print('| 至少一个 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_either']/r1['total']*100, r2['hit_either']/r2['total']*100, r1['hit_either']/r1['total']*100 - r2['hit_either']/r2['total']*100))

print()
if r1['hit_5nums']/r1['total'] > r2['hit_5nums']/r2['total']:
    print('结论: 方法1（百位加一 + 十位减一）更好')
else:
    print('结论: 方法2（两期和值相加）更好')

print()
print('='*70)