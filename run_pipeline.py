import os
import sys

# 将src目录添加到Python路径中，以便可以导入其中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# 从各个模块中导入主执行函数
from data_loader import main as data_loader_main #
from poi_processing import main as poi_processing_main #
from geocoding import main as geocoding_main #
from filter import main as filter_main #
from distance import main as distance_main #
from river import calculate_river_distance as river_main #
from area import calculate_commercial_area as area_main #
from get_data_research import extract_research_data as get_data_research_main #
from get_data_predict import extract_predict_data as get_data_predict_main

def run_step(step_name, main_func):
    """
    封装单个步骤的执行，包含日志和错误处理。
    """
    print(f"\n{'='*20} [开始] {step_name} {'='*20}")
    try:
        main_func()
        print(f"{'='*20} [完成] {step_name} {'='*20}")
    except Exception as e:
        print(f"!!!!!! [错误] 在执行 {step_name} 时发生错误: {e} !!!!!!")
        # 决定是否在出错时停止整个流程
        # exit() # 如果希望在任何一步出错时都停止，可以取消此行注释

def main():
    """
    定义并按顺序执行整个数据处理流水线。
    """
    # 定义流水线中的所有步骤
    pipeline = [
        ("步骤 1/9: 清洗并整合小区原始数据", data_loader_main),
        ("步骤 2/9: 清洗并提取POI数据", poi_processing_main),
        ("步骤 3/9: 为小区数据进行地理编码", geocoding_main),
        ("步骤 4/9: 按中心城区边界过滤小区", filter_main),
        ("步骤 5/9: 计算小区到各类POI的距离", distance_main),
        ("步骤 6/9: 计算小区到珠江的距离", river_main),
        ("步骤 7/9: 计算小区周边的商业面积", area_main),
        ("步骤 8/9: 提取研究用数据集", get_data_research_main),
        ("步骤 9/9: 提取预测用数据集", get_data_predict_main),
    ]

    # 按顺序执行流水线
    for name, func in pipeline:
        run_step(name, func)

    print("\n\n🎉 全部数据处理流水线已成功执行！🎉")
    print("现在可以在 data/processed/communities/ 目录下找到最终文件:")
    print("- data_research.csv")
    print("- data_predict.csv")
    print("可以开始进行Notebook分析了。")


if __name__ == "__main__":
    main()