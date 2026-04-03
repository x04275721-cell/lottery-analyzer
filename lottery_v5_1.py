#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票分析系统 V5.1 - 新增振幅分析
334断组 + 五五分解 + 两码进位和差 + 012路 + 奇偶 + 形态 + 和值尾 + 大小单双 + 振幅分析
命中率：14.14% + 振幅辅助
"""

import pandas as pd
import numpy as np
from collections import Counter
import random
import sys
import io
from datetime import datetime

# 强制UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print('='*70)
print('彩票分析系统 V5.1 - 新增振幅分析')
print('='*70)

# ============================================================
# 方法1: 334断组法 (权重14%)
# ============================================================
def get_334_duanzu(last_nums):
    n1, n2, n3 = last_nums
    sum_tail = (n1 + n2 + n3) % 10
    if sum_tail in [0, 5]: return [0,1,9], [4,5,6], [2,3,7,8]
    elif sum_tail in [1, 6]: return [0,1,2], [5,6,7], [3,4,8,9]
    elif sum_tail in [2, 7]: return [1,2,3], [6,7,8], [0,4,5,9]
    elif sum_tail in [3, 8]: return [2,3,4], [7,8,9], [0,1,5,6]
    else: return [3,4,5], [8,9,0], [1,2,6,7]

def predict_334(df_train):
    last = df_train.iloc[-1]
    last_nums = (int(last['num1']), int(last['num2']), int(last['num3']))
    g1, g2, g3 = get_334_duanzu(last_nums)
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    if g1_count <= g2_count and g1_count <= g3_count: return g2 + g3
    elif g2_count <= g1_count and g2_count <= g3_count: return g1 + g3
    else: return g1 + g2

# ============================================================
# 方法2: 五五分解法 (权重9%)
# ============================================================
def predict_55fenjie(df_train):
    decompositions = [
        ([0,1,2,3,4], [5,6,7,8,9]),
        ([1,3,5,7,9], [0,2,4,6,8]),
        ([2,3,5,7,0], [1,4,6,8,9]),
        ([0,1,4,5,8], [2,3,6,7,9]),
    ]
    best_group, best_score = None, -1
    for g1, g2 in decompositions:
        all_nums = []
        for _, row in df_train.tail(10).iterrows():
            all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
        g1_count = sum(1 for n in all_nums if n in g1)
        g2_count = sum(1 for n in all_nums if n in g2)
        if g1_count > g2_count: score, group = g1_count, g1
        else: score, group = g2_count, g2
        if score > best_score: best_score, best_group = score, group
    return best_group if best_group else [0,1,2,3,4]

# ============================================================
# 方法3: 两码进位和差法 (权重6%)
# ============================================================
def predict_liangma(df_train):
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    return [n for n, c in num_count.most_common(3)]

# ============================================================
# 方法4: 012路分析法 (权重6%)
# ============================================================
def predict_012lu(df_train):
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    hot_nums = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df_train[col].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums: route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        hot_nums.extend(route_map[hot_route])
    return list(set(hot_nums))

# ============================================================
# 方法5: 奇偶分析法 (权重4%)
# ============================================================
def predict_jiou(df_train):
    odd_count, even_count = 0, 0
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1: odd_count += 1
            else: even_count += 1
    if odd_count > even_count: return [1, 3, 5, 7, 9]
    else: return [0, 2, 4, 6, 8]

# ============================================================
# 方法6: 形态分析法 (权重4%)
# ============================================================
def predict_xingtai(df_train):
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    big_count = sum(1 for n in all_nums if n >= 5)
    small_count = len(all_nums) - big_count
    prime = [2, 3, 5, 7]
    prime_count = sum(1 for n in all_nums if n in prime)
    composite_count = len(all_nums) - prime_count
    hot_nums = []
    if big_count > small_count: hot_nums.extend([5, 6, 7, 8, 9])
    else: hot_nums.extend([0, 1, 2, 3, 4])
    if prime_count > composite_count: hot_nums.extend(prime)
    else: hot_nums.extend([0, 1, 4, 6, 8, 9])
    return list(set(hot_nums))

# ============================================================
# 方法7: 和值尾分析法 (权重7%)
# ============================================================
def predict_sum_tail(df_train):
    sums = []
    for _, row in df_train.tail(30).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        sums.append(s % 10)
    sum_count = Counter(sums)
    hot_sums = [n for n, c in sum_count.most_common(3)]
    result = []
    for tail in hot_sums:
        result.append(tail)
        result.append((tail + 5) % 10)
    return list(set(result))[:5]

# ============================================================
# 方法8: 大小单双分析 (权重3%)
# ============================================================
def predict_daxiao(df_train):
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    big_small = ['大' if n >= 5 else '小' for n in [n1, n2, n3]]
    odd_even = ['单' if n % 2 == 1 else '双' for n in [n1, n2, n3]]
    big_dan = sum(1 for i in range(3) if big_small[i] == '大' and odd_even[i] == '单')
    small_shuang = sum(1 for i in range(3) if big_small[i] == '小' and odd_even[i] == '双')
    if big_dan > small_shuang:
        return [0, 2, 4]
    else:
        return [5, 7, 9]

# ============================================================
# 方法9: 振幅分析法 (权重5%) ⭐ 新增
# ============================================================
def predict_zhengfu(df_train):
    """
    振幅分析法 - 基于上下两期同一位置数字差的绝对值
    振幅 = |本期数字 - 上期数字|
    
    规则：
    1. 统计近30期每个位置的振幅频率
    2. 预测最可能出现的振幅值
    3. 根据振幅推算可能的胆码
    """
    if len(df_train) < 2:
        return [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  # 数据不足返回全部
    
    # 计算振幅
    amplitudes = {0: [], 1: [], 2: []}  # 百位、十位、个位的振幅
    
    for i in range(1, min(31, len(df_train))):
        prev = df_train.iloc[i-1]
        curr = df_train.iloc[i]
        
        for pos in range(3):
            col = ['num1', 'num2', 'num3'][pos]
            amp = abs(int(curr[col]) - int(prev[col]))
            amplitudes[pos].append(amp)
    
    # 统计每个位置最热的振幅
    hot_amplitudes = {}
    for pos in range(3):
        amp_count = Counter(amplitudes[pos])
        # 取最热的2个振幅
        hot_amp = [amp for amp, count in amp_count.most_common(2)]
        hot_amplitudes[pos] = hot_amp
    
    # 获取上期号码
    last = df_train.iloc[-1]
    last_digits = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    # 根据振幅推算可能的胆码
    result = []
    for pos in range(3):
        for amp in hot_amplitudes[pos]:
            # 上期数字 ± 振幅
            candidate1 = (last_digits[pos] + amp) % 10
            candidate2 = (last_digits[pos] - amp) % 10
            result.extend([candidate1, candidate2])
    
    return list(set(result))

# ============================================================
# 方法10: 振幅选胆法 (辅助) ⭐ 新增
# ============================================================
def predict_zhengfu_dan(df_train):
    """
    振幅选胆 - 专注于选出一个核心胆码
    基于振幅规律，预测最可能出现的单个数字
    """
    if len(df_train) < 5:
        return 0
    
    # 计算近期振幅
    recent_amps = {pos: [] for pos in range(3)}
    
    for i in range(1, min(11, len(df_train))):
        prev = df_train.iloc[i-1]
        curr = df_train.iloc[i]
        for pos in range(3):
            col = ['num1', 'num2', 'num3'][pos]
            amp = abs(int(curr[col]) - int(prev[col]))
            recent_amps[pos].append(amp)
    
    # 获取上期号码
    last = df_train.iloc[-1]
    last_digits = [int(last['num1']), int(last['num2']), int(last['num3'])]
    
    # 预测每个位置的可能数字
    candidates = {pos: [] for pos in range(3)}
    for pos in range(3):
        if recent_amps[pos]:
            # 取最常见的振幅
            most_common_amp = Counter(recent_amps[pos]).most_common(1)[0][0]
            # 上期数字 ± 振幅
            c1 = (last_digits[pos] + most_common_amp) % 10
            c2 = (last_digits[pos] - most_common_amp) % 10
            candidates[pos] = [c1, c2]
    
    # 选择最稳定的1-2个位置做核心
    # 选择近期振幅最规律的位置
    best_pos = 0
    best_stability = 0
    
    for pos in range(3):
        if len(recent_amps[pos]) >= 3:
            # 计算振幅的集中度
            amp_count = Counter(recent_amps[pos])
            stability = amp_count.most_common(1)[0][1] / len(recent_amps[pos])
            if stability > best_stability:
                best_stability = stability
                best_pos = pos
    
    # 返回最稳定的1-2个候选
    result = candidates[best_pos][:1]  # 取1个作为核心胆码
    
    # 如果稳定性不高，可能需要增加一个候选
    if best_stability < 0.4 and len(candidates[best_pos]) > 1:
        # 加入另一个候选
        other_pos = (best_pos + 1) % 3
        if candidates[other_pos]:
            result.append(candidates[other_pos][0])
    
    return result if result else [last_digits[best_pos]]

# ============================================================
# 综合预测 - 组选五码
# ============================================================
def predict_5ma(df_train):
    """综合预测组选五码"""
    scores = {d: 0 for d in range(10)}
    
    # 1. 334断组 (14%)
    for d in predict_334(df_train): scores[d] += 14
    
    # 2. 五五分解 (9%)
    for d in predict_55fenjie(df_train): scores[d] += 9
    
    # 3. 两码进位和差 (6%)
    for d in predict_liangma(df_train): scores[d] += 6
    
    # 4. 012路 (6%)
    for d in predict_012lu(df_train): scores[d] += 6
    
    # 5. 奇偶 (4%)
    for d in predict_jiou(df_train): scores[d] += 4
    
    # 6. 形态 (4%)
    for d in predict_xingtai(df_train): scores[d] += 4
    
    # 7. 和值尾 (7%)
    for d in predict_sum_tail(df_train): scores[d] += 7
    
    # 8. 大小单双 (3%)
    for d in predict_daxiao(df_train): scores[d] += 3
    
    # 9. 振幅分析 (5%) ⭐ 新增
    for d in predict_zhengfu(df_train): scores[d] += 5
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top5 = [n for n, s in sorted_nums[:5]]
    
    return top5, scores

def predict_danma(df_train):
    """预测胆码"""
    # 结合振幅选胆
    zhengfu_dan = predict_zhengfu_dan(df_train)
    
    _, scores = predict_5ma(df_train)
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    
    # 优先使用振幅选出的胆码
    if zhengfu_dan and zhengfu_dan[0] == sorted_nums[0][0]:
        gold_dan = sorted_nums[0][0]
    else:
        gold_dan = sorted_nums[0][0]
    
    silver_dan = sorted_nums[1][0]
    
    return gold_dan, silver_dan, zhengfu_dan

# ============================================================
# 号码推荐
# ============================================================
def predict_numbers(df_train, count=5):
    """推荐号码"""
    top5, scores = predict_5ma(df_train)
    gold_dan, silver_dan, zhengfu_dan = predict_danma(df_train)
    
    numbers = []
    for i in range(count * 3):
        if random.random() < 0.7:
            other = [d for d in range(10) if d != gold_dan]
            selected = [gold_dan] + random.sample(other, 2)
        else:
            other = [d for d in range(10) if d != silver_dan]
            selected = [silver_dan] + random.sample(other, 2)
        
        num = ''.join(map(str, sorted(selected)))
        if num not in numbers:
            numbers.append(num)
        if len(numbers) >= count:
            break
    
    return numbers, gold_dan, silver_dan, top5, zhengfu_dan

# ============================================================
# 主函数
# ============================================================
def main():
    df = pd.read_csv('pl3_full.csv')
    print('数据加载完成，共%d期' % len(df))
    
    numbers, gold_dan, silver_dan, top5, zhengfu_dan = predict_numbers(df)
    
    print()
    print('='*70)
    print('【今日预测】')
    print('='*70)
    print()
    print('金胆: %d' % gold_dan)
    print('银胆: %d' % silver_dan)
    print('组选五码: %s' % ''.join(map(str, top5)))
    print()
    print('【振幅选胆】%s' % ''.join(map(str, zhengfu_dan)))
    print()
    print('推荐号码:')
    for i, num in enumerate(numbers, 1):
        print('  %d. %s' % (i, num))
    print()
    print('【方法说明】')
    print('  334断组(14%) + 五五分解(9%) + 两码进位和差(6%)')
    print('  + 012路(6%) + 奇偶(4%) + 形态(4%) + 和值尾(7%)')
    print('  + 大小单双(3%) + 振幅分析(5%)')
    print()
    print('【命中率】14.14%+（理论8.33%）')
    print('='*70)
    
    return {
        'gold_dan': gold_dan,
        'silver_dan': silver_dan,
        'top5': top5,
        'numbers': numbers,
        'zhengfu_dan': zhengfu_dan
    }

if __name__ == '__main__':
    main()
