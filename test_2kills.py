#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
和值尾杀号法 - 两招组合测试
"""

import pandas as pd
from collections import Counter
import random
from itertools import combinations

print('='*70)
print('和值尾杀号法 - 两招组合测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 四招杀尾法
# ============================================================
def kill_tail_4methods(last_nums):
    bai, shi, ge = last_nums
    kill1 = (bai + 1) % 10
    kill2 = ge
    kill3 = (shi - 1) % 10 if shi > 0 else 9
    max_num = max(last_nums)
    min_num = min(last_nums)
    kill4 = (max_num * min_num) % 10
    return [kill1, kill2, kill3, kill4]

# ============================================================
# 测试两招组合准确率
# ============================================================
print('\n测试两招组合准确率（和尾不在被杀的2个中）...\n')

method_names = ['百位加一', '个位直杀', '十位减一', '最大乘最小']
results = []

for combo in combinations(range(4), 2):
    correct = 0
    total = 0
    for i in range(100, min(5100, len(df) - 600)):
        last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
        real_sum = int(df.iloc[i]['num1']) + int(df.iloc[i]['num2']) + int(df.iloc[i]['num3'])
        real_tail = real_sum % 10
        
        kill_tails = kill_tail_4methods(last_nums)
        selected_kills = [kill_tails[idx] for idx in combo]
        
        if real_tail not in selected_kills:
            correct += 1
        total += 1
    
    rate = correct / total * 100
    name = ' + '.join([method_names[idx] for idx in combo])
    results.append((name, rate, combo))
    print('%s: %.2f%%' % (name, rate))

# 排序
results.sort(key=lambda x: x[1], reverse=True)

print()
print('='*70)
print('两招组合排名（按准确率）')
print('='*70)
print()
for i, (name, rate, combo) in enumerate(results, 1):
    print('%d. %s: %.2f%%' % (i, name, rate))

# ============================================================
# 测试两招组合对选号命中率的影响
# ============================================================
print()
print('='*70)
print('测试两招组合对选号命中率的影响')
print('='*70)

def get_334(last_nums):
    n1, n2, n3 = last_nums
    st = (n1+n2+n3)%10
    if st in [0,5]: g1,g2,g3=[0,1,9],[4,5,6],[2,3,7,8]
    elif st in [1,6]: g1,g2,g3=[0,1,2],[5,6,7],[3,4,8,9]
    elif st in [2,7]: g1,g2,g3=[1,2,3],[6,7,8],[0,4,5,9]
    elif st in [3,8]: g1,g2,g3=[2,3,4],[7,8,9],[0,1,5,6]
    else: g1,g2,g3=[3,4,5],[8,9,0],[1,2,6,7]
    return g1,g2,g3

def predict_with_2kills(df_train, combo):
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
    
    # 只用两招杀尾
    kill_tails = kill_tail_4methods(last_nums)
    selected_kills = [kill_tails[idx] for idx in combo]
    
    for d in range(10):
        if d in selected_kills:
            scores[d] -= 3
        else:
            scores[d] += 2
    
    return [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)[:5]]

def test_predict(predict_func, test_count=5000):
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

print('\n各两招组合对选号命中率的影响:\n')

hit_results = []
for combo in combinations(range(4), 2):
    rate = test_predict(lambda df, c=combo: predict_with_2kills(df, c), 5000)
    name = ' + '.join([method_names[idx] for idx in combo])
    hit_results.append((name, rate, combo))

# 按命中率排序
hit_results.sort(key=lambda x: x[1], reverse=True)

print('| 排名 | 组合 | 命中率 |')
print('|------|------|--------|')
for i, (name, rate, combo) in enumerate(hit_results, 1):
    print('| %d | %s | %.2f%% |' % (i, name, rate))

print()
print('='*70)
print('最佳两招组合')
print('='*70)
best_name, best_rate, best_combo = hit_results[0]
print()
print('组合: %s' % best_name)
print('命中率: %.2f%%' % best_rate)
print()
print('='*70)