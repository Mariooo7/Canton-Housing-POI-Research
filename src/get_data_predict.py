import os

import pandas as pd
from sklearn.preprocessing import StandardScaler

from config.config import (
    COMMUNITIES_DATA_PROCESSED_DIR,
    COMMUNITIES_DATA_WITH_AREA_FILENAME,
    PREDICT_FEATURES,
    PREDICT_DATA_FILENAME,
    CONTINUOUS_FEATURES,
)


def extract_predict_data():
    """提取预测任务所需数据"""
    try:
        # 加载完整数据
        input_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_WITH_AREA_FILENAME)
        data = pd.read_csv(input_path)

        # 提取所需特征
        predict_data = data[PREDICT_FEATURES].copy()
        # 1. 检查并转换布尔值为0/1整数
        bool_cols = predict_data.select_dtypes(include='bool').columns
        predict_data[bool_cols] = predict_data[bool_cols].astype(int)
        # 2. 确保数值列是float类型
        num_cols = predict_data.select_dtypes(include=['int64', 'float64']).columns
        predict_data[num_cols] = predict_data[num_cols].astype(float)
        # 处理连续特征
        scaler = StandardScaler()
        predict_data[CONTINUOUS_FEATURES] = scaler.fit_transform(predict_data[CONTINUOUS_FEATURES])

        # 保存结果
        output_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, PREDICT_DATA_FILENAME)
        predict_data.to_csv(output_path, index=False)
        print(f"预测任务数据已提取并保存至: {output_path}")

    except Exception as e:
        print(f"提取预测数据时出错: {e}")


if __name__ == "__main__":
    extract_predict_data()