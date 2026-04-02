#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复倒计时显示"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the countdown area
old = '<div class="countdown" id="countdownArea"><span id="countdownText">加载中...</span></div>'
new = '''<div class="countdown-area">
                <div class="lottery-status" id="pl3Status">
                    <span class="lottery-name pl3">排列三</span>
                    <span class="lottery-countdown" id="pl3Countdown">加载中...</span>
                </div>
                <div class="lottery-status" id="fc3dStatus">
                    <span class="lottery-name fc3d">3D</span>
                    <span class="lottery-countdown" id="fc3dCountdown">加载中...</span>
                </div>
            </div>'''

content = content.replace(old, new)

# Replace the JS updateCountdown function
old_js = '''function updateCountdown() {
            const now = new Date();
            let target = new Date();
            target.setHours(21, 15, 0, 0);
            if (now > target) target.setDate(target.getDate() + 1);
            
            const diff = target - now;
            const hours = Math.floor(diff / 3600000);
            const minutes = Math.floor((diff % 3600000) / 60000);
            const seconds = Math.floor((diff % 60000) / 1000);
            
            document.getElementById('countdown').textContent = 
                hours.toString().padStart(2,'0') + ':' +
                minutes.toString().padStart(2,'0') + ':' +
                seconds.toString().padStart(2,'0');
        }'''

new_js = '''function updateCountdown() {
            const now = new Date();
            
            // 排列三（体彩）倒计时 - 21:25开奖
            let pl3Target = new Date();
            pl3Target.setHours(21, 25, 0, 0);
            if (now > pl3Target) pl3Target.setDate(pl3Target.getDate() + 1);
            
            let pl3Diff = pl3Target - now;
            let pl3Hours = Math.floor(pl3Diff / 3600000);
            let pl3Minutes = Math.floor((pl3Diff % 3600000) / 60000);
            let pl3Seconds = Math.floor((pl3Diff % 60000) / 1000);
            
            document.getElementById('pl3Countdown').textContent = 
                pl3Hours.toString().padStart(2,'0') + ':' +
                pl3Minutes.toString().padStart(2,'0') + ':' +
                pl3Seconds.toString().padStart(2,'0');
            
            // 3D（福彩）倒计时 - 21:15开奖
            let fc3dTarget = new Date();
            fc3dTarget.setHours(21, 15, 0, 0);
            if (now > fc3dTarget) fc3dTarget.setDate(fc3dTarget.getDate() + 1);
            
            let fc3dDiff = fc3dTarget - now;
            let fc3dHours = Math.floor(fc3dDiff / 3600000);
            let fc3dMinutes = Math.floor((fc3dDiff % 3600000) / 60000);
            let fc3dSeconds = Math.floor((fc3dDiff % 60000) / 1000);
            
            document.getElementById('fc3dCountdown').textContent = 
                fc3dHours.toString().padStart(2,'0') + ':' +
                fc3dMinutes.toString().padStart(2,'0') + ':' +
                fc3dSeconds.toString().padStart(2,'0');
        }'''

content = content.replace(old_js, new_js)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
