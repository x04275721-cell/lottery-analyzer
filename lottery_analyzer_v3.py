#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票分析系统 V3
规则：试机号/开机号仅作为参考，不作为开奖号
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

class LotteryAnalyzer:
    """彩票分析器 - 遵循核心规则：试机号/开机号仅作参考"""
    
    # 核心规则常量
    RULE_EXCLUDE_TEST_BOOT = True  # 必须排除试机号开机号
    
    def __init__(self, pl3_file='pl3_full.csv', fc3d_file='fc3d_5years.csv'):
        """初始化分析器"""
        self.pl3_data = pd.read_csv(pl3_file)
        self.fc3d_data = pd.read_csv(fc3d_file)
        self.excluded_numbers = []  # 排除列表（试机号、开机号）
        
    def set_excluded_numbers(self, test_number, boot_number):
        """
        设置排除号码（试机号和开机号）
        
        规则：试机号和开机号仅作为参考，不作为开奖号码
        """
        self.excluded_numbers = [test_number, boot_number]
        print(f"⚠️  已设置排除号码（仅作参考）：")
        print(f"   试机号：{test_number}")
        print(f"   开机号：{boot_number}")
        print(f"   ✅ 精选推荐将不包含以上号码")
        
    def is_excluded(self, numbers):
        """检查号码是否在排除列表中"""
        return numbers in self.excluded_numbers
        
    def get_hot_numbers(self, df, periods=50, top_n=5):
        """获取热号"""
        recent = df.head(periods)
        all_nums = []
        for _, row in recent.iterrows():
            all_nums.extend([row['num1'], row['num2'], row['num3']])
        
        counter = Counter(all_nums)
        hot = [n for n, c in counter.most_common(top_n)]
        cold = [n for n, c in counter.most_common()[-3:]]
        return hot, cold
        
    def get_position_hot(self, df, periods=50, top_n=3):
        """获取各位置热号"""
        recent = df.head(periods)
        positions = [[], [], []]
        
        for _, row in recent.iterrows():
            positions[0].append(row['num1'])
            positions[1].append(row['num2'])
            positions[2].append(row['num3'])
            
        pos_hot = []
        for pos in positions:
            c = Counter(pos)
            pos_hot.append([n for n, _ in c.most_common(top_n)])
            
        return pos_hot
        
    def generate_recommendations(self, df, game_type='排列三'):
        """
        生成推荐号码
        
        核心规则：必须排除试机号和开机号
        """
        print(f"\n{'='*60}")
        print(f"🎯 {game_type} 推荐生成")
        print(f"{'='*60}")
        
        # 获取热号和位置热号
        hot_numbers, cold_numbers = self.get_hot_numbers(df)
        pos_hot = self.get_position_hot(df)
        
        print(f"\n📊 热号：{hot_numbers}")
        print(f"📊 冷号：{cold_numbers}")
        print(f"📍 位置热号：{pos_hot}")
        
        # 生成精选2注（核心：排除试机号开机号）
        recommendations = []
        strategies = []
        
        # 策略1：热号组合
        max_attempts = 100
        attempts = 0
        while attempts < max_attempts:
            rec1 = [pos_hot[0][0], pos_hot[1][1], pos_hot[2][2]]
            if not self.is_excluded(rec1):
                recommendations.append(rec1)
                strategies.append("热号组合")
                break
            attempts += 1
            
        # 策略2：冷热搭配
        attempts = 0
        while attempts < max_attempts:
            rec2 = [hot_numbers[0], cold_numbers[0], hot_numbers[1]]
            if not self.is_excluded(rec2) and rec2 not in recommendations:
                recommendations.append(rec2)
                strategies.append("冷热搭配")
                break
            attempts += 1
            
        # 如果无法生成不重复的，使用备选方案
        if len(recommendations) < 2:
            print("⚠️  警告：无法生成完全独立的推荐，使用备选方案")
            # 使用随机偏移
            for i in range(2 - len(recommendations)):
                offset = (i + 1) * 2
                rec = [(hot_numbers[0] + offset) % 10, 
                       (hot_numbers[1] + offset) % 10,
                       (hot_numbers[2] + offset) % 10]
                if not self.is_excluded(rec):
                    recommendations.append(rec)
                    strategies.append("偏移调整")
                    
        # 打印推荐
        print(f"\n⭐ 精选2注：")
        for i, (nums, strategy) in enumerate(zip(recommendations, strategies), 1):
            s = sum(nums)
            sp = max(nums) - min(nums)
            form = "豹子" if len(set(nums)) == 1 else "组三" if len(set(nums)) == 2 else "组六"
            print(f"\n   推荐{i}：{nums[0]}{nums[1]}{nums[2]}")
            print(f"   ├─ 和值：{s} | 跨度：{sp} | 形态：{form}")
            print(f"   └─ 策略：{strategy}")
            
        # 验证排除
        print(f"\n✅ 验证：")
        for nums in recommendations:
            if self.is_excluded(nums):
                print(f"   ❌ 错误：{nums} 在排除列表中！")
            else:
                print(f"   ✅ {nums} 不在排除列表中")
                
        return recommendations
        
    def generate_30_base(self, df):
        """生成30注大底（排除试机号开机号）"""
        pos_hot = self.get_position_hot(df)
        base_30 = []
        
        random.seed(2026081)
        for i in range(30):
            attempts = 0
            while attempts < 50:
                nums = [
                    random.choice(pos_hot[0] + [random.randint(0,9)]),
                    random.choice(pos_hot[1] + [random.randint(0,9)]),
                    random.choice(pos_hot[2] + [random.randint(0,9)])
                ]
                if not self.is_excluded(nums) and nums not in base_30:
                    base_30.append(nums)
                    break
                attempts += 1
                
        return base_30


def main():
    """主程序"""
    print("="*60)
    print("🎲 彩票分析系统 V3")
    print("="*60)
    print("\n📋 核心规则：")
    print("   ⭐ 试机号/开机号仅作为参考")
    print("   ⭐ 精选推荐不得与试机号/开机号重复")
    print("="*60)
    
    analyzer = LotteryAnalyzer()
    
    # 排列三分析
    print("\n" + "="*60)
    print("📊 排列三 2026081期")
    print("="*60)
    
    today_test_pl3 = [6, 3, 1]
    today_boot_pl3 = [0, 6, 1]
    
    analyzer.set_excluded_numbers(today_test_pl3, today_boot_pl3)
    recs_pl3 = analyzer.generate_recommendations(analyzer.pl3_data, "排列三")
    base_30_pl3 = analyzer.generate_30_base(analyzer.pl3_data)
    
    print(f"\n📋 30注大底：")
    for i, nums in enumerate(base_30_pl3):
        print(f"   {i+1:2d}. {nums[0]}{nums[1]}{nums[2]}", end="")
        if (i+1) % 5 == 0:
            print()
        else:
            print("  ", end="")
            
    # 福彩3D分析
    print("\n\n" + "="*60)
    print("📊 福彩3D 2026081期")
    print("="*60)
    
    today_test_fc3d = [7, 3, 0]
    today_boot_fc3d = [3, 0, 1]
    
    analyzer.set_excluded_numbers(today_test_fc3d, today_boot_fc3d)
    recs_fc3d = analyzer.generate_recommendations(analyzer.fc3d_data, "福彩3D")
    base_30_fc3d = analyzer.generate_30_base(analyzer.fc3d_data)
    
    print(f"\n📋 30注大底：")
    for i, nums in enumerate(base_30_fc3d):
        print(f"   {i+1:2d}. {nums[0]}{nums[1]}{nums[2]}", end="")
        if (i+1) % 5 == 0:
            print()
        else:
            print("  ", end="")
            
    print("\n\n" + "="*60)
    print("✅ 分析完成！所有推荐已排除试机号/开机号")
    print("="*60)


if __name__ == "__main__":
    main()
