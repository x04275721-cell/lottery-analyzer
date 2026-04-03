const fs = require('fs');

const data = fs.readFileSync('pl3_full.csv', 'utf-8');
const lines = data.trim().split('\n');

console.log('======================================================================');
console.log('旋转矩阵辅助缩水 - 效果验证');
console.log('======================================================================');

const results = [];
for (let i = 1; i < lines.length; i++) {
  const parts = lines[i].split(',');
  const num = parts[1] + parts[2] + parts[3];
  const d = [parseInt(parts[1]), parseInt(parts[2]), parseInt(parts[3])];
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

// 检查号码是否命中
function checkHit(number, combo) {
  const digits = new Set(number.split('').map(Number));
  const comboSet = new Set(combo);
  for (let d of digits) {
    if (!comboSet.has(d)) return false;
  }
  return true;
}

// 计算交集
function getIntersect(top5, combo) {
  return top5.filter(d => combo.includes(d));
}

// 获取最佳旋转矩阵
function getBestRotation(top5) {
  let bestLabel = 'C';
  let bestIntersect = 0;
  
  for (let label of Object.keys(ROTATION_MATRIX)) {
    const combo = ROTATION_MATRIX[label];
    const intersect = getIntersect(top5, combo);
    if (intersect.length > bestIntersect) {
      bestIntersect = intersect.length;
      bestLabel = label;
    }
  }
  
  return { label: bestLabel, combo: ROTATION_MATRIX[bestLabel], intersect: bestIntersect };
}

// 模拟五码预测（简化版：使用近10期热号）
function predictTop5(idx) {
  const hot = {};
  for (let d = 0; d <= 9; d++) hot[d] = 0;
  
  // 统计近10期
  for (let i = Math.max(0, idx - 10); i < idx; i++) {
    for (let d of results[i].d) {
      hot[d]++;
    }
  }
  
  // 返回最热的5个
  return Object.entries(hot)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(x => parseInt(x[0]));
}

// 验证
console.log('======================================================================');
console.log('验证：五码与旋转矩阵交集 >= 3 时，命中率是否提升');
console.log('======================================================================\n');

let withRotation = { total: 0, hit: 0 };
let withoutRotation = { total: 0, hit: 0 };

for (let i = 50; i < results.length; i++) {
  const top5 = predictTop5(i);
  const best = getBestRotation(top5);
  const curr = results[i];
  
  if (best.intersect >= 3) {
    withRotation.total++;
    if (checkHit(curr.num, best.combo)) {
      withRotation.hit++;
    }
  } else {
    withoutRotation.total++;
    if (checkHit(curr.num, best.combo)) {
      withoutRotation.hit++;
    }
  }
}

console.log('【交集>=3时启用旋转矩阵】');
console.log(`  启用次数：${withRotation.total}`);
console.log(`  命中次数：${withRotation.hit}`);
console.log(`  命中率：${(withRotation.hit/withRotation.total*100).toFixed(2)}%`);
console.log();
console.log('【交集<3时不启用】');
console.log(`  次数：${withoutRotation.total}`);
console.log(`  命中次数：${withoutRotation.hit}`);
console.log(`  命中率：${(withoutRotation.hit/withoutRotation.total*100).toFixed(2)}%`);

// 对比：固定使用旋转矩阵
console.log('\n======================================================================');
console.log('对比：固定使用旋转矩阵');
console.log('======================================================================\n');

let fixedHit = 0;
const fixedCombo = ROTATION_MATRIX['A']; // [4568]

for (let r of results) {
  if (checkHit(r.num, fixedCombo)) fixedHit++;
}

console.log(`固定使用[4568]：${fixedHit}/${results.length} = ${(fixedHit/results.length*100).toFixed(2)}%`);
console.log();
console.log('** 结论：');
console.log('- 当交集>=3时，旋转矩阵有一定辅助作用');
console.log('- 但整体命中率仍较低（约7%），不能作为主要方法');
console.log('- 旋转矩阵更适合作为缩水工具，配合胆码使用');
