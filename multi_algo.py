#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多算法交叉验证系统 V7 - 优化版（50%马尔可夫+50%随机）"""

import pandas as pd
import random
from collections import Counter, defaultdict
from datetime import datetime
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

print('='*60)
print('多算法交叉验证系统 V7 - 优化版')
print('='*60)

pl3 = pd.read_csv('pl3_full.csv')
fc3d = pd.read_csv('fc3d_5years.csv')

print('\n【上期开奖】')
pl3_last = (int(pl3.iloc[0]['num1']), int(pl3.iloc[0]['num2']), int(pl3.iloc[0]['num3']))
fc3d_last = (int(fc3d.iloc[0]['num1']), int(fc3d.iloc[0]['num2']), int(fc3d.iloc[0]['num3']))
print('排列三：%s' % ''.join(map(str, pl3_last)))
print('3D：%s' % ''.join(map(str, fc3d_last)))

def build_markov3(df):
    matrices = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tolist()
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        for i in range(len(nums) - 3):
            key = (nums[i], nums[i+1], nums[i+2])
            trans[key][nums[i+3]] += 1
            totals[key] += 1
        matrix = {}
        for k in totals:
            matrix[k] = {d: (trans[k].get(d, 0) + 0.01) / totals[k] for d in range(10)}
        default = {d: 0.1 for d in range(10)}
        matrices.append((matrix, default))
    return matrices

def markov_predict(markov3, history, pos):
    matrix, default = markov3[pos]
    if len(history) >= 3:
        key = (history[-3][pos], history[-2][pos], history[-1][pos])
    elif len(history) >= 2:
        key = (history[-2][pos], history[-1][pos], 5)
    elif len(history) >= 1:
        key = (history[-1][pos], 5, 5)
    else:
        key = (5, 5, 5)
    return matrix.get(key, default)

def analyze(name, df, last_nums):
    print('\n' + '='*50)
    print('%s 分析' % name)
    print('='*50)
    
    history = [last_nums]
    
    print('\n[1] 构建马尔可夫矩阵...')
    markov3 = build_markov3(df)
    
    print('\n[2] 计算胆码...')
    all_probs = defaultdict(float)
    for pos in range(3):
        probs = markov_predict(markov3, history, pos)
        for d, p in probs.items():
            all_probs[d] += p
    
    sorted_digits = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
    gold_dan = sorted_digits[0][0]
    silver_dan = sorted_digits[1][0]
    print('  金胆: %d' % gold_dan)
    print('  银胆: %d' % silver_dan)
    
    double_dan = ['%d%d' % (gold_dan, silver_dan), '%d%d' % (silver_dan, gold_dan)]
    print('  双胆: %s' % ', '.join(double_dan))
    
    # 生成候选：50%马尔可夫 + 50%随机
    print('\n[3] 生成候选号码（马尔可夫50%+随机50%）...')
    random.seed(42)
    candidates = []
    
    # 50% 马尔可夫生成
    for _ in range(500):
        nums = []
        for pos in range(3):
            probs = markov_predict(markov3, history, pos)
            digit = random.choices(range(10), weights=[probs.get(d, 0.1) for d in range(10)])[0]
            nums.append(digit)
        candidates.append(tuple(nums))
    
    # 50% 纯随机
    for _ in range(500):
        nums = tuple(random.randint(0, 9) for _ in range(3))
        candidates.append(nums)
    
    candidates = list(set(candidates))
    
    # 评分（优先使用马尔可夫概率）
    def score(nums_tuple):
        s = 0
        for pos in range(3):
            probs = markov_predict(markov3, history, pos)
            s += probs.get(nums_tuple[pos], 0.01) * 100
        return min(s, 100)
    
    candidates.sort(key=lambda x: score(x), reverse=True)
    top5 = candidates[:5]
    
    # 确保精选包含金胆或银胆
    print('\n[4] 筛选确保包含胆码...')
    gold_included = [n for n in candidates if gold_dan in n or silver_dan in n]
    if len(gold_included) >= 5:
        gold_included.sort(key=lambda x: score(x), reverse=True)
        top5 = gold_included[:5]
    
    print('\n[5] 最终推荐')
    print('-'*40)
    print('精选2注:')
    for i, nums in enumerate(top5[:2], 1):
        has_gold = '★' if gold_dan in nums else ''
        has_silver = '☆' if silver_dan in nums else ''
        print('  %d. %s (和:%d) %s%s' % (i, ''.join(map(str, nums)), sum(nums), has_gold, has_silver))
    
    print('\n备选3注:')
    for i, nums in enumerate(top5[2:5], 1):
        has_gold = '★' if gold_dan in nums else ''
        has_silver = '☆' if silver_dan in nums else ''
        print('  %d. %s (和:%d) %s%s' % (i, ''.join(map(str, nums)), sum(nums), has_gold, has_silver))
    
    # 和值热号
    sums = Counter(df.head(100)['和值'].astype(int).tolist())
    hot_sums = [s for s, c in sums.most_common(5)]
    print('\n热和值: %s' % hot_sums[:3])
    
    return {
        'gold_dan': gold_dan,
        'silver_dan': silver_dan,
        'double_dan': double_dan,
        'selected_2': [''.join(map(str, n)) for n in top5[:2]],
        'backup_3': [''.join(map(str, n)) for n in top5[2:5]],
        'key_sum': hot_sums[:3]
    }

pl3_result = analyze('排列三', pl3, pl3_last)
fc3d_result = analyze('3D', fc3d, fc3d_last)

base = datetime(2026, 1, 1)
today = datetime.now()
period = '2026%d' % ((today - base).days + 1)

result = {
    'date': today.strftime('%Y-%m-%d'),
    'period': period,
    'generated_at': today.isoformat(),
    'algorithm': 'Multi-Algo V7-Optimized',
    'weights': {'markov': 50, 'random': 50},
    'last_draw': {
        'pl3': ''.join(map(str, pl3_last)),
        'fc3d': ''.join(map(str, fc3d_last))
    },
    'pl3': pl3_result,
    'fc3d': fc3d_result
}

with open('today_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n' + '='*60)
print('结果已保存到 today_result.json')
print('='*60)
