#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 彩票智能分析系统 V5 - 真正的马尔可夫链

多阶马尔可夫链 + 前缀匹配 + 多算法综合评分

作者：AI助手
日期：2026-04-02
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from datetime import datetime
import json
import random

class MarkovChainAnalyzer:
    """真正的马尔可夫链分析器"""
    
    def __init__(self, data_file, name="彩种"):
        self.name = name
        self.data = pd.read_csv(data_file)
        self.data['num1'] = self.data['num1'].astype(int)
        self.data['num2'] = self.data['num2'].astype(int)
        self.data['num3'] = self.data['num3'].astype(int)
        
        # 构建转移矩阵
        self.first_order_matrix = {}  # 一阶：P(本期|上期)
        self.second_order_matrix = {}  # 二阶：P(本期|前两期)
        self.prefix_patterns = {}      # 前缀模式
        self.position_hot = {}          # 各位置热号
        self.sum_distribution = {}      # 和值分布
        self.span_distribution = {}    # 跨度分布
        
        self._build_matrices()
    
    def _build_matrices(self):
        """构建所有分析矩阵"""
        print(f"\n{'='*50}")
        print(f"📊 构建{self.name}分析矩阵...")
        print(f"{'='*50}")
        
        nums = list(zip(self.data['num1'], self.data['num2'], self.data['num3']))
        
        # ========== 1. 一阶马尔可夫矩阵 ==========
        print("\n1️⃣ 构建一阶马尔可夫转移矩阵...")
        first_transitions = defaultdict(lambda: defaultdict(int))
        first_totals = defaultdict(int)
        
        for i in range(len(nums) - 1):
            prev = nums[i]
            curr = nums[i + 1]
            for p, c in zip(prev, curr):
                first_transitions[p][c] += 1
                first_totals[p] += 1
        
        # 转换为概率
        for prev_digit in range(10):
            self.first_order_matrix[prev_digit] = {}
            for curr_digit in range(10):
                if first_totals[prev_digit] > 0:
                    prob = first_transitions[prev_digit][curr_digit] / first_totals[prev_digit]
                    self.first_order_matrix[prev_digit][curr_digit] = prob
                else:
                    self.first_order_matrix[prev_digit][curr_digit] = 0.0
        
        # 找出最强转移
        strong_transitions = []
        for prev_digit in range(10):
            best_next = max(self.first_order_matrix[prev_digit].items(), key=lambda x: x[1])
            strong_transitions.append((prev_digit, best_next[0], best_next[1]))
        
        strong_transitions.sort(key=lambda x: x[2], reverse=True)
        print("   Top 5 强转移：")
        for prev, curr, prob in strong_transitions[:5]:
            print(f"   {prev} → {curr}: {prob*100:.1f}%")
        
        # ========== 2. 二阶马尔可夫矩阵 ==========
        print("\n2️⃣ 构建二阶马尔可夫转移矩阵...")
        second_transitions = defaultdict(lambda: defaultdict(int))
        second_totals = defaultdict(int)
        
        for i in range(len(nums) - 1):
            prev2 = nums[i]
            prev1 = nums[i + 1]
            curr = nums[i + 2] if i + 2 < len(nums) else nums[-1]
            
            for p2, p1, c in zip(prev2, prev1, curr):
                key = (p2, p1)
                second_transitions[key][c] += 1
                second_totals[key] += 1
        
        for key in second_totals:
            self.second_order_matrix[key] = {}
            for digit in range(10):
                if second_totals[key] > 0:
                    self.second_order_matrix[key][digit] = second_transitions[key][digit] / second_totals[key]
                else:
                    self.second_order_matrix[key][digit] = 0.0
        
        print(f"   二阶状态数：{len(self.second_order_matrix)}")
        
        # ========== 3. 前缀模式匹配 ==========
        print("\n3️⃣ 构建前缀模式库...")
        for pos in range(3):
            prefix_counter = Counter()
            for i in range(len(nums) - 2):
                prefix = tuple(nums[i:i+3])  # 3期连续
                prefix_counter[prefix[pos]] += 1
            
            self.prefix_patterns[pos] = {}
            total = sum(prefix_counter.values())
            for digit, count in prefix_counter.items():
                self.prefix_patterns[pos][digit] = count / total if total > 0 else 0
        
        print("   前缀模式构建完成")
        
        # ========== 4. 各位置热号 ==========
        print("\n4️⃣ 分析各位置热号...")
        for pos, col in enumerate(['num1', 'num2', 'num3']):
            recent = self.data.head(100)[col].tolist()
            counter = Counter(recent)
            self.position_hot[pos] = counter.most_common(10)
            print(f"   {['百位','十位','个位'][pos]}热号：{[f'{d}({c})' for d,c in self.position_hot[pos][:5]]}")
        
        # ========== 5. 和值分布 ==========
        print("\n5️⃣ 分析和值分布...")
        recent_sums = self.data.head(100)['和值'].tolist()
        self.sum_distribution = Counter(recent_sums)
        hot_sums = self.sum_distribution.most_common(5)
        print(f"   热门和值：{[f'{s}({c})' for s,c in hot_sums]}")
        
        # ========== 6. 跨度分布 ==========
        print("\n6️⃣ 分析跨度分布...")
        recent_spans = self.data.head(100)['跨度'].tolist()
        self.span_distribution = Counter(recent_spans)
        hot_spans = self.span_distribution.most_common(3)
        print(f"   热门跨度：{[f'{s}({c})' for s,c in hot_spans]}")
    
    def predict_position(self, prev_digits, order=1):
        """
        使用马尔可夫链预测单个位置
        
        参数：
            prev_digits: 前面的数字（上1期或上2期）
            order: 1=一阶, 2=二阶
        """
        if order == 1:
            matrix = self.first_order_matrix
            key = prev_digits[-1] if prev_digits else 5  # 无历史则用中位数
        else:
            matrix = self.second_order_matrix
            if len(prev_digits) >= 2:
                key = (prev_digits[-2], prev_digits[-1])
            else:
                key = (5, 5)
        
        if key in matrix:
            probs = matrix[key]
            # 返回概率最高的几个数字
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            return [(digit, prob) for digit, prob in sorted_probs[:5]]
        else:
            return [(i, 0.1) for i in range(10)]
    
    def score_number(self, nums, last_nums=None):
        """
        给号码打分（综合多算法）
        
        返回：总分 (0-100)
        """
        score = 0
        details = []
        
        # ========== 权重设置 ==========
        WEIGHTS = {
            'first_order': 25,   # 一阶马尔可夫
            'second_order': 20,   # 二阶马尔可夫
            'prefix': 15,         # 前缀匹配
            'position_hot': 20,   # 位置热号
            'sum_match': 10,      # 和值匹配
            'span_match': 5,      # 跨度匹配
            'global_hot': 5       # 全局热号
        }
        
        # ========== 1. 一阶马尔可夫得分 ==========
        first_score = 0
        for i, digit in enumerate(nums):
            if last_nums and len(last_nums) > 0:
                probs = self.predict_position(last_nums[i], order=1)
                for pred_digit, prob in probs:
                    if pred_digit == digit:
                        first_score += prob * 10
                        break
            else:
                first_score += 1  # 无历史时给基础分
        first_score = min(first_score / 3, 10) * WEIGHTS['first_order'] / 10
        details.append(f"一阶:{first_score:.1f}")
        
        # ========== 2. 二阶马尔可夫得分 ==========
        second_score = 0
        if last_nums and len(last_nums) >= 1:
            for i, digit in enumerate(nums):
                probs = self.predict_position(last_nums[i], order=2)
                for pred_digit, prob in probs:
                    if pred_digit == digit:
                        second_score += prob * 10
                        break
        else:
            second_score = 5
        second_score = min(second_score / 3, 10) * WEIGHTS['second_order'] / 10
        details.append(f"二阶:{second_score:.1f}")
        
        # ========== 3. 前缀匹配得分 ==========
        prefix_score = 0
        for pos in range(3):
            if nums[pos] in self.prefix_patterns[pos]:
                prefix_score += self.prefix_patterns[pos][nums[pos]] * 10
        prefix_score = min(prefix_score / 3, 10) * WEIGHTS['prefix'] / 10
        details.append(f"前缀:{prefix_score:.1f}")
        
        # ========== 4. 位置热号得分 ==========
        hot_score = 0
        for pos, digit in enumerate(nums):
            for hot_digit, count in self.position_hot[pos]:
                if hot_digit == digit:
                    hot_score += count / 100 * 10
                    break
        hot_score = min(hot_score / 3, 10) * WEIGHTS['position_hot'] / 10
        details.append(f"热号:{hot_score:.1f}")
        
        # ========== 5. 和值匹配得分 ==========
        total_sum = sum(nums)
        sum_score = 0
        for s, count in self.sum_distribution.most_common(10):
            if s == total_sum:
                sum_score = count / 100 * 10
                break
        sum_score = sum_score * WEIGHTS['sum_match'] / 10
        details.append(f"和值:{sum_score:.1f}")
        
        # ========== 6. 跨度匹配得分 ==========
        span = max(nums) - min(nums)
        span_score = 0
        for s, count in self.span_distribution.most_common(10):
            if s == span:
                span_score = count / 100 * 10
                break
        span_score = span_score * WEIGHTS['span_match'] / 10
        details.append(f"跨度:{span_score:.1f}")
        
        # ========== 7. 全局热号得分 ==========
        global_counter = Counter(self.data.head(500)['num1'].tolist() + 
                                 self.data.head(500)['num2'].tolist() + 
                                 self.data.head(500)['num3'].tolist())
        global_score = 0
        for digit in nums:
            if digit in [d for d, c in global_counter.most_common(5)]:
                global_score += 2
        global_score = min(global_score, 10) * WEIGHTS['global_hot'] / 10
        details.append(f"全局:{global_score:.1f}")
        
        total = first_score + second_score + prefix_score + hot_score + sum_score + span_score + global_score
        
        return round(total, 2), '; '.join(details)
    
    def generate_recommendations(self, last_nums, count=10):
        """
        生成推荐号码
        
        参数：
            last_nums: 上期开奖号码
            count: 生成数量
        """
        print(f"\n{'='*50}")
        print(f"🎯 生成{self.name}推荐（基于上期：{last_nums}）")
        print(f"{'='*50}")
        
        candidates = []
        
        # 方法1：从马尔可夫预测生成
        print("\n📌 方法1：马尔可夫链预测...")
        for _ in range(500):
            nums = []
            prev = list(last_nums) if last_nums else [5, 5, 5]
            
            # 百位预测
            probs1 = self.predict_position(prev, order=1)
            nums.append(random.choices([p[0] for p in probs1], 
                                       weights=[p[1] for p in probs1])[0])
            
            # 十位预测
            probs2 = self.predict_position(prev, order=2)
            nums.append(random.choices([p[0] for p in probs2], 
                                       weights=[p[1] for p in probs2])[0])
            
            # 个位预测
            nums.append(random.randint(0, 9))
            
            score, detail = self.score_number(nums, prev)
            candidates.append((nums, score, detail))
        
        # 方法2：热号组合生成
        print("📌 方法2：热号组合...")
        for _ in range(200):
            nums = []
            for pos in range(3):
                hot_list = [d for d, c in self.position_hot[pos][:5]]
                nums.append(random.choice(hot_list))
            
            score, detail = self.score_number(nums, prev)
            candidates.append((nums, score, detail))
        
        # 方法3：和值区间生成
        print("📌 方法3：和值区间筛选...")
        hot_sum_list = [s for s, c in self.sum_distribution.most_common(10)]
        for _ in range(200):
            s = random.choice(hot_sum_list)
            nums = [
                random.randint(0, 9),
                random.randint(0, 9),
                s - random.randint(0, 9) - random.randint(0, 9)
            ]
            nums = [max(0, min(9, n)) for n in nums]
            
            score, detail = self.score_number(nums, prev)
            candidates.append((nums, score, detail))
        
        # 去重并排序
        candidates = list(set([(tuple(n), s, d) for n, s, d in candidates]))
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 取最优
        best = candidates[:count]
        
        print(f"\n🏆 TOP {count} 推荐号码：")
        print("-" * 70)
        print(f"{'排名':<4} {'号码':<8} {'总分':<6} {'详情'}")
        print("-" * 70)
        
        results = []
        for i, (nums, score, detail) in enumerate(best, 1):
            num_str = ''.join(map(str, nums))
            s = sum(nums)
            sp = max(nums) - min(nums)
            print(f"{i:<4} {num_str:<8} {score:<6.2f} 和:{s} 跨:{sp}")
            print(f"     {detail}")
            results.append({
                'number': num_str,
                'score': score,
                'sum': s,
                'span': sp,
                'detail': detail
            })
        
        return results


def main():
    """主函数"""
    print("\n" + "="*60)
    print("=== 彩票智能分析系统 V5 - 真正的马尔可夫链 ===")
    print("="*60)
    
    # 分析排列三
    print("\n\n" + "🔴"*25)
    print("排列三分析")
    print("🔴"*25)
    
    try:
        pl3_analyzer = MarkovChainAnalyzer('pl3_full.csv', '排列三')
        
        # 获取上期开奖
        last_pl3 = (4, 0, 6)  # 需要从实际数据获取
        pl3_results = pl3_analyzer.generate_recommendations(last_pl3, count=10)
        
    except Exception as e:
        print(f"⚠️ 排列三分析失败：{e}")
        pl3_results = []
    
    # 分析3D
    print("\n\n" + "🟢"*25)
    print("福彩3D分析")
    print("🟢"*25)
    
    try:
        fc3d_analyzer = MarkovChainAnalyzer('fc3d_5years.csv', '3D')
        
        # 获取上期开奖 (082期：827)
        last_fc3d = (8, 2, 7)
        fc3d_results = fc3d_analyzer.generate_recommendations(last_fc3d, count=10)
        
    except Exception as e:
        print(f"⚠️ 3D分析失败：{e}")
        fc3d_results = []
        last_fc3d = (0, 0, 0)
    
    # 保存结果
    result = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'generated_at': datetime.now().isoformat(),
        'algorithm': 'Markov Chain V5',
        'locked': True,
        'pl3': {
            'last_draw': ''.join(map(str, last_pl3 if 'last_pl3' in dir() else [0,0,0])),
            'recommendations': pl3_results[:2],
            'base_10': [r['number'] for r in pl3_results[:10]]
        },
        'fc3d': {
            'last_draw': ''.join(map(str, last_fc3d)),
            'recommendations': fc3d_results[:2],
            'base_10': [r['number'] for r in fc3d_results[:10]]
        }
    }
    
    with open('today_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n\n" + "="*60)
    print("✅ 分析完成！结果已保存到 today_result.json")
    print("="*60)


if __name__ == '__main__':
    main()
