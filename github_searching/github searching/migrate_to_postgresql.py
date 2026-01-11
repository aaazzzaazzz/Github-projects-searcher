#!/usr/bin/env python3
"""
SQLite到PostgreSQL数据库迁移脚本
将现有的SQLite数据迁移到PostgreSQL数据库
"""

import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime
import sys
from config import settings

def connect_sqlite():
    """连接SQLite数据库"""
    try:
        conn = sqlite3.connect('github_search.db')
        return conn
    except Exception as e:
        print(f"连接SQLite数据库失败: {e}")
        return None

def connect_postgresql():
    """连接PostgreSQL数据库"""
    try:
        # 从settings获取数据库URL
        db_url = settings.database_url
        # 解析连接参数
        # 格式: postgresql://postgres:lsy20061229@localhost:5432/github_search
        if db_url.startswith('postgresql://'):
            url_parts = db_url.replace('postgresql://', '').split('@')
            user_pass = url_parts[0].split(':')
            host_db = url_parts[1].split('/')
            
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ''
            host_port = host_db[0].split(':')
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else '5432'
            database = host_db[1]
            
            conn = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            return conn
    except Exception as e:
        print(f"连接PostgreSQL数据库失败: {e}")
        print("请确保PostgreSQL服务正在运行，并且数据库已创建")
        return None

def get_sqlite_tables(conn):
    """获取SQLite所有表名"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    return tables

def get_table_schema(conn, table_name):
    """获取表结构"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    return columns

def create_postgresql_table(pg_conn, table_name, columns):
    """在PostgreSQL中创建表"""
    cursor = pg_conn.cursor()
    
    # 转换SQLite数据类型到PostgreSQL
    type_mapping = {
        'INTEGER': 'INTEGER',
        'TEXT': 'TEXT',
        'REAL': 'REAL',
        'BLOB': 'BYTEA',
        'VARCHAR': 'VARCHAR(255)',
        'DATETIME': 'TIMESTAMP',
        'BOOLEAN': 'BOOLEAN'
    }
    
    column_defs = []
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        not_null = 'NOT NULL' if col[3] else ''
        default_val = f"DEFAULT {col[4]}" if col[4] else ''
        
        # 数据类型转换
        pg_type = 'TEXT'  # 默认类型
        for sqlite_type, pg_type_mapped in type_mapping.items():
            if sqlite_type in col_type:
                pg_type = pg_type_mapped
                break
        
        # 特殊处理ID字段
        if col_name.lower() == 'id' and 'INTEGER' in col_type.upper():
            pg_type = 'SERIAL PRIMARY KEY'
            column_defs.append(f"{col_name} {pg_type}")
        else:
            column_defs.append(f"{col_name} {pg_type} {not_null} {default_val}".strip())
    
    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)});"
    
    try:
        cursor.execute(create_sql)
        pg_conn.commit()
        print(f"✓ 创建表 {table_name} 成功")
        return True
    except Exception as e:
        print(f"✗ 创建表 {table_name} 失败: {e}")
        return False

def migrate_table_data(sqlite_conn, pg_conn, table_name):
    """迁移表数据"""
    try:
        # 从SQLite读取数据
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", sqlite_conn)
        
        if df.empty:
            print(f"表 {table_name} 没有数据，跳过")
            return True
        
        # 插入到PostgreSQL
        cursor = pg_conn.cursor()
        
        # 准备插入语句
        columns = list(df.columns)
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        
        # 批量插入数据
        data_to_insert = [tuple(row) for row in df.itertuples(index=False)]
        cursor.executemany(insert_sql, data_to_insert)
        
        pg_conn.commit()
        print(f"✓ 迁移表 {table_name} 数据成功 ({len(df)} 条记录)")
        return True
        
    except Exception as e:
        print(f"✗ 迁移表 {table_name} 数据失败: {e}")
        pg_conn.rollback()
        return False

def main():
    """主函数"""
    print("=== SQLite到PostgreSQL数据库迁移工具 ===\n")
    
    # 连接SQLite数据库
    print("1. 连接SQLite数据库...")
    sqlite_conn = connect_sqlite()
    if not sqlite_conn:
        sys.exit(1)
    print("SQLite数据库连接成功")
    
    # 连接PostgreSQL数据库
    print("\n2. 连接PostgreSQL数据库...")
    pg_conn = connect_postgresql()
    if not pg_conn:
        sqlite_conn.close()
        sys.exit(1)
    print("PostgreSQL数据库连接成功")
    
    try:
        # 获取所有表
        print("\n3. 获取数据库表结构...")
        tables = get_sqlite_tables(sqlite_conn)
        print(f"发现 {len(tables)} 个表: {', '.join(tables)}")
        
        # 迁移每个表
        print("\n4. 开始迁移数据...")
        success_count = 0
        
        for table_name in tables:
            print(f"\n处理表: {table_name}")
            
            # 获取表结构
            columns = get_table_schema(sqlite_conn, table_name)
            
            # 在PostgreSQL中创建表
            if create_postgresql_table(pg_conn, table_name, columns):
                # 迁移数据
                if migrate_table_data(sqlite_conn, pg_conn, table_name):
                    success_count += 1
        
        print(f"\n=== 迁移完成 ===")
        print(f"成功迁移 {success_count}/{len(tables)} 个表")
        
        if success_count == len(tables):
            print("🎉 所有数据迁移成功！")
        else:
            print("⚠️ 部分数据迁移失败，请检查错误信息")
    
    except Exception as e:
        print(f"迁移过程中发生错误: {e}")
    
    finally:
        sqlite_conn.close()
        pg_conn.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()