# 🎯 彩票智能分析系统

> 基于马尔可夫链和历史数据统计的彩票智能分析系统

![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 功能特点

- **📊 今日分析** - 排列三、福彩3D双彩同步分析
- **🤖 自动生成** - 每天09:00自动生成推荐，22:00更新历史
- **📈 回溯追踪** - 查看往期推荐与开奖结果对比
- **💭 智能反思** - 基于历史数据自动优化预测算法

## 🕐 自动运行时间

| 时间 | 操作 |
|------|------|
| 09:00 (北京时间) | 自动生成今日推荐并锁定 |
| 22:00 (北京时间) | 自动获取开奖结果并更新历史 |

## 📂 项目结构

```
lottery-analyzer/
├── index.html          # 今日分析页面
├── automation.html     # 自动生成系统页面
├── tracking.html       # 历史回溯页面
├── today_result.json   # 今日推荐数据
├── history_records.json # 历史记录
├── pl3_full.csv        # 排列三历史数据
├── fc3d_5years.csv     # 3D历史数据
└── .github/
    └── workflows/
        └── daily-update.yml  # GitHub Actions自动化
```

## 🔧 技术栈

- **前端**: HTML5 + CSS3 + Vanilla JavaScript
- **后端**: GitHub Actions (Python)
- **数据源**: 17500.cn 历史开奖数据
- **托管**: GitHub Pages

## 📊 分析方法

1. **马尔可夫链** - 基于上期数字转移概率
2. **统计分析** - 近100期/1000期热号分析
3. **和值筛选** - 智能识别热和值区间
4. **跨度分析** - 组三/组六类型判断

## ⚠️ 免责声明

- 本系统仅供学习研究
- 彩票有风险，投注需谨慎
- 系统预测结果不构成投注建议

## 📝 License

MIT License - 欢迎Star和Fork
