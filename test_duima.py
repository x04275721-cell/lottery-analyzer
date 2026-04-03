#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对码组合法测试
对码: 05, 16, 27, 38, 49
"""

import pandas as pd
from collections import Counter
import random

print('='*70)
print('对码组合法测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 对码定义
# ============================================================
DUI_MA = {
    0: 5, 5: 0,  # 05对码
    1: 6, 6: 1,  # 16对码
    2: 7, 7: 2,  # 27对码
    3: 8, 8: 3,  # 38对码
    4: 9, 9: 4,  # 49对码
}

# 对码组合表（从用户提供的数据解析）
# 格式: {排除号码: (6码组1, 6码组2)}
DUI_MA_TABLE = {
    (0,2,4): ([1,6,3,8,4,9], [0,5,2,7]),  # 024=163849--0527
    (0,2,6): ([2,7,3,8,4,9], [0,5,1,6]),  # 026=273849--0516
    (0,2,8): ([0,5,2,7,3,8], [1,6,4,9]),  # 028=052738--1649
    (0,4,8): ([1,6,2,7,3,8], [0,5,4,9]),  # 048=162738--0549
    (0,4,6): ([0,5,1,6,4,9], [2,7,3,8]),  # 046=051649--2738
    (0,6,8): ([1,6,2,7,4,9], [3,8,0,5]),  # 068=162749--3805
    (2,4,6): ([0,5,2,7,4,9], [1,6,3,8]),  # 246=052749--1638
    (2,4,8): ([0,5,3,8,4,9], [1,6,2,7]),  # 248=053849--1627
    (2,6,8): ([0,5,1,6,2,7], [4,9,3,8]),  # 268=051627--4938
    (4,6,8): ([0,5,1,6,3,8], [2,7,4,9]),  # 468=051638--2749
}

def get_duima(num):
    """获取对码"""
    return DUI_MA[num]

def find_duima_group(nums):
    """
    根据上期号码找到对码组
    用户提供的数据：024, 026, 028, 048, 046, 068, 246, 248, 268, 468
    这些是排除号码
    """
    # 排除号码 = 上期号码的对码组合
    exclude = tuple(sorted([get_duima(n) for n in nums]))
    
    return DUI_MA_TABLE.get(exclude)

# ============================================================
# 测试对码覆盖率
# ============================================================
print('\n测试对码覆盖率...')

# 测试：开奖号码是否在对码组中
coverage_6ma = 0  # 在6码组中
coverage_4ma = 0  # 在4码组中
coverage_total = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    # 获取对码组
    groups = find_duima_group(last_nums)
    
    if groups:
        group1, group2 = groups
        
        # 检查开奖号码是否在组中
        real_set = set(real)
        
        # 组六：开奖号码必须在其中一组
        if len(real_set) == 3:  # 组六
            if real_set.issubset(set(group1)):
                coverage_6ma += 1
            elif real_set.issubset(set(group2)):
                if len(group2) == 4:
                    coverage_4ma += 1
                else:
                    coverage_6ma += 1
        
        coverage_total += 1

print('6码组覆盖率: %.2f%% (%d/%d)' % (coverage_6ma/coverage_total*100, coverage_6ma, coverage_total))
print('4码组覆盖率: %.2f%% (%d/%d)' % (coverage_4ma/coverage_total*100, coverage_4ma, coverage_total))
print('总覆盖率: %.2f%%' % ((coverage_6ma + coverage_4ma)/coverage_total*100))

# ============================================================
# 测试所有开奖号码在对码组中的情况
# ============================================================
print('\n测试所有开奖号码（包括组三）...')

all_coverage = 0
all_total = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    groups = find_duima_group(last_nums)
    
    if groups:
        group1, group2 = groups
        real_set = set(real)
        
        # 检查开奖号码是否在任一组中
        if real_set.issubset(set(group1)) or real_set.issubset(set(group2)):
            all_coverage += 1
        
        all_total += 1

print('所有开奖覆盖率: %.2f%% (%d/%d)' % (all_coverage/all_total*100, all_coverage, all_total))

# ============================================================
# 测试对码组对选号的帮助
# ============================================================
print('\n测试对码组对选号的帮助...')

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
    bai, shi, ge = last_nums
    kill1 = (bai + 1) % 10
    kill3 = (shi - 1) % 10 if shi > 0 else 9
    return [kill1, kill3]

def predict_full(df_train):
    """完整预测"""
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
    
    kill_tails = kill_tail_2methods(last_nums)
    for d in range(10):
        if d in kill_tails:
            scores[d] -= 3
        else:
            scores[d] += 2
    
    # 大小单双
    daxiao_counter = Counter()
    danshuang_counter = Counter()
    for _, row in df_train.tail(10).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        for n in nums:
            daxiao_counter['大' if n >= 5 else '小'] += 1
            danshuang_counter['单' if n % 2 == 1 else '双'] += 1
    
    if daxiao_counter['大'] > daxiao_counter['小']:
        for d in [5, 6, 7, 8, 9]: scores[d] += 1
    else:
        for d in [0, 1, 2, 3, 4]: scores[d] += 1
    
    if danshuang_counter['单'] > danshuang_counter['双']:
        for d in [0, 2, 4, 6, 8]: scores[d] += 1
    else:
        for d in [1, 3, 5, 7, 9]: scores[d] += 1
    
    sorted_nums = [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
    hot_tails = [n for n, c in sum_count.most_common(2)]
    
    return sorted_nums, hot_tails

def predict_with_duima(df_train):
    """加入对码组"""
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
    
    kill_tails = kill_tail_2methods(last_nums)
    for d in range(10):
        if d in kill_tails:
            scores[d] -= 3
        else:
            scores[d] += 2
    
    # 大小单双
    daxiao_counter = Counter()
    danshuang_counter = Counter()
    for _, row in df_train.tail(10).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        for n in nums:
            daxiao_counter['大' if n >= 5 else '小'] += 1
            danshuang_counter['单' if n % 2 == 1 else '双'] += 1
    
    if daxiao_counter['大'] > daxiao_counter['小']:
        for d in [5, 6, 7, 8, 9]: scores[d] += 1
    else:
        for d in [0, 1, 2, 3, 4]: scores[d] += 1
    
    if danshuang_counter['单'] > danshuang_counter['双']:
        for d in [0, 2, 4, 6, 8]: scores[d] += 1
    else:
        for d in [1, 3, 5, 7, 9]: scores[d] += 1
    
    # 对码组
    groups = find_duima_group(last_nums)
    if groups:
        group1, group2 = groups
        # 给对码组中的数字加分
        for d in group1:
            scores[d] += 3
        for d in group2:
            scores[d] += 2
    
    sorted_nums = [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
    hot_tails = [n for n, c in sum_count.most_common(2)]
    
    return sorted_nums, hot_tails

# ============================================================
# 测试
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

print('\n测试当前方法...')
r1 = test_predict(predict_full)
print('完成')

print('\n测试+对码组...')
r2 = test_predict(predict_with_duima)
print('完成')

print()
print('='*70)
print('对比结果')
print('='*70)
print()
print('| 指标 | 当前方法 | +对码组 | 提升 |')
print('|------|---------|--------|------|')
print('| 五码命中率 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_5nums']/r1['total']*100, r2['hit_5nums']/r2['total']*100, r2['hit_5nums']/r2['total']*100 - r1['hit_5nums']/r1['total']*100))
print('| 四注号码 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_4nums']/r1['total']*100, r2['hit_4nums']/r2['total']*100, r2['hit_4nums']/r2['total']*100 - r1['hit_4nums']/r1['total']*100))
print('| 两个和值尾 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_2tails']/r1['total']*100, r2['hit_2tails']/r2['total']*100, r2['hit_2tails']/r2['total']*100 - r1['hit_2tails']/r1['total']*100))
print('| 至少一个 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_either']/r1['total']*100, r2['hit_either']/r2['total']*100, r2['hit_either']/r2['total']*100 - r1['hit_either']/r1['total']*100))

print()
if r2['hit_5nums']/r2['total'] > r1['hit_5nums']/r1['total']:
    print('对码组有效！')
else:
    print('对码组效果不佳')

print()
print('='*70)