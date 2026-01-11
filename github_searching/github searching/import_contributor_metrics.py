#!/usr/bin/env python3
"""
导入贡献者指标数据到数据库
从 top_300_metrics_full.xlsx 文件的 Contributor_Metrics 工作表中读取数据
"""

import pandas as pd
import json
from project.database import engine, Base
from project.models import Project
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

def import_contributor_metrics():
    """从Excel文件导入贡献者指标数据到数据库"""
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # 读取Excel文件
        df = pd.read_excel('top_300_metrics_full.xlsx', sheet_name='Contributor_Metrics')
        
        print(f"读取到 {len(df)} 行贡献者指标数据")
        print(f"列名: {list(df.columns)}")
        
        # 更新每个项目的贡献者指标
        updated_count = 0
        for index, row in df.iterrows():
            project_key = str(row['Project_Key']) if not pd.isna(row['Project_Key']) else None
            
            if not project_key:
                print(f"跳过第 {index+1} 行：Project_Key 为空")
                continue
                
            # 查找项目
            project = session.query(Project).filter(Project.project_key == project_key).first()
            if not project:
                print(f"未找到项目: {project_key}")
                continue
            
            # 构建贡献者指标数据
            contributor_metrics = {
                'new_contributors_Latest': float(row['new_contributors_Latest']) if not pd.isna(row['new_contributors_Latest']) else None,
                'new_contributors_Data_Points': float(row['new_contributors_Data_Points']) if not pd.isna(row['new_contributors_Data_Points']) else None,
                'new_contributors_Average': float(row['new_contributors_Average']) if not pd.isna(row['new_contributors_Average']) else None,
                'new_contributors_Min': float(row['new_contributors_Min']) if not pd.isna(row['new_contributors_Min']) else None,
                'new_contributors_Max': float(row['new_contributors_Max']) if not pd.isna(row['new_contributors_Max']) else None,
                'new_contributors_detail_Latest': float(row['new_contributors_detail_Latest']) if not pd.isna(row['new_contributors_detail_Latest']) else None,
                'new_contributors_detail_Data_Points': float(row['new_contributors_detail_Data_Points']) if not pd.isna(row['new_contributors_detail_Data_Points']) else None,
                'inactive_contributors_Latest': float(row['inactive_contributors_Latest']) if not pd.isna(row['inactive_contributors_Latest']) else None,
                'inactive_contributors_Data_Points': float(row['inactive_contributors_Data_Points']) if not pd.isna(row['inactive_contributors_Data_Points']) else None,
                'inactive_contributors_Average': float(row['inactive_contributors_Average']) if not pd.isna(row['inactive_contributors_Average']) else None,
                'inactive_contributors_Min': float(row['inactive_contributors_Min']) if not pd.isna(row['inactive_contributors_Min']) else None,
                'inactive_contributors_Max': float(row['inactive_contributors_Max']) if not pd.isna(row['inactive_contributors_Max']) else None,
                'contributor_email_suffixes_Latest': float(row['contributor_email_suffixes_Latest']) if not pd.isna(row['contributor_email_suffixes_Latest']) else None,
                'contributor_email_suffixes_Data_Points': float(row['contributor_email_suffixes_Data_Points']) if not pd.isna(row['contributor_email_suffixes_Data_Points']) else None
            }
            
            # 获取现有的metrics_data
            metrics_data = {}
            if project.metrics_data:
                try:
                    if isinstance(project.metrics_data, str):
                        metrics_data = json.loads(project.metrics_data)
                    else:
                        metrics_data = project.metrics_data
                except Exception as e:
                    print(f"解析现有metrics_data失败: {e}")
                    metrics_data = {}
            
            # 更新Contributor_Metrics部分
            metrics_data['Contributor_Metrics'] = contributor_metrics
            
            # 将更新后的数据转换回JSON字符串
            updated_metrics_data = json.dumps(metrics_data)
            
            # 更新项目记录
            project.metrics_data = updated_metrics_data
            updated_count += 1
            
            print(f"更新项目 {project_key} 的贡献者指标数据")
            
            # 每10个项目提交一次
            if updated_count % 10 == 0:
                session.commit()
                print(f"已提交 {updated_count} 个项目")
        
        # 提交所有更改
        session.commit()
        print(f"成功更新 {updated_count} 个项目的贡献者指标数据")
        
    except Exception as e:
        print(f"导入贡献者指标数据时出错: {e}")
        logger.error(f"导入贡献者指标数据时出错: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    import_contributor_metrics()