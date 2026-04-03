#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三招新方法测试
1. π乘法定胆术
2. 冷号休假规律
3. 百位杀码公式
"""

import pandas as pd
from collections import Counter
import random
import math

print('='*70)
print('三招新方法测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 第一招：π乘法定胆术
# ============================================================
def pi_method(last_nums):
    """
    π乘法定胆：
    上期号码当成三位数 × 3.14，取前三位
    """
    # 组成三位数
    num = last_nums[0] * 100 + last_nums[1] * 10 + last_nums[2]
    
    # 乘以π
    result = num * math.pi
    
    # 取前三位数字
    result_str = str(int(result * 100))[:3]
    
    danma = [int(d) for d in result_str]
    
    return danma

print('\n测试π乘法定胆准确率...')

pi_correct = 0
pi_total = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    danma = pi_method(last_nums)
    
    # 检查至少命中1个
    if any(d in real for d in danma):
        pi_correct += 1
    pi_total += 1

print('π乘法定胆（至少1个）: %.2f%% (%d/%d)' % (pi_correct/pi_total*100, pi_correct, pi_total))

# 检查命中2个
pi_2correct = 0
for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    danma = pi_method(last_nums)
    
    hit_count = sum(1 for d in danma if d in real)
    if hit_count >= 2:
        pi_2correct += 1

print('π乘法定胆（至少2个）: %.2f%% (%d/%d)' % (pi_2correct/pi_total*100, pi_2correct, pi_total))

# ============================================================
# 第二招：冷号休假规律
# ============================================================
def get_cold_number(df_train, lookback=30):
    """获取最冷号码（遗漏最多的）"""
    counter = Counter()
    for _, row in df_train.tail(lookback).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        for d in set(nums):
            counter[d] += 1
    
    # 找遗漏最多的
    all_nums = set(range(10))
    appeared = set(counter.keys())
    not_appeared = all_nums - appeared
    
    if not_appeared:
        # 完全没出现的，取第一个
        return list(not_appeared)[0]
    else:
        # 都出现过，取最少的
        return counter.most_common()[-1][0]

print('\n测试冷号休假规律...')

# 测试：冷号出现后的规律
leng_law_correct = {0: 0, 1: 0, 2: 0, 3: 0}  # 隔0期、1期、2期、3期

for i in range(100, min(3100, len(df) - 600)):
    # 找冷号
    df_train = df.iloc[max(0, i-30):i]
    cold_num = get_cold_number(df_train)
    
    # 检查本期是否开出冷号
    real = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    if cold_num in real:
        # 冷号出现了，检查后续
        for gap in range(1, 5):
            if i + gap < len(df):
                future = [int(df.iloc[i+gap]['num1']), int(df.iloc[i+gap]['num2']), int(df.iloc[i+gap]['num3'])]
                if cold_num in future:
                    leng_law_correct[gap-1] += 1
                    break

print('冷号隔1期再出: %d次' % leng_law_correct[0])
print('冷号隔2期再出: %d次' % leng_law_correct[1])
print('冷号隔3期再出: %d次' % leng_law_correct[2])
print('冷号隔4期再出: %d次' % leng_law_correct[3])

# ============================================================
# 第三招：百位杀码公式
# ============================================================
def kill_baiwei(last_nums):
    """
    百位杀码公式：
    上期百位 × 3 + 3，取个位
    """
    bai = last_nums[0]
    kill = (bai * 3 + 3) % 10
    return kill

print('\n测试百位杀码公式准确率...')

kill_correct = 0
kill_total = 0

for i in range(100, min(3100, len(df) - 600)):
    last_nums = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real_bai = int(df.iloc[i]['num1'])
    
    kill = kill_baiwei(last_nums)
    
    if real_bai != kill:
        kill_correct += 1
    kill_total += 1

print('百位杀码准确率: %.2f%% (%d/%d)' % (kill_correct/kill_total*100, kill_correct, kill_total))

# ============================================================
# 综合测试
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

def predict_with_3methods(df_train):
    """加入三招新方法"""
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
    
    # 三招新方法
    # 1. π乘法定胆
    danma = pi_method(last_nums)
    for d in danma:
        scores[d] += 3
    
    # 2. 冷号休假规律
    cold = get_cold_number(df_train)
    # 检查冷号是否刚出现（如果是，则不加分）
    cold_just_appeared = cold in last_nums
    if not cold_just_appeared:
        scores[cold] += 2
    
    # 3. 百位杀码（杀掉得分降低）
    kill_bai = kill_baiwei(last_nums)
    scores[kill_bai] -= 2
    
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

print('\n测试+三招新方法...')
r2 = test_predict(predict_with_3methods)
print('完成')

print()
print('='*70)
print('对比结果')
print('='*70)
print()
print('| 指标 | 当前方法 | +三招新方法 | 提升 |')
print('|------|---------|------------|------|')
print('| 五码命中率 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_5nums']/r1['total']*100, r2['hit_5nums']/r2['total']*100, r2['hit_5nums']/r2['total']*100 - r1['hit_5nums']/r1['total']*100))
print('| 四注号码 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_4nums']/r1['total']*100, r2['hit_4nums']/r2['total']*100, r2['hit_4nums']/r2['total']*100 - r1['hit_4nums']/r1['total']*100))
print('| 两个和值尾 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_2tails']/r1['total']*100, r2['hit_2tails']/r2['total']*100, r2['hit_2tails']/r2['total']*100 - r1['hit_2tails']/r1['total']*100))
print('| 至少一个 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_either']/r1['total']*100, r2['hit_either']/r2['total']*100, r2['hit_either']/r2['total']*100 - r1['hit_either']/r1['total']*100))

print()
if r2['hit_5nums']/r2['total'] > r1['hit_5nums']/r1['total']:
    print('三招新方法有效！')
else:
    print('三招新方法效果不佳')

print()
print('='*70)