#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DataEase Windows自动部署脚本
为GitHub项目搜索引擎自动部署DataEase数据大屏
"""

import os
import sys
import subprocess
import requests
import time
import json
from pathlib import Path
import zipfile
import shutil

class DataEaseDeployer:
    """DataEase部署器"""
    
    def __init__(self, install_dir="C:\\dataease"):
        self.install_dir = Path(install_dir)
        self.download_url = "https://github.com/dataease/dataease/releases/latest"
        self.api_base_url = "http://localhost:8000"
        
    def print_banner(self):
        """打印部署横幅"""
        banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    🚀 DataEase数据大屏自动部署工具                             ║
    ║                                                              ║
    ║    为GitHub项目搜索引擎部署DataEase数据可视化平台                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_system_requirements(self):
        """检查系统要求"""
        print("🔍 检查系统要求...")
        
        # 检查操作系统
        if os.name != 'nt':
            print("❌ 此脚本仅支持Windows系统")
            return False
        
        # 检查Java
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Java已安装")
            else:
                print("❌ Java未安装，请先安装Java 11+")
                return False
        except FileNotFoundError:
            print("❌ Java未安装，请先安装Java 11+")
            return False
        
        # 检查网络连接
        try:
            response = requests.get("https://github.com", timeout=10)
            if response.status_code == 200:
                print("✅ 网络连接正常")
            else:
                print("❌ 网络连接异常")
                return False
        except:
            print("❌ 网络连接异常")
            return False
        
        # 检查端口占用
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 8080))
            sock.close()
            if result == 0:
                print("❌ 端口8080已被占用")
                return False
            else:
                print("✅ 端口8080可用")
        except:
            print("⚠️ 无法检查端口占用")
        
        return True
    
    def create_install_directory(self):
        """创建安装目录"""
        print(f"📁 创建安装目录: {self.install_dir}")
        
        try:
            self.install_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ 安装目录创建成功")
            return True
        except Exception as e:
            print(f"❌ 创建安装目录失败: {e}")
            return False
    
    def download_dataease(self):
        """下载DataEase"""
        print("📥 下载DataEase...")
        
        try:
            # 获取最新版本信息
            response = requests.get("https://api.github.com/repos/dataease/dataease/releases/latest")
            if response.status_code == 200:
                release_info = response.json()
                assets = release_info.get('assets', [])
                
                # 查找Windows版本
                windows_asset = None
                for asset in assets:
                    if 'windows' in asset['name'].lower() and asset['name'].endswith('.zip'):
                        windows_asset = asset
                        break
                
                if windows_asset:
                    download_url = windows_asset['browser_download_url']
                    filename = windows_asset['name']
                    
                    print(f"   下载文件: {filename}")
                    
                    # 下载文件
                    response = requests.get(download_url, stream=True)
                    total_size = int(response.headers.get('content-length', 0))
                    
                    downloaded = 0
                    with open(self.install_dir / filename, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    percent = (downloaded / total_size) * 100
                                    print(f"   下载进度: {percent:.1f}%", end='\r')
                    
                    print(f"\n✅ DataEase下载完成")
                    return filename
                else:
                    print("❌ 未找到Windows版本的DataEase")
                    return None
            else:
                print("❌ 获取版本信息失败")
                return None
                
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return None
    
    def extract_dataease(self, filename):
        """解压DataEase"""
        print("📦 解压DataEase...")
        
        try:
            zip_path = self.install_dir / filename
            extract_path = self.install_dir / "dataease_app"
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            print(f"✅ DataEase解压完成")
            return extract_path
        except Exception as e:
            print(f"❌ 解压失败: {e}")
            return None
    
    def create_config_file(self, dataease_path):
        """创建配置文件"""
        print("⚙️ 创建配置文件...")
        
        config_content = f"""
server:
  port: 8080

datasource:
  mysql:
    host: localhost
    port: 3306
    database: dataease
    username: root
    password: dataease123

# API数据源配置
api:
  external:
    github-search:
      url: {self.api_base_url}
      timeout: 30000
      headers:
        Content-Type: application/json

# 缓存配置
cache:
  enabled: true
  ttl: 300
  max_size: 1000

# 安全配置
security:
  cors:
    allowed_origins:
      - "http://localhost:8000"
      - "http://localhost:8100"
    allowed_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers: ["Content-Type", "Authorization"]
"""
        
        config_file = dataease_path / "conf" / "application.yml"
        
        try:
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print(f"✅ 配置文件创建成功: {config_file}")
            return True
        except Exception as e:
            print(f"❌ 配置文件创建失败: {e}")
            return False
    
    def create_startup_script(self, dataease_path):
        """创建启动脚本"""
        print("📝 创建启动脚本...")
        
        # Windows批处理脚本
        batch_content = f"""@echo off
echo 启动DataEase数据大屏...
cd /d "{dataease_path}"
set JAVA_OPTS=-Xms2g -Xmx4g -XX:+UseG1GC
java %JAVA_OPTS% -jar dataease.jar
pause
"""
        
        batch_file = self.install_dir / "start_dataease.bat"
        
        try:
            with open(batch_file, 'w', encoding='gbk') as f:
                f.write(batch_content)
            
            print(f"✅ 启动脚本创建成功: {batch_file}")
            return True
        except Exception as e:
            print(f"❌ 启动脚本创建失败: {e}")
            return False
    
    def create_service_script(self):
        """创建服务安装脚本"""
        print("🔧 创建服务安装脚本...")
        
        service_content = f"""@echo off
echo 安装DataEase为Windows服务...
sc create DataEase binPath= "\"C:\\Program Files\\Java\\jdk-11.0.12\\bin\\java.exe\" -Xms2g -Xmx4g -XX:+UseG1GC -jar \"{self.install_dir}\\dataease_app\\dataease.jar\"" start= auto
sc description DataEase "DataEase数据可视化平台"
sc start DataEase
echo DataEase服务安装完成
pause
"""
        
        service_file = self.install_dir / "install_service.bat"
        
        try:
            with open(service_file, 'w', encoding='gbk') as f:
                f.write(service_content)
            
            print(f"✅ 服务安装脚本创建成功: {service_file}")
            return True
        except Exception as e:
            print(f"❌ 服务安装脚本创建失败: {e}")
            return False
    
    def create_desktop_shortcut(self):
        """创建桌面快捷方式"""
        print("🖥️ 创建桌面快捷方式...")
        
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "DataEase数据大屏.lnk")
            target = str(self.install_dir / "start_dataease.bat")
            wDir = str(self.install_dir)
            icon = target
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = icon
            shortcut.save()
            
            print("✅ 桌面快捷方式创建成功")
            return True
        except ImportError:
            print("⚠️ 需要安装winshell和pywin32才能创建桌面快捷方式")
            print("   pip install winshell pywin32")
            return False
        except Exception as e:
            print(f"❌ 桌面快捷方式创建失败: {e}")
            return False
    
    def test_api_connection(self):
        """测试API连接"""
        print("🔗 测试API连接...")
        
        try:
            response = requests.get(f"{self.api_base_url}/api/health", timeout=10)
            if response.status_code == 200:
                print("✅ API连接成功")
                return True
            else:
                print(f"❌ API连接失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API连接异常: {e}")
            return False
    
    def create_dataease_dashboard_config(self):
        """创建DataEase数据大屏配置"""
        print("📊 创建数据大屏配置...")
        
        dashboard_config = {
            "name": "GitHub项目数据大屏",
            "description": "基于GitHub项目搜索引擎的数据可视化大屏",
            "datasource": {
                "type": "api",
                "url": f"{self.api_base_url}/api/dataease",
                "headers": {
                    "Content-Type": "application/json"
                }
            },
            "components": [
                {
                    "type": "wordcloud",
                    "title": "活跃度TOP20",
                    "api": "/wordcloud/activity",
                    "field": "name",
                    "value": "value"
                },
                {
                    "type": "wordcloud", 
                    "title": "参与者TOP20",
                    "api": "/wordcloud/participants",
                    "field": "name",
                    "value": "value"
                },
                {
                    "type": "wordcloud",
                    "title": "关注度TOP20", 
                    "api": "/wordcloud/attention",
                    "field": "name",
                    "value": "value"
                },
                {
                    "type": "stats",
                    "title": "项目统计",
                    "api": "/dashboard/stats"
                }
            ]
        }
        
        config_file = self.install_dir / "dashboard_config.json"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(dashboard_config, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 数据大屏配置创建成功: {config_file}")
            return True
        except Exception as e:
            print(f"❌ 数据大屏配置创建失败: {e}")
            return False
    
    def deploy(self):
        """执行完整部署"""
        self.print_banner()
        
        # 检查系统要求
        if not self.check_system_requirements():
            print("\n❌ 系统要求检查失败，请解决上述问题后重试")
            return False
        
        # 创建安装目录
        if not self.create_install_directory():
            return False
        
        # 测试API连接
        if not self.test_api_connection():
            print("\n⚠️ API连接失败，请确保GitHub项目搜索引擎正在运行")
            print("   启动命令: python run.py")
            
            response = input("是否继续部署？(y/n): ")
            if response.lower() != 'y':
                return False
        
        # 下载DataEase
        filename = self.download_dataease()
        if not filename:
            return False
        
        # 解压DataEase
        dataease_path = self.extract_dataease(filename)
        if not dataease_path:
            return False
        
        # 创建配置文件
        if not self.create_config_file(dataease_path):
            return False
        
        # 创建启动脚本
        if not self.create_startup_script(dataease_path):
            return False
        
        # 创建服务安装脚本
        if not self.create_service_script():
            return False
        
        # 创建数据大屏配置
        if not self.create_dataease_dashboard_config():
            return False
        
        # 创建桌面快捷方式
        self.create_desktop_shortcut()
        
        print("\n🎉 DataEase部署完成！")
        print(f"   安装目录: {self.install_dir}")
        print(f"   启动脚本: {self.install_dir}\\start_dataease.bat")
        print(f"   服务脚本: {self.install_dir}\\install_service.bat")
        print(f"   配置文件: {dataease_path}\\conf\\application.yml")
        
        print("\n📖 使用说明:")
        print("1. 启动DataEase: 双击 start_dataease.bat")
        print("2. 访问数据大屏: http://localhost:8080")
        print("3. 导入词云模板: 使用项目中的 词云-TEMPLATE.DET2 文件")
        print("4. 配置数据源: http://localhost:8080/datasource")
        
        return True

def main():
    """主函数"""
    print("DataEase Windows自动部署工具")
    print("=" * 50)
    
    # 检查是否以管理员权限运行
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("⚠️ 建议以管理员权限运行此脚本")
            response = input("是否继续？(y/n): ")
            if response.lower() != 'y':
                return
    except:
        pass
    
    # 创建部署器
    deployer = DataEaseDeployer()
    
    # 执行部署
    success = deployer.deploy()
    
    if success:
        print("\n✅ 部署成功！")
        input("按回车键退出...")
    else:
        print("\n❌ 部署失败！")
        input("按回车键退出...")

if __name__ == "__main__":
    main()