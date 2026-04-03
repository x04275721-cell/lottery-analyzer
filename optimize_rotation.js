const fs = require('fs');

// 读取PL3数据
const data = fs.readFileSync('pl3_full.csv', 'utf-8');
const lines = data.trim().split('\n');

console.log('======================================================================');
console.log('旋转矩阵优化分析');
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

// 分析：找出最优的5个四码组合
console.log('======================================================================');
console.log('一、寻找最优四码组合');
console.log('======================================================================\n');

// 生成所有可能的四码组合（C(10,4) = 210种）
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

// 统计每个组合的命中率
const comboStats = [];
for (let combo of allCombos) {
  let hits = 0;
  for (let r of results) {
    if (checkHit(r.num, combo)) hits++;
  }
  comboStats.push({
    combo,
    hits,
    rate: hits / results.length * 100
  });
}

// 排序
comboStats.sort((a, b) => b.hits - a.hits);

console.log('命中率最高的前20个四码组合：\n');
console.log('排名 | 组合 | 命中次数 | 命中率');
console.log('-----|------|----------|-------');
for (let i = 0; i < 20; i++) {
  const s = comboStats[i];
  console.log(`${(i+1).toString().padStart(2)} | [${s.combo.join('')}] | ${s.hits}次 | ${s.rate.toFixed(2)}%`);
}

// 找出最优的5个组合（覆盖所有数字）
console.log('\n======================================================================');
console.log('二、构建最优旋转矩阵');
console.log('======================================================================\n');

// 策略1：选择命中率最高的5个组合
console.log('策略1：直接选择命中率最高的5个组合\n');

const top5 = comboStats.slice(0, 5);
let totalHits1 = 0;

for (let r of results) {
  let hit = false;
  for (let s of top5) {
    if (checkHit(r.num, s.combo)) {
      hit = true;
      break;
    }
  }
  if (hit) totalHits1++;
}

console.log('最优5组合：');
for (let i = 0; i < 5; i++) {
  console.log(`  ${i+1}. [${top5[i].combo.join('')}] - ${top5[i].rate.toFixed(2)}%`);
}
console.log(`\n组合覆盖率：${totalHits1}/${results.length} = ${(totalHits1/results.length*100).toFixed(2)}%`);

// 检查是否覆盖所有数字
const coveredDigits1 = new Set();
for (let s of top5) {
  for (let d of s.combo) coveredDigits1.add(d);
}
console.log(`覆盖数字：[${[...coveredDigits1].sort().join('')}] (${coveredDigits1.size}/10)`);

// 策略2：确保覆盖所有数字的最优组合
console.log('\n策略2：确保覆盖所有0-9数字的最优组合\n');

// 贪心算法：每次选择命中率最高且覆盖新数字的组合
const selected = [];
const covered = new Set();

while (covered.size < 10) {
  let bestCombo = null;
  let bestRate = 0;
  
  for (let s of comboStats) {
    // 检查这个组合是否能覆盖新数字
    const newDigits = s.combo.filter(d => !covered.has(d));
    if (newDigits.length > 0 && s.rate > bestRate) {
      bestRate = s.rate;
      bestCombo = s;
    }
  }
  
  if (bestCombo) {
    selected.push(bestCombo);
    for (let d of bestCombo.combo) covered.add(d);
  } else {
    break;
  }
}

// 如果还不够5个，用命中率最高的补充
while (selected.length < 5) {
  for (let s of comboStats) {
    if (!selected.find(x => x.combo.join('') === s.combo.join(''))) {
      selected.push(s);
      break;
    }
  }
}

let totalHits2 = 0;
for (let r of results) {
  let hit = false;
  for (let s of selected) {
    if (checkHit(r.num, s.combo)) {
      hit = true;
      break;
    }
  }
  if (hit) totalHits2++;
}

console.log('覆盖全数字的最优5组合：');
for (let i = 0; i < selected.length; i++) {
  console.log(`  ${i+1}. [${selected[i].combo.join('')}] - ${selected[i].rate.toFixed(2)}%`);
}
console.log(`\n组合覆盖率：${totalHits2}/${results.length} = ${(totalHits2/results.length*100).toFixed(2)}%`);
console.log(`覆盖数字：[${[...covered].sort().join('')}] (${covered.size}/10)`);

// 策略3：基于热号的组合
console.log('\n策略3：基于热号的组合优化\n');

// 统计近1000期热号
const hotNumbers = {};
for (let d = 0; d <= 9; d++) hotNumbers[d] = 0;

const recent = results.slice(-1000);
for (let r of recent) {
  for (let d of r.d) hotNumbers[d]++;
}

const sortedHot = Object.entries(hotNumbers)
  .sort((a, b) => b[1] - a[1])
  .map(x => parseInt(x[0]));

console.log('近1000期热号排名：');
console.log(sortedHot.map(d => `${d}(${hotNumbers[d]})`).join(' > '));

// 选择包含最多热号的组合
const hotCombos = [];
for (let s of comboStats) {
  let hotScore = 0;
  for (let d of s.combo) {
    hotScore += 10 - sortedHot.indexOf(d); // 越热分数越高
  }
  hotCombos.push({ ...s, hotScore });
}

hotCombos.sort((a, b) => b.hotScore - a.hotScore);

const top5Hot = hotCombos.slice(0, 5);
let totalHits3 = 0;
for (let r of results) {
  let hit = false;
  for (let s of top5Hot) {
    if (checkHit(r.num, s.combo)) {
      hit = true;
      break;
    }
  }
  if (hit) totalHits3++;
}

console.log('\n基于热号的最优5组合：');
for (let i = 0; i < 5; i++) {
  console.log(`  ${i+1}. [${top5Hot[i].combo.join('')}] - ${top5Hot[i].rate.toFixed(2)}% (热值${top5Hot[i].hotScore})`);
}
console.log(`\n组合覆盖率：${totalHits3}/${results.length} = ${(totalHits3/results.length*100).toFixed(2)}%`);

// 策略4：使用三码+四码混合
console.log('\n======================================================================');
console.log('三、三码+四码混合矩阵');
console.log('======================================================================\n');

// 生成所有三码组合
const allCombos3 = [];
for (let a = 0; a <= 7; a++) {
  for (let b = a + 1; b <= 8; b++) {
    for (let c = b + 1; c <= 9; c++) {
      allCombos3.push([a, b, c]);
    }
  }
}

const comboStats3 = [];
for (let combo of allCombos3) {
  let hits = 0;
  for (let r of results) {
    if (checkHit(r.num, combo)) hits++;
  }
  comboStats3.push({
    combo,
    hits,
    rate: hits / results.length * 100
  });
}

comboStats3.sort((a, b) => b.hits - a.hits);

console.log('命中率最高的前10个三码组合：\n');
for (let i = 0; i < 10; i++) {
  const s = comboStats3[i];
  console.log(`${(i+1).toString().padStart(2)}. [${s.combo.join('')}] - ${s.hits}次 - ${s.rate.toFixed(2)}%`);
}

// 混合策略：4个四码 + 1个三码
console.log('\n混合策略：4个四码 + 1个三码\n');

const mixedCombo = [...comboStats.slice(0, 4), comboStats3[0]];
let totalHits4 = 0;
for (let r of results) {
  let hit = false;
  for (let s of mixedCombo) {
    if (checkHit(r.num, s.combo)) {
      hit = true;
      break;
    }
  }
  if (hit) totalHits4++;
}

console.log('混合组合：');
for (let i = 0; i < 5; i++) {
  const type = mixedCombo[i].combo.length === 4 ? '四码' : '三码';
  console.log(`  ${i+1}. [${mixedCombo[i].combo.join('')}] (${type}) - ${mixedCombo[i].rate.toFixed(2)}%`);
}
console.log(`\n组合覆盖率：${totalHits4}/${results.length} = ${(totalHits4/results.length*100).toFixed(2)}%`);

// 最终优化：生成新的旋转矩阵
console.log('\n======================================================================');
console.log('四、优化后的旋转矩阵');
console.log('======================================================================\n');

// 使用策略2的结果
const optimizedMatrix = {
  '最优': selected.slice(0, 5).map(s => s.combo)
};

// 计算遗漏期数
console.log('优化后的矩阵（覆盖所有数字）：\n');
for (let i = 0; i < 5; i++) {
  const combo = selected[i].combo;
  
  // 计算遗漏
  let missStreaks = [];
  let currentMiss = 0;
  
  for (let r of results) {
    if (checkHit(r.num, combo)) {
      if (currentMiss > 0) missStreaks.push(currentMiss);
      currentMiss = 0;
    } else {
      currentMiss++;
    }
  }
  
  const maxMiss = missStreaks.length > 0 ? Math.max(...missStreaks) : 0;
  const avgMiss = missStreaks.length > 0 ? 
    (missStreaks.reduce((a,b) => a+b, 0) / missStreaks.length).toFixed(1) : 0;
  
  console.log(`${i+1}. [${combo.join('')}] - 命中率${selected[i].rate.toFixed(2)}% | 最大遗漏${maxMiss}期 | 平均遗漏${avgMiss}期`);
}

// 统计覆盖率
let finalHits = 0;
for (let r of results) {
  let hit = false;
  for (let s of selected.slice(0, 5)) {
    if (checkHit(r.num, s.combo)) {
      hit = true;
      break;
    }
  }
  if (hit) finalHits++;
}

console.log(`\n最终覆盖率：${finalHits}/${results.length} = ${(finalHits/results.length*100).toFixed(2)}%`);

// 对比原矩阵
console.log('\n======================================================================');
console.log('五、新旧矩阵对比');
console.log('======================================================================\n');

// 原矩阵最佳组合
const oldBest = [[2,4,6,8]]; // 原矩阵命中率最高的组合
let oldHits = 0;
for (let r of results) {
  if (checkHit(r.num, oldBest[0])) oldHits++;
}

console.log('| 矩阵 | 最佳组合 | 命中率 | 最大遗漏 |');
console.log('|------|---------|--------|---------|');
console.log(`| 原矩阵 | [2468] | ${(oldHits/results.length*100).toFixed(2)}% | 14期 |`);
console.log(`| 优化矩阵 | [${selected[0].combo.join('')}] | ${selected[0].rate.toFixed(2)}% | - |`);
console.log(`| 优化矩阵(5组合) | 全覆盖 | ${(finalHits/results.length*100).toFixed(2)}% | - |`);

// 总结
console.log('\n======================================================================');
console.log('总结');
console.log('======================================================================\n');
console.log('1. 优化后的矩阵覆盖率与原矩阵相当（约100%）');
console.log('2. 单组合命中率提升：' + (selected[0].rate - oldHits/results.length*100).toFixed(2) + '%');
console.log('3. 建议使用优化后的矩阵替代原矩阵');
