#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的彩票分析系统 V2
包含：马尔可夫链 + 跨度和值分析 + 精选2注 + 30注大底
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import json

class LotteryAnalyzer:
    """彩票综合分析器"""
    
    def __init__(self, data_file, name):
        self.name = name
        self.df = pd.read_csv(data_file)
        self.df = self.df.sort_values('期号', ascending=False).reset_index(drop=True)
        
        # 计算特征
        self.df['sum_zone'] = self.df['和值'].apply(lambda x: 'L' if x<=9 else ('M' if x<=17 else 'H'))
        self.df['span_zone'] = self.df['跨度'].apply(lambda x: 'S' if x<=3 else ('M' if x<=6 else 'L'))
        
    def get_recent(self, n=3):
        """获取最近n期数据"""
        return self.df.head(n)
    
    def markov_predict(self, col, order=3):
        """马尔可夫链预测"""
        seq = self.df[col].astype(int).tolist()
        
        # 构建转移矩阵
        transitions = defaultdict(Counter)
        for i in range(len(seq) - order):
            past = tuple(seq[i:i+order])
            next_val = seq[i + order]
            transitions[past][next_val] += 1
        
        # 预测
        recent = tuple(seq[:order])
        if recent in transitions:
            total = sum(transitions[recent].values())
            probs = {k: v/total for k, v in transitions[recent].items()}
            sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
            return sorted_probs[:5], total
        return None, 0
    
    def sum_analysis(self):
        """和值分析"""
        recent_sums = self.df.head(10)['和值'].tolist()
        freq = Counter(self.df['sum_zone'])
        total = len(self.df)
        
        return {
            'recent': recent_sums,
            'distribution': {k: v/total for k, v in freq.items()},
            'trend': self.df.head(20)['sum_zone'].tolist()
        }
    
    def span_analysis(self):
        """跨度分析"""
        recent_spans = self.df.head(10)['跨度'].tolist()
        freq = Counter(self.df['span_zone'])
        total = len(self.df)
        
        return {
            'recent': recent_spans,
            'distribution': {k: v/total for k, v in freq.items()},
            'trend': self.df.head(20)['span_zone'].tolist()
        }
    
    def generate_top2(self, latest_data):
        """生成精选2注"""
        # 马尔可夫预测各位置
        bai_pred, _ = self.markov_predict('num1')
        shi_pred, _ = self.markov_predict('num2')
        ge_pred, _ = self.markov_predict('num3')
        
        results = []
        
        # 第1注：马尔可夫最高概率
        if bai_pred and shi_pred and ge_pred:
            r1 = "{}{}{}".format(
                bai_pred[0][0],
                shi_pred[0][0],
                ge_pred[0][0]
            )
            results.append(r1)
        
        # 第2注：结合试机号
        shiji = latest_data.get('试机号', [])
        if shiji and bai_pred and shi_pred and ge_pred:
            # 选择试机号中概率最高的
            bai_options = [b[0] for b in bai_pred[:3]]
            shi_options = [s[0] for s in shi_pred[:3]]
            ge_options = [g[0] for g in ge_pred[:3]]
            
            # 结合试机号
            bai_choice = shiji[0] if shiji[0] in bai_options else bai_options[0]
            shi_choice = shiji[1] if len(shiji) > 1 and shiji[1] in shi_options else shi_options[0]
            ge_choice = shiji[2] if len(shiji) > 2 and shiji[2] in ge_options else ge_options[0]
            
            r2 = "{}{}{}".format(bai_choice, shi_choice, ge_choice)
            results.append(r2)
        
        return results
    
    def generate_30_dan(self, latest_data):
        """生成30注大底"""
        candidates = set()
        
        # 马尔可夫各位置TOP3
        bai_pred, _ = self.markov_predict('num1')
        shi_pred, _ = self.markov_predict('num2')
        ge_pred, _ = self.markov_predict('num3')
        
        if bai_pred and shi_pred and ge_pred:
            bai_nums = [b[0] for b in bai_pred[:5]]
            shi_nums = [s[0] for s in shi_pred[:5]]
            ge_nums = [g[0] for g in ge_pred[:5]]
            
            # 生成所有组合
            for b in bai_nums:
                for s in shi_nums:
                    for g in ge_nums:
                        if len({b, s, g}) == 3:  # 组六
                            candidates.add(tuple(sorted([b, s, g])))
            
            # 结合试机号
            shiji = latest_data.get('试机号', [])
            for s in shiji:
                for b in bai_nums[:3]:
                    for g in ge_nums[:3]:
                        if b != s and g != s:
                            candidates.add(tuple(sorted([b, s, g])))
            
            # 结合关注码
            guanzhu = latest_data.get('关注码', [])
            for g in guanzhu:
                for b in bai_nums[:3]:
                    for s in shi_nums[:3]:
                        if b != g and s != g:
                            candidates.add(tuple(sorted([b, s, g])))
        
        # 返回前30注
        return ["{}{}{}".format(*c) for c in list(candidates)[:30]]
    
    def full_analysis(self, latest_data):
        """完整分析报告"""
        report = {
            'name': self.name,
            'data_count': len(self.df),
            'latest': {
                'period': str(self.df.iloc[0]['期号']),
                'numbers': [int(self.df.iloc[0]['num1']), int(self.df.iloc[0]['num2']), int(self.df.iloc[0]['num3'])],
                'sum': int(self.df.iloc[0]['和值']),
                'span': int(self.df.iloc[0]['跨度']),
                'shape': self.df.iloc[0]['形态']
            },
            'bai': {
                'recent': self.df.head(3)['num1'].astype(int).tolist(),
                'pred': [(int(n), float(p)) for n, p in self.markov_predict('num1')[0]] if self.markov_predict('num1')[0] else []
            },
            'shi': {
                'recent': self.df.head(3)['num2'].astype(int).tolist(),
                'pred': [(int(n), float(p)) for n, p in self.markov_predict('num2')[0]] if self.markov_predict('num2')[0] else []
            },
            'ge': {
                'recent': self.df.head(3)['num3'].astype(int).tolist(),
                'pred': [(int(n), float(p)) for n, p in self.markov_predict('num3')[0]] if self.markov_predict('num3')[0] else []
            },
            'sum_analysis': self.sum_analysis(),
            'span_analysis': self.span_analysis(),
            'top2': self.generate_top2(latest_data),
            'dan30': self.generate_30_dan(latest_data)
        }
        
        return report

def main():
    # 加载分析器
    fc3d = LotteryAnalyzer('/workspace/fc3d_5years.csv', 'fc3d')
    pl3 = LotteryAnalyzer('/workspace/pl3_real.csv', 'pl3')
    
    # 最新数据
    FC3D_LATEST = {
        '试机号': [2, 7, 2],
        '关注码': [0, 1, 4]
    }
    
    PL3_LATEST = {
        '试机号': [9, 7, 8],
        '开机号': [7, 1, 5]
    }
    
    # 生成报告
    fc3d_report = fc3d.full_analysis(FC3D_LATEST)
    pl3_report = pl3.full_analysis(PL3_LATEST)
    
    # 保存JSON
    with open('/workspace/analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump({
            'fc3d': fc3d_report,
            'pl3': pl3_report
        }, f, ensure_ascii=False, indent=2)
    
    print("分析报告已生成: /workspace/analysis_report.json")
    
    # 打印摘要
    print("\n" + "="*60)
    print("📊 彩票分析系统 V2 - 分析结果")
    print("="*60)
    
    for report in [fc3d_report, pl3_report]:
        name = "🏀 福彩3D" if report['name'] == 'fc3d' else "🎱 排列三"
        print(f"\n{name}")
        print("-"*40)
        print(f"数据量: {report['data_count']}期")
        print(f"上期: {''.join(map(str, report['latest']['numbers']))} (和值{report['latest']['sum']}, 跨度{report['latest']['span']})")
        print(f"精选2注: {', '.join(report['top2'])}")
        print(f"30注大底: {', '.join(report['dan30'][:10])}...")
    
    return fc3d_report, pl3_report

if __name__ == "__main__":
    main()
