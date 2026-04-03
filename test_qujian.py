#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
区间划分分析法测试
"""

import pandas as pd
from collections import Counter
import random

print('='*70)
print('区间划分分析法测试')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 区间划分
# ============================================================
# 标准大中小三区
XIAO_QU = [0, 1, 2]
ZHONG_QU = [3, 4, 5, 6]
DA_QU = [7, 8, 9]

# 首尾对调分区
A_QU = [1, 2, 9]
B_QU = [3, 4, 5, 6]
C_QU = [0, 7, 8]

# 隔3对调分区
D_QU = [0, 1, 5]
E_QU = [2, 3, 6, 7]
F_QU = [4, 8, 9]

def get_qujian(num):
    """获取区间"""
    if num in XIAO_QU:
        return '小'
    elif num in ZHONG_QU:
        return '中'
    else:
        return '大'

def predict_qujian(df_train):
    """
    区间划分预测：
    1. 统计各区间的出号频率
    2. 检测断区回补
    3. 预测下期区间分布
    """
    scores = {d: 0 for d in range(10)}
    
    if len(df_train) < 10:
        return scores
    
    # 统计近10期区间分布
    qujian_list = []
    for _, row in df_train.tail(10).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        qujian_list.append([get_qujian(n) for n in nums])
    
    # 统计各区出现次数
    all_qu = []
    for qj in qujian_list:
        all_qu.extend(qj)
    
    qu_counter = Counter(all_qu)
    
    # 检测断区
    # 连续3期某区断区，下期回补概率72%
    last3_qu = []
    for i in range(-3, 0):
        nums = [int(df_train.iloc[i]['num1']), int(df_train.iloc[i]['num2']), int(df_train.iloc[i]['num3'])]
        last3_qu.append([get_qujian(n) for n in nums])
    
    # 统计每区在近3期的出现情况
    qu_appear = {'小': 0, '中': 0, '大': 0}
    for qj in last3_qu:
        for q in qj:
            qu_appear[q] += 1
    
    # 如果某区近3期出现很少，给该区数字加分
    for qu_name, count in qu_appear.items():
        if count <= 1:  # 近3期只出现1次或0次
            if qu_name == '小':
                for d in XIAO_QU:
                    scores[d] += 3
            elif qu_name == '中':
                for d in ZHONG_QU:
                    scores[d] += 3
            else:
                for d in DA_QU:
                    scores[d] += 3
    
    # 三区均衡出号（组六主流）
    # 给各区的热号加分
    if qu_counter['小'] < qu_counter['中'] and qu_counter['小'] < qu_counter['大']:
        for d in XIAO_QU:
            scores[d] += 2
    if qu_counter['中'] < qu_counter['小'] and qu_counter['中'] < qu_counter['大']:
        for d in ZHONG_QU:
            scores[d] += 2
    if qu_counter['大'] < qu_counter['小'] and qu_counter['大'] < qu_counter['中']:
        for d in DA_QU:
            scores[d] += 2
    
    return scores

# ============================================================
# 测试区间规律
# ============================================================
print('\n测试区间规律...')

# 统计三区各出1枚的情况
three_qu_hit = 0
total_count = 0

for i in range(100, min(3100, len(df) - 600)):
    nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
    
    # 检查是否组六
    if len(set(nums)) == 3:
        total_count += 1
        # 检查三区各出1枚
        qu_set = set([get_qujian(n) for n in nums])
        if len(qu_set) == 3:  # 三个区都有
            three_qu_hit += 1

print('组六三区均衡出号: %.2f%% (%d/%d)' % (three_qu_hit/total_count*100, three_qu_hit, total_count))

# 检测断区回补
duanqu_huibu = 0
duanqu_total = 0

for i in range(10, min(3100, len(df) - 600)):
    # 检查近3期是否有某区断区
    qu_appear = {'小': 0, '中': 0, '大': 0}
    for j in range(i-3, i):
        nums = [int(df.iloc[j]['num1']), int(df.iloc[j]['num2']), int(df.iloc[j]['num3'])]
        for n in nums:
            qu_appear[get_qujian(n)] += 1
    
    # 如果某区近3期出现0次
    duan_qu = [q for q, c in qu_appear.items() if c == 0]
    
    if duan_qu:
        duanqu_total += 1
        # 检查本期是否回补
        curr_nums = [int(df.iloc[i]['num1']), int(df.iloc[i]['num2']), int(df.iloc[i]['num3'])]
        curr_qu = [get_qujian(n) for n in curr_nums]
        
        if any(q in curr_qu for q in duan_qu):
            duanqu_huibu += 1

print('断区回补概率: %.2f%% (%d/%d)' % (duanqu_huibu/duanqu_total*100 if duanqu_total > 0 else 0, duanqu_huibu, duanqu_total))

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

def get_daxiao(num):
    return '大' if num >= 5 else '小'

def get_danshuang(num):
    return '单' if num % 2 == 1 else '双'

def get_zhengfu(n1, n2):
    if n2 > n1:
        return '正'
    elif n2 < n1:
        return '负'
    else:
        return '平'

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
    
    # 大小单双+正负组合
    daxiao_patterns = []
    danshuang_patterns = []
    zhengfu_patterns = []
    
    for _, row in df_train.tail(10).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        daxiao_patterns.append(''.join([get_daxiao(n) for n in nums]))
        danshuang_patterns.append(''.join([get_danshuang(n) for n in nums]))
        zhengfu_patterns.append(get_zhengfu(nums[0], nums[1]) + get_zhengfu(nums[1], nums[2]))
    
    last_daxiao = ''.join([get_daxiao(n) for n in last_nums])
    last_danshuang = ''.join([get_danshuang(n) for n in last_nums])
    
    daxiao_counter = Counter(''.join(daxiao_patterns))
    if daxiao_counter['大'] > daxiao_counter['小']:
        for d in [5, 6, 7, 8, 9]:
            scores[d] += 1
    else:
        for d in [0, 1, 2, 3, 4]:
            scores[d] += 1
    
    danshuang_counter = Counter(''.join(danshuang_patterns))
    if danshuang_counter['单'] > danshuang_counter['双']:
        for d in [0, 2, 4, 6, 8]:
            scores[d] += 1
    else:
        for d in [1, 3, 5, 7, 9]:
            scores[d] += 1
    
    sorted_nums = [n for n, s in sorted(scores.items(), key=lambda x:x[1], reverse=True)]
    hot_tails = [n for n, c in sum_count.most_common(2)]
    
    return sorted_nums, hot_tails

def predict_with_qujian(df_train):
    """加入区间划分"""
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
    
    # 大小单双+正负组合
    daxiao_patterns = []
    danshuang_patterns = []
    for _, row in df_train.tail(10).iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        daxiao_patterns.append(''.join([get_daxiao(n) for n in nums]))
        danshuang_patterns.append(''.join([get_danshuang(n) for n in nums]))
    
    daxiao_counter = Counter(''.join(daxiao_patterns))
    if daxiao_counter['大'] > daxiao_counter['小']:
        for d in [5, 6, 7, 8, 9]:
            scores[d] += 1
    else:
        for d in [0, 1, 2, 3, 4]:
            scores[d] += 1
    
    danshuang_counter = Counter(''.join(danshuang_patterns))
    if danshuang_counter['单'] > danshuang_counter['双']:
        for d in [0, 2, 4, 6, 8]:
            scores[d] += 1
    else:
        for d in [1, 3, 5, 7, 9]:
            scores[d] += 1
    
    # 区间划分
    for d, s in predict_qujian(df_train).items():
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

print('\n测试+区间划分...')
r2 = test_predict(predict_with_qujian)
print('完成')

print()
print('='*70)
print('对比结果')
print('='*70)
print()
print('| 指标 | 当前方法 | +区间划分 | 提升 |')
print('|------|---------|----------|------|')
print('| 五码命中率 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_5nums']/r1['total']*100, r2['hit_5nums']/r2['total']*100, r2['hit_5nums']/r2['total']*100 - r1['hit_5nums']/r1['total']*100))
print('| 四注号码 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_4nums']/r1['total']*100, r2['hit_4nums']/r2['total']*100, r2['hit_4nums']/r2['total']*100 - r1['hit_4nums']/r1['total']*100))
print('| 两个和值尾 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_2tails']/r1['total']*100, r2['hit_2tails']/r2['total']*100, r2['hit_2tails']/r2['total']*100 - r1['hit_2tails']/r1['total']*100))
print('| 至少一个 | %.2f%% | %.2f%% | %+.2f%% |' % (r1['hit_either']/r1['total']*100, r2['hit_either']/r2['total']*100, r2['hit_either']/r2['total']*100 - r1['hit_either']/r1['total']*100))

print()
if r2['hit_5nums']/r2['total'] > r1['hit_5nums']/r1['total']:
    print('区间划分有效！')
else:
    print('区间划分效果不佳')

print()
print('='*70)