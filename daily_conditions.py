#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日条件更新 - 7种方法单独输出
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
from datetime import datetime

print('='*70)
print('每日条件更新 - 7种方法')
print('='*70)

# 加载数据
pl3_df = pd.read_csv('pl3_full.csv')
d3_df = pd.read_csv('fc3d_5years.csv')

print('排列三数据: %d期' % len(pl3_df))
print('3D数据: %d期' % len(d3_df))

# ============================================================
# 7种方法实现
# ============================================================

def method_334_duanzu(df_train):
    """方法1: 334断组法 - 综合加权"""
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    sum_tail = (n1 + n2 + n3) % 10
    
    if sum_tail in [0, 5]: g1, g2, g3 = [0,1,9], [4,5,6], [2,3,7,8]
    elif sum_tail in [1, 6]: g1, g2, g3 = [0,1,2], [5,6,7], [3,4,8,9]
    elif sum_tail in [2, 7]: g1, g2, g3 = [1,2,3], [6,7,8], [0,4,5,9]
    elif sum_tail in [3, 8]: g1, g2, g3 = [2,3,4], [7,8,9], [0,1,5,6]
    else: g1, g2, g3 = [3,4,5], [8,9,0], [1,2,6,7]
    
    # 统计近10期各组出现次数
    all_nums = []
    for _, row in df_train.tail(10).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    g1_count = sum(1 for n in all_nums if n in g1)
    g2_count = sum(1 for n in all_nums if n in g2)
    g3_count = sum(1 for n in all_nums if n in g3)
    
    # 综合加权：按出现次数排序，热组权重高，冷组权重低但不为0
    counts = [(g1, g1_count, 1), (g2, g2_count, 2), (g3, g3_count, 3)]
    counts.sort(key=lambda x: x[1], reverse=True)  # 按次数降序
    
    hot_group = counts[0][0]  # 最热
    mid_group = counts[1][0]  # 中等
    cold_group = counts[2][0]  # 最冷
    
    # 最佳权重：热组14分，中组10分，冷组2分
    result_scores = {d: 0 for d in range(10)}
    for d in hot_group:
        result_scores[d] += 14
    for d in mid_group:
        result_scores[d] += 10
    for d in cold_group:
        result_scores[d] += 2  # 冷组保留低权重
    
    # 返回综合评分后的推荐数字
    sorted_nums = sorted(result_scores.items(), key=lambda x: x[1], reverse=True)
    top_nums = [n for n, s in sorted_nums[:7]]  # 返回7个数字
    
    return {
        'name': '334断组',
        'weight': '14%',
        'result': sorted(top_nums),
        'kill': [],
        'desc': '和值尾%d，综合加权' % sum_tail,
        'groups': {
            'group1': {'nums': g1, 'count': g1_count, 'weight': 14 if g1 == hot_group else (10 if g1 == mid_group else 2)},
            'group2': {'nums': g2, 'count': g2_count, 'weight': 14 if g2 == hot_group else (10 if g2 == mid_group else 2)},
            'group3': {'nums': g3, 'count': g3_count, 'weight': 14 if g3 == hot_group else (10 if g3 == mid_group else 2)}
        },
        'sum_tail': sum_tail,
        'scores': result_scores  # 返回评分供综合计算使用
    }

def method_55fenjie(df_train):
    """方法2: 五五分解法"""
    decompositions = [
        ('大小', [0,1,2,3,4], [5,6,7,8,9]),
        ('奇偶', [1,3,5,7,9], [0,2,4,6,8]),
        ('质合', [2,3,5,7,0], [1,4,6,8,9]),
        ('四方', [0,1,4,5,8], [2,3,6,7,9]),
    ]
    
    best_group, best_score, best_name = None, -1, ''
    
    for name, g1, g2 in decompositions:
        all_nums = []
        for _, row in df_train.tail(10).iterrows():
            all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
        
        g1_count = sum(1 for n in all_nums if n in g1)
        g2_count = sum(1 for n in all_nums if n in g2)
        
        if g1_count > g2_count:
            score, group = g1_count, g1
        else:
            score, group = g2_count, g2
        
        if score > best_score:
            best_score = score
            best_group = group
            best_name = name
    
    return {
        'name': '五五分解',
        'weight': '9%',
        'result': sorted(best_group),
        'kill': [],  # 不显示杀号
        'desc': '%s分解热组' % best_name
    }

def method_liangma(df_train):
    """方法3: 两码进位和差"""
    last = df_train.iloc[-1]
    n1, n2, n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    
    he12, he13, he23 = (n1+n2)%10, (n1+n3)%10, (n2+n3)%10
    cha12, cha13, cha23 = abs(n1-n2), abs(n1-n3), abs(n2-n3)
    jin12, jin13, jin23 = (n1+n2)//10, (n1+n3)//10, (n2+n3)//10
    
    all_nums = [he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23]
    num_count = Counter(all_nums)
    top3 = [n for n, c in num_count.most_common(3)]
    
    return {
        'name': '两码和差',
        'weight': '6%',
        'result': top3,
        'kill': [],
        'desc': '和%d%d%d 差%d%d%d 进%d%d%d' % (he12, he13, he23, cha12, cha13, cha23, jin12, jin13, jin23)
    }

def method_012lu(df_train):
    """方法4: 012路分析"""
    route_map = {0: [0,3,6,9], 1: [1,4,7], 2: [2,5,8]}
    hot_nums = []
    hot_routes = []
    
    for pos in range(3):
        nums = df_train['num%d' % (pos+1)].astype(int).tail(30).tolist()
        route_count = {0: 0, 1: 0, 2: 0}
        for n in nums:
            route_count[n % 3] += 1
        hot_route = max(route_count, key=route_count.get)
        hot_routes.append(hot_route)
        hot_nums.extend(route_map[hot_route])
    
    return {
        'name': '012路',
        'weight': '6%',
        'result': sorted(list(set(hot_nums))),
        'kill': [],
        'desc': '热路%d%d%d' % tuple(hot_routes)
    }

def method_jiou(df_train):
    """方法5: 奇偶分析 - 综合加权"""
    odd_count, even_count = 0, 0
    
    for _, row in df_train.tail(30).iterrows():
        for col in ['num1', 'num2', 'num3']:
            if int(row[col]) % 2 == 1:
                odd_count += 1
            else:
                even_count += 1
    
    # 综合加权：热类型权重高，冷类型权重低但不为0
    result_scores = {d: 0 for d in range(10)}
    
    if odd_count > even_count:
        # 奇数热：热14，冷2
        for d in [1, 3, 5, 7, 9]:
            result_scores[d] += 14
        for d in [0, 2, 4, 6, 8]:
            result_scores[d] += 2
        hot = '奇'
    else:
        # 偶数热：热14，冷2
        for d in [0, 2, 4, 6, 8]:
            result_scores[d] += 14
        for d in [1, 3, 5, 7, 9]:
            result_scores[d] += 2
        hot = '偶'
    
    # 返回所有数字的评分
    return {
        'name': '奇偶',
        'weight': '4%',
        'result': sorted([d for d, s in result_scores.items() if s >= 8]),  # 显示热类型
        'kill': [],
        'desc': '%s数过热(综合加权)' % hot,
        'scores': result_scores
    }

def method_xingtai(df_train):
    """方法6: 形态分析"""
    all_nums = []
    for _, row in df_train.tail(30).iterrows():
        all_nums.extend([int(row['num1']), int(row['num2']), int(row['num3'])])
    
    big_count = sum(1 for n in all_nums if n >= 5)
    small_count = len(all_nums) - big_count
    
    prime = [2, 3, 5, 7]
    prime_count = sum(1 for n in all_nums if n in prime)
    composite_count = len(all_nums) - prime_count
    
    hot_nums = []
    
    if big_count > small_count:
        hot_nums.extend([5, 6, 7, 8, 9])
        size_hot = '大'
    else:
        hot_nums.extend([0, 1, 2, 3, 4])
        size_hot = '小'
    
    if prime_count > composite_count:
        hot_nums.extend(prime)
        prime_hot = '质'
    else:
        hot_nums.extend([0, 1, 4, 6, 8, 9])
        prime_hot = '合'
    
    return {
        'name': '形态',
        'weight': '4%',
        'result': sorted(list(set(hot_nums))),
        'kill': [],
        'desc': '%s%s过热' % (size_hot, prime_hot)
    }

def method_sum_tail(df_train):
    """方法7: 和值尾分析"""
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
    
    return {
        'name': '和值尾',
        'weight': '7%',
        'result': sorted(list(set(result)))[:5],
        'kill': [],
        'desc': '热尾%d%d%d' % tuple(hot_sums)
    }

def is_banshun(nums):
    """判断是否为半顺（任意两个数字相邻）"""
    n1, n2, n3 = sorted(nums)
    if abs(n1-n2) == 1 or abs(n2-n3) == 1 or abs(n1-n3) == 1:
        return True
    return False

def method_banshun(df_train):
    """方法8: 半顺细分技巧（辅助方法）
    半顺开出率60.7%，平均1.6期开出1次
    热态二连码：89、90、01最热
    热态单码：8、9、0最热
    """
    # 获取近50期数据
    recent = df_train.tail(50)
    
    # 统计二连码出现次数
    consecutive_counts = Counter()
    for _, row in recent.iterrows():
        nums = sorted([int(row['num1']), int(row['num2']), int(row['num3'])])
        for i in range(3):
            for j in range(i+1, 3):
                if abs(nums[j] - nums[i]) == 1:
                    consecutive_counts[(min(nums[i], nums[j]), max(nums[i], nums[j]))] += 1
    
    # 统计含各数字的半顺次数
    digit_counts = Counter()
    for _, row in recent.iterrows():
        nums = [int(row['num1']), int(row['num2']), int(row['num3'])]
        if is_banshun(nums):
            for d in nums:
                digit_counts[d] += 1
    
    # 获取热门二连码和单码
    hot_pairs = [p[0] for p in consecutive_counts.most_common(3)]
    hot_digits = [d[0] for d in digit_counts.most_common(3)]
    
    # 构建结果
    result = list(set(hot_pairs[0] + hot_pairs[1] + hot_pairs[2] + hot_digits)) if hot_pairs or hot_digits else []
    
    # 计算半顺开出比例
    banshun_count = sum(1 for _, row in recent.iterrows() if is_banshun([int(row['num1']), int(row['num2']), int(row['num3'])]))
    banshun_rate = banshun_count / len(recent) * 100
    
    # 获取最热的二连码类型
    hot_pair_str = ''
    if consecutive_counts:
        top_pair = consecutive_counts.most_common(1)[0][0]
        hot_pair_str = '%d%d型' % (top_pair[0], top_pair[1])
    
    return {
        'name': '半顺',
        'weight': '3%',
        'result': sorted(list(set(result)))[:6] if result else list(range(10)),
        'kill': [],
        'desc': '半顺%d期出%d次(%d%%)，%s' % (len(recent), banshun_count, int(banshun_rate), hot_pair_str)
    }

# ============================================================
# 综合预测
# ============================================================
def predict_all_methods(df_train):
    """运行所有方法"""
    methods = [
        method_334_duanzu(df_train),
        method_55fenjie(df_train),
        method_liangma(df_train),
        method_012lu(df_train),
        method_jiou(df_train),
        method_xingtai(df_train),
        method_sum_tail(df_train),
        method_banshun(df_train),  # 第8种：半顺技巧
    ]
    
    # 综合评分 - 8种方法
    scores = {d: 0 for d in range(10)}
    weights = [14, 9, 6, 6, 4, 4, 7, 3]  # 半顺权重3%
    
    for i, m in enumerate(methods):
        # 如果方法返回了详细评分，使用详细评分
        if 'scores' in m and m['scores']:
            for d, s in m['scores'].items():
                scores[d] += s * weights[i] / 10  # 归一化
        else:
            # 否则使用 result 列表
            for d in m['result']:
                scores[d] += weights[i]
    
    sorted_nums = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top5 = [n for n, s in sorted_nums[:5]]
    gold_dan = sorted_nums[0][0]
    silver_dan = sorted_nums[1][0]
    
    return methods, top5, gold_dan, silver_dan

# ============================================================
# 生成每日数据
# ============================================================
def generate_daily_data():
    """生成每日数据"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 排列三
    pl3_methods, pl3_top5, pl3_gold, pl3_silver = predict_all_methods(pl3_df)
    
    # 3D
    d3_methods, d3_top5, d3_gold, d3_silver = predict_all_methods(d3_df)
    
    data = {
        'date': today,
        'pl3': {
            'methods': pl3_methods,
            'top5': pl3_top5,
            'gold_dan': pl3_gold,
            'silver_dan': pl3_silver,
            'top5_str': ''.join(map(str, pl3_top5))
        },
        'd3': {
            'methods': d3_methods,
            'top5': d3_top5,
            'gold_dan': d3_gold,
            'silver_dan': d3_silver,
            'top5_str': ''.join(map(str, d3_top5))
        }
    }
    
    # 保存
    with open('daily_conditions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print()
    print('='*70)
    print('每日条件更新 (%s)' % today)
    print('='*70)
    
    print()
    print('【排列三】')
    print('  金胆: %d | 银胆: %d | 五码: %s' % (pl3_gold, pl3_silver, ''.join(map(str, pl3_top5))))
    print()
    for m in pl3_methods:
        print('  %s (%s): %s' % (m['name'], m['weight'], ''.join(map(str, m['result']))))
        if m['kill']:
            print('    杀: %s' % ''.join(map(str, m['kill'])))
        print('    %s' % m['desc'])
    print()
    
    print('【3D】')
    print('  金胆: %d | 银胆: %d | 五码: %s' % (d3_gold, d3_silver, ''.join(map(str, d3_top5))))
    print()
    for m in d3_methods:
        print('  %s (%s): %s' % (m['name'], m['weight'], ''.join(map(str, m['result']))))
        if m['kill']:
            print('    杀: %s' % ''.join(map(str, m['kill'])))
        print('    %s' % m['desc'])
    
    print()
    print('='*70)
    print('数据已保存到 daily_conditions.json')
    print('='*70)
    
    return data

if __name__ == '__main__':
    data = generate_daily_data()
