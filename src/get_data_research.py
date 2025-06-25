import os

import pandas as pd

from config.config import (
    COMMUNITIES_DATA_PROCESSED_DIR,
    COMMUNITIES_DATA_WITH_AREA_FILENAME,
    RESEARCH_FEATURES,
    RESEARCH_DATA_FILENAME
)


def extract_research_data():
    """提取研究任务所需数据"""
    try:
        # 加载完整数据
        input_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_WITH_AREA_FILENAME)
        data = pd.read_csv(input_path)

        # 提取所需特征
        research_data = data[RESEARCH_FEATURES].copy()

        # 保存结果
        output_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, RESEARCH_DATA_FILENAME)
        research_data.to_csv(output_path, index=False)
        print(f"研究任务数据已提取并保存至: {output_path}")

    except Exception as e:
        print(f"提取研究数据时出错: {e}")


if __name__ == "__main__":
    extract_research_data()