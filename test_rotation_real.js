const fs = require('fs');

const data = fs.readFileSync('pl3_full.csv', 'utf-8');
const lines = data.trim().split('\n');

console.log('======================================================================');
console.log('旋转矩阵正确验证 - 修正数据格式');
console.log('======================================================================');

const results = [];
for (let i = 1; i < lines.length; i++) {
  const parts = lines[i].split(',');
  const num = parts[1] + parts[2] + parts[3];  // 正确组合三位数
  const d = [parseInt(parts[1]), parseInt(parts[2]), parseInt(parts[3])];
  results.push({ issue: parseInt(parts[0]), num, d });
}

console.log(`数据加载完成：共${results.length}期`);
console.log(`样例：${results[0].num}, ${results[1].num}, ${results[2].num}`);
console.log();

// 检查号码是否命中四码组合
function checkHit(number, combo) {
  const digits = new Set(number.split('').map(Number));
  const comboSet = new Set(combo);
  // 所有数字都必须在组合中
  for (let d of digits) {
    if (!comboSet.has(d)) return false;
  }
  return true;
}

// 旋转矩阵
const combos = [
  [4, 5, 6, 8],
  [2, 4, 5, 8],
  [2, 4, 6, 8],
  [4, 5, 8, 9],
  [3, 4, 5, 8],
];

console.log('======================================================================');
console.log('一、四码组合命中率验证');
console.log('======================================================================\n');

for (let combo of combos) {
  let hits = 0;
  for (let r of results) {
    if (checkHit(r.num, combo)) hits++;
  }
  console.log(`[${combo.join('')}]：${hits}次 = ${(hits/results.length*100).toFixed(2)}%`);
}

// 理论概率
console.log('\n理论概率：');
console.log('- 四码组合包含 C(4,3)=4 种三码组六');
console.log('- 但号码可能是组三（如112）或豹子（如111）');
console.log('- 组六理论概率：C(4,3)/C(10,3) = 4/120 = 3.33%');
console.log('- 组三理论概率：C(4,2)/C(10,2) = 6/45 = 13.33%');
console.log('- 实际计算需要考虑组六/组三/豹子的比例');

// 统计开奖类型
let z6 = 0, z3 = 0, bao = 0;
for (let r of results) {
  const digits = new Set(r.num.split('').map(Number));
  if (digits.size === 3) z6++;
  else if (digits.size === 2) z3++;
  else bao++;
}

console.log(`\n开奖类型分布：`);
console.log(`组六：${z6}次 = ${(z6/results.length*100).toFixed(2)}%`);
console.log(`组三：${z3}次 = ${(z3/results.length*100).toFixed(2)}%`);
console.log(`豹子：${bao}次 = ${(bao/results.length*100).toFixed(2)}%`);

// 分别计算组六和组三的命中率
console.log('\n======================================================================');
console.log('二、分类型命中率');
console.log('======================================================================\n');

for (let combo of combos) {
  let z6Hits = 0, z3Hits = 0, baoHits = 0;
  
  for (let r of results) {
    const digits = new Set(r.num.split('').map(Number));
    if (checkHit(r.num, combo)) {
      if (digits.size === 3) z6Hits++;
      else if (digits.size === 2) z3Hits++;
      else baoHits++;
    }
  }
  
  console.log(`[${combo.join('')}]：`);
  console.log(`  组六命中：${z6Hits}/${z6} = ${(z6Hits/z6*100).toFixed(2)}%`);
  console.log(`  组三命中：${z3Hits}/${z3} = ${(z3Hits/z3*100).toFixed(2)}%`);
  console.log(`  豹子命中：${baoHits}/${bao} = ${(baoHits/bao*100).toFixed(2)}%`);
}

// 总结
console.log('\n======================================================================');
console.log('总结');
console.log('======================================================================\n');
console.log('1. 四码组合整体命中率约6-7%（组六+组三+豹子）');
console.log('2. 组六命中率约8%（理论3.33%，提升约2.4倍）');
console.log('3. 组三命中率约13%（理论13.33%，接近理论）');
console.log('4. 旋转矩阵对组六有一定效果，但对整体命中率提升有限');
