import math
import os

import pandas as pd
import requests

from config.config import (URL,
                           AK,
                           COMMUNITIES_DATA_FILENAME,
                           COMMUNITIES_DATA_PROCESSED_DIR,
                           COMMUNITIES_DATA_GEOCODED_FILENAME)


def bd09_to_wgs84(lng: float, lat: float) -> tuple:
    """
    百度坐标系(BD-09)转WGS84坐标系。
    该函数首先将BD-09转为GCJ-02，然后通过迭代算法将GCJ-02精确反解为WGS84。
    """
    # ========= 步骤1: 百度坐标系(BD-09)转国测局坐标系(GCJ-02) =========
    # (此部分沿用你原来的正确算法)
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    x = lng - 0.0065
    y = lat - 0.006
    z = (x ** 2 + y ** 2) ** 0.5 - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gcj_lng = z * math.cos(theta)
    gcj_lat = z * math.sin(theta)

    # ========= 步骤2: 国测局坐标系(GCJ-02)转WGS84坐标系 (修正部分) =========
    # 采用基于迭代的精确算法进行反解
    a = 6378245.0  # 克拉索夫斯基椭球体长半轴a
    ee = 0.00669342162296594323  # 椭球体第一偏心率的平方

    def transform(lng, lat):
        """计算GCJ-02坐标相对于WGS84的偏移量"""
        rad_lat = lat / 180.0 * math.pi
        magic = math.sin(rad_lat)
        magic = 1 - ee * magic * magic
        sqrt_magic = math.sqrt(magic)
        d_lat = (180.0 * (lat / 180.0 * math.pi + math.atan2(1 - ee, 1) * (
                1 - sqrt_magic) / sqrt_magic))
        d_lng = (180.0 * (lng / 180.0 * math.pi + math.atan2(1 - ee, 1) * (
                1 - sqrt_magic) / sqrt_magic * math.tan(rad_lat)))
        rad_lat = lat / 180.0 * math.pi
        magic = math.sin(rad_lat)
        d_lat = (d_lat * 180.0) / (a * (1 - ee)) * math.sqrt(magic) * math.cos(rad_lat) * math.pi
        d_lng = (d_lng * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * math.pi)
        return d_lng, d_lat

    # 迭代反解
    wgs_lng, wgs_lat = gcj_lng, gcj_lat
    # 通常迭代2-3次即可达到足够精度
    for i in range(5):
        lng_offset, lat_offset = transform(wgs_lng, wgs_lat)
        wgs_lng = gcj_lng - lng_offset
        wgs_lat = gcj_lat - lat_offset

    return wgs_lng, wgs_lat

def get_geocode(address: str, ak: str) -> tuple:
    """通过百度地图API获取地址的经纬度并转换为WGS84"""
    params = {
        "address": address,
        "output": "json",
        "ak": ak
    }
    try:
        response = requests.get(URL, params=params, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 0:
                location = result['result']['location']
                # 转换坐标
                return bd09_to_wgs84(location['lng'], location['lat'])
    except Exception as e:
        print(f"地址 '{address}' 查询失败: {e}")
    return None, None


def main():
    # 读取数据
    community_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_FILENAME)
    community = pd.read_csv(community_path)

    # 初始化经纬度列
    community['latitude'] = None
    community['longitude'] = None

    # 批量获取经纬度
    for index, row in community.iterrows():
        lat, lng = get_geocode(row['小区地址'], AK)
        community.at[index, 'latitude'] = lat
        community.at[index, 'longitude'] = lng
        print(f"处理第{index + 1}条数据: {row['小区地址']}, 经纬度: ({lat}, {lng})")

    # 过滤并保存有效数据
    community_with_coords = community.dropna(subset=['latitude', 'longitude'])
    community_with_coords_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_GEOCODED_FILENAME)
    community_with_coords.to_csv(community_with_coords_path, index=False)

    print(f"处理完成，有效数据已保存。原始数据{len(community)}条，有效数据{len(community_with_coords)}条")


if __name__ == "__main__":
    main()