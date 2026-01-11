"""
从top_300_metrics_full.xlsx的Issue_Metrics工作表导入Issue统计数据到数据库
"""
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from project.models import Project
from config import settings
import json

def import_issue_metrics():
    """导入Issue指标数据到数据库"""
    excel_file = 'top_300_metrics_full.xlsx'

    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("=" * 80)
        print("导入Issue指标数据到数据库")
        print("=" * 80)

        # 读取Issue_Metrics工作表
        df = pd.read_excel(excel_file, sheet_name='Issue_Metrics')

        print(f"\n从Excel读取了 {len(df)} 行Issue指标数据")

        # 准备Issue指标数据
        issue_metrics_data = {}

        for idx, row in df.iterrows():
            project_key = row['Project_Key']

            # 构建Issue指标的字典
            metrics = {
                'issues_new': {
                    'latest': row['issues_new_Latest'] if pd.notna(row['issues_new_Latest']) else None,
                    'data_points': int(row['issues_new_Data_Points']) if pd.notna(row['issues_new_Data_Points']) else None,
                    'average': row['issues_new_Average'] if pd.notna(row['issues_new_Average']) else None,
                    'min': row['issues_new_Min'] if pd.notna(row['issues_new_Min']) else None,
                    'max': row['issues_new_Max'] if pd.notna(row['issues_new_Max']) else None,
                },
                'issues_closed': {
                    'latest': row['issues_closed_Latest'] if pd.notna(row['issues_closed_Latest']) else None,
                    'data_points': int(row['issues_closed_Data_Points']) if pd.notna(row['issues_closed_Data_Points']) else None,
                    'average': row['issues_closed_Average'] if pd.notna(row['issues_closed_Average']) else None,
                    'min': row['issues_closed_Min'] if pd.notna(row['issues_closed_Min']) else None,
                    'max': row['issues_closed_Max'] if pd.notna(row['issues_closed_Max']) else None,
                },
                'issue_age': {
                    'keys_count': int(row['issue_age_Keys_Count']) if pd.notna(row['issue_age_Keys_Count']) else None,
                    'sample_keys': eval(row['issue_age_Sample_Keys']) if pd.notna(row['issue_age_Sample_Keys']) and isinstance(row['issue_age_Sample_Keys'], str) else None,
                },
                'issue_comments': {
                    'latest': int(row['issue_comments_Latest']) if pd.notna(row['issue_comments_Latest']) else None,
                    'data_points': int(row['issue_comments_Data_Points']) if pd.notna(row['issue_comments_Data_Points']) else None,
                    'average': row['issue_comments_Average'] if pd.notna(row['issue_comments_Average']) else None,
                    'min': int(row['issue_comments_Min']) if pd.notna(row['issue_comments_Min']) else None,
                    'max': int(row['issue_comments_Max']) if pd.notna(row['issue_comments_Max']) else None,
                },
                'issue_resolution_duration': {
                    'keys_count': int(row['issue_resolution_duration_Keys_Count']) if pd.notna(row['issue_resolution_duration_Keys_Count']) else None,
                    'sample_keys': eval(row['issue_resolution_duration_Sample_Keys']) if pd.notna(row['issue_resolution_duration_Sample_Keys']) and isinstance(row['issue_resolution_duration_Sample_Keys'], str) else None,
                },
                'issue_response_time': {
                    'keys_count': int(row['issue_response_time_Keys_Count']) if pd.notna(row['issue_response_time_Keys_Count']) else None,
                    'sample_keys': eval(row['issue_response_time_Sample_Keys']) if pd.notna(row['issue_response_time_Sample_Keys']) and isinstance(row['issue_response_time_Sample_Keys'], str) else None,
                },
                'issues_and_change_request_active': {
                    'latest': int(row['issues_and_change_request_active_Latest']) if pd.notna(row['issues_and_change_request_active_Latest']) else None,
                    'data_points': int(row['issues_and_change_request_active_Data_Points']) if pd.notna(row['issues_and_change_request_active_Data_Points']) else None,
                    'average': row['issues_and_change_request_active_Average'] if pd.notna(row['issues_and_change_request_active_Average']) else None,
                    'min': int(row['issues_and_change_request_active_Min']) if pd.notna(row['issues_and_change_request_active_Min']) else None,
                    'max': int(row['issues_and_change_request_active_Max']) if pd.notna(row['issues_and_change_request_active_Max']) else None,
                }
            }

            issue_metrics_data[project_key] = metrics

        print(f"\n准备了 {len(issue_metrics_data)} 个项目的Issue指标数据")

        # 更新数据库中的项目
        updated_count = 0
        not_found_count = 0

        for project_key, issue_metrics in issue_metrics_data.items():
            # 查找项目
            project = session.query(Project).filter(Project.project_key == project_key).first()

            if project:
                # 获取现有的metrics_data
                existing_metrics = {}
                if project.metrics_data:
                    try:
                        existing_metrics = json.loads(project.metrics_data)
                    except:
                        existing_metrics = {}

                # 合并Issue指标
                existing_metrics['issue_metrics'] = issue_metrics

                # 更新项目的metrics_data
                project.metrics_data = json.dumps(existing_metrics, ensure_ascii=False)
                updated_count += 1

                if updated_count % 50 == 0:
                    print(f"已更新 {updated_count} 个项目...")
            else:
                not_found_count += 1

        # 提交更改
        session.commit()

        print(f"\n" + "=" * 80)
        print("导入完成")
        print("=" * 80)
        print(f"成功更新: {updated_count} 个项目")
        print(f"未找到的项目: {not_found_count} 个")

        # 验证导入结果
        print(f"\n验证导入结果 (前5个项目):")
        projects_with_issue_metrics = session.query(Project)\
            .filter(Project.metrics_data.isnot(None))\
            .limit(5).all()

        for project in projects_with_issue_metrics:
            if project.metrics_data:
                metrics = json.loads(project.metrics_data)
                if 'issue_metrics' in metrics:
                    issue_metrics = metrics['issue_metrics']
                    print(f"\n项目: {project.project_key}")
                    print(f"  新建Issue (最新): {issue_metrics.get('issues_new', {}).get('latest')}")
                    print(f"  关闭Issue (最新): {issue_metrics.get('issues_closed', {}).get('latest')}")
                    print(f"  Issue评论 (最新): {issue_metrics.get('issue_comments', {}).get('latest')}")
                    print(f"  活跃Issue (最新): {issue_metrics.get('issues_and_change_request_active', {}).get('latest')}")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == '__main__':
    import_issue_metrics()
