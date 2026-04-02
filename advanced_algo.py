#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""高级算法系统 V9 - 混沌分形 + 机器学习"""

import pandas as pd
import random
from collections import Counter, defaultdict
import math
import sys

sys.stdout.reconfigure(encoding='utf-8')

print('='*60)
print('高级算法系统 V9 - 混沌分形 + 机器学习')
print('='*60)

pl3 = pd.read_csv('pl3_full.csv')
print('排列三总共: %d期' % len(pl3))

# ========== 基础数据准备 ==========
pl3['和值'] = pl3['num1'] + pl3['num2'] + pl3['num3']
pl3['跨度'] = pl3.apply(lambda x: max(x['num1'], x['num2'], x['num3']) - min(x['num1'], x['num2'], x['num3']), axis=1)

# ========== 算法1: 混沌分形 - 奇怪吸引子分析 ==========
def strange_attractor_score(df, nums_tuple):
    """
    奇怪吸引子分析：分析数字序列的自相似性和周期性
    """
    score = 0
    n = len(df)
    
    # 计算各数字的"吸引子距离"
    for i, d in enumerate(nums_tuple):
        col = ['num1', 'num2', 'num3'][i]
        nums = df[col].astype(int).tolist()[-100:]  # 最近100期
        
        # 计算该数字的均值和标准差
        mean = sum(nums) / len(nums)
        variance = sum((x - mean) ** 2 for x in nums) / len(nums)
        std = variance ** 0.5
        
        # 数字距离均值的程度
        distance = abs(d - mean)
        if std > 0:
            # 距离在1个标准差内得分高
            z_score = distance / std
            if z_score <= 1:
                score += 0.8 - z_score * 0.3
            else:
                score += 0.2
    
    return score / 3

# ========== 算法2: 混沌分形 - 分形维度分析 ==========
def fractal_dimension_score(df, nums_tuple):
    """
    分形维度分析：计算数字序列的盒维数近似
    """
    score = 0
    n = len(df)
    
    # 分析和值的分形特征
    sums = df['和值'].astype(int).tolist()[-50:]
    
    # 计算和值的自相似性
    if len(sums) >= 10:
        # 简单近似：计算相邻和值的差值
        diffs = [abs(sums[i] - sums[i-1]) for i in range(1, len(sums))]
        avg_diff = sum(diffs) / len(diffs) if diffs else 0
        
        # 当前和值与均值的偏离
        current_sum = sum(nums_tuple)
        sum_mean = sum(sums) / len(sums)
        sum_deviation = abs(current_sum - sum_mean)
        
        # 偏离越小，分数越高
        if sum_deviation <= avg_diff * 2:
            score += 0.7
        else:
            score += 0.3 - sum_deviation / 50
    
    return score

# ========== 算法3: 混沌分形 - 李雅普诺夫指数近似 ==========
def lyapunov_score(df, nums_tuple):
    """
    李雅普诺夫指数：衡量系统的混沌程度
    简化版：分析数字序列的收敛/发散程度
    """
    score = 0
    n = len(df)
    
    # 分析跨度
    spans = df['跨度'].astype(int).tolist()[-30:]
    span_mean = sum(spans) / len(spans) if spans else 4
    
    current_span = max(nums_tuple) - min(nums_tuple)
    span_diff = abs(current_span - span_mean)
    
    # 跨度接近均值得分高
    if span_diff <= 2:
        score += 0.8 - span_diff * 0.2
    
    # 分析奇偶分布
    odd_count = sum(1 for d in nums_tuple if d % 2 == 1)
    # 1个或2个奇数最常见
    if odd_count in [1, 2]:
        score += 0.8
    else:
        score += 0.4
    
    return score / 2

# ========== 算法4: 机器学习 - 简单决策树 ==========
class SimpleDecisionTree:
    """简化决策树：根据特征进行分类"""
    
    def __init__(self):
        self.features = []
    
    def extract_features(self, df, pos):
        """提取特征"""
        col = ['num1', 'num2', 'num3'][pos]
        nums = df[col].astype(int).tolist()
        
        # 特征1: 频率
        counter = Counter(nums)
        freq = {d: counter.get(d, 0) / len(nums) for d in range(10)}
        
        # 特征2: 遗漏值
        missing = {}
        last_seen = {}
        for i, d in enumerate(nums):
            last_seen[d] = i
        for d in range(10):
            missing[d] = len(nums) - last_seen.get(d, -1) - 1
            if missing[d] == len(nums):
                missing[d] = len(nums)  # 从未出现
        
        # 特征3: 趋势（最近vs历史）
        recent = Counter(nums[:20])
        older = Counter(nums[20:])
        trend = {}
        for d in range(10):
            r = recent.get(d, 0) / 20
            o = older.get(d, 0) / max(len(nums) - 20, 1)
            trend[d] = r - o
        
        return freq, missing, trend
    
    def predict(self, df, pos):
        """预测最可能的数字"""
        freq, missing, trend = self.extract_features(df, pos)
        
        # 综合评分
        scores = {}
        for d in range(10):
            # 频率得分（越高越好）
            freq_score = freq[d] * 50
            
            # 遗漏值得分（适中最好）
            miss = missing[d]
            if miss < 5:
                miss_score = 30 + miss * 5  # 回补预期
            elif miss < 20:
                miss_score = 50
            else:
                miss_score = 50 - (miss - 20) * 2  # 太冷
            
            # 趋势得分
            trend_score = 20 + trend.get(d, 0) * 100
            
            scores[d] = freq_score + miss_score + trend_score
        
        return scores

# ========== 算法5: 机器学习 - 随机森林简化版 ==========
class SimpleRandomForest:
    """简化随机森林：多棵决策树的集成"""
    
    def __init__(self, n_trees=10):
        self.n_trees = n_trees
        self.trees = [SimpleDecisionTree() for _ in range(n_trees)]
    
    def predict(self, df, pos):
        """集成预测"""
        all_scores = defaultdict(list)
        
        for tree in self.trees:
            scores = tree.predict(df, pos)
            for d, s in scores.items():
                all_scores[d].append(s)
        
        # 取平均
        final_scores = {}
        for d in range(10):
            if all_scores[d]:
                final_scores[d] = sum(all_scores[d]) / len(all_scores[d])
            else:
                final_scores[d] = 0.1
        
        return final_scores
    
    def predict_tuple(self, df, nums_tuple):
        """预测整个号码"""
        score = 0
        for pos, d in enumerate(nums_tuple):
            scores = self.predict(df, pos)
            score += scores.get(d, 0.1)
        return score

# ========== 算法6: 机器学习 - 梯度提升简化版 ==========
class SimpleGradientBoosting:
    """简化梯度提升：逐步优化预测"""
    
    def __init__(self, n_iterations=5):
        self.n_iterations = n_iterations
        self.models = []
        self.weights = []
    
    def fit(self, df):
        """训练模型"""
        # 简化：用频率作为基础
        self.models = []
        for pos in range(3):
            col = ['num1', 'num2', 'num3'][pos]
            counter = Counter(df[col].astype(int).tolist())
            total = sum(counter.values())
            probs = {d: counter.get(d, 0) / total for d in range(10)}
            self.models.append(probs)
    
    def predict(self, df, nums_tuple):
        """预测得分"""
        score = 0
        for pos, d in enumerate(nums_tuple):
            prob = self.models[pos].get(d, 0.01)
            score += prob
        return score

# ========== 综合评分函数 ==========
def comprehensive_score(nums_tuple, df, history):
    """综合所有算法的评分"""
    score = 0
    
    # 机器学习得分 (30%)
    gb = SimpleGradientBoosting()
    gb.fit(df)
    score += gb.predict(df, nums_tuple) * 30
    
    # 奇怪吸引子 (15%)
    score += strange_attractor_score(df, nums_tuple) * 15
    
    # 分形维度 (15%)
    score += fractal_dimension_score(df, nums_tuple) * 15
    
    # 李雅普诺夫 (15%)
    score += lyapunov_score(df, nums_tuple) * 15
    
    # 决策树集成 (15%)
    rf = SimpleRandomForest(n_trees=5)
    for pos, d in enumerate(nums_tuple):
        scores = rf.predict(df, pos)
        score += scores.get(d, 0.1) * 5
    
    # 马尔可夫基础 (10%)
    # 简化：使用频率
    freq_score = 0
    for pos, d in enumerate(nums_tuple):
        col = ['num1', 'num2', 'num3'][pos]
        counter = Counter(df[col].astype(int).tolist()[:100])
        freq = counter.get(d, 0) / 100
        freq_score += freq
    score += freq_score * 10
    
    return score

# ========== 回测 ==========
def backtest(test_count=300):
    random.seed(42)
    group_hits = 0
    partial_hits = 0
    direct_hits = 0
    total = min(test_count, len(pl3) - 500)
    
    for i in range(200, 200 + total):
        train = pl3.iloc[:i]
        
        history = [(int(pl3.iloc[i]['num1']), int(pl3.iloc[i]['num2']), int(pl3.iloc[i]['num3']))]
        real = (int(pl3.iloc[i+1]['num1']), int(pl3.iloc[i+1]['num2']), int(pl3.iloc[i+1]['num3']))
        real_set = set(real)
        
        # 生成候选
        candidates = []
        for _ in range(2000):
            nums = tuple(random.randint(0, 9) for _ in range(3))
            candidates.append(nums)
        
        # 综合评分
        scored = []
        for nums in candidates:
            s = comprehensive_score(nums, train, history)
            scored.append((nums, s))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        top5 = [n for n, s in scored[:5]]
        
        # 检查命中
        if any(set(nums) == real_set for nums in top5):
            group_hits += 1
        if any(nums == real for nums in top5):
            direct_hits += 1
        if any(len(set(nums) & real_set) >= 2 for nums in top5):
            partial_hits += 1
        
        if i % 50 == 0:
            print('进度: %d/%d' % (i - 200, total))
    
    return {
        'direct': direct_hits / total * 100,
        'group': group_hits / total * 100,
        'partial': partial_hits / total * 100
    }

# ========== 运行测试 ==========
print('\n' + '='*60)
print('混沌分形 + 机器学习 综合算法测试')
print('='*60)

print('\n正在测试（请等待）...')
r = backtest(500)

print('\n' + '='*60)
print('测试结果：')
print('='*60)
print('直选命中: %.1f%%' % r['direct'])
print('组选命中: %.1f%%' % r['group'])
print('2个相同: %.1f%%' % r['partial'])

print('\n对比理论值：')
print('直选: 0.5%%')
print('组选: 2.4%%')
print('2个相同: ~60%%')

print('\n对比原算法（马尔可夫50%+随机50%）：')
print('组选: 3.6%')
print('2个相同: 45.2%')

print('\n' + '='*60)
if r['partial'] > 45.2:
    print('✅ 2个相同提升: +%.1f%%' % (r['partial'] - 45.2))
else:
    print('❌ 2个相同下降: %.1f%%' % (r['partial'] - 45.2))

if r['group'] > 3.6:
    print('✅ 组选提升: +%.1f%%' % (r['group'] - 3.6))
else:
    print('❌ 组选下降: %.1f%%' % (r['group'] - 3.6))
print('='*60)
