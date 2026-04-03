const fs = require('fs');

const data = fs.readFileSync('pl3_full.csv', 'utf-8');
const lines = data.trim().split('\n');

console.log('CSV格式检查：');
console.log('第一行:', lines[0]);
console.log('第二行:', lines[1]);
console.log();

const parts = lines[1].split(',');
console.log('字段解析：');
console.log('parts[0]:', parts[0]);  // 期号
console.log('parts[1]:', parts[1]);  // num1
console.log('parts[2]:', parts[2]);  // num2
console.log('parts[3]:', parts[3]);  // num3
console.log();

// 正确的号码应该是 parts[1]+parts[2]+parts[3]
const correctNum = parts[1] + parts[2] + parts[3];
console.log('正确号码:', correctNum);

// 错误的号码是 parts[1]
const wrongNum = parts[1];
console.log('错误号码(之前):', wrongNum);
