import os

import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree

from config.config import (
    COMMUNITIES_DATA_FILTERED_FILENAME,
    POI_DATA_PROCESSED_DIR,
    CBD_CONFIG,
    POI_TYPE_MAPPING,
    COMMUNITIES_DATA_WITH_DISTANCE_FILENAME,
    COMMUNITIES_DATA_PROCESSED_DIR
)


def load_poi_data(poi_type: str) -> pd.DataFrame:
    """加载指定类型的POI数据"""
    file_path = os.path.join(POI_DATA_PROCESSED_DIR, f'{poi_type}.csv')
    return pd.read_csv(file_path)


def calculate_min_distances(community_df: pd.DataFrame, poi_df: pd.DataFrame) -> np.ndarray:
    """
    计算小区到POI的最短距离

    Args:
        community_df: 包含小区经纬度的DataFrame
        poi_df: 包含POI经纬度的DataFrame

    Returns:
        每个小区到最近POI的距离数组(单位:米)
    """
    # 将经纬度转化为弧度
    community_coords = np.radians(np.c_[community_df['latitude'], community_df['longitude']])
    poi_coords = np.radians(np.c_[poi_df['latitude'], poi_df['longitude']])

    # 使用BallTree查询最近邻
    tree = BallTree(poi_coords)
    min_dist, _ = tree.query(community_coords, k=1)

    # 转换为米
    return min_dist * 6371000  # 地球半径


def main():
    # 加载小区数据
    communities_filtered_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_FILTERED_FILENAME)
    communities = pd.read_csv(communities_filtered_path)

    # 准备POI数据
    pois = {}
    for prefix, poi_type in POI_TYPE_MAPPING.items():
        pois[prefix] = pd.read_csv(f'{POI_DATA_PROCESSED_DIR}/{poi_type}.csv')

    # 添加CBD数据
    cbd = pd.DataFrame({
        '地名': [list(CBD_CONFIG['珠江新城'].keys())[0]],
        'latitude': [CBD_CONFIG['珠江新城']['latitude']],
        'longitude': [CBD_CONFIG['珠江新城']['longitude']]
    })

    s_cbd = pd.DataFrame({
        '地名': list(CBD_CONFIG['副CBD'].keys()),
        'latitude': [x[0] for x in CBD_CONFIG['副CBD'].values()],
        'longitude': [x[1] for x in CBD_CONFIG['副CBD'].values()]
    })

    pois.update({'CBD': cbd, 'SCBD': s_cbd})

    # 计算距离
    for name, poi in pois.items():
        communities[name] = calculate_min_distances(communities, poi)
        print(f"已计算 {name} 距离")

    # 保存结果
    communities_with_distance_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_WITH_DISTANCE_FILENAME)
    communities.to_csv(communities_with_distance_path, index=False)
    print(f"距离计算结果已保存到 {communities_with_distance_path}")


if __name__ == "__main__":
    main()
