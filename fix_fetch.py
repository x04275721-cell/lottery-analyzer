#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复fetch超时"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace loadData with timeout
old_load = '''async function loadData() {
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
        }'''

new_load = '''async function fetchWithTimeout(url, timeout = 3000) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), timeout);
                const res = await fetch(url, { signal: controller.signal });
                clearTimeout(timeoutId);
                return res;
            } catch (e) {
                return null;
            }
        }
        
        async function loadData() {
            // 先显示默认数据
            loadDefaultData();
            
            // 异步加载真实数据
            const res = await fetchWithTimeout('today_result.json?t=' + Date.now(), 5000);
            if (res && res.ok) {
                try {
                    data = await res.json();
                    updateUI();
                    updatePeriod();
                } catch (e) {
                    console.log('JSON parse error');
                }
            }
            
            const res2 = await fetchWithTimeout('stats.json?t=' + Date.now(), 5000);
            if (res2 && res2.ok) {
                try {
                    historyData = await res2.json();
                    updateStats();
                } catch (e) {
                    console.log('Stats JSON error');
                }
            }
            
            updateHotList();
            updateSumChart();
        }'''

content = content.replace(old_load, new_load)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
