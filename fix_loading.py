#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复加载状态"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace loadData to handle errors better
old_load = '''async function loadData() {
            try {
                const res = await fetch('today_result.json');
                data = await res.json();
                updateUI();
                updatePeriod();
            } catch (e) {
                console.log('Loading default data');
            }
            
            try {
                const res2 = await fetch('stats.json');
                historyData = await res2.json();
                updateStats();
            } catch (e) {
                console.log('No stats data');
            }
            
            updateHotList();
            updateSumChart();
        }'''

new_load = '''async function loadData() {
            try {
                const res = await fetch('today_result.json?t=' + Date.now());
                if (res.ok) {
                    data = await res.json();
                    updateUI();
                    updatePeriod();
                } else {
                    console.log('Failed to load today_result.json');
                    loadDefaultData();
                }
            } catch (e) {
                console.log('Error loading data:', e);
                loadDefaultData();
            }
            
            try {
                const res2 = await fetch('stats.json?t=' + Date.now());
                if (res2.ok) {
                    historyData = await res2.json();
                    updateStats();
                }
            } catch (e) {
                console.log('No stats data');
            }
            
            updateHotList();
            updateSumChart();
        }
        
        function loadDefaultData() {
            // 默认数据
            data = {
                period: '2026092',
                pl3: {
                    selected_2: ['886', '881'],
                    backup_3: ['286', '686', '888'],
                    gold_dan: 8,
                    silver_dan: 2,
                    double_dan: ['82', '28'],
                    key_sum: [14, 16, 15]
                },
                fc3d: {
                    selected_2: ['875', '873'],
                    backup_3: ['874', '878', '974'],
                    gold_dan: 7,
                    silver_dan: 8,
                    double_dan: ['78', '87'],
                    key_sum: [17, 10, 9]
                }
            };
            updateUI();
            updatePeriod();
        }'''

content = content.replace(old_load, new_load)

# Also fix the countdown area text
content = content.replace('加载中...', '等待加载...')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
