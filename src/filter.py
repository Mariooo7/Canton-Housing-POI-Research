import os

import geopandas as gpd
import pandas as pd

from config.config import (COMMUNITIES_DATA_PROCESSED_DIR,
                           COMMUNITIES_DATA_FILTERED_FILENAME,
                           CENTER_CITY_SHP_PATH,
                           COMMUNITIES_DATA_GEOCODED_FILENAME
                           )


def filter_communities_in_center_city(input_csv: str) -> pd.DataFrame:
    """
       过滤出位于广州市中心城区的小区数据

       Args:
           input_csv: 包含小区数据的CSV文件路径

       Returns:
           过滤后的DataFrame，仅包含中心城区小区
       """
    # 读取数据
    data = pd.read_csv(input_csv)
    center_city = gpd.read_file(CENTER_CITY_SHP_PATH)

    # 创建地理DataFrame
    community_gdf = gpd.GeoDataFrame(
        data,
        geometry=gpd.points_from_xy(
            data.longitude,
            data.latitude,
            crs='EPSG:4326'
        )
    )


    # 空间过滤
    filtered = gpd.sjoin(
        community_gdf,
        center_city,
        how='inner',
        predicate='within'
    )

    # 处理区域编码
    filtered['REGION'] = filtered['小区地址'].str[:2]
    encoded_region = pd.get_dummies(filtered['REGION'], prefix='REG')

    # 清理列
    columns_to_drop = [
        'index_right', 'adcode', 'name', 'center',
        'centroid', 'childrenNu', 'level', 'parent',
        'subFeature', 'acroutes', 'REGION'
    ]
    filtered = filtered.drop(columns=columns_to_drop)

    return pd.concat([filtered, encoded_region], axis=1)


def main():
    """主处理流程"""
    try:
        # 输入文件路径
        input_path = os.path.join(
            COMMUNITIES_DATA_PROCESSED_DIR,
            COMMUNITIES_DATA_GEOCODED_FILENAME
        )

        # 过滤数据
        filtered_data = filter_communities_in_center_city(input_path)

        # 保存结果
        output_path = os.path.join(
            COMMUNITIES_DATA_PROCESSED_DIR,
            COMMUNITIES_DATA_FILTERED_FILENAME
        )
        filtered_data.to_csv(output_path, index=False)
        print(f"中心城区小区数据已保存至: {output_path}")

    except Exception as e:
        print(f"过滤数据时出错: {e}")


if __name__ == "__main__":
    main()