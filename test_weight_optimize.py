#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权重优化测试 - 让各方法灵活配合
"""

import pandas as pd
from collections import Counter
import random
from itertools import product

print('='*70)
print('权重优化测试 - 各方法灵活配合')
print('='*70)

df = pd.read_csv('pl3_full.csv')
print('数据加载完成，共%d期' % len(df))

# ============================================================
# 方法实现
# ============================================================
def get_334(last_nums):
    n1, n2, n3 = last_nums
    st = (n1+n2+n3)%10
    if st in [0,5]: g1,g2,g3=[0,1,9],[4,5,6],[2,3,7,8]
    elif st in [1,6]: g1,g2,g3=[0,1,2],[5,6,7],[3,4,8,9]
    elif st in [2,7]: g1,g2,g3=[1,2,3],[6,7,8],[0,4,5,9]
    elif st in [3,8]: g1,g2,g3=[2,3,4],[7,8,9],[0,1,5,6]
    else: g1,g2,g3=[3,4,5],[8,9,0],[1,2,6,7]
    return g1,g2,g3

def method_334(df_train):
    last = df_train.iloc[-1]
    ln = [int(last['num1']), int(last['num2']), int(last['num3'])]
    g1,g2,g3 = get_334(tuple(ln))
    an = []
    for _,r in df_train.tail(10).iterrows():
        an.extend([int(r['num1']),int(r['num2']),int(r['num3'])])
    c = sorted([(g1,sum(1 for n in an if n in g1)),(g2,sum(1 for n in an if n in g2)),(g3,sum(1 for n in an if n in g3))], key=lambda x:x[1], reverse=True)
    s={d:0 for d in range(10)}
    for d in c[0][0]: s[d]=14
    for d in c[1][0]: s[d]=10
    for d in c[2][0]: s[d]=2
    return s

def method_hot(df_train):
    an = []
    for _,r in df_train.tail(10).iterrows():
        an.extend([int(r['num1']),int(r['num2']),int(r['num3'])])
    ct = Counter(an)
    s={d:0 for d in range(10)}
    for d,cnt in ct.items(): s[d]=cnt
    return s

def method_lin_gua(df_train):
    last = df_train.iloc[-1]
    ln = [int(last['num1']), int(last['num2']), int(last['num3'])]
    ch,li=set(ln),set()
    for n in ln:
        if n>0: li.add(n-1)
        if n<9: li.add(n+1)
    s={d:0 for d in range(10)}
    for d in ch: s[d]=3
    for d in li: s[d]=4
    return s

def method_banshun(df_train):
    def is_b(ns):
        n1,n2,n3=sorted(ns)
        return abs(n1-n2)==1 or abs(n2-n3)==1 or abs(n1-n3)==1
    s={d:0 for d in range(10)}
    for _,r in df_train.tail(50).iterrows():
        ns=[int(r['num1']),int(r['num2']),int(r['num3'])]
        if is_b(ns):
            for d in ns: s[d]+=1
    return s

def method_wanneng(df_train):
    W6=[[0,1,2,3,4,5],[0,1,2,3,6,7],[0,1,2,3,8,9],[0,1,4,5,6,7],[0,1,4,5,8,9],[0,1,6,7,8,9],[2,3,4,5,6,7],[2,3,4,5,8,9],[2,3,6,7,8,9],[4,5,6,7,8,9]]
    an = []
    for _,r in df_train.tail(10).iterrows():
        an.extend([int(r['num1']),int(r['num2']),int(r['num3'])])
    ct = Counter(an)
    hot=[d for d,cnt in ct.items() if cnt>=3]
    if not hot: hot=[d for d,cnt in ct.most_common(2)]
    bg,bs=None,-1
    for g in W6:
        m=sum(1 for h in hot if h in g)
        if m>bs: bs,bg=m,g
    s={d:0 for d in range(10)}
    if bg:
        for d in bg: s[d]=5
    return s

def method_liangma(df_train):
    last = df_train.iloc[-1]
    n1,n2,n3 = int(last['num1']), int(last['num2']), int(last['num3'])
    lm=[(n1+n2)%10,(n1+n3)%10,(n2+n3)%10,abs(n1-n2),abs(n1-n3),abs(n2-n3),(n1+n2)//10,(n1+n3)//10,(n2+n3)//10]
    ct = Counter(lm)
    s={d:0 for d in range(10)}
    for d,cnt in ct.items(): s[d]=cnt
    return s

def method_sum_tail(df_train):
    sums = []
    for _, r in df_train.tail(30).iterrows():
        s = int(r['num1']) + int(r['num2']) + int(r['num3'])
        sums.append(s % 10)
    sum_count = Counter(sums)
    hot_sums = [n for n, c in sum_count.most_common(3)]
    result = []
    for tail in hot_sums:
        result.append(tail)
        result.append((tail + 5) % 10)
    s={d:0 for d in range(10)}
    for d in set(result): s[d]=7
    return s

# ============================================================
# 综合预测
# ============================================================
def predict_weights(df_train, w334, whot, wlin, wban, wwan, wlia, wsum):
    """可调权重的综合预测"""
    s={d:0 for d in range(10)}
    
    for d,sc in method_334(df_train).items(): s[d] += sc * w334 / 10
    for d,sc in method_hot(df_train).items(): s[d] += sc * whot / 10
    for d,sc in method_lin_gua(df_train).items(): s[d] += sc * wlin / 10
    for d,sc in method_banshun(df_train).items(): s[d] += sc * wban / 10
    for d,sc in method_wanneng(df_train).items(): s[d] += sc * wwan / 10
    for d,sc in method_liangma(df_train).items(): s[d] += sc * wlia / 10
    for d,sc in method_sum_tail(df_train).items(): s[d] += sc * wsum / 10
    
    return [n for n,sc in sorted(s.items(), key=lambda x:x[1], reverse=True)[:5]]

def test_weights(w334, whot, wlin, wban, wwan, wlia, wsum):
    random.seed(42)
    r=[]
    for i in range(100, 5100):
        dt=df.iloc[max(0,i-500):i]
        if len(dt)<100: continue
        rl=set([int(df.iloc[i]['num1']),int(df.iloc[i]['num2']),int(df.iloc[i]['num3'])])
        p=set(predict_weights(dt, w334, whot, wlin, wban, wwan, wlia, wsum))
        r.append(len(rl&p)==len(rl))
    return sum(r)/len(r)*100

# ============================================================
# 测试不同权重组合
# ============================================================
print('\n测试不同权重组合...\n')

# 当前权重
print('当前配置:')
print('w334=14, whot=3, wlin=4, wban=1, wwan=5, wlia=2, wsum=7')
r1 = test_weights(14, 3, 4, 1, 5, 2, 7)
print('命中率: %.2f%%\n' % r1)

# 测试不同组合
configs = [
    # (w334, whot, wlin, wban, wwan, wlia, wsum, 描述)
    (14, 3, 4, 1, 5, 2, 7, '当前配置'),
    (15, 3, 5, 1, 5, 2, 8, '加和值尾'),
    (16, 3, 5, 1, 5, 2, 8, '再加334'),
    (14, 4, 5, 2, 5, 3, 8, '均衡提升'),
    (14, 5, 6, 2, 6, 3, 9, '全部提升'),
    (12, 3, 4, 1, 5, 2, 6, '降低334'),
    (14, 3, 4, 1, 6, 2, 7, '加万能六码'),
    (14, 3, 4, 2, 5, 2, 7, '加半顺'),
    (14, 3, 5, 1, 5, 2, 7, '加邻孤传'),
    (14, 3, 4, 1, 5, 3, 7, '加两码'),
    (13, 4, 4, 1, 5, 2, 7, '微调334'),
    (14, 4, 4, 1, 5, 2, 7, '微调热号'),
]

print('| 序号 | 配置 | 命中率 | 提升 |')
print('|------|------|--------|------|')

best_rate = 0
best_config = None

for i, (w334, whot, wlin, wban, wwan, wlia, wsum, desc) in enumerate(configs, 1):
    rate = test_weights(w334, whot, wlin, wban, wwan, wlia, wsum)
    diff = rate - r1
    print('| %d | %s | %.2f%% | %+.2f%% |' % (i, desc, rate, diff))
    
    if rate > best_rate:
        best_rate = rate
        best_config = (w334, whot, wlin, wban, wwan, wlia, wsum, desc)

print()
print('='*70)
print('最佳配置')
print('='*70)
print()
print('配置: %s' % best_config[7])
print('命中率: %.2f%%' % best_rate)
print('权重: w334=%d, whot=%d, wlin=%d, wban=%d, wwan=%d, wlia=%d, wsum=%d' % best_config[:7])
print()
print('='*70)