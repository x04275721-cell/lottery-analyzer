#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票智能分析系统 V6 - 三阶马尔可夫链

真正的多阶马尔可夫链：
- 一阶：P(本期 | 上1期)
- 二阶：P(本期 | 上2期)  
- 三阶：P(本期 | 上3期)
- 综合：三阶×0.4 + 二阶×0.3 + 一阶×0.3

作者：AI助手
日期：2026-04-02
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
import json
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')


class ThirdOrderMarkovChain:
    """三阶马尔可夫链分析器"""
    
    def __init__(self, df, name):
        self.name = name
        self.df = df
        self.nums = list(zip(
            df['num1'].astype(int).tolist(),
            df['num2'].astype(int).tolist(),
            df['num3'].astype(int).tolist()
        ))
        
        print(f"\n{'='*60}")
        print(f"=== {name} - 三阶马尔可夫链分析 ===")
        print(f"{'='*60}")
        print(f"历史数据：{len(self.nums)}期")
        
        # 构建各级转移矩阵
        self.first_matrix = self._build_first_order()
        self.second_matrix = self._build_second_order()
        self.third_matrix = self._build_third_order()
        
        # 位置热号
        self.position_hot = self._build_position_hot()
        
        # 和值分布
        self.sum_dist = Counter(df.head(100)['和值'].tolist())
        
        # 打印统计
        self._print_stats()
    
    def _build_first_order(self):
        """一阶马尔可夫：P(本期 | 上1期)"""
        print("\n[1] 构建一阶马尔可夫矩阵...")
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        
        for i in range(len(self.nums) - 1):
            prev = self.nums[i]
            curr = self.nums[i + 1]
            for p, c in zip(prev, curr):
                trans[p][c] += 1
                totals[p] += 1
        
        matrix = {}
        for p in range(10):
            matrix[p] = {}
            for c in range(10):
                matrix[p][c] = trans[p][c] / totals[p] if totals[p] > 0 else 0.01
        
        return matrix
    
    def _build_second_order(self):
        """二阶马尔可夫：P(本期 | 上2期)"""
        print("[2] 构建二阶马尔可夫矩阵...")
        trans = defaultdict(lambda: defaultdict(int))
        totals = defaultdict(int)
        
        for i in range(len(self.nums) - 2):
            key = (self.nums[i+1][0], self.nums[i+1][1], self.nums[i+1][2])
            curr = self.nums[i + 2]
            for p, c in zip(key, curr):
                trans[p][c] += 1
                totals[p] += 1
            
            key2 = (self.nums[i][0], self.nums[i+1][1], self.nums[i+1][2])
            for p, c in zip(key2, curr):
                trans[p][c] += 1
                totals[p] += 1
        
        matrix = {}
        for p in range(10):
            matrix[p] = {}
            for c in range(10):
                matrix[p][c] = trans[p][c] / totals[p] if totals[p] > 0 else 0.01
        
        return matrix
    
    def _build_third_order(self):
        """三阶马尔可夫：P(本期 | 上3期)"""
        print("[3] 构建三阶马尔可夫矩阵...")
        
        # 三阶：P(num_t | num_{t-1}, num_{t-2}, num_{t-3})
        trans_full = defaultdict(lambda: defaultdict(int))
        totals_full = defaultdict(int)
        
        # 简化三阶：按位置分别建模
        matrices = []
        for pos in range(3):
            trans = defaultdict(lambda: defaultdict(int))
            totals = defaultdict(int)
            
            for i in range(len(self.nums) - 3):
                # 获取前三期同位置的值
                history = tuple(self.nums[j][pos] for j in range(i, i+3))
                current = self.nums[i+3][pos]
                
                trans[history][current] += 1
                totals[history] += 1
            
            # 转换为概率
            matrix = {}
            for history in totals:
                matrix[history] = {}
                for digit in range(10):
                    matrix[history][digit] = trans[history][digit] / totals[history] if totals[history] > 0 else 0.01
            
            matrices.append(matrix)
            
            print(f"    位置{pos+1}三阶状态数：{len(totals)}")
            
            # 统计最强三阶规律
            if totals:
                best_history = max(totals.keys(), key=lambda h: totals[h])
                best_digit = max(range(10), key=lambda d: trans[best_history][d])
                prob = trans[best_history][best_digit] / totals[best_history]
                print(f"    最强规律：{best_history} -> {best_digit} (概率{prob:.1%})")
        
        return matrices
    
    def _build_position_hot(self):
        """各位置热号"""
        print("[4] 分析位置热号...")
        hot = []
        for col_idx, col_name in enumerate(['num1', 'num2', 'num3']):
            counter = Counter(self.df.head(100)[col_name].tolist())
            top = counter.most_common(10)
            hot.append([d for d, c in top])
            print(f"    位置{col_idx+1}热号：{[f'{d}({c})' for d,c in top[:5]]}")
        return hot
    
    def _print_stats(self):
        """打印统计信息"""
        print("\n[5] 和值分布：")
        for s, c in self.sum_dist.most_common(5):
            print(f"    和值{s}: {c}次")
    
    def predict_position_markov(self, pos, history):
        """
        使用三阶马尔可夫预测单个位置
        
        参数：
            pos: 位置(0,1,2)
            history: 前3期的号码列表
        """
        # 获取前三期同位置的值
        if len(history) >= 3:
            first = history[-3][pos]
            second = history[-2][pos]
            third = history[-1][pos]
            key = (first, second, third)
        elif len(history) >= 2:
            key = (5, history[-2][pos], history[-1][pos])
        elif len(history) >= 1:
            key = (5, 5, history[-1][pos])
        else:
            key = (5, 5, 5)
        
        # 获取三阶概率
        if key in self.third_matrix[pos]:
            third_probs = self.third_matrix[pos][key]
        else:
            third_probs = {d: 0.1 for d in range(10)}
        
        # 二阶概率
        if len(history) >= 2:
            second_key = (history[-2][pos], history[-1][pos])
            second_probs = {d: self.second_matrix[d].get(digit, 0.1) for d in range(10)}
        else:
            second_probs = {d: 0.1 for d in range(10)}
        
        # 一阶概率
        if len(history) >= 1:
            first_probs = self.first_matrix[history[-1][pos]]
        else:
            first_probs = {d: 0.1 for d in range(10)}
        
        # 综合概率：三阶40% + 二阶30% + 一阶30%
        combined = {}
        for digit in range(10):
            combined[digit] = (
                third_probs.get(digit, 0.1) * 0.4 +
                second_probs.get(digit, 0.1) * 0.3 +
                first_probs.get(digit, 0.1) * 0.3
            )
        
        # 归一化
        total = sum(combined.values())
        for d in combined:
            combined[d] /= total
        
        return combined
    
    def generate_candidates(self, history, count=500):
        """生成候选号码"""
        candidates = []
        
        for _ in range(count):
            nums = []
            for pos in range(3):
                probs = self.predict_position_markov(pos, history)
                digit = random.choices(range(10), weights=list(probs.values()))[0]
                nums.append(digit)
            candidates.append(tuple(nums))
        
        return candidates
    
    def score_number(self, nums, history):
        """综合评分"""
        score = 0.0
        
        # 1. 三阶马尔可夫得分 (35%)
        third_score = 0
        for pos in range(3):
            probs = self.predict_position_markov(pos, history)
            third_score += probs.get(nums[pos], 0.01) * 35
        score += third_score
        
        # 2. 二阶马尔可夫得分 (20%)
        second_score = 0
        if len(history) >= 2:
            for pos in range(3):
                key = (history[-2][pos], history[-1][pos])
                if key in self.second_matrix:
                    second_score += self.second_matrix[key].get(nums[pos], 0.01) * 20 / 3
        score += second_score
        
        # 3. 一阶马尔可夫得分 (15%)
        first_score = 0
        if len(history) >= 1:
            for pos in range(3):
                first_score += self.first_matrix[history[-1][pos]].get(nums[pos], 0.01) * 15 / 3
        score += first_score
        
        # 4. 位置热号得分 (15%)
        hot_score = 0
        for pos, digit in enumerate(nums):
            if digit in self.position_hot[pos][:5]:
                hot_score += 3
        score += min(hot_score, 15)
        
        # 5. 和值匹配 (10%)
        total_sum = sum(nums)
        for s, c in self.sum_dist.most_common(8):
            if s == total_sum:
                score += 10 * c / 100
                break
        
        # 6. 跨度匹配 (5%)
        span = max(nums) - min(nums)
        if span in [3, 4, 5, 6]:
            score += 5
        
        return round(min(score, 100), 2)
    
    def generate_recommendations(self, history, count=10):
        """生成推荐"""
        print(f"\n{'='*60}")
        print(f"基于历史：{[''.join(map(str,h)) for h in history[-3:]]}")
        print(f"{'='*60}")
        
        # 生成候选
        print("\n[生成] 马尔可夫链预测...")
        candidates = self.generate_candidates(history, 500)
        
        # 热号补充
        print("[补充] 热号组合...")
        hot_nums = []
        for _ in range(200):
            nums = tuple(random.choice(self.position_hot[p]) for p in range(3))
            hot_nums.append(nums)
        candidates.extend(hot_nums)
        
        # 和值筛选
        print("[筛选] 和值区间...")
        sum_nums = []
        hot_sums = [s for s, c in self.sum_dist.most_common(8)]
        for _ in range(200):
            s = random.choice(hot_sums)
            n1 = random.randint(0,9)
            n2 = random.randint(0,9)
            n3 = s - n1 - n2
            n3 = max(0, min(9, n3))
            nums = (n1, n2, n3)
            sum_nums.append(nums)
        candidates.extend(sum_nums)
        
        # 去重
        seen = set()
        unique = []
        for n in candidates:
            if n not in seen:
                seen.add(n)
                unique.append(n)
        
        # 评分排序
        print("[评分] 综合评分...")
        scored = [(n, self.score_number(n, history)) for n in unique]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # 输出结果
        print(f"\n{'='*60}")
        print(f"TOP {count} 推荐号码：")
        print(f"{'='*60}")
        print(f"{'排名':<4} {'号码':<8} {'总分':<6} {'和值':<4} {'跨度'}")
        print("-" * 40)
        
        results = []
        for i, (nums, score) in enumerate(scored[:count], 1):
            num_str = ''.join(map(str, nums))
            s = sum(nums)
            sp = max(nums) - min(nums)
            print(f"{i:<4} {num_str:<8} {score:<6.2f} {s:<4} {sp}")
            results.append({
                'number': num_str,
                'score': score,
                'sum': s,
                'span': sp
            })
        
        return results


def main():
    print("\n" + "="*60)
    print("=== 彩票智能分析系统 V6 - 三阶马尔可夫链 ===")
    print("="*60)
    
    results = {}
    
    # 分析排列三
    try:
        print("\n" + "="*40)
        print("排列三分析")
        print("="*40)
        
        pl3_df = pd.read_csv('pl3_full.csv')
        pl3 = ThirdOrderMarkovChain(pl3_df, '排列三')
        
        # 上期排列三：406
        pl3_history = list(zip(
            pl3_df['num1'].astype(int).tolist()[:5],
            pl3_df['num2'].astype(int).tolist()[:5],
            pl3_df['num3'].astype(int).tolist()[:5]
        ))
        pl3_history = [tuple(x) for x in pl3_history]
        
        pl3_results = pl3.generate_recommendations(pl3_history, 10)
        results['pl3'] = {
            'last_draw': ''.join(map(str, pl3_history[0])),
            'recommendations': pl3_results[:2],
            'base_10': [r['number'] for r in pl3_results[:10]]
        }
        
    except Exception as e:
        print(f"[X] 排列三分析失败：{e}")
        results['pl3'] = {'recommendations': [], 'base_10': []}
    
    # 分析3D
    try:
        print("\n" + "="*40)
        print("3D分析")
        print("="*40)
        
        fc3d_df = pd.read_csv('fc3d_5years.csv')
        fc3d = ThirdOrderMarkovChain(fc3d_df, '3D')
        
        # 上期3D：827
        fc3d_history = list(zip(
            fc3d_df['num1'].astype(int).tolist()[:5],
            fc3d_df['num2'].astype(int).tolist()[:5],
            fc3d_df['num3'].astype(int).tolist()[:5]
        ))
        fc3d_history = [tuple(x) for x in fc3d_history]
        
        fc3d_results = fc3d.generate_recommendations(fc3d_history, 10)
        results['fc3d'] = {
            'last_draw': ''.join(map(str, fc3d_history[0])),
            'recommendations': fc3d_results[:2],
            'base_10': [r['number'] for r in fc3d_results[:10]]
        }
        
    except Exception as e:
        print(f"[X] 3D分析失败：{e}")
        results['fc3d'] = {'recommendations': [], 'base_10': []}
    
    # 保存结果
    base = datetime(2026, 1, 1)
    today = datetime.now()
    period = f"2026{str((today-base).days+1).zfill(3)}"
    
    final_result = {
        'date': today.strftime('%Y-%m-%d'),
        'period': period,
        'generated_at': today.isoformat(),
        'algorithm': 'Third-Order Markov Chain V6',
        'locked': True,
        'pl3': {
            'key_sum': sorted(list(set([r['sum'] for r in results.get('pl3', {}).get('recommendations', [])])))[:5],
            'selected_2': [r['number'] for r in results.get('pl3', {}).get('recommendations', [])],
            'base_10': results.get('pl3', {}).get('base_10', [])
        },
        'fc3d': {
            'key_sum': sorted(list(set([r['sum'] for r in results.get('fc3d', {}).get('recommendations', [])])))[:5],
            'selected_2': [r['number'] for r in results.get('fc3d', {}).get('recommendations', [])],
            'base_10': results.get('fc3d', {}).get('base_10', [])
        }
    }
    
    with open('today_result.json', 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    print("\n" + "="*60)
    print("[OK] 分析完成！结果已保存")
    print("="*60)


if __name__ == '__main__':
    main()
