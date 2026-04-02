#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三本书完整方法实现 - 15种分析方法
1. 《彩票3D排列3综合分析方法大全》- 花生
2. 《3D战法》- 吴明
3. 《轻松玩转福彩3D》- 宁夏九门
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import random
import json

# ============================================================
# 方法1: 012路分析法
# ============================================================
def analyze_012_route(df, recent=50):
    """012路分析：按除3余数分类"""
    # 0路: 0,3,6,9  1路: 1,4,7  2路: 2,5,8
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    
    results = {}
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        recent_nums = df[col].astype(int).tail(recent).tolist()
        
        # 统计各路出现次数
        route_count = {0: 0, 1: 0, 2: 0}
        for n in recent_nums:
            route = n % 3
            route_count[route] += 1
        
        # 找出热路和冷路
        hot_route = max(route_count, key=route_count.get)
        cold_route = min(route_count, key=route_count.get)
        
        results[pos] = {
            'route_count': route_count,
            'hot_route': hot_route,
            'hot_nums': route_map[hot_route],
            'cold_route': cold_route,
            'cold_nums': route_map[cold_route]
        }
    
    return results

def get_012_route_score(nums, analysis):
    """根据012路分析打分"""
    score = 0
    for pos, n in enumerate(nums):
        route = n % 3
        if route == analysis[pos]['hot_route']:
            score += 1.5
        elif route == analysis[pos]['cold_route']:
            score -= 0.5
    return score

# ============================================================
# 方法2: 分解式杀号法
# ============================================================
def analyze_decomposition(df, recent=30):
    """分解式分析：将0-9分成两组"""
    # 常用分解式：01349 vs 25678
    group1 = [0,1,3,4,9]
    group2 = [2,5,6,7,8]
    
    results = {}
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        recent_nums = df[col].astype(int).tail(recent).tolist()
        
        # 统计两组出现比例
        g1_count = sum(1 for n in recent_nums if n in group1)
        g2_count = len(recent_nums) - g1_count
        
        # 判断哪组更热
        if g1_count > g2_count:
            hot_group = group1
            cold_group = group2
        else:
            hot_group = group2
            cold_group = group1
        
        results[pos] = {
            'hot_group': hot_group,
            'cold_group': cold_group,
            'g1_ratio': g1_count / len(recent_nums)
        }
    
    return results

def get_decomposition_score(nums, analysis):
    """根据分解式分析打分"""
    score = 0
    for pos, n in enumerate(nums):
        if n in analysis[pos]['hot_group']:
            score += 1
        else:
            score -= 0.3
    return score

# ============================================================
# 方法3: 跨度杀号法
# ============================================================
def analyze_span_kill(df):
    """跨度杀号：用上期跨度与百位数相减作为杀号"""
    last = df.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    
    # 跨度 = 最大 - 最小
    span = max(n1, n2, n3) - min(n1, n2, n3)
    
    # 杀号 = 跨度 - 百位
    kill_num = abs(span - n1) % 10
    
    return {
        'last_nums': (n1, n2, n3),
        'span': span,
        'kill_num': kill_num
    }

def get_span_kill_score(nums, analysis):
    """根据跨度杀号打分"""
    kill = analysis['kill_num']
    score = 0
    for n in nums:
        if n == kill:
            score -= 2  # 杀号扣分
    return score

# ============================================================
# 方法4: MACD技术分析
# ============================================================
def analyze_macd(df, recent=50):
    """MACD技术分析：借用股票指标"""
    results = {}
    
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tail(recent).tolist()
        
        # 计算EMA12和EMA26
        ema12 = []
        ema26 = []
        multiplier12 = 2 / (12 + 1)
        multiplier26 = 2 / (26 + 1)
        
        ema12_val = nums[0]
        ema26_val = nums[0]
        
        for n in nums:
            ema12_val = (n - ema12_val) * multiplier12 + ema12_val
            ema26_val = (n - ema26_val) * multiplier26 + ema26_val
            ema12.append(ema12_val)
            ema26.append(ema26_val)
        
        # DIF = EMA12 - EMA26
        dif = [e12 - e26 for e12, e26 in zip(ema12, ema26)]
        
        # DEA = EMA9(DIF)
        dea = []
        multiplier9 = 2 / (9 + 1)
        dea_val = dif[0]
        for d in dif:
            dea_val = (d - dea_val) * multiplier9 + dea_val
            dea.append(dea_val)
        
        # MACD = (DIF - DEA) * 2
        macd = [(d - de) * 2 for d, de in zip(dif, dea)]
        
        # 判断金叉/死叉
        if len(macd) >= 2:
            if macd[-2] < 0 and macd[-1] > 0:
                signal = 'golden_cross'  # 金叉，看涨
            elif macd[-2] > 0 and macd[-1] < 0:
                signal = 'death_cross'  # 死叉，看跌
            else:
                signal = 'hold'
        else:
            signal = 'hold'
        
        results[pos] = {
            'dif': dif[-1] if dif else 0,
            'dea': dea[-1] if dea else 0,
            'macd': macd[-1] if macd else 0,
            'signal': signal
        }
    
    return results

def get_macd_score(nums, analysis):
    """根据MACD分析打分"""
    score = 0
    for pos, n in enumerate(nums):
        sig = analysis[pos]['signal']
        if sig == 'golden_cross':
            # 金叉时，选择近期热号
            score += 0.5
        elif sig == 'death_cross':
            # 死叉时，选择冷号
            score -= 0.3
    return score

# ============================================================
# 方法5: 和值战法
# ============================================================
def analyze_sum_value(df, recent=100):
    """和值分析：统计和值出现规律"""
    sums = []
    for _, row in df.tail(recent).iterrows():
        s = int(row['num1']) + int(row['num2']) + int(row['num3'])
        sums.append(s)
    
    # 统计各和值出现次数
    sum_count = Counter(sums)
    
    # 找出热和值（出现最多的前5个）
    hot_sums = [s for s, c in sum_count.most_common(5)]
    
    # 和值区间统计
    small = sum(1 for s in sums if s <= 9)  # 小
    medium = sum(1 for s in sums if 10 <= s <= 18)  # 中
    large = sum(1 for s in sums if s >= 19)  # 大
    
    return {
        'sum_count': dict(sum_count),
        'hot_sums': hot_sums,
        'distribution': {'small': small, 'medium': medium, 'large': large},
        'recent_sums': sums[-10:]
    }

def get_sum_score(nums, analysis):
    """根据和值分析打分"""
    s = sum(nums)
    score = 0
    
    # 热和值加分
    if s in analysis['hot_sums']:
        score += 1.5
    
    # 中区和值加分
    if 10 <= s <= 18:
        score += 0.5
    
    return score

# ============================================================
# 方法6: 奇偶数战法
# ============================================================
def analyze_parity(df, recent=50):
    """奇偶分析：统计奇偶组合规律"""
    patterns = []
    for _, row in df.tail(recent).iterrows():
        n1, n2, n3 = int(row['num1']), int(row['num2']), int(row['num3'])
        pattern = ''.join(['O' if n % 2 == 1 else 'E' for n in [n1, n2, n3]])
        patterns.append(pattern)
    
    # 统计各组合出现次数
    pattern_count = Counter(patterns)
    
    # 找出热组合
    hot_patterns = [p for p, c in pattern_count.most_common(3)]
    
    return {
        'pattern_count': dict(pattern_count),
        'hot_patterns': hot_patterns,
        'recent_patterns': patterns[-10:]
    }

def get_parity_score(nums, analysis):
    """根据奇偶分析打分"""
    pattern = ''.join(['O' if n % 2 == 1 else 'E' for n in nums])
    
    if pattern in analysis['hot_patterns']:
        return 1.0
    return 0

# ============================================================
# 方法7: 除3余数战法
# ============================================================
def analyze_mod3(df, recent=50):
    """除3余数分析：统计余数组合规律"""
    patterns = []
    for _, row in df.tail(recent).iterrows():
        n1, n2, n3 = int(row['num1']), int(row['num2']), int(row['num3'])
        pattern = ''.join([str(n % 3) for n in [n1, n2, n3]])
        patterns.append(pattern)
    
    pattern_count = Counter(patterns)
    hot_patterns = [p for p, c in pattern_count.most_common(3)]
    
    return {
        'pattern_count': dict(pattern_count),
        'hot_patterns': hot_patterns
    }

def get_mod3_score(nums, analysis):
    """根据除3余数分析打分"""
    pattern = ''.join([str(n % 3) for n in nums])
    
    if pattern in analysis['hot_patterns']:
        return 1.0
    return 0

# ============================================================
# 方法8: 胆码战法
# ============================================================
def analyze_danma(df, recent=30):
    """胆码分析：找出近期高频数字"""
    all_nums = []
    for _, row in df.tail(recent).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    num_count = Counter(all_nums)
    
    # 金胆：出现最多的数字
    gold_dan = num_count.most_common(1)[0][0]
    
    # 银胆：出现第2、3多的数字
    silver_dan = [n for n, c in num_count.most_common(3)[1:]]
    
    return {
        'num_count': dict(num_count),
        'gold_dan': gold_dan,
        'silver_dan': silver_dan
    }

def get_danma_score(nums, analysis):
    """根据胆码分析打分"""
    score = 0
    
    if analysis['gold_dan'] in nums:
        score += 2.0
    
    for sd in analysis['silver_dan']:
        if sd in nums:
            score += 1.0
    
    return score

# ============================================================
# 方法9: 倍投技巧（资金管理）
# ============================================================
def analyze_bet_strategy(df, recent=50):
    """倍投策略分析：根据连续未中次数调整"""
    # 这里返回基础信息，实际倍投需要结合资金
    return {
        'base_bet': 1,
        'max_bet': 5,
        'recent_miss': 0  # 需要外部传入
    }

# ============================================================
# 方法10: 单码分析
# ============================================================
def analyze_single_digit(df, recent=100):
    """单码分析：每个位置每个数字的出现频率"""
    results = {}
    
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tail(recent).tolist()
        
        num_count = Counter(nums)
        total = len(nums)
        
        # 计算频率
        freq = {n: num_count.get(n, 0) / total for n in range(10)}
        
        # 找出热号和冷号
        sorted_nums = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        hot_nums = [n for n, f in sorted_nums[:3]]
        cold_nums = [n for n, f in sorted_nums[-3:]]
        
        results[pos] = {
            'freq': freq,
            'hot_nums': hot_nums,
            'cold_nums': cold_nums
        }
    
    return results

def get_single_digit_score(nums, analysis):
    """根据单码分析打分"""
    score = 0
    for pos, n in enumerate(nums):
        if n in analysis[pos]['hot_nums']:
            score += 1.0
        elif n in analysis[pos]['cold_nums']:
            score -= 0.5
    return score

# ============================================================
# 方法11: 九宫胆码法
# ============================================================
def analyze_jiugong(df, recent=30):
    """九宫胆码：基于九宫格的胆码分析"""
    # 九宫格排列
    # 4 9 2
    # 3 5 7
    # 8 1 6
    jiugong = {
        0: [4, 9, 2],
        1: [3, 5, 7],
        2: [8, 1, 6]
    }
    
    all_nums = []
    for _, row in df.tail(recent).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    # 统计各宫出现次数
    gong_count = {0: 0, 1: 0, 2: 0}
    for n in all_nums:
        for g, nums in jiugong.items():
            if n in nums:
                gong_count[g] += 1
                break
    
    # 找出热宫
    hot_gong = max(gong_count, key=gong_count.get)
    hot_nums = jiugong[hot_gong]
    
    return {
        'jiugong': jiugong,
        'gong_count': gong_count,
        'hot_gong': hot_gong,
        'hot_nums': hot_nums
    }

def get_jiugong_score(nums, analysis):
    """根据九宫胆码打分"""
    score = 0
    for n in nums:
        if n in analysis['hot_nums']:
            score += 1.0
    return score

# ============================================================
# 方法12: 字谜图谜法（简化版）
# ============================================================
def analyze_zimi(df, recent=20):
    """字谜图谜：基于历史规律的数字联想"""
    # 简化实现：根据上期号码推算
    last = df.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    
    # 简单规则：和值个位、跨度、差值
    sum_last = (n1 + n2 + n3) % 10
    span_last = max(n1, n2, n3) - min(n1, n2, n3)
    diff_last = abs(n1 - n2)
    
    return {
        'sum_last': sum_last,
        'span_last': span_last,
        'diff_last': diff_last,
        'suggest_nums': [sum_last, span_last, diff_last]
    }

def get_zimi_score(nums, analysis):
    """根据字谜分析打分"""
    score = 0
    for n in nums:
        if n in analysis['suggest_nums']:
            score += 0.5
    return score

# ============================================================
# 方法13: 组选选号法
# ============================================================
def analyze_zuxuan(df, recent=50):
    """组选分析：统计组选形态"""
    types = []
    for _, row in df.tail(recent).iterrows():
        n1, n2, n3 = int(row['num1']), int(row['num2']), int(row['num3'])
        if n1 == n2 == n3:
            types.append('baozi')  # 豹子
        elif n1 == n2 or n2 == n3 or n1 == n3:
            types.append('zu3')  # 组三
        else:
            types.append('zu6')  # 组六
    
    type_count = Counter(types)
    
    return {
        'type_count': dict(type_count),
        'hot_type': type_count.most_common(1)[0][0]
    }

def get_zuxuan_score(nums, analysis):
    """根据组选分析打分"""
    n1, n2, n3 = nums
    if n1 == n2 == n3:
        t = 'baozi'
    elif n1 == n2 or n2 == n3 or n1 == n3:
        t = 'zu3'
    else:
        t = 'zu6'
    
    if t == analysis['hot_type']:
        return 1.0
    return 0

# ============================================================
# 方法14: 二码法
# ============================================================
def analyze_erma(df, recent=50):
    """二码分析：统计两码组合"""
    pairs = []
    for _, row in df.tail(recent).iterrows():
        n1, n2, n3 = int(row['num1']), int(row['num2']), int(row['num3'])
        # 所有两码组合
        pairs.extend([
            tuple(sorted([n1, n2])),
            tuple(sorted([n2, n3])),
            tuple(sorted([n1, n3]))
        ])
    
    pair_count = Counter(pairs)
    hot_pairs = [p for p, c in pair_count.most_common(10)]
    
    return {
        'pair_count': dict(pair_count),
        'hot_pairs': hot_pairs
    }

def get_erma_score(nums, analysis):
    """根据二码分析打分"""
    n1, n2, n3 = nums
    pairs = [
        tuple(sorted([n1, n2])),
        tuple(sorted([n2, n3])),
        tuple(sorted([n1, n3]))
    ]
    
    score = 0
    for p in pairs:
        if p in analysis['hot_pairs']:
            score += 0.5
    
    return score

# ============================================================
# 方法15: 形态分析法
# ============================================================
def analyze_xingtai(df, recent=50):
    """形态分析：大小、质合、奇偶"""
    results = {}
    
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tail(recent).tolist()
        
        # 大小：0-4小，5-9大
        big = sum(1 for n in nums if n >= 5)
        small = len(nums) - big
        
        # 质合：质数2,3,5,7，合数0,1,4,6,8,9
        prime = sum(1 for n in nums if n in [2,3,5,7])
        composite = len(nums) - prime
        
        # 奇偶
        odd = sum(1 for n in nums if n % 2 == 1)
        even = len(nums) - odd
        
        results[pos] = {
            'big_ratio': big / len(nums),
            'prime_ratio': prime / len(nums),
            'odd_ratio': odd / len(nums)
        }
    
    return results

def get_xingtai_score(nums, analysis):
    """根据形态分析打分"""
    score = 0
    for pos, n in enumerate(nums):
        a = analysis[pos]
        # 根据比例调整分数
        if n >= 5 and a['big_ratio'] > 0.5:
            score += 0.3
        elif n < 5 and a['big_ratio'] < 0.5:
            score += 0.3
        
        if n % 2 == 1 and a['odd_ratio'] > 0.5:
            score += 0.3
        elif n % 2 == 0 and a['odd_ratio'] < 0.5:
            score += 0.3
    
    return score

# ============================================================
# 综合评分函数
# ============================================================
def comprehensive_score(nums, analyses, weights=None):
    """综合15种方法的评分"""
    if weights is None:
        # 默认权重：均等
        weights = {
            'route_012': 1.0,
            'decomposition': 1.0,
            'span_kill': 1.0,
            'macd': 1.0,
            'sum_value': 1.0,
            'parity': 1.0,
            'mod3': 1.0,
            'danma': 1.0,
            'single_digit': 1.0,
            'jiugong': 1.0,
            'zimi': 1.0,
            'zuxuan': 1.0,
            'erma': 1.0,
            'xingtai': 1.0
        }
    
    score = 0
    
    score += get_012_route_score(nums, analyses['route_012']) * weights['route_012']
    score += get_decomposition_score(nums, analyses['decomposition']) * weights['decomposition']
    score += get_span_kill_score(nums, analyses['span_kill']) * weights['span_kill']
    score += get_macd_score(nums, analyses['macd']) * weights['macd']
    score += get_sum_score(nums, analyses['sum_value']) * weights['sum_value']
    score += get_parity_score(nums, analyses['parity']) * weights['parity']
    score += get_mod3_score(nums, analyses['mod3']) * weights['mod3']
    score += get_danma_score(nums, analyses['danma']) * weights['danma']
    score += get_single_digit_score(nums, analyses['single_digit']) * weights['single_digit']
    score += get_jiugong_score(nums, analyses['jiugong']) * weights['jiugong']
    score += get_zimi_score(nums, analyses['zimi']) * weights['zimi']
    score += get_zuxuan_score(nums, analyses['zuxuan']) * weights['zuxuan']
    score += get_erma_score(nums, analyses['erma']) * weights['erma']
    score += get_xingtai_score(nums, analyses['xingtai']) * weights['xingtai']
    
    return score

def run_all_analyses(df):
    """运行所有分析"""
    return {
        'route_012': analyze_012_route(df),
        'decomposition': analyze_decomposition(df),
        'span_kill': analyze_span_kill(df),
        'macd': analyze_macd(df),
        'sum_value': analyze_sum_value(df),
        'parity': analyze_parity(df),
        'mod3': analyze_mod3(df),
        'danma': analyze_danma(df),
        'single_digit': analyze_single_digit(df),
        'jiugong': analyze_jiugong(df),
        'zimi': analyze_zimi(df),
        'zuxuan': analyze_zuxuan(df),
        'erma': analyze_erma(df),
        'xingtai': analyze_xingtai(df)
    }

print("15种分析方法已加载完成！")
