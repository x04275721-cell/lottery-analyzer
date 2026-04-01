#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票分析系统 - 自我优化版本
根据历史结果自动分析并优化策略
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
import random
from datetime import datetime

class SelfLearningAnalyzer:
    """自我学习分析器"""
    
    def __init__(self):
        self.pl3_data = pd.read_csv('pl3_full.csv')
        self.fc3d_data = pd.read_csv('fc3d_5years.csv')
        self.learning_file = 'learning_data.json'
        self.load_learning_data()
    
    def load_learning_data(self):
        """加载学习数据"""
        try:
            with open(self.learning_file, 'r') as f:
                self.learning_data = json.load(f)
        except:
            self.learning_data = {
                'total_predictions': 0,
                'direct_hits': 0,
                'group_hits': 0,
                'sum_accuracy': {},      # 和值预测准确度
                'span_accuracy': {},     # 跨度预测准确度
                'position_accuracy': {}, # 位置预测准确度
                'adjustments': []        # 调整记录
            }
    
    def analyze_yesterday_result(self, yesterday_recommend, yesterday_result):
        """
        分析昨日推荐结果
        找出失败原因并调整策略
        """
        print("\n" + "=" * 60)
        print("📊 自我分析：昨日推荐 vs 实际开奖")
        print("=" * 60)
        
        # 1. 和值分析
        rec_sum = sum([int(c) for c in yesterday_recommend])
        actual_sum = sum([int(c) for c in yesterday_result])
        sum_diff = abs(rec_sum - actual_sum)
        
        print(f"\n📈 和值分析：")
        print(f"   推荐：{rec_sum} | 实际：{actual_sum} | 差距：{sum_diff}")
        
        if sum_diff <= 2:
            print(f"   ✅ 和值接近，策略有效")
        else:
            print(f"   ⚠️ 和值偏差较大，需要调整")
            # 记录并调整
            self.learning_data['sum_accuracy'][str(actual_sum)] = \
                self.learning_data['sum_accuracy'].get(str(actual_sum), 0) + 1
        
        # 2. 跨度分析
        rec_span = max([int(c) for c in yesterday_recommend]) - min([int(c) for c in yesterday_recommend])
        actual_span = max([int(c) for c in yesterday_result]) - min([int(c) for c in yesterday_result])
        span_diff = abs(rec_span - actual_span)
        
        print(f"\n📐 跨度分析：")
        print(f"   推荐：{rec_span} | 实际：{actual_span} | 差距：{span_diff}")
        
        if span_diff <= 1:
            print(f"   ✅ 跨度接近，策略有效")
        else:
            print(f"   ⚠️ 跨度偏差较大，需要调整")
        
        # 3. 位置分析
        print(f"\n📍 位置分析：")
        match_count = 0
        for i in range(3):
            if yesterday_recommend[i] == yesterday_result[i]:
                match_count += 1
                print(f"   位置{i+1}：✅ 命中")
            else:
                print(f"   位置{i+1}：❌ 推荐{yesterday_recommend[i]}，实际{yesterday_result[i]}")
        
        # 4. 生成调整建议
        adjustments = []
        if sum_diff > 3:
            adjustments.append(f"和值范围需扩大±{sum_diff}")
        if span_diff > 2:
            adjustments.append(f"跨度范围需调整")
        if match_count == 0:
            adjustments.append("位置号码需更多变化")
        
        print(f"\n💡 调整建议：")
        for adj in adjustments:
            print(f"   - {adj}")
        
        # 记录调整
        self.learning_data['adjustments'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'recommendation': yesterday_recommend,
            'result': yesterday_result,
            'adjustments': adjustments
        })
        
        # 保存学习数据
        self.save_learning_data()
        
        return adjustments
    
    def get_optimized_key_sums(self, game='pl3'):
        """基于学习数据优化重点和值"""
        
        # 基础：最近50期高频和值
        if game == 'pl3':
            recent_sums = self.pl3_data.head(50)['和值'].tolist()
        else:
            recent_sums = self.fc3d_data.head(100)['和值'].tolist()
        
        sum_counter = Counter(recent_sums)
        base_sums = [s for s, c in sum_counter.most_common(10)]
        
        # 结合学习数据调整
        learned_sums = []
        for s, count in sorted(self.learning_data['sum_accuracy'].items(), 
                               key=lambda x: x[1], reverse=True)[:5]:
            learned_sums.append(int(s))
        
        # 融合：基础 + 学习
        optimized_sums = list(set(base_sums[:5] + learned_sums))[:5]
        
        # 如果不够5个，用高频补充
        while len(optimized_sums) < 5:
            for s in base_sums:
                if s not in optimized_sums:
                    optimized_sums.append(s)
                    if len(optimized_sums) >= 5:
                        break
        
        return sorted(optimized_sums)
    
    def save_learning_data(self):
        """保存学习数据"""
        with open(self.learning_file, 'w') as f:
            json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
    
    def generate_recommendation(self, game='pl3'):
        """生成优化的推荐"""
        
        print(f"\n🎯 生成{game}推荐（自我优化版）")
        
        # 使用优化后的重点和值
        key_sums = self.get_optimized_key_sums(game)
        print(f"   重点和值（优化后）：{key_sums}")
        
        # 排除号码（试机号、开机号）
        excluded = []
        
        # 生成推荐
        def gen_valid():
            for _ in range(100):
                nums = [random.randint(0, 9) for _ in range(3)]
                if nums not in excluded and sum(nums) in key_sums:
                    return nums
            return None
        
        selected = []
        for _ in range(2):
            n = gen_valid()
            if n and n not in selected:
                selected.append(n)
        
        base = selected.copy()
        while len(base) < 10:
            n = gen_valid()
            if n and n not in base:
                base.append(n)
        
        print(f"   精选2注：{[''.join(map(str, n)) for n in selected]}")
        print(f"   十注大底：{[''.join(map(str, n)) for n in base]}")
        
        return selected, base


def main():
    """主程序"""
    print("=" * 60)
    print("🤖 彩票分析系统 - 自我优化版本")
    print("=" * 60)
    
    analyzer = SelfLearningAnalyzer()
    
    # 如果有昨日数据，进行分析
    try:
        with open('yesterday_data.json', 'r') as f:
            yesterday = json.load(f)
        analyzer.analyze_yesterday_result(
            yesterday['recommendation'],
            yesterday['result']
        )
    except:
        print("\n⚠️ 没有昨日数据，跳过分析")
    
    # 生成今日推荐
    pl3_selected, pl3_base = analyzer.generate_recommendation('pl3')
    fc3d_selected, fc3d_base = analyzer.generate_recommendation('fc3d')
    
    # 保存结果
    result = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'generated_at': datetime.now().isoformat(),
        'locked': True,
        'pl3': {
            'selected_2': [''.join(map(str, n)) for n in pl3_selected],
            'base_10': [''.join(map(str, n)) for n in pl3_base],
            'key_sum': analyzer.get_optimized_key_sums('pl3')
        },
        'fc3d': {
            'selected_2': [''.join(map(str, n)) for n in fc3d_selected],
            'base_10': [''.join(map(str, n)) for n in fc3d_base],
            'key_sum': analyzer.get_optimized_key_sums('fc3d')
        }
    }
    
    with open('today_result.json', 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print("\n✅ 今日推荐已生成（含自我优化）")


if __name__ == "__main__":
    main()