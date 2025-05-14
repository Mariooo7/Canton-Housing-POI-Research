# 基于POI数据的房价影响因素空间异质性分析

本项目分析广州市中心城区的房价空间分布特征，利用POI数据研究房价影响因素的空间异质性。

## 项目结构

housing-poi-analysis/
├── data/ # 数据目录
│ ├── raw/ # 原始分区房价数据
│ ├── processed/ # 处理完成数据
│ ├── region/ # 广州市中心城区边界shp文件
│ ├── river/ # 珠江边界shp文件
│ └── poi/ # POI数据
├── src/ # 源代码
│ ├── data/ # 数据处理模块
│ ├── features/ # 特征工程模块
│ ├── analysis/ # 数据分析模块
│ └── visualization/ # 可视化模块
├── notebooks/ # Jupyter笔记本
├── results/ # 结果
│ ├── figures/ # 图表
│ └── models/ # 模型
├── main.py # 主执行脚本
└── README.md # 项目说明
