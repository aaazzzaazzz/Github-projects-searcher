#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from data_importer import DataImporter
from project.models import GitHubEvent
import sqlite3

def safe_bool(value):
    """安全地转换布尔值，处理NaN"""
    if pd.isna(value) or value == 'nan':
        return False
    return bool(value)

def import_all_events():
    """导入所有事件数据"""
    print("=== 导入所有事件数据 ===")
    
    try:
        # 创建数据导入器
        importer = DataImporter()
        session = importer.Session()
        
        # 读取Excel文件
        df = pd.read_excel("top300_20_23_robust_all_fixed.xlsx")
        print(f"Excel文件总行数: {len(df)}")
        
        # 清空现有事件
        session.query(GitHubEvent).delete()
        session.commit()
        print("清空现有事件数据")
        
        # 获取项目列表中的所有项目
        conn = sqlite3.connect('github_search.db')
        cursor = conn.cursor()
        cursor.execute('SELECT project_key FROM projects')
        valid_projects = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        print(f"有效项目数量: {len(valid_projects)}")
        
        # 只导入有效项目的事件
        imported_count = 0
        skipped_count = 0
        
        for i, (_, row) in enumerate(df.iterrows()):
            project_key = row.get('repo_name')
            if project_key in valid_projects:
                try:
                    # 处理日期时间字段
                    created_at = importer._parse_datetime(row.get('created_at'))
                    
                    event = GitHubEvent(
                        github_event_id=row.get('id'),
                        event_type=row.get('type'),
                        action=row.get('action'),
                        created_at=created_at,
                        actor_id=row.get('actor_id'),
                        actor_login=row.get('actor_login'),
                        repo_id=row.get('repo_id'),
                        repo_name=row.get('repo_name'),
                        project_key=project_key,
                        org_id=row.get('org_id'),
                        org_login=row.get('org_login'),
                        
                        # Issue信息
                        issue_id=row.get('issue_id'),
                        issue_number=row.get('issue_number'),
                        issue_title=row.get('issue_title'),
                        issue_body=row.get('body'),
                        issue_author_id=row.get('issue_author_id'),
                        issue_author_login=row.get('issue_author_login'),
                        issue_author_type=row.get('issue_author_type'),
                        issue_author_association=row.get('issue_author_association'),
                        issue_created_at=importer._parse_datetime(row.get('issue_created_at')),
                        issue_updated_at=importer._parse_datetime(row.get('issue_updated_at')),
                        issue_closed_at=importer._parse_datetime(row.get('issue_closed_at')),
                        issue_comments=row.get('issue_comments'),
                        
                        # Pull Request信息
                        pull_commits=row.get('pull_commits'),
                        pull_additions=row.get('pull_additions'),
                        pull_deletions=row.get('pull_deletions'),
                        pull_changed_files=row.get('pull_changed_files'),
                        pull_merged=safe_bool(row.get('pull_merged')),
                        pull_merged_at=importer._parse_datetime(row.get('pull_merged_at')),
                        pull_merged_by_login=row.get('pull_merged_by_login'),
                        pull_review_comments=row.get('pull_review_comments'),
                        
                        # Push信息
                        push_size=row.get('push_size'),
                        push_distinct_size=row.get('push_distinct_size'),
                        push_ref=row.get('push_ref'),
                        push_head=row.get('push_head'),
                        
                        # Release信息
                        release_id=row.get('release_id'),
                        release_tag_name=row.get('release_tag_name'),
                        release_name=row.get('release_name'),
                        release_draft=safe_bool(row.get('release_draft')),
                        release_prerelease=safe_bool(row.get('release_prerelease')),
                        release_created_at=importer._parse_datetime(row.get('release_created_at')),
                        release_published_at=importer._parse_datetime(row.get('release_published_at')),
                        release_body=row.get('release_body')
                    )
                    
                    session.add(event)
                    imported_count += 1
                    
                    if imported_count % 1000 == 0:
                        print(f"已导入 {imported_count} 个事件...")
                        
                except Exception as e:
                    print(f"导入事件时出错 (ID: {row.get('id')}): {e}")
                    continue
            else:
                skipped_count += 1
        
        # 提交事务
        session.commit()
        session.close()
        
        print(f"成功导入 {imported_count} 个事件")
        print(f"跳过 {skipped_count} 个无效项目的事件")
        
        # 生成统计信息
        print("生成贡献者统计信息...")
        importer.generate_contributor_stats()
        
        print("生成项目活跃度统计信息...")
        importer.generate_activity_stats()
        
        return True
        
    except Exception as e:
        print(f"导入所有事件失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import_all_events()