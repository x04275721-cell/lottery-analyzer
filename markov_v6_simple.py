#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""彩票V6 - 三阶马尔可夫链 + 胆码推荐"""

import pandas as pd
from collections import Counter, defaultdict
from datetime import datetime
import json
import random
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')


def build_third_order(df):
    matrices = []
    for pos in range(3):
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tolist()
        
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        
        for i in range(len(nums) - 3):
            key = (nums[i], nums[i+1], nums[i+2])
            curr = nums[i+3]
            trans[key][curr] += 1
            totals[key] += 1
        
        matrix = {}
        for key in totals:
            matrix[key] = {d: trans[key].get(d, 0) + 0.01 for d in range(10)}
            total = sum(matrix[key].values())
            for d in matrix[key]:
                matrix[key][d] /= total
        
        if totals:
            best_key = max(totals.keys(), key=lambda k: totals[k])
            best_digit = max(range(10), key=lambda d: trans[best_key][d])
            prob = trans[best_key][best_digit] / totals[best_key]
            print(f"  位置{pos+1}最强：三连({best_key}) -> {best_digit} ({prob:.1%})")
        
        matrices.append(matrix)
    return matrices


def build_first_order(df):
    nums = list(zip(df['num1'].astype(int), df['num2'].astype(int), df['num3'].astype(int)))
    matrix = defaultdict(lambda: defaultdict(int))
    totals = defaultdict(int)
    
    for i in range(len(nums) - 1):
        for p, c in zip(nums[i], nums[i+1]):
            matrix[p][c] += 1
            totals[p] += 1
    
    result = {}
    for p in range(10):
        result[p] = {c: (matrix[p][c] / totals[p] if totals[p] > 0 else 0.01) for c in range(10)}
        total = sum(result[p].values())
        for c in result[p]:
            result[p][c] /= total
    return result


def predict_prob(markov3, markov1, history, pos):
    if len(history) >= 3:
        key = (history[-3][pos], history[-2][pos], history[-1][pos])
    elif len(history) >= 2:
        key = (history[-2][pos], history[-1][pos], 5)
    elif len(history) >= 1:
        key = (history[-1][pos], 5, 5)
    else:
        key = (5, 5, 5)
    
    probs3 = markov3[pos].get(key, {d: 0.1 for d in range(10)})
    if history:
        probs1 = markov1.get(history[-1][pos], {d: 0.1 for d in range(10)})
    else:
        probs1 = {d: 0.1 for d in range(10)}
    
    combined = {d: probs3.get(d, 0.1) * 0.6 + probs1.get(d, 0.1) * 0.4 for d in range(10)}
    total = sum(combined.values())
    for d in combined:
        combined[d] /= total
    return combined


def analyze(df, name, history):
    print(f"\n{'='*50}")
    print(f"{name}分析 (历史:{len(df)}期)")
    print(f"{'='*50}")
    
    print("\n构建马尔可夫矩阵...")
    markov3 = build_third_order(df)
    markov1 = build_first_order(df)
    
    print("\n位置热号:")
    hot = []
    for i, col in enumerate(['num1', 'num2', 'num3']):
        counter = Counter(df.head(100)[col].tolist())
        top = [d for d, c in counter.most_common(8)]
        hot.append(top)
        print(f"  {col}: {top}")
    
    sums = Counter(df.head(100)['和值'].tolist())
    hot_sums = [s for s, c in sums.most_common(8)]
    
    # 计算胆码
    print("\n胆码推荐:")
    danma = []
    for pos in range(3):
        probs = predict_prob(markov3, markov1, history, pos)
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        top_digits = [str(d) for d, p in sorted_probs[:3]]
        danma.append(top_digits)
        print(f"  位置{pos+1}: {top_digits}")
    
    # 双胆组合
    double_dan = []
    for i in range(3):
        for j in range(i+1, 3):
            for d1 in danma[i][:2]:
                for d2 in danma[j][:2]:
                    if d1 != d2:
                        double_dan.append(d1 + d2)
    double_dan = list(set(double_dan))[:5]
    print(f"双胆: {double_dan}")
    
    # 生成候选
    print("\n生成候选号码...")
    candidates = []
    
    for _ in range(500):
        nums = []
        for pos in range(3):
            probs = predict_prob(markov3, markov1, history, pos)
            digit = random.choices(range(10), weights=[probs[d] for d in range(10)])[0]
            nums.append(digit)
        candidates.append(tuple(nums))
    
    for _ in range(200):
        nums = tuple(random.choice(hot[p]) for p in range(3))
        candidates.append(nums)
    
    seen = set(candidates)
    candidates = list(seen)
    
    def score(nums):
        s = 0
        for pos in range(3):
            probs = predict_prob(markov3, markov1, history, pos)
            s += probs.get(nums[pos], 0.01) * 50
        for pos, d in enumerate(nums):
            if d in hot[pos][:5]:
                s += 10
        if sum(nums) in hot_sums[:5]:
            s += 15
        span = max(nums) - min(nums)
        if span in [3,4,5,6]:
            s += 10
        return min(s, 100)
    
    candidates.sort(key=lambda x: score(x), reverse=True)
    
    print(f"\n精选5注:")
    print("-" * 40)
    results = []
    for i, nums in enumerate(candidates[:5], 1):
        num_str = ''.join(map(str, nums))
        s = sum(nums)
        sc = score(nums)
        print(f"  {i}. {num_str} (和:{s} 分:{sc:.1f})")
        results.append(num_str)
    
    return results, danma, double_dan


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    
    print("\n" + "="*60)
    print("彩票智能分析 V6 - 三阶马尔可夫链 + 胆码")
    print("="*60)
    
    results = {}
    
    try:
        print("\n" + "="*30)
        print("排列三")
        print("="*30)
        pl3_df = pd.read_csv('pl3_full.csv')
        pl3_history = list(zip(pl3_df['num1'].astype(int), pl3_df['num2'].astype(int), pl3_df['num3'].astype(int)))
        pl3_history = list(pl3_history[:5])
        pl3_rec, pl3_danma, pl3_double = analyze(pl3_df, "排列三", pl3_history)
        results['pl3'] = pl3_rec[:2]
        results['pl3_base'] = pl3_rec[:5]
        results['pl3_danma'] = pl3_danma
        results['pl3_double'] = pl3_double
    except Exception as e:
        print(f"排列三失败: {e}")
        results['pl3'] = ['???', '???']
        results['pl3_base'] = ['???'] * 5
        results['pl3_danma'] = [['0'], ['0'], ['0']]
        results['pl3_double'] = ['00']
    
    try:
        print("\n" + "="*30)
        print("3D")
        print("="*30)
        fc3d_df = pd.read_csv('fc3d_5years.csv')
        fc3d_history = list(zip(fc3d_df['num1'].astype(int), fc3d_df['num2'].astype(int), fc3d_df['num3'].astype(int)))
        fc3d_history = list(fc3d_history[:5])
        fc3d_rec, fc3d_danma, fc3d_double = analyze(fc3d_df, "3D", fc3d_history)
        results['fc3d'] = fc3d_rec[:2]
        results['fc3d_base'] = fc3d_rec[:5]
        results['fc3d_danma'] = fc3d_danma
        results['fc3d_double'] = fc3d_double
    except Exception as e:
        print(f"3D失败: {e}")
        results['fc3d'] = ['???', '???']
        results['fc3d_base'] = ['???'] * 5
        results['fc3d_danma'] = [['0'], ['0'], ['0']]
        results['fc3d_double'] = ['00']
    
    base = datetime(2026, 1, 1)
    today = datetime.now()
    period = f"2026{str((today-base).days+1).zfill(3)}"
    
    output = {
        'date': today.strftime('%Y-%m-%d'),
        'period': period,
        'generated_at': today.isoformat(),
        'algorithm': 'Third-Order Markov Chain V6',
        'locked': True,
        'pl3': {
            'selected_2': results['pl3'],
            'base_5': results['pl3_base'],
            'danma': results['pl3_danma'],
            'double_dan': results['pl3_double'],
            'key_sum': sorted(list(set([int(r[0])+int(r[1])+int(r[2]) for r in results['pl3_base'] if r.isdigit()])))[:5]
        },
        'fc3d': {
            'selected_2': results['fc3d'],
            'base_5': results['fc3d_base'],
            'danma': results['fc3d_danma'],
            'double_dan': results['fc3d_double'],
            'key_sum': sorted(list(set([int(r[0])+int(r[1])+int(r[2]) for r in results['fc3d_base'] if r.isdigit()])))[:5]
        }
    }
    
    with open('today_result.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("[OK] V6三阶马尔可夫分析完成!")
    print("="*60)


if __name__ == '__main__':
    main()
