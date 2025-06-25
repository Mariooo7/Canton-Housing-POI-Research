# 导入需要的库
import os

import pandas as pd

from config.config import (COMMUNITIES_DATA_RAW_DIR,
                           COMMUNITIES_DATA_PROCESSED_DIR,
                           AGE_CATEGORY_BOUNDARIES,
                           COLUMNS_TO_DROP,
                           COLUMNS_TO_PROCESS,
                           COMMUNITIES_DATA_FILENAME)


def read_and_concat_data(data_dir: str) -> pd.DataFrame:
    """
    批量读取指定目录下的 CSV 文件并拼接成一个 DataFrame

    Args:
        data_dir: 数据所在目录路径

    Returns:
        拼接后的 DataFrame

    Raises:
        FileNotFoundError: 如果目录不存在或没有CSV文件
    """
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"目录不存在: {data_dir}")

    all_data = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    all_data.append(df)
                except Exception as e:
                    print(f"读取文件 {file_path} 时出错: {e}")

    if not all_data:
        raise FileNotFoundError(f"目录 {data_dir} 中没有找到CSV文件")

    return pd.concat(all_data, ignore_index=True).drop_duplicates()


def clean_communities_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    清洗小区数据

    Args:
        df: 原始数据 DataFrame

    Returns:
        清洗后的 DataFrame
    """
    # 过滤数据
    df = df[
        df['AGE'].str.contains(r'\d+年', na=False) &
        df['YEAR'].str.contains(r'\d+年', na=False) &
        (df['物业类型'] == '住宅')
        ].copy()

    # 删除列
    df.drop(COLUMNS_TO_DROP[:1], axis=1, inplace=True)

    # 删除含有'暂无'的行
    df = df[~df.isin(['暂无']).any(axis=1)]

    # 数值处理
    df['PRO'] = df['PRO'].str.extract(r'(\d+\.\d+)').astype('float')
    df['GRE'] = df['GRE'].str.extract(r'(\d+\.\d+)%')[0]
    df = df.dropna()
    df['GRE'] = round(df['GRE'].astype('float') / 100, 2)
    df['FAR'] = df['FAR'].astype('float')

    # 处理异常值
    for column in COLUMNS_TO_PROCESS:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)].copy()

    # 处理年份数据
    df['YEAR'] = df['YEAR'].str.extract(r'(\d+)').astype('int')
    df['AGE'] = df['AGE'].str.extract(r'(\d+)').astype('int')

    # 年龄分类
    def age_category(age: int) -> str:
        for category, (lower, upper) in AGE_CATEGORY_BOUNDARIES.items():
            if (lower is None or age > lower) and (upper is None or age <= upper):
                return category
        return 'unknown'

    df['AGE_category'] = df['AGE'].apply(age_category)
    df = pd.concat([df, pd.get_dummies(df['AGE_category'], prefix='AGE')], axis=1)

    # 删除处理前的列
    df.drop(COLUMNS_TO_DROP[1:], axis=1, inplace=True)

    return df


def main():
    """主处理流程"""
    try:
        # 读取并处理数据
        communities = read_and_concat_data(COMMUNITIES_DATA_RAW_DIR)
        cleaned_data = clean_communities_data(communities)

        # 保存数据
        output_path = os.path.join(COMMUNITIES_DATA_PROCESSED_DIR, COMMUNITIES_DATA_FILENAME)
        cleaned_data.to_csv(output_path, index=False)
        print(f"数据已成功处理并保存到: {output_path}")

    except Exception as e:
        print(f"处理数据时出错: {e}")


if __name__ == "__main__":
    main()