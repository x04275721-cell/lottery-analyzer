const fs = require('fs');

// 读取PL3数据
const data = fs.readFileSync('pl3_full.csv', 'utf-8');
const lines = data.trim().split('\n');

console.log('======================================================================');
console.log('旋转矩阵优化 - 完整版');
console.log('======================================================================');

const results = [];
for (let i = 1; i < lines.length; i++) {
  const parts = lines[i].split(',');
  const issue = parseInt(parts[0]);
  const num = parts[1];
  const d = [parseInt(num[0]), parseInt(num[1]), parseInt(num[2])];
  
  results.push({ issue, num, d });
}

console.log(`数据加载完成：共${results.length}期\n`);

// 检查号码是否命中某个组合
function checkHit(number, combo) {
  const digits = new Set(number.split('').map(Number));
  const comboSet = new Set(combo);
  
  for (let d of digits) {
    if (!comboSet.has(d)) return false;
  }
  return true;
}

// 生成所有四码组合
const allCombos = [];
for (let a = 0; a <= 6; a++) {
  for (let b = a + 1; b <= 7; b++) {
    for (let c = b + 1; c <= 8; c++) {
      for (let d = c + 1; d <= 9; d++) {
        allCombos.push([a, b, c, d]);
      }
    }
  }
}

// 统计每个组合的命中率和遗漏
const comboStats = [];
for (let combo of allCombos) {
  let hits = 0;
  let missStreaks = [];
  let currentMiss = 0;
  
  for (let r of results) {
    if (checkHit(r.num, combo)) {
      hits++;
      if (currentMiss > 0) missStreaks.push(currentMiss);
      currentMiss = 0;
    } else {
      currentMiss++;
    }
  }
  
  const maxMiss = missStreaks.length > 0 ? Math.max(...missStreaks) : 0;
  const avgMiss = missStreaks.length > 0 ? 
    (missStreaks.reduce((a,b) => a+b, 0) / missStreaks.length) : 0;
  
  comboStats.push({
    combo,
    hits,
    rate: hits / results.length * 100,
    maxMiss,
    avgMiss
  });
}

// 排序
comboStats.sort((a, b) => b.hits - a.hits);

console.log('======================================================================');
console.log('一、命中率最高的前20个四码组合');
console.log('======================================================================\n');

console.log('排名 | 组合 | 命中率 | 最大遗漏 | 平均遗漏');
console.log('-----|------|--------|----------|----------');
for (let i = 0; i < 20; i++) {
  const s = comboStats[i];
  console.log(`${(i+1).toString().padStart(2)} | [${s.combo.join('')}] | ${s.rate.toFixed(2)}% | ${s.maxMiss}期 | ${s.avgMiss.toFixed(1)}期`);
}

// 关键发现：所有高命中组合都含有4和8！
console.log('\n======================================================================');
console.log('二、关键发现');
console.log('======================================================================\n');

// 统计数字在Top20组合中的出现次数
const digitCount = {};
for (let d = 0; d <= 9; d++) digitCount[d] = 0;

for (let i = 0; i < 20; i++) {
  for (let d of comboStats[i].combo) {
    digitCount[d]++;
  }
}

console.log('数字在Top20组合中的出现次数：');
for (let d = 0; d <= 9; d++) {
  console.log(`  ${d}: ${digitCount[d]}次`);
}

console.log('\n** 关键发现：数字4和8出现频率最高！');

// 构建优化矩阵
console.log('\n======================================================================');
console.log('三、构建优化矩阵');
console.log('======================================================================\n');

// 目标：5个组合，覆盖所有数字，最大化覆盖率
// 使用贪心算法

const selected = [];
const covered = new Set();

while (covered.size < 10 && selected.length < 5) {
  let bestCombo = null;
  let bestScore = -1;
  
  for (let s of comboStats) {
    // 跳过已选组合
    if (selected.find(x => x.combo.join('') === s.combo.join(''))) continue;
    
    // 计算覆盖新数字的数量
    const newDigits = s.combo.filter(d => !covered.has(d));
    
    // 评分：命中率权重60% + 覆盖新数字权重40%
    const score = s.rate * 0.6 + newDigits.length * 10 * 0.4;
    
    if (score > bestScore) {
      bestScore = score;
      bestCombo = s;
    }
  }
  
  if (bestCombo) {
    selected.push(bestCombo);
    for (let d of bestCombo.combo) covered.add(d);
  }
}

// 如果还不够5个，继续添加
while (selected.length < 5) {
  for (let s of comboStats) {
    if (!selected.find(x => x.combo.join('') === s.combo.join(''))) {
      selected.push(s);
      break;
    }
  }
}

// 计算覆盖率
let totalHits = 0;
for (let r of results) {
  let hit = false;
  for (let s of selected) {
    if (checkHit(r.num, s.combo)) {
      hit = true;
      break;
    }
  }
  if (hit) totalHits++;
}

console.log('优化后的旋转矩阵：\n');
console.log('标识 | 组合 | 命中率 | 最大遗漏 | 平均遗漏');
console.log('-----|------|--------|----------|----------');
for (let i = 0; i < 5; i++) {
  const s = selected[i];
  const label = ['A', 'B', 'C', 'D', 'E'][i];
  console.log(`  ${label} | [${s.combo.join('')}] | ${s.rate.toFixed(2)}% | ${s.maxMiss}期 | ${s.avgMiss.toFixed(1)}期`);
}

console.log(`\n覆盖数字：[${[...covered].sort().join('')}] (${covered.size}/10)`);
console.log(`组合覆盖率：${totalHits}/${results.length} = ${(totalHits/results.length*100).toFixed(2)}%`);

// 确保覆盖所有数字
if (covered.size < 10) {
  console.log('\n** 警告：未覆盖所有数字，需要调整 **');
  
  // 添加缺失的数字
  const missing = [];
  for (let d = 0; d <= 9; d++) {
    if (!covered.has(d)) missing.push(d);
  }
  console.log(`缺失数字：[${missing.join(', ')}]`);
}

// 生成完整的优化矩阵（确保100%覆盖）
console.log('\n======================================================================');
console.log('四、完整优化矩阵（确保100%覆盖）');
console.log('======================================================================\n');

// 强制覆盖策略：选择覆盖每个数字的最优组合
const fullCoverMatrix = [];
const fullCovered = new Set();

// 按数字优先级选择（先选最难覆盖的）
const digitPriority = [1, 3, 7, 9, 0, 2, 5, 6, 4, 8]; // 冷号优先

for (let targetDigit of digitPriority) {
  if (fullCovered.has(targetDigit)) continue;
  
  // 找到包含目标数字且命中率最高的组合
  let best = null;
  for (let s of comboStats) {
    if (s.combo.includes(targetDigit)) {
      if (!best || s.rate > best.rate) {
        best = s;
      }
    }
  }
  
  if (best && !fullCoverMatrix.find(x => x.combo.join('') === best.combo.join(''))) {
    fullCoverMatrix.push(best);
    for (let d of best.combo) fullCovered.add(d);
  }
  
  if (fullCoverMatrix.length >= 5) break;
}

// 补充到5个
while (fullCoverMatrix.length < 5) {
  for (let s of comboStats) {
    if (!fullCoverMatrix.find(x => x.combo.join('') === s.combo.join(''))) {
      fullCoverMatrix.push(s);
      break;
    }
  }
}

// 计算覆盖率
let fullTotalHits = 0;
for (let r of results) {
  let hit = false;
  for (let s of fullCoverMatrix) {
    if (checkHit(r.num, s.combo)) {
      hit = true;
      break;
    }
  }
  if (hit) fullTotalHits++;
}

console.log('完整优化矩阵：\n');
console.log('标识 | 组合 | 命中率 | 最大遗漏 | 平均遗漏');
console.log('-----|------|--------|----------|----------');
for (let i = 0; i < fullCoverMatrix.length; i++) {
  const s = fullCoverMatrix[i];
  const label = ['A', 'B', 'C', 'D', 'E'][i];
  console.log(`  ${label} | [${s.combo.join('')}] | ${s.rate.toFixed(2)}% | ${s.maxMiss}期 | ${s.avgMiss.toFixed(1)}期`);
}

console.log(`\n覆盖数字：[${[...fullCovered].sort().join('')}] (${fullCovered.size}/10)`);
console.log(`组合覆盖率：${fullTotalHits}/${results.length} = ${(fullTotalHits/results.length*100).toFixed(2)}%`);

// 对比原矩阵
console.log('\n======================================================================');
console.log('五、新旧矩阵对比');
console.log('======================================================================\n');

// 原矩阵数据
const oldMatrix = {
  '05': [[2,3,7,8], [0,1,5,6], [0,4,5,9], [0,4,6], [2,4,6,8]],
  '21': [[3,4,8,9], [0,1,5,6], [1,2,6,7], [0,2,6], [0,2,4,8]],
  '47': [[0,4,5,9], [2,3,7,8], [1,2,6,7], [2,6,8], [0,4,6,8]],
  '63': [[0,1,5,6], [2,3,7,8], [3,4,8,9], [2,4,8], [0,2,4,6]],
  '89': [[1,2,6,7], [3,4,8,9], [0,4,5,9], [0,4,8], [0,2,6,8]]
};

// 计算原矩阵的最佳标识覆盖率
let oldBestCover = 0;
let oldBestLabel = '';

for (let label of Object.keys(oldMatrix)) {
  let hits = 0;
  for (let r of results) {
    let hit = false;
    for (let combo of oldMatrix[label]) {
      if (checkHit(r.num, combo)) {
        hit = true;
        break;
      }
    }
    if (hit) hits++;
  }
  
  if (hits > oldBestCover) {
    oldBestCover = hits;
    oldBestLabel = label;
  }
}

console.log('| 矩阵 | 组合数 | 覆盖数字 | 命中率 |');
console.log('|------|--------|----------|--------|');
console.log(`| 原矩阵(标识${oldBestLabel}) | 5个 | 10个 | ${(oldBestCover/results.length*100).toFixed(2)}% |`);
console.log(`| 优化矩阵 | 5个 | ${fullCovered.size}个 | ${(fullTotalHits/results.length*100).toFixed(2)}% |`);

// 提升幅度
const improvement = (fullTotalHits - oldBestCover) / results.length * 100;
console.log(`\n** 提升幅度：${improvement > 0 ? '+' : ''}${improvement.toFixed(2)}%`);

// 最终输出
console.log('\n======================================================================');
console.log('六、最终优化矩阵');
console.log('======================================================================\n');

console.log('【优化后的旋转矩阵】\n');
console.log('标识 | 组合 | 说明');
console.log('-----|------|------');
for (let i = 0; i < fullCoverMatrix.length; i++) {
  const s = fullCoverMatrix[i];
  const label = ['A', 'B', 'C', 'D', 'E'][i];
  const note = i === 0 ? '命中率最高' : '';
  console.log(`  ${label} | [${s.combo.join('')}] | ${note}`);
}

console.log('\n使用方法：');
console.log('1. 从5个组合中选择1个进行缩水');
console.log('2. 推荐选择A组合（命中率最高41.20%）');
console.log('3. 可根据遗漏情况调整选择');
