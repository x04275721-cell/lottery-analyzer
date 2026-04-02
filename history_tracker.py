#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""历史记录追踪器"""

import pandas as pd
import json
import os
from datetime import datetime

def check_hits(recommend, real):
    """检查是否命中"""
    rec_set = set(recommend)
    real_set = set(real)
    
    if recommend == real:
        return 'direct'
    if rec_set == real_set:
        return 'group'
    if len(rec_set & real_set) >= 2:
        return 'partial'
    return 'miss'

def update_history():
    """更新历史记录"""
    if not os.path.exists('today_result.json'):
        print('today_result.json not found')
        return {'pl3': [], 'fc3d': []}
    
    with open('today_result.json', 'r', encoding='utf-8') as f:
        today = json.load(f)
    
    history_file = 'history_records.json'
    
    # 初始化
    history = {'pl3': [], 'fc3d': []}
    
    # 读取现有历史
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                raw = f.read()
            if raw:
                history = json.loads(raw)
                if isinstance(history, dict) and 'pl3' in history:
                    pass
                else:
                    history = {'pl3': [], 'fc3d': []}
        except:
            history = {'pl3': [], 'fc3d': []}
    
    current_period = today.get('period', '')
    
    for lottery in ['pl3', 'fc3d']:
        existing = [h for h in history.get(lottery, []) if h.get('period') == current_period]
        if existing:
            print('Period %s already recorded for %s' % (current_period, lottery))
            continue
        
        last_draw = today.get('last_draw', {}).get(lottery, '')
        if not last_draw:
            print('No draw result for %s' % lottery)
            continue
        
        rec_data = today.get(lottery, {})
        all_recommend = rec_data.get('selected_2', []) + rec_data.get('backup_3', [])
        
        real_nums = list(map(int, list(last_draw)))
        hit_type = 'miss'
        for rec in all_recommend:
            result = check_hits(list(map(int, list(rec))), real_nums)
            if result == 'direct':
                hit_type = 'direct'
                break
            elif result == 'group':
                hit_type = 'group'
                break
            elif result == 'partial':
                hit_type = 'partial'
        
        record = {
            'period': current_period,
            'date': today.get('date', ''),
            'last_draw': last_draw,
            'recommend': all_recommend,
            'hit': hit_type,
            'gold_dan': str(rec_data.get('gold_dan', '')),
            'silver_dan': str(rec_data.get('silver_dan', ''))
        }
        
        if lottery not in history:
            history[lottery] = []
        history[lottery].insert(0, record)
        history[lottery] = history[lottery][:100]
    
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    
    print('History updated!')
    return history

def get_stats(history):
    """计算统计"""
    stats = {}
    for lottery in ['pl3', 'fc3d']:
        records = history.get(lottery, [])
        if not records:
            stats[lottery] = {'total': 0, 'direct': 0, 'group': 0, 'partial': 0}
            continue
        
        total = len(records)
        direct = len([r for r in records if r.get('hit') == 'direct'])
        group = len([r for r in records if r.get('hit') == 'group'])
        partial = len([r for r in records if r.get('hit') == 'partial'])
        
        recent10 = records[:min(10, len(records))]
        recent_group = len([r for r in recent10 if r.get('hit') == 'group'])
        recent_partial = len([r for r in recent10 if r.get('hit') == 'partial'])
        
        stats[lottery] = {
            'total': total,
            'direct': direct,
            'group': group,
            'partial': partial,
            'direct_rate': direct / total * 100,
            'group_rate': group / total * 100,
            'partial_rate': partial / total * 100,
            'recent10_group': recent_group,
            'recent10_partial': recent_partial
        }
    
    return stats

# 运行
history = update_history()
stats = get_stats(history)

print('')
print('='*60)
print('统计报告')
print('='*60)

for lottery in ['pl3', 'fc3d']:
    name = '排列三' if lottery == 'pl3' else '3D'
    s = stats.get(lottery, {})
    print('')
    print('[%s]' % name)
    print('总预测: %d期' % s.get('total', 0))
    print('直选命中: %d次 (%.1f%%)' % (s.get('direct', 0), s.get('direct_rate', 0)))
    print('组选命中: %d次 (%.1f%%)' % (s.get('group', 0), s.get('group_rate', 0)))
    print('2个相同: %d次 (%.1f%%)' % (s.get('partial', 0), s.get('partial_rate', 0)))
    print('最近10期: 组选%d次, 2个相同%d次' % (s.get('recent10_group', 0), s.get('recent10_partial', 0)))

# 保存统计
with open('stats.json', 'w', encoding='utf-8') as f:
    json.dump({'stats': stats}, f, ensure_ascii=False, indent=2)
print('')
print('统计数据已保存')
