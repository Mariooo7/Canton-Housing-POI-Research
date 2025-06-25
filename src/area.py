import os

import geopandas as gpd
import pandas as pd

from config.config import (
    COMMUNITIES_DATA_PROCESSED_DIR,
    COMMUNITIES_DATA_WITH_RIVER_FILENAME,
    POI_DATA_PROCESSED_DIR,
    COMMUNITIES_DATA_WITH_AREA_FILENAME,
    COMMERCIAL_AREA_BY_TYPE,
    COMMERCIAL_POI_FILENAME,
)


def calculate_commercial_area():
    """计算小区800米范围内的商业面积"""
    try:
        # 1. 加载小区数据
        communities = pd.read_csv(
            os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_WITH_RIVER_FILENAME)
        )
        community_gdf = gpd.GeoDataFrame(
            communities,
            geometry=gpd.points_from_xy(communities.longitude, communities.latitude),
            crs="epsg:4326"
        )

        # 2. 加载购物POI数据
        shopping = pd.read_csv(os.path.join(POI_DATA_PROCESSED_DIR, COMMERCIAL_POI_FILENAME))
        shopping_gdf = gpd.GeoDataFrame(
            shopping,
            geometry=gpd.points_from_xy(shopping.longitude, shopping.latitude),
            crs="epsg:4326"
        )

        # 3. 定义商业业态面积
        area_by_type = COMMERCIAL_AREA_BY_TYPE

        # 4. 计算800米范围内的商业面积
        total_commercial_area = []
        for community in community_gdf.itertuples():
            buffer = community.geometry.buffer(800 / 111320)  # 800米缓冲区
            poi_in_buffer = shopping_gdf[shopping_gdf.geometry.within(buffer)]
            total_area = sum(area_by_type.get(poi.中类, 0) for poi in poi_in_buffer.itertuples())
            total_commercial_area.append(total_area)

        # 5. 保存结果
        communities['ARE'] = total_commercial_area
        output_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_WITH_AREA_FILENAME)
        communities.to_csv(output_path, index=False)
        print(f"商业面积计算完成，结果已保存至: {output_path}")

    except Exception as e:
        print(f"计算商业面积时出错: {e}")


if __name__ == "__main__":
    calculate_commercial_area()