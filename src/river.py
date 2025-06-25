import os

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from shapely.ops import nearest_points

from config.config import (
    COMMUNITIES_DATA_PROCESSED_DIR,
    FIGURES_DIR,
    RIVER_DATA_DIR,
    COMMUNITIES_DATA_WITH_DISTANCE_FILENAME,
    RIVER_DISTANCE_FIGURE_FILENAME,
    COMMUNITIES_DATA_WITH_RIVER_FILENAME,
    CENTER_CITY_SHP_PATH
)


def calculate_river_distance():
    """计算小区到珠江的最短距离并保存结果"""
    try:
        # 1. 加载珠江边界数据
        river_shape = gpd.read_file(
            os.path.join(RIVER_DATA_DIR, 'hyd1_4l.shp'),
            encoding='gbk'
        )

        # 筛选珠江边界
        pearl_river = river_shape[river_shape['NAME'] == '珠江(前航道、后航道、虎门水道)']
        pearl_river_union = pearl_river.union_all()

        # 2. 加载小区数据
        communities = pd.read_csv(
            os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_WITH_DISTANCE_FILENAME)
        )

        # 3. 创建地理DataFrame (使用EPSG:4326坐标系)
        community_gdf = gpd.GeoDataFrame(
            communities,
            geometry=gpd.points_from_xy(communities.longitude, communities.latitude),
            crs="EPSG:4326"
        )

        # 4. 计算最短距离
        def calculate_min_distance(point):
            nearest = nearest_points(point, pearl_river_union)
            return point.distance(nearest[1]) * 111320  # 转换为米

        community_gdf['RIV'] = community_gdf['geometry'].apply(calculate_min_distance)

        # 5. 可视化并保存
        fig, ax = plt.subplots(figsize=(10, 8))

        # 获取小区点的边界范围
        minx, miny, maxx, maxy = community_gdf.total_bounds
        margin = 0.05  # 5%的边距
        xlim = (minx - (maxx - minx) * margin, maxx + (maxx - minx) * margin)
        ylim = (miny - (maxy - miny) * margin, maxy + (maxy - miny) * margin)

        # 加载中心城区边界数据
        center_city = gpd.read_file(CENTER_CITY_SHP_PATH)
        center_city_clipped = center_city.cx[xlim[0]:xlim[1], ylim[0]:ylim[1]]

        # 绘制底图
        center_city_clipped.plot(
            ax=ax,
            color='lightgray',
            edgecolor='orange',
            linewidth=0.5,
            alpha=0.9,
            label='City Boundary'
        )

        # 绘制河流
        pearl_river_clipped = pearl_river.cx[xlim[0]:xlim[1], ylim[0]:ylim[1]]
        pearl_river_clipped.plot(
            ax=ax,
            color='blue',
            alpha=0.5,
            linewidth=0.8,
            label='Pearl River'
        )

        # 绘制小区点
        community_gdf.plot(
            ax=ax,
            color='red',
            markersize=12,
            alpha=0.5,
            label='Communities'
        )

        # 设置坐标范围
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

        plt.title('Communities Distance to Pearl River')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.grid(True)
        # 手动创建图例
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color='orange', lw=2, label='City Boundary'),
            Line2D([0], [0], color='blue', lw=2, label='Pearl River'),
            Line2D([0], [0], marker='o', color='w', label='Communities',
                  markerfacecolor='red', markersize=8)
        ]
        ax.legend(handles=legend_elements)
        plt.savefig(os.path.join(FIGURES_DIR, RIVER_DISTANCE_FIGURE_FILENAME))
        plt.close()
        print(f"可视化图表已保存至: {os.path.join(FIGURES_DIR, RIVER_DISTANCE_FIGURE_FILENAME)}")

        # 6. 保存结果
        communities['RIV'] = community_gdf['RIV']
        output_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_WITH_RIVER_FILENAME)
        communities.to_csv(output_path, index=False)
        print(f"珠江距离计算完成，结果已保存至: {output_path}")

    except Exception as e:
        print(f"计算珠江距离时出错: {e}")


if __name__ == "__main__":
    calculate_river_distance()