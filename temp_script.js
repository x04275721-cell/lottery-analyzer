
        // 切换标签
        function switchTab(type) {
            document.querySelectorAll('.tabs .tab').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            
            document.getElementById('pl3-content').classList.add('hidden');
            document.getElementById('d3-content').classList.add('hidden');
            document.getElementById('history-content').classList.add('hidden');
            document.getElementById('methods-content').classList.add('hidden');
            
            document.getElementById(type + '-content').classList.remove('hidden');
        }
        
        // 倒计时
        function updateCountdown() {
            const now = new Date();
            const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            const drawTime = new Date(today.getTime() + 21 * 60 * 60 * 1000 + 15 * 60 * 1000);
            
            const pl3Status = document.getElementById('pl3-status');
            const d3Status = document.getElementById('d3-status');
            
            if (now < drawTime) {
                const diff = drawTime - now;
                const hours = Math.floor(diff / (1000 * 60 * 60));
                const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                
                const text = `${hours}时${minutes}分${seconds}秒`;
                document.getElementById('pl3-countdown').textContent = text;
                document.getElementById('d3-countdown').textContent = text;
                document.getElementById('pl3-countdown').className = 'lottery-countdown waiting';
                document.getElementById('d3-countdown').className = 'lottery-countdown waiting';
            } else {
                document.getElementById('pl3-countdown').textContent = '已开奖';
                document.getElementById('d3-countdown').textContent = '已开奖';
                document.getElementById('pl3-countdown').className = 'lottery-countdown closed';
                document.getElementById('d3-countdown').className = 'lottery-countdown closed';
                pl3Status.classList.add('closed');
                d3Status.classList.add('closed');
            }
        }
        
        // 加载数据
        async function loadData() {
            try {
                const response = await fetch('daily_conditions.json');
                const data = await response.json();
                
                // 更新时间
                document.getElementById('update-time').textContent = data.date;
                
                // 排列三
                const gold = data.pl3.gold_dan;
                const silver = data.pl3.silver_dan;
                const wuma = data.pl3.top5_str;
                
                document.getElementById('pl3-gold').textContent = gold;
                document.getElementById('pl3-silver').textContent = silver;
                document.getElementById('pl3-double-dan').textContent = gold + silver;
                document.getElementById('pl3-wuma').textContent = wuma;
                
                // 推荐和值跨度
                document.getElementById('pl3-sum').textContent = '12-16';
                document.getElementById('pl3-span').textContent = '4-6';
                
                // 推荐号码
                const recommendations = generateNumbers(gold, silver, wuma, 5);
                document.getElementById('pl3-rec1').textContent = recommendations[0];
                document.getElementById('pl3-rec2').textContent = recommendations[1];
                document.getElementById('pl3-rec3').textContent = recommendations[2];
                document.getElementById('pl3-rec4').textContent = recommendations[3];
                document.getElementById('pl3-rec5').textContent = recommendations[4];
                
                // 条件列表 - 排列三
                let conditionsHtml = '';
                data.pl3.methods.forEach(m => {
                    if (m.name === '334断组' && m.groups) {
                        conditionsHtml += `
                            <div class="condition-item">
                                <div class="condition-left">
                                    <span class="condition-name">${m.name}</span>
                                    <span class="condition-weight">(${m.weight})</span>
                                </div>
                                <div class="condition-right">
                                    <span class="condition-result">${m.result.join('')}</span>
                                </div>
                            </div>
                            <div class="condition-desc" style="padding-left:12px">和值尾${m.sum_tail}，保留热组</div>
                            <div class="duanzu-groups">
                                <div class="duanzu-group ${m.groups.group1.is_cold ? 'cold' : 'hot'}">
                                    <div class="group-label">第一组(3个)</div>
                                    <div class="group-nums">${m.groups.group1.nums.join('')}</div>
                                    <div class="group-count">${m.groups.group1.count}次</div>
                                </div>
                                <div class="duanzu-group ${m.groups.group2.is_cold ? 'cold' : 'hot'}">
                                    <div class="group-label">第二组(3个)</div>
                                    <div class="group-nums">${m.groups.group2.nums.join('')}</div>
                                    <div class="group-count">${m.groups.group2.count}次</div>
                                </div>
                                <div class="duanzu-group ${m.groups.group3.is_cold ? 'cold' : 'hot'}">
                                    <div class="group-label">第三组(4个)</div>
                                    <div class="group-nums">${m.groups.group3.nums.join('')}</div>
                                    <div class="group-count">${m.groups.group3.count}次</div>
                                </div>
                            </div>
                        `;
                    } else {
                        conditionsHtml += `
                            <div class="condition-item">
                                <div class="condition-left">
                                    <span class="condition-name">${m.name}</span>
                                    <span class="condition-weight">(${m.weight})</span>
                                </div>
                                <div class="condition-right">
                                    <span class="condition-result">${m.result.join('')}</span>
                                </div>
                            </div>
                            ${m.desc ? \`<div class="condition-desc" style="padding-left:12px">\${m.desc}</div>\` : ''}
                        `;
                    }
                });
                document.getElementById('pl3-conditions').innerHTML = conditionsHtml;
                
                // 3D
                const gold3d = data.d3.gold_dan;
                const silver3d = data.d3.silver_dan;
                const wuma3d = data.d3.top5_str;
                
                document.getElementById('d3-gold').textContent = gold3d;
                document.getElementById('d3-silver').textContent = silver3d;
                document.getElementById('d3-double-dan').textContent = gold3d + silver3d;
                document.getElementById('d3-wuma').textContent = wuma3d;
                
                document.getElementById('d3-sum').textContent = '12-16';
                document.getElementById('d3-span').textContent = '4-6';
                
                const recommendations3d = generateNumbers(gold3d, silver3d, wuma3d, 5);
                document.getElementById('d3-rec1').textContent = recommendations3d[0];
                document.getElementById('d3-rec2').textContent = recommendations3d[1];
                document.getElementById('d3-rec3').textContent = recommendations3d[2];
                document.getElementById('d3-rec4').textContent = recommendations3d[3];
                document.getElementById('d3-rec5').textContent = recommendations3d[4];
                
                // 条件列表 - 3D
                conditionsHtml = '';
                data.d3.methods.forEach(m => {
                    if (m.name === '334断组' && m.groups) {
                        conditionsHtml += `
                            <div class="condition-item">
                                <div class="condition-left">
                                    <span class="condition-name">${m.name}</span>
                                    <span class="condition-weight">(${m.weight})</span>
                                </div>
                                <div class="condition-right">
                                    <span class="condition-result">${m.result.join('')}</span>
                                </div>
                            </div>
                            <div class="condition-desc" style="padding-left:12px">和值尾${m.sum_tail}，保留热组</div>
                            <div class="duanzu-groups">
                                <div class="duanzu-group ${m.groups.group1.is_cold ? 'cold' : 'hot'}">
                                    <div class="group-label">第一组(3个)</div>
                                    <div class="group-nums">${m.groups.group1.nums.join('')}</div>
                                    <div class="group-count">${m.groups.group1.count}次</div>
                                </div>
                                <div class="duanzu-group ${m.groups.group2.is_cold ? 'cold' : 'hot'}">
                                    <div class="group-label">第二组(3个)</div>
                                    <div class="group-nums">${m.groups.group2.nums.join('')}</div>
                                    <div class="group-count">${m.groups.group2.count}次</div>
                                </div>
                                <div class="duanzu-group ${m.groups.group3.is_cold ? 'cold' : 'hot'}">
                                    <div class="group-label">第三组(4个)</div>
                                    <div class="group-nums">${m.groups.group3.nums.join('')}</div>
                                    <div class="group-count">${m.groups.group3.count}次</div>
                                </div>
                            </div>
                        `;
                    } else {
                        conditionsHtml += `
                            <div class="condition-item">
                                <div class="condition-left">
                                    <span class="condition-name">${m.name}</span>
                                    <span class="condition-weight">(${m.weight})</span>
                                </div>
                                <div class="condition-right">
                                    <span class="condition-result">${m.result.join('')}</span>
                                </div>
                            </div>
                            ${m.desc ? \`<div class="condition-desc" style="padding-left:12px">\${m.desc}</div>\` : ''}
                        `;
                    }
                });
                document.getElementById('d3-conditions').innerHTML = conditionsHtml;
                
            } catch (error) {
                console.error('加载数据失败:', error);
                document.getElementById('pl3-conditions').innerHTML = '<div class="condition-item">数据加载失败，请点击刷新按钮</div>';
            }
        }
        
        // 生成推荐号码
        function generateNumbers(gold, silver, wuma, count) {
            const wumaArr = wuma.split('').map(Number);
            const nums = [];
            
            // 前2个：必须含金胆，用五码中的数字
            for (let i = 0; i < 2 && nums.length < count; i++) {
                const others = wumaArr.filter(d => d !== gold);
                const selected = [gold, others[Math.floor(Math.random() * others.length)], others[Math.floor(Math.random() * others.length)]];
                const num = selected.sort((a,b) => a-b).join('');
                if (!nums.includes(num)) nums.push(num);
            }
            
            // 后3个：含银胆或随机组合
            while (nums.length < count) {
                const useGold = Math.random() < 0.7;
                if (useGold) {
                    const others = wumaArr.filter(d => d !== gold);
                    const selected = [gold, others[Math.floor(Math.random() * others.length)], others[Math.floor(Math.random() * others.length)]];
                    const num = selected.sort((a,b) => a-b).join('');
                    if (!nums.includes(num)) nums.push(num);
                } else {
                    const others = wumaArr.filter(d => d !== silver);
                    const selected = [silver, others[Math.floor(Math.random() * others.length)], others[Math.floor(Math.random() * others.length)]];
                    const num = selected.sort((a,b) => a-b).join('');
                    if (!nums.includes(num)) nums.push(num);
                }
            }
            
            return nums;
        }
        
        // 初始化
        updateCountdown();
        setInterval(updateCountdown, 1000);
        loadData();
    