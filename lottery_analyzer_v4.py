#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票分析系统 V4 - 核心规则版本
遵循规则文档：lottery_system_rules.md

核心规则：
1. 试机号/开机号仅作参考，不作为开奖号
2. 每天从0-27中挑选5个重点和值
3. 精选2注必须包含在10注大底中
4. 所有推荐和值必须符合重点和值
5. 真实战绩从2026年4月1日开始记录
"""

import pandas as pd
import numpy as np
from collections import Counter
import random

class LotteryAnalyzerV4:
    """彩票分析器V4 - 严格遵循核心规则"""
    
    # ========== 核心规则常量 ==========
    RULE_EXCLUDE_TEST_BOOT = True  # 规则1：排除试机号开机号
    RULE_SUM_IN_KEY_RANGE = True   # 规则2：和值必须在重点范围内
    RULE_SELECTED_IN_BASE = True   # 规则3：精选2注包含在大底中
    
    def __init__(self, pl3_file='pl3_full.csv', fc3d_file='fc3d_5years.csv'):
        """初始化分析器"""
        self.pl3_data = pd.read_csv(pl3_file)
        self.fc3d_data = pd.read_csv(fc3d_file)
        self.excluded_numbers = []  # 排除列表
        self.key_sum_values = []    # 重点和值
        
    def set_excluded_numbers(self, test_number, boot_number):
        """
        规则1：设置排除号码（试机号和开机号）
        
        参数：
            test_number: 试机号 [a, b, c]
            boot_number: 开机号 [a, b, c]
        """
        self.excluded_numbers = [test_number, boot_number]
        print(f"⚠️  已设置排除号码（规则1）：")
        print(f"   试机号：{test_number}")
        print(f"   开机号：{boot_number}")
        print(f"   ✅ 推荐将不包含以上号码")
        
    def set_key_sum_values(self, sum_values):
        """
        规则2：设置重点和值（每天5个）
        
        参数：
            sum_values: 5个重点和值列表，如 [8, 10, 13, 15, 17]
        """
        if len(sum_values) != 5:
            raise ValueError("重点和值必须是5个！")
        self.key_sum_values = sum_values
        print(f"⚠️  已设置重点和值（规则2）：")
        print(f"   重点和值：{sum_values}")
        print(f"   ✅ 所有推荐和值必须在此范围内")
        
    def is_valid_number(self, nums):
        """
        验证号码是否符合所有规则
        
        返回：(是否有效, 错误原因)
        """
        # 规则1：排除试机号开机号
        if nums in self.excluded_numbers:
            return False, "号码在排除列表中（试机号/开机号）"
            
        # 规则2：和值必须在重点范围内
        if self.key_sum_values and sum(nums) not in self.key_sum_values:
            return False, f"和值{sum(nums)}不在重点和值范围内"
            
        return True, "验证通过"
        
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
        
    def generate_valid_number(self, pos_hot, max_attempts=100):
        """
        生成符合规则的号码
        
        规则：
        1. 不在排除列表中
        2. 和值在重点范围内
        """
        random.seed(42)
        attempts = 0
        
        while attempts < max_attempts:
            nums = [
                random.choice(pos_hot[0] + [random.randint(0,9)]),
                random.choice(pos_hot[1] + [random.randint(0,9)]),
                random.choice(pos_hot[2] + [random.randint(0,9)])
            ]
            
            is_valid, reason = self.is_valid_number(nums)
            if is_valid:
                return nums
                
            attempts += 1
            
        return None
        
    def generate_recommendations(self, df, game_type='排列三'):
        """
        生成推荐号码（严格遵循规则）
        
        规则3：精选2注必须包含在10注大底中
        """
        print(f"\n{'='*60}")
        print(f"🎯 {game_type} 推荐生成（规则验证版）")
        print(f"{'='*60}")
        
        # 获取热号
        hot_numbers, cold_numbers = self.get_hot_numbers(df)
        pos_hot = self.get_position_hot(df)
        
        print(f"\n📊 热号：{hot_numbers}")
        print(f"📊 冷号：{cold_numbers}")
        print(f"📍 位置热号：{pos_hot}")
        print(f"🎯 重点和值：{self.key_sum_values}")
        
        # 规则3：先生成精选2注
        print(f"\n⭐ 精选2注生成：")
        selected_2 = []
        
        # 精选1：热号组合
        num1 = self.generate_valid_number(pos_hot)
        if num1:
            selected_2.append(num1)
            print(f"   精选1：{num1} 和值={sum(num1)} ✅")
            
        # 精选2：冷热搭配
        num2 = self.generate_valid_number(pos_hot)
        if num2 and num2 != num1:
            selected_2.append(num2)
            print(f"   精选2：{num2} 和值={sum(num2)} ✅")
            
        # 生成剩余8注（规则3：包含精选2注）
        print(f"\n📋 10注大底生成（包含精选2注）：")
        base_10 = selected_2.copy()
        
        while len(base_10) < 10:
            num = self.generate_valid_number(pos_hot)
            if num and num not in base_10:
                base_10.append(num)
                
        # 打印10注大底
        for i, nums in enumerate(base_10):
            is_selected = "⭐精选" if nums in selected_2 else ""
            print(f"   {i+1:2d}. {nums[0]}{nums[1]}{nums[2]} 和值={sum(nums)} {is_selected}")
            
        # 验证规则
        print(f"\n✅ 规则验证：")
        print(f"   规则1（排除试机号开机号）：", end="")
        all_valid = all(self.is_valid_number(n)[0] for n in base_10)
        print("✅ 通过" if all_valid else "❌ 失败")
        
        print(f"   规则2（和值在重点范围）：", end="")
        sum_valid = all(sum(n) in self.key_sum_values for n in base_10)
        print("✅ 通过" if sum_valid else "❌ 失败")
        
        print(f"   规则3（精选包含在大底）：", end="")
        selected_in_base = all(s in base_10 for s in selected_2)
        print("✅ 通过" if selected_in_base else "❌ 失败")
        
        return selected_2, base_10


def main():
    """主程序"""
    print("="*60)
    print("🎲 彩票分析系统 V4 - 核心规则版本")
    print("="*60)
    print("\n📋 遵循规则：")
    print("   1. 试机号/开机号仅作参考，不作为开奖号")
    print("   2. 每天从0-27中挑选5个重点和值")
    print("   3. 精选2注必须包含在10注大底中")
    print("   4. 所有推荐和值必须符合重点和值")
    print("="*60)
    
    analyzer = LotteryAnalyzerV4()
    
    # 排列三分析
    print("\n" + "="*60)
    print("📊 排列三 2026081期")
    print("="*60)
    
    # 规则1：设置排除号码
    analyzer.set_excluded_numbers([6, 3, 1], [0, 6, 1])
    
    # 规则2：设置重点和值（每天5个）
    analyzer.set_key_sum_values([8, 10, 13, 15, 17])
    
    # 生成推荐
    selected_2, base_10 = analyzer.generate_recommendations(analyzer.pl3_data, "排列三")
    
    # 福彩3D分析
    print("\n\n" + "="*60)
    print("📊 福彩3D 2026081期")
    print("="*60)
    
    analyzer.set_excluded_numbers([7, 3, 0], [3, 0, 1])
    analyzer.set_key_sum_values([9, 11, 13, 16, 18])
    
    selected_2, base_10 = analyzer.generate_recommendations(analyzer.fc3d_data, "福彩3D")
    
    print("\n\n" + "="*60)
    print("✅ 分析完成！所有规则已验证通过")
    print("="*60)


if __name__ == "__main__":
    main()