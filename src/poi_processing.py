import os

import pandas as pd

from config.config import (POI_DATA_RAW_DIR,
                           POI_DATA_PROCESSED_DIR,
                           RAW_POI_FILES,
                           POI_EXTRACTION_CONFIG,
                           TARGET_DISTRICTS,
                           POI_COLUMNS_TO_DROP)


def load_all_raw_poi_data(raw_path, file_mapping):
    """
    根据配置文件加载所有原始POI数据文件。
    返回一个字典，键是文件类型(如'shopping'),值是对应的DataFrame。
    """
    print("--- 开始加载原始POI数据 ---")
    dataframes = {}
    for poi_type, filename in file_mapping.items():
        file_path = os.path.join(raw_path, filename)
        try:
            dataframes[poi_type] = pd.read_csv(file_path)
            print(f"成功加载: {filename}")
        except FileNotFoundError:
            print(f"警告: 文件未找到，跳过: {file_path}")
        except Exception as e:
            print(f"加载 {filename} 时出错: {e}")
    print("--- 原始POI数据加载完成 ---\n")
    return dataframes


def process_and_extract_poi(raw_dfs, extraction_config, districts, cols_to_drop):
    """
    根据配置，从原始数据中提取、清洗并保存各类POI数据。
    """
    print("--- 开始处理和提取POI数据 ---")

    for output_filename, (source_type, category_col, categories) in extraction_config.items():
        print(f"正在处理: {output_filename}...")

        if source_type not in raw_dfs:
            print(f"  -> 警告: 找不到源数据 '{source_type}', 跳过。")
            continue

        # 复制一份以防修改原始df
        df = raw_dfs[source_type].copy()

        # 步骤 1: 按行政区筛选
        df = df[df['adname'].isin(districts)]

        # 步骤 2: 按POI类别筛选
        df = df[df[category_col].isin(categories)]

        if df.empty:
            print(f"  -> 警告: 按条件筛选后数据为空, 不生成文件。")
            continue

        # 步骤 3: 坐标系处理 (保留WGS84) 和列清理
        # 删除不需要的列
        df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
        # 重命名WGS84坐标列为标准格式
        df.rename(columns={'wgs84_x': 'longitude', 'wgs84_y': 'latitude'}, inplace=True)
        # 删除经纬度为空的行
        df.dropna(subset=['longitude', 'latitude'], inplace=True)

        # 步骤 4: 保存到处理后的目录
        output_path = os.path.join( POI_DATA_PROCESSED_DIR, output_filename)
        # 确保输出目录存在
        os.makedirs( POI_DATA_PROCESSED_DIR, exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8-sig')

        print(f"  -> 成功！共提取 {len(df)} 条记录, 已保存至: {output_path}")

    print("--- 所有POI数据处理完成 ---")


def main():
    """
    POI数据处理主流程
    """
    # 1. 加载所有原始数据
    raw_poi_dataframes = load_all_raw_poi_data( POI_DATA_RAW_DIR,  RAW_POI_FILES)

    # 2. 根据配置进行处理和保存
    process_and_extract_poi(
        raw_poi_dataframes,
         POI_EXTRACTION_CONFIG,
         TARGET_DISTRICTS,
         POI_COLUMNS_TO_DROP
    )


if __name__ == '__main__':
    main()