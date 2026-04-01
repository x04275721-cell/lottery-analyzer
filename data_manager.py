#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票分析系统 - 智能优化版本
每天22:00自动执行：更新历史 + 反思分析 + 优化下期推荐
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
import random
from datetime import datetime

class SmartLotteryAnalyzer:
    """智能彩票分析器 - 带反思和优化"""
    
    def __init__(self):
        self.pl3_data = pd.read_csv('pl3_full.csv')
        self.fc3d_data = pd.read_csv('fc3d_5years.csv')
        self.history_file = 'history_records.json'
        self.learning_file = 'learning_data.json'
        self.today_result_file = 'today_result.json'
        
        # 加载历史数据
        self.load_history()
        self.load_learning_data()
    
    def load_history(self):
        """加载历史推荐记录"""
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                self.history_records = json.load(f)
        except:
            self.history_records = []
    
    def load_learning_data(self):
        """加载学习数据"""
        try:
            with open(self.learning_file, 'r', encoding='utf-8') as f:
                self.learning_data = json.load(f)
        except:
            self.learning_data = {
                'sum_weights': {},      # 和值权重
                'span_weights': {},     # 跨度权重
                'position_weights': {}, # 位置权重
                'success_patterns': [],  # 成功模式
                'fail_patterns': [],    # 失败模式
                'total_predictions': 0,
                'total_hits': 0
            }
    
    def reflect_on_yesterday(self):
        """
        反思昨日推荐
        分析为什么中/不中，生成优化建议
        """
        print("\n" + "="*60)
        print("🔍 开始反思昨日推荐...")
        print("="*60)
        
        if not self.history_records:
            print("⚠️ 没有历史记录，跳过反思")
            return
        
        # 获取最近一条记录
        recent = self.history_records[-1] if self.history_records else None
        if not recent:
            return
        
        print(f"\n📅 分析期号：{recent['period']}")
        print(f"   彩种：{recent['game']}")
        print(f"   推荐：{recent['recommendation']}")
        print(f"   开奖：{recent['result']}")
        print(f"   状态：{recent['status']}")
        
        # 解析号码
        rec_nums = recent['recommendation'].split(',')
        result_nums = recent['result']
        
        # 分析失败原因
        if recent['status'] == '未中':
            self.analyze_failure(rec_nums, result_nums, recent['game'])
        else:
            self.analyze_success(rec_nums, result_nums, recent['game'])
    
    def analyze_failure(self, rec_nums, result, game):
        """分析失败原因"""
        print("\n❌ 失败原因分析：")
        
        # 计算推荐和值
        rec_sums = [sum(int(c) for c in num) for num in rec_nums]
        actual_sum = sum(int(c) for c in result)
        
        print(f"   推荐和值：{rec_sums}")
        print(f"   实际和值：{actual_sum}")
        
        # 和值偏差分析
        sum_diffs = [abs(s - actual_sum) for s in rec_sums]
        min_diff = min(sum_diffs)
        
        if min_diff > 3:
            print(f"   ⚠️ 和值偏差较大：最小偏差{min_diff}")
            # 调整和值权重
            self.adjust_sum_weight(actual_sum, 'increase')
        
        # 跨度分析
        rec_spans = [max(num) - min(num) for num in [list(n) for n in rec_nums]]
        actual_span = max(int(c) for c in result) - min(int(c) for c in result)
        
        print(f"   推荐跨度：{rec_spans}")
        print(f"   实际跨度：{actual_span}")
        
        # 记录失败模式
        self.learning_data['fail_patterns'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'rec_sums': rec_sums,
            'actual_sum': actual_sum,
            'rec_spans': rec_spans,
            'actual_span': actual_span,
            'diff': min_diff
        })
        
        # 生成优化建议
        self.generate_optimization_suggestions(actual_sum, actual_span, game)
    
    def analyze_success(self, rec_nums, result, game):
        """分析成功原因"""
        print("\n✅ 成功分析：")
        
        actual_sum = sum(int(c) for c in result)
        actual_span = max(int(c) for c in result) - min(int(c) for c in result)
        
        print(f"   成功和值：{actual_sum}")
        print(f"   成功跨度：{actual_span}")
        
        # 记录成功模式
        self.learning_data['success_patterns'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sum': actual_sum,
            'span': actual_span,
            'numbers': result
        })
        
        # 增加权重
        self.adjust_sum_weight(actual_sum, 'reward')
    
    def adjust_sum_weight(self, sum_value, action):
        """调整和值权重"""
        key = str(sum_value)
        if key not in self.learning_data['sum_weights']:
            self.learning_data['sum_weights'][key] = 1.0
        
        if action == 'increase':
            self.learning_data['sum_weights'][key] += 0.5
        elif action == 'reward':
            self.learning_data['sum_weights'][key] += 1.0
    
    def generate_optimization_suggestions(self, actual_sum, actual_span, game):
        """生成优化建议"""
        print("\n💡 下期优化建议：")
        
        suggestions = []
        
        # 和值优化
        suggestions.append(f"   1. 和值范围扩大到：{max(0, actual_sum-3)} - {min(27, actual_sum+3)}")
        
        # 跨度优化
        suggestions.append(f"   2. 跨度关注：{max(0, actual_span-2)} - {min(9, actual_span+2)}")
        
        # 热号优化
        if game == '排列三':
            recent = self.pl3_data.head(20)
        else:
            recent = self.fc3d_data.head(20)
        
        hot_nums = []
        for col in ['num1', 'num2', 'num3']:
            counter = Counter(recent[col].tolist())
            hot_nums.extend([n for n, c in counter.most_common(3)])
        
        suggestions.append(f"   3. 关注热号：{list(set(hot_nums))[:5]}")
        
        for s in suggestions:
            print(s)
        
        return suggestions
    
    def generate_optimized_recommendation(self, game='pl3'):
        """基于反思生成优化推荐"""
        print(f"\n🎯 生成{game}优化推荐...")
        
        # 获取历史数据
        if game == 'pl3':
            data = self.pl3_data
            periods = 50
        else:
            data = self.fc3d_data
            periods = 100
        
        recent = data.head(periods)
        
        # 1. 基础热号分析
        hot_by_position = []
        for col in ['num1', 'num2', 'num3']:
            counter = Counter(recent[col].tolist())
            hot_by_position.append([n for n, c in counter.most_common(5)])
        
        print(f"   百位热号：{hot_by_position[0]}")
        print(f"   十位热号：{hot_by_position[1]}")
        print(f"   个位热号：{hot_by_position[2]}")
        
        # 2. 和值分析（结合学习权重）
        sum_counter = Counter(recent['和值'].tolist())
        base_sums = [s for s, c in sum_counter.most_common(8)]
        
        # 根据学习数据调整
        weighted_sums = []
        for s in base_sums:
            weight = self.learning_data['sum_weights'].get(str(s), 1.0)
            weighted_sums.append((s, weight))
        
        # 排序并取前5
        weighted_sums.sort(key=lambda x: x[1], reverse=True)
        key_sums = [s[0] for s in weighted_sums[:5]]
        
        print(f"   优化后重点和值：{key_sums}")
        
        # 3. 生成推荐
        excluded = []  # 试机号、开机号排除
        
        def gen_valid():
            random.seed(datetime.now().timestamp())
            for _ in range(100):
                nums = [
                    random.choice(hot_by_position[0] + [random.randint(0,9)]),
                    random.choice(hot_by_position[1] + [random.randint(0,9)]),
                    random.choice(hot_by_position[2] + [random.randint(0,9)])
                ]
                if nums not in excluded and sum(nums) in key_sums:
                    return nums
            return None
        
        # 精选2注
        selected = []
        for _ in range(2):
            n = gen_valid()
            if n and n not in selected:
                selected.append(n)
        
        # 10注大底
        base = selected.copy()
        while len(base) < 10:
            n = gen_valid()
            if n and n not in base:
                base.append(n)
        
        print(f"   精选2注：{[''.join(map(str, n)) for n in selected]}")
        print(f"   十注大底：{[''.join(map(str, n)) for n in base]}")
        
        return selected, base, key_sums
    
    def save_learning_data(self):
        """保存学习数据"""
        with open(self.learning_file, 'w', encoding='utf-8') as f:
            json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        print("✅ 学习数据已保存")
    
    def run_daily_update(self):
        """每天22:00运行的完整流程"""
        print("="*60)
        print("🕐 每日自动更新任务开始")
        print(f"   时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 1. 反思昨日推荐
        self.reflect_on_yesterday()
        
        # 2. 生成今日优化推荐
        pl3_selected, pl3_base, pl3_sums = self.generate_optimized_recommendation('pl3')
        fc3d_selected, fc3d_base, fc3d_sums = self.generate_optimized_recommendation('fc3d')
        
        # 3. 保存结果
        result = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'period': self.calculate_period(),
            'generated_at': datetime.now().isoformat(),
            'locked': True,
            'pl3': {
                'test': '待更新',  # 18:00填入
                'boot': '待更新',
                'key_sum': pl3_sums,
                'selected_2': [''.join(map(str, n)) for n in pl3_selected],
                'base_10': [''.join(map(str, n)) for n in pl3_base]
            },
            'fc3d': {
                'test': '待更新',
                'boot': '待更新',
                'key_sum': fc3d_sums,
                'selected_2': [''.join(map(str, n)) for n in fc3d_selected],
                'base_10': [''.join(map(str, n)) for n in fc3d_base]
            }
        }
        
        with open(self.today_result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 4. 保存学习数据
        self.save_learning_data()
        
        print("\n✅ 每日更新任务完成！")
    
    def calculate_period(self):
        """计算期号"""
        # 简单计算，实际需要根据日期
        return '2026082'


if __name__ == '__main__':
    analyzer = SmartLotteryAnalyzer()
    analyzer.run_daily_update()