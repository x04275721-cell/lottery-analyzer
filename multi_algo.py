#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多算法交叉验证系统 V7.1 - 增加历史记录"""

import pandas as pd
import random
from collections import Counter, defaultdict
from datetime import datetime
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

print('='*60)
print('多算法交叉验证系统 V7.1')
print('='*60)

pl3 = pd.read_csv('pl3_full.csv')
fc3d = pd.read_csv('fc3d_5years.csv')

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

def analyze(name, df, last_nums, period_num):
    print('\n[分析] %s 第%s期' % (name, period_num))
    
    history = [last_nums]
    markov3 = build_markov3(df)
    
    # 计算胆码
    all_probs = defaultdict(float)
    for pos in range(3):
        probs = markov_predict(markov3, history, pos)
        for d, p in probs.items():
            all_probs[d] += p
    
    sorted_digits = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
    gold_dan = sorted_digits[0][0]
    silver_dan = sorted_digits[1][0]
    double_dan = ['%d%d' % (gold_dan, silver_dan), '%d%d' % (silver_dan, gold_dan)]
    
    # 生成候选
    random.seed(42)
    candidates = []
    
    for _ in range(500):
        nums = [random.choices(range(10), weights=[markov3[pos][1].get(d,0.1) for d in range(10)])[0] for pos in range(3)]
        candidates.append(tuple(nums))
    
    for _ in range(500):
        candidates.append(tuple(random.randint(0, 9) for _ in range(3)))
    
    candidates = list(set(candidates))
    
    def score(nums_tuple):
        s = 0
        for pos in range(3):
            probs = markov_predict(markov3, history, pos)
            s += probs.get(nums_tuple[pos], 0.01) * 100
        return min(s, 100)
    
    candidates.sort(key=lambda x: score(x), reverse=True)
    top5 = candidates[:5]
    
    # 确保包含胆码
    gold_included = [n for n in candidates if gold_dan in n or silver_dan in n]
    if len(gold_included) >= 5:
        gold_included.sort(key=lambda x: score(x), reverse=True)
        top5 = gold_included[:5]
    
    # 和值热号
    sums = Counter(df.head(100)['和值'].astype(int).tolist())
    hot_sums = [s for s, c in sums.most_common(5)]
    
    # 热号榜
    hot_list = []
    for col in ['num1', 'num2', 'num3']:
        counter = Counter(df.head(100)[col].astype(int).tolist())
        hot_list.append([{'num': d, 'count': c} for d, c in counter.most_common(5)])
    
    return {
        'period': period_num,
        'gold_dan': gold_dan,
        'silver_dan': silver_dan,
        'double_dan': double_dan,
        'selected_2': [''.join(map(str, n)) for n in top5[:2]],
        'backup_3': [''.join(map(str, n)) for n in top5[2:5]],
        'key_sum': hot_sums[:3],
        'hot_list': hot_list,
        'last_draw': ''.join(map(str, last_nums))
    }

# 获取上期
pl3_last = (int(pl3.iloc[0]['num1']), int(pl3.iloc[0]['num2']), int(pl3.iloc[0]['num3']))
fc3d_last = (int(fc3d.iloc[0]['num1']), int(fc3d.iloc[0]['num2']), int(fc3d.iloc[0]['num3']))

# 获取当前期号
base = datetime(2026, 1, 1)
today = datetime.now()
current_period = '2026%d' % ((today - base).days + 1)

# 分析
pl3_result = analyze('排列三', pl3, pl3_last, current_period)
fc3d_result = analyze('3D', fc3d, fc3d_last, current_period)

# 生成最终结果
result = {
    'date': today.strftime('%Y-%m-%d'),
    'period': current_period,
    'generated_at': today.isoformat(),
    'algorithm': 'Multi-Algo V7.1',
    'weights': {'markov': 50, 'random': 50},
    'last_draw': {
        'pl3': pl3_result['last_draw'],
        'fc3d': fc3d_result['last_draw']
    },
    'pl3': pl3_result,
    'fc3d': fc3d_result
}

with open('today_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('\n' + '='*60)
print('分析完成！')
print('='*60)
print('\n排列三推荐：')
print('  精选:', ', '.join(pl3_result['selected_2']))
print('  备选:', ', '.join(pl3_result['backup_3']))
print('  金胆:', pl3_result['gold_dan'], '| 银胆:', pl3_result['silver_dan'])

print('\n3D推荐：')
print('  精选:', ', '.join(fc3d_result['selected_2']))
print('  备选:', ', '.join(fc3d_result['backup_3']))
print('  金胆:', fc3d_result['gold_dan'], '| 银胆:', fc3d_result['silver_dan'])
print('\n结果已保存到 today_result.json')
