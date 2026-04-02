#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""收集完整历史数据"""

import requests
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("收集完整历史数据")
print("="*60)

# 排列三
print("\n[1] 正在获取排列三历史数据...")
try:
    resp = requests.get('http://data.17500.cn/pl3_asc.txt', timeout=30)
    if resp.status_code == 200:
        lines = resp.text.strip().split('\n')
        print("   获取到 {} 行原始数据".format(len(lines)))
        
        data = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 6:
                issue = parts[0]
                n1, n2, n3 = parts[1], parts[2], parts[3]
                s = int(n1) + int(n2) + int(n3)
                sp = max(int(n1),int(n2),int(n3)) - min(int(n1),int(n2),int(n3))
                typ = '豹子' if n1==n2==n3 else ('组三' if n1==n2 or n1==n3 or n2==n3 else '组六')
                data.append({
                    '期号': issue,
                    'num1': int(n1),
                    'num2': int(n2),
                    'num3': int(n3),
                    '和值': s,
                    '跨度': sp,
                    '类型': typ
                })
        
        df = pd.DataFrame(data)
        df.to_csv('pl3_full.csv', index=False, encoding='utf-8')
        print("   [OK] 已保存 {} 期排列三数据".format(len(df)))
        print("   最新：{}，最老：{}".format(df.iloc[0]['期号'], df.iloc[-1]['期号']))
except Exception as e:
    print("   [FAIL] {}".format(e))

# 3D
print("\n[2] 正在获取3D历史数据...")
try:
    resp = requests.get('http://data.17500.cn/3d_asc.txt', timeout=30)
    if resp.status_code == 200:
        lines = resp.text.strip().split('\n')
        print("   获取到 {} 行原始数据".format(len(lines)))
        
        data = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) >= 6:
                issue = parts[0]
                n1, n2, n3 = parts[1], parts[2], parts[3]
                s = int(n1) + int(n2) + int(n3)
                sp = max(int(n1),int(n2),int(n3)) - min(int(n1),int(n2),int(n3))
                typ = '豹子' if n1==n2==n3 else ('组三' if n1==n2 or n1==n3 or n2==n3 else '组六')
                data.append({
                    '期号': issue,
                    'num1': int(n1),
                    'num2': int(n2),
                    'num3': int(n3),
                    '和值': s,
                    '跨度': sp,
                    '类型': typ
                })
        
        df = pd.DataFrame(data)
        df.to_csv('fc3d_5years.csv', index=False, encoding='utf-8')
        print("   [OK] 已保存 {} 期3D数据".format(len(df)))
        print("   最新：{}，最老：{}".format(df.iloc[0]['期号'], df.iloc[-1]['期号']))
except Exception as e:
    print("   [FAIL] {}".format(e))

print("\n" + "="*60)
print("[OK] 历史数据收集完成!")
print("="*60)
