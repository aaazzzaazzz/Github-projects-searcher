#!/usr/bin/env python3
"""
将贡献者指标数据导入到PostgreSQL数据库
"""

import pandas as pd
import json
import psycopg2
from config import settings

def import_contributor_metrics():
    """将贡献者指标数据导入到PostgreSQL数据库"""
    try:
        # 读取Excel文件
        df = pd.read_excel('top_300_metrics_full.xlsx', sheet_name='Contributor_Metrics')
        
        print(f"读取到 {len(df)} 行贡献者指标数据")
        
        # 连接PostgreSQL数据库
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        
        updated_count = 0
        for index, row in df.iterrows():
            project_key = str(row['Project_Key']) if not pd.isna(row['Project_Key']) else None
            
            if not project_key:
                print(f"跳过第 {index+1} 行：Project_Key 为空")
                continue
            
            # 检查项目是否存在
            cursor.execute("SELECT id FROM projects WHERE project_key = %s", (project_key,))
            if not cursor.fetchone():
                print(f"未找到项目: {project_key}")
                continue
            
            # 构建贡献者指标数据
            contributor_metrics = {}
            
            # 安全地添加各个字段
            fields_to_add = [
                ('new_contributors_Latest', 'new_contributors_Latest'),
                ('new_contributors_Data_Points', 'new_contributors_Data_Points'),
                ('new_contributors_Average', 'new_contributors_Average'),
                ('new_contributors_Min', 'new_contributors_Min'),
                ('new_contributors_Max', 'new_contributors_Max'),
                ('new_contributors_detail_Latest', 'new_contributors_detail_Latest'),
                ('new_contributors_detail_Data_Points', 'new_contributors_detail_Data_Points'),
                ('inactive_contributors_Latest', 'inactive_contributors_Latest'),
                ('inactive_contributors_Data_Points', 'inactive_contributors_Data_Points'),
                ('inactive_contributors_Average', 'inactive_contributors_Average'),
                ('inactive_contributors_Min', 'inactive_contributors_Min'),
                ('inactive_contributors_Max', 'inactive_contributors_Max'),
                ('inactive_contributors_detail_Latest', 'inactive_contributors_detail_Latest'),
                ('inactive_contributors_detail_Data_Points', 'inactive_contributors_detail_Data_Points'),
                ('total_contributors_Latest', 'total_contributors_Latest'),
                ('total_contributors_Data_Points', 'total_contributors_Data_Points'),
                ('total_contributors_Average', 'total_contributors_Average'),
                ('total_contributors_Min', 'total_contributors_Min'),
                ('total_contributors_Max', 'total_contributors_Max'),
                ('total_contributors_detail_Latest', 'total_contributors_detail_Latest'),
                ('total_contributors_detail_Data_Points', 'total_contributors_detail_Data_Points'),
                ('contributor_growth_rate_Latest', 'contributor_growth_rate_Latest'),
                ('contributor_growth_rate_Data_Points', 'contributor_growth_rate_Data_Points'),
                ('contributor_growth_rate_Average', 'contributor_growth_rate_Average'),
                ('contributor_growth_rate_Min', 'contributor_growth_rate_Min'),
                ('contributor_growth_rate_Max', 'contributor_growth_rate_Max'),
                ('contributor_retention_rate_Latest', 'contributor_retention_rate_Latest'),
                ('contributor_retention_rate_Data_Points', 'contributor_retention_rate_Data_Points'),
                ('contributor_retention_rate_Average', 'contributor_retention_rate_Average'),
                ('contributor_retention_rate_Min', 'contributor_retention_rate_Min'),
                ('contributor_retention_rate_Max', 'contributor_retention_rate_Max')
            ]
            
            for field_name, key in fields_to_add:
                if field_name in row and not pd.isna(row[field_name]):
                    value = row[field_name]
                    # 处理NaN值
                    if isinstance(value, float) and (value != value):  # NaN检查
                        contributor_metrics[key] = None
                    else:
                        contributor_metrics[key] = value
            
            # 获取现有的metrics_data
            cursor.execute("SELECT metrics_data FROM projects WHERE project_key = %s", (project_key,))
            result = cursor.fetchone()
            
            if result and result[0]:
                try:
                    # 解析现有的metrics_data
                    existing_metrics = json.loads(result[0].replace(':NaN', ':null'))
                except json.JSONDecodeError:
                    existing_metrics = {}
            else:
                existing_metrics = {}
            
            # 更新Contributor_Metrics部分
            existing_metrics['Contributor_Metrics'] = contributor_metrics
            
            # 将更新后的metrics_data写回数据库
            updated_metrics_json = json.dumps(existing_metrics, ensure_ascii=False)
            cursor.execute(
                "UPDATE projects SET metrics_data = %s WHERE project_key = %s",
                (updated_metrics_json, project_key)
            )
            
            updated_count += 1
            print(f"已更新项目 {project_key} 的贡献者指标数据")
        
        # 提交事务
        conn.commit()
        print(f"成功更新了 {updated_count} 个项目的贡献者指标数据")
        
    except Exception as e:
        print(f"导入贡献者指标数据时出错: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    import_contributor_metrics()