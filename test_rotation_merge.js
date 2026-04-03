const fs = require('fs');

// 读取PL3数据
const data = fs.readFileSync('pl3_full.csv', 'utf-8');
const lines = data.trim().split('\n');

console.log('======================================================================');
console.log('旋转矩阵融入系统 - 效果验证');
console.log('======================================================================');

const results = [];
for (let i = 1; i < lines.length; i++) {
  const parts = lines[i].split(',');
  // CSV格式: 期号,num1,num2,num3,...
  const num1 = parts[1];
  const num2 = parts[2];
  const num3 = parts[3];
  const num = num1 + num2 + num3;
  const d = [parseInt(num1), parseInt(num2), parseInt(num3)];
  results.push({ issue: parseInt(parts[0]), num, d });
}

console.log(`数据加载完成：共${results.length}期\n`);

// 旋转矩阵
const ROTATION_MATRIX = {
  'A': [4, 5, 6, 8],
  'B': [2, 4, 5, 8],
  'C': [2, 4, 6, 8],
  'D': [4, 5, 8, 9],
  'E': [3, 4, 5, 8],
};

// 选择旋转矩阵标识
function selectRotationLabel(lastNums) {
  const [n1, n2, n3] = lastNums;
  const sumTail = (n1 + n2 + n3) % 10;
  
  // 修复：和值尾 0-9 对应不同标识
  const mapping = {
    0: 'A', 5: 'A',
    1: 'B', 6: 'B',
    2: 'C', 7: 'C',
    3: 'D', 8: 'D',
    4: 'E', 9: 'E'
  };
  
  return mapping[sumTail] || 'C';
}

// 检查号码是否命中组合
function checkHit(number, combo) {
  const digits = new Set(number.split('').map(Number));
  const comboSet = new Set(combo);
  for (let d of digits) {
    if (!comboSet.has(d)) return false;
  }
  return true;
}

// 验证旋转矩阵选择规律
console.log('======================================================================');
console.log('一、旋转矩阵标识选择规律验证');
console.log('======================================================================\n');

const labelHitStats = {};
for (let label of Object.keys(ROTATION_MATRIX)) {
  labelHitStats[label] = { total: 0, hit: 0 };
}

for (let i = 1; i < results.length; i++) {
  const prev = results[i - 1];
  const curr = results[i];
  
  // 根据上期选择标识
  const label = selectRotationLabel(prev.d);
  const combo = ROTATION_MATRIX[label];
  
  labelHitStats[label].total++;
  if (checkHit(curr.num, combo)) {
    labelHitStats[label].hit++;
  }
}

console.log('标识选择命中率：\n');
console.log('标识 | 选择次数 | 命中次数 | 命中率');
console.log('-----|----------|----------|--------');
for (let label of Object.keys(ROTATION_MATRIX)) {
  const s = labelHitStats[label];
  const rate = s.total > 0 ? (s.hit / s.total * 100).toFixed(2) : 0;
  console.log(`  ${label} | ${s.total}次 | ${s.hit}次 | ${rate}%`);
}

// 验证整体效果
console.log('\n======================================================================');
console.log('二、旋转矩阵整体效果验证');
console.log('======================================================================\n');

// 策略1：固定选择最佳组合[4568]
let fixedHits = 0;
const bestCombo = ROTATION_MATRIX['A'];
for (let r of results) {
  if (checkHit(r.num, bestCombo)) fixedHits++;
}

// 策略2：根据和值尾动态选择
let dynamicHits = 0;
for (let i = 1; i < results.length; i++) {
  const prev = results[i - 1];
  const curr = results[i];
  const label = selectRotationLabel(prev.d);
  const combo = ROTATION_MATRIX[label];
  if (checkHit(curr.num, combo)) dynamicHits++;
}

// 策略3：固定选择[2468]（原最佳）
let originalHits = 0;
const originalCombo = ROTATION_MATRIX['C'];
for (let r of results) {
  if (checkHit(r.num, originalCombo)) originalHits++;
}

console.log('策略对比：\n');
console.log('策略 | 命中次数 | 命中率');
console.log('-----|----------|--------');
console.log(`固定[4568] | ${fixedHits}次 | ${(fixedHits/results.length*100).toFixed(2)}%`);
console.log(`动态选择 | ${dynamicHits}次 | ${(dynamicHits/(results.length-1)*100).toFixed(2)}%`);
console.log(`固定[2468]（原） | ${originalHits}次 | ${(originalHits/results.length*100).toFixed(2)}%`);

// 分析：旋转矩阵与系统的配合
console.log('\n======================================================================');
console.log('三、旋转矩阵与系统配合分析');
console.log('======================================================================\n');

// 模拟：先用系统选出候选号码，再用旋转矩阵缩水
console.log('模拟流程：');
console.log('1. 系统选出候选号码（含金胆/银胆）');
console.log('2. 用旋转矩阵缩水');
console.log('3. 检查命中率\n');

// 简化模拟：假设系统选出的号码包含某个热号
let withRotationHits = 0;
let withoutRotationHits = 0;
const sampleSize = 1000;

for (let i = results.length - sampleSize; i < results.length; i++) {
  const r = results[i];
  const prev = results[i - 1];
  
  // 选择旋转矩阵
  const label = selectRotationLabel(prev.d);
  const combo = ROTATION_MATRIX[label];
  
  // 统计是否命中
  if (checkHit(r.num, combo)) {
    withRotationHits++;
  }
  withoutRotationHits++;
}

console.log(`近${sampleSize}期测试：`);
console.log(`旋转矩阵命中：${withRotationHits}/${sampleSize} = ${(withRotationHits/sampleSize*100).toFixed(2)}%`);

// 总结
console.log('\n======================================================================');
console.log('总结');
console.log('======================================================================\n');

const dynamicRate = dynamicHits / (results.length - 1) * 100;
const fixedRate = fixedHits / results.length * 100;
const originalRate = originalHits / results.length * 100;

console.log('1. 固定选择[4568]：' + fixedRate.toFixed(2) + '%');
console.log('2. 动态选择（根据和值尾）：' + dynamicRate.toFixed(2) + '%');
console.log('3. 固定选择[2468]（原最佳）：' + originalRate.toFixed(2) + '%');
console.log();

if (dynamicRate > fixedRate) {
  console.log('** 结论：动态选择优于固定选择，提升 ' + (dynamicRate - fixedRate).toFixed(2) + '%');
} else {
  console.log('** 结论：固定选择优于动态选择，差距 ' + (fixedRate - dynamicRate).toFixed(2) + '%');
}

console.log('\n** 建议：旋转矩阵更适合作为缩水工具，而非主要预测方法');
console.log('** 融入方式：系统先选号，再用旋转矩阵过滤不合理的号码');
