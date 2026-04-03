#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
各位极差分析法测试
"""

import pandas as pd
from collections import Counter
import random

print('='*70)
print('各位极差分析法测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 各位极差分析
# ============================================================
def get_ji_cha(last_nums, current_nums):
    """
    计算各位极差：
    百位极差 = |上期百位 - 本期百位|
    十位极差 = |上期十位 - 本期十位|
    个位极差 = |上个位 - 本个位|
    """
    bai_cha = abs(last_nums[0] - current_nums[0])
    shi_cha = abs(last_nums[1] - current_nums[1])
    ge_cha = abs(last_nums[2] - current_nums[2])
    
    return [bai_cha, shi_cha, ge_cha]

def get_012_road(num):
    """获取012路"""
    return num % 3

def predict_ji_cha(df_train):
    """
    各位极差预测：
    1. 分析近几期极差走势（顺子、同路）
    2. 预测下期极差范围
    3. 反推下期号码
    """
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 5:
        return scores
    
    # 获取近5期极差
    ji_cha_history = []
    for i in range(-5, 0):
        if i == -1:
            continue
        last_nums = [int(df_train.iloc[i-1]['num1']), int(df_train.iloc[i-1]['num2']), int(df_train.iloc[i-1]['num3'])]
        curr_nums = [int(df_train.iloc[i]['num1']), int(df_train.iloc[i]['num2']), int(df_train.iloc[i]['num3'])]
        ji_cha = get_ji_cha(last_nums, curr_nums)
        ji_cha_history.append(ji_cha)
    
    if len(ji_cha_history) < 4:
        return scores
    
    # 分析百位极差走势
    bai_cha_list = [jc[0] for jc in ji_cha_history]
    
    # 检查顺子趋势（递增或递减）
    if len(bai_cha_list) >= 3:
        last3 = bai_cha_list[-3:]
        # 递增顺子
        if last3[1] == last3[0] + 1 and last3[2] == last3[1] + 1:
            # 预测下个是last3[2]+1或反弹
            next_cha = last3[2] + 1
            if next_cha <= 9:
                # 给能形成这个极差的数字加分
                last_bai = int(df_train.iloc[-1]['num1'])
                for d in range(10):
                    if abs(last_bai - d) == next_cha:
                        scores[d] += 3
        # 递减顺子
        elif last3[1] == last3[0] - 1 and last3[2] == last3[1] - 1:
            next_cha = last3[2] - 1
            if next_cha >= 0:
                last_bai = int(df_train.iloc[-1]['num1'])
                for d in range(10):
                    if abs(last_bai - d) == next_cha:
                        scores[d] += 3
    
    # 检查同路趋势
    bai_roads = [get_012_road(c) for c in bai_cha_list[-3:]]
    if len(set(bai_roads)) == 1:
        # 连续同路，预测继续同路
        same_road = bai_roads[0]
        last_bai = int(df_train.iloc[-1]['num1'])
        for d in range(10):
            cha = abs(last_bai - d)
            if get_012_road(cha) == same_road:
                scores[d] += 2
    
    # 十位、个位同样处理
    shi_cha_list = [jc[1] for jc in ji_cha_history]
    ge_cha_list = [jc[2] for jc in ji_cha_history]
    
    # 同路分析
    shi_roads = [get_012_road(c) for c in shi_cha_list[-3:]]
    if len(set(shi_roads)) == 1:
        same_road = shi_roads[0]
        last_shi = int(df_train.iloc[-1]['num2'])
        for d in range(10):
            cha = abs(last_shi - d)
            if get_012_road(cha) == same_road:
                scores[d] += 2
    
    ge_roads = [get_012_road(c) for c in ge_cha_list[-3:]]
    if len(set(ge_roads)) == 1:
        same_road = ge_roads[0]
        last_ge = int(df_train.iloc[-1]['num3'])
        for d in range(10):
            cha = abs(last_ge - d)
            if get_012_road(cha) == same_road:
                scores[d] += 2
    
    return scores

# ============================================================
# 测试极差规律准确率
# ============================================================
print('\n测试极差规律准确率...')

# 顺子规律
shunzi_count = 0
shunzi_correct = 0

# 同路规律
tonglu_count = 0
tonglu_correct = 0

for i in range(100, min(3100, len(df) - 600)):
    # 获取近4期极差
    ji_cha_list = []
    for j in range(i-4, i):
        last_nums = [int(df.iloc[j-1]['num1']), int(df.iloc[j-1]['num2']), int(df.iloc[j-1]['num3'])]
        curr_nums = [int(df.iloc[j]['num1']), int(df.iloc[j]['num2']), int(df.iloc[j]['num3'])]
        ji_cha = get_ji_cha(last_nums, curr_nums)
        ji_cha_list.append(ji_cha)
    
    # 获取本期实际极差
    real_last = [int(df.iloc[i-1]['num1']), int(df.iloc[i-1]['num2']), int(df.iloc[i-1]['num3'])]
    real_curr = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    real_ji_cha = get_ji_cha(real_last, real_curr)
    
    # 检查百位顺子
    bai_list = [jc[0] for jc in ji_cha_list]
    if len(bai_list) >= 3:
        last3 = bai_list[-3:]
        # 检测顺子趋势
        if (last3[1] == last3[0] + 1 and last3[2] == last3[1] + 1) or \
           (last3[1] == last3[0] - 1 and last3[2] == last3[1] - 1):
            shunzi_count += 1
            # 预测延续或反弹
            if last3[1] == last3[0] + 1:
                pred = last3[2] + 1
            else:
                pred = last3[2] - 1
            
            if 0 <= pred <= 9 and real_ji_cha[0] == pred:
                shunzi_correct += 1
    
    # 检查百位同路
    bai_roads = [get_012_road(jc[0]) for jc in ji_cha_list[-3:]]
    if len(set(bai_roads)) == 1:
        tonglu_count += 1
        if get_012_road(real_ji_cha[0]) == bai_roads[0]:
            tonglu_correct += 1

print('顺子规律准确率: %.2f%% (%d/%d)' % (shunzi_correct/shunzi_count*100 if shunzi_count > 0 else 0, shunzi_correct, shunzi_count))
print('同路规律准确率: %.2f%% (%d/%d)' % (tonglu_correct/tonglu_count*100 if tonglu_count > 0 else 0, tonglu_correct, tonglu_count))

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

def predict_with_ji_cha(df_train):
    """加入极差分析"""
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
    
    # 极差分析
    for d, s in predict_ji_cha(df_train).items():
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

print('\n测试+极差分析...')
r2 = test_predict(predict_with_ji_cha)
print('完成')

print()
print('='*70)
print('对比结果')
print('='*70)
print()
print('| 指标 | 当前方法 | +极差分析 | 提升 |')
print('|------|---------|----------|------|')
print('| 五码命中率 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_5nums']/r1['total']*100, r2['hit_5nums']/r2['total']*100, r2['hit_5nums']/r2['total']*100 - r1['hit_5nums']/r1['total']*100))
print('| 四注号码 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_4nums']/r1['total']*100, r2['hit_4nums']/r2['total']*100, r2['hit_4nums']/r2['total']*100 - r1['hit_4nums']/r1['total']*100))
print('| 两个和值尾 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_2tails']/r1['total']*100, r2['hit_2tails']/r2['total']*100, r2['hit_2tails']/r2['total']*100 - r1['hit_2tails']/r1['total']*100))
print('| 至少一个 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_either']/r1['total']*100, r2['hit_either']/r2['total']*100, r2['hit_either']/r2['total']*100 - r1['hit_either']/r1['total']*100))

print()
if r2['hit_5nums']/r2['total'] > r1['hit_5nums']/r1['total']:
    print('极差分析有效！')
else:
    print('极差分析效果不佳')

print()
print('='*70)