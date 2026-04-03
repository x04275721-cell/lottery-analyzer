#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
两码转万四方法测试
"""

import pandas as pd
from collections import Counter
import random

print('='*70)
print('两码转万四方法测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 两码转万四映射表
# ============================================================
LIANGMA_WAN4 = {
    (0,1): [4,5,7,8],  # 01=4578
    (0,2): [1,2,3,7],  # 02=1237
    (0,3): [1,2,4,5],  # 03=1245
    (0,4): [1,4,7,9],  # 04=1479
    (0,6): [1,3,6,9],  # 06=1369
    (0,7): [5,6,8,9],  # 07=5689
    (0,8): [3,7,8,9],  # 08=3789
    (0,9): [2,3,5,6],  # 09=2356
    (1,2): [0,6,7,9],  # 12=0679
    (1,3): [3,4,5,9],  # 13=3459
    (1,4): [3,4,6,7],  # 14=3467
    (1,7): [1,3,5,8],  # 17=1358
    (1,8): [0,1,7,8],  # 18=0178
    (1,9): [0,1,5,9],  # 19=0159
    (2,3): [1,2,8,9],  # 23=1289
    (2,4): [1,5,6,7],  # 24=1567
    (2,8): [0,3,5,7],  # 28=0357
    (2,9): [0,2,3,9],  # 29=0239
    (3,4): [0,1,3,4],  # 34=0134
    (3,9): [2,5,7,9],  # 39=2579
}

def get_wan4_from_liangma(n1, n2):
    """从两码获取万四"""
    key = tuple(sorted([n1, n2]))
    return LIANGMA_WAN4.get(key, [])

def predict_liangma_wan4(df_train):
    """
    两码转万四预测：
    1. 取上期开奖号码的所有两码组合
    2. 查找对应的万四
    3. 统计出现次数，给高频数字加分
    """
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 1:
        return scores
    
    last = df_train.iloc[-1]
    last_nums = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    # 所有两码组合
    wan4_count = Counter()
    
    # 百十
    wan4 = get_wan4_from_liangma(last_nums[0], last_nums[1])
    for d in wan4:
        wan4_count[d] += 1
    
    # 百个
    wan4 = get_wan4_from_liangma(last_nums[0], last_nums[2])
    for d in wan4:
        wan4_count[d] += 1
    
    # 十个
    wan4 = get_wan4_from_liangma(last_nums[1], last_nums[2])
    for d in wan4:
        wan4_count[d] += 1
    
    # 给高频万四数字加分
    for d, ct in wan4_count.items():
        scores[d] += ct * 2
    
    return scores

# ============================================================
# 测试两码转万四准确率
# ============================================================
print('\n测试两码转万四准确率...')

# 测试：万四中出现开奖号码的比例
wan4_correct = 0
wan4_total = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    # 获取所有万四
    all_wan4 = set()
    for n1, n2 in [(last_nums[0], last_nums[1]), (last_nums[0], last_nums[2]), (last_nums[1], last_nums[2])]:
        wan4 = get_wan4_from_liangma(n1, n2)
        all_wan4.update(wan4)
    
    # 检查开奖号码是否在万四中
    real_set = set(real)
    if real_set & all_wan4:  # 至少有1个数字在万四中
        wan4_correct += 1
    wan4_total += 1

print('万四包含开奖号码至少1个: %.2f%% (%d/%d)' % (wan4_correct/wan4_total*100, wan4_correct, wan4_total))

# 统计出现次数最多的数字
all_wan4_count = Counter()
for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    
    for n1, n2 in [(last_nums[0], last_nums[1]), (last_nums[0], last_nums[2]), (last_nums[1], last_nums[2])]:
        wan4 = get_wan4_from_liangma(n1, n2)
        for d in wan4:
            all_wan4_count[d] += 1

print('\n万四数字出现频率:')
for d, ct in all_wan4_count.most_common(10):
    print('%d: %d次 (%.2f%%)' % (d, ct, ct/3000/3*100))

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
    
    sorted_nums = [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
    hot_tails = [n for n, c in sum_count.most_common(2)]
    
    return sorted_nums, hot_tails

def predict_with_wan4(df_train):
    """加入两码转万四"""
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
    
    # 两码转万四
    for d, s in predict_liangma_wan4(df_train).items():
        scores[d] += s
    
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

print('\n测试+两码转万四...')
r2 = test_predict(predict_with_wan4)
print('完成')

print()
print('='*70)
print('对比结果')
print('='*70)
print()
print('| 指标 | 当前方法 | +两码转万四 | 提升 |')
print('|------|---------|------------|------|')
print('| 五码命中率 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_5nums']/r1['total']*100, r2['hit_5nums']/r2['total']*100, r2['hit_5nums']/r2['total']*100 - r1['hit_5nums']/r1['total']*100))
print('| 四注号码 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_4nums']/r1['total']*100, r2['hit_4nums']/r2['total']*100, r2['hit_4nums']/r2['total']*100 - r1['hit_4nums']/r1['total']*100))
print('| 两个和值尾 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_2tails']/r1['total']*100, r2['hit_2tails']/r2['total']*100, r2['hit_2tails']/r2['total']*100 - r1['hit_2tails']/r1['total']*100))
print('| 至少一个 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_either']/r1['total']*100, r2['hit_either']/r2['total']*100, r2['hit_either']/r2['total']*100 - r1['hit_either']/r1['total']*100))

print()
if r2['hit_5nums']/r2['total'] > r1['hit_5nums']/r1['total']:
    print('两码转万四有效！')
else:
    print('两码转万四效果不佳')

print()
print('='*70)