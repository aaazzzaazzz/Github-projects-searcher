<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DataEase数据大屏 - GitHub项目搜索引擎</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Microsoft YaHei', sans-serif;
            background-color: #f5f5f5;
        }
        
        .embed-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .embed-container {
            height: calc(100vh - 70px);
            width: 100%;
            position: relative;
        }
        
        .embed-iframe {
            width: 100%;
            height: 100%;
            border: none;
            background: white;
        }
        
        .embed-controls {
            position: fixed;
            top: 80px;
            right: 20px;
            z-index: 1000;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        }
        
        .url-input {
            width: 300px;
            margin-right: 10px;
        }
        
        .fullscreen-btn {
            position: fixed;
            top: 80px;
            left: 20px;
            z-index: 1000;
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 8px;
            cursor: pointer;
        }
        
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 8px;
            margin: 20px;
            border: 1px solid #f5c6cb;
        }
        
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 400px;
            font-size: 18px;
            color: #666;
        }
    </style>
</head>
<body>
    <!-- 嵌入头部 -->
    <div class="embed-header">
        <div class="container">
            <div class="row align-items-center">
                <div class="col">
                    <h1 class="h3 mb-0">
                        <i class="fas fa-chart-line me-2"></i>
                        DataEase数据大屏
                    </h1>
                </div>
                <div class="col-auto">
                    <a href="/" class="btn btn-light">
                        <i class="fas fa-arrow-left me-2"></i>
                        返回搜索
                    </a>
                </div>
            </div>
        </div>
    </div>

    <!-- 嵌入控制 -->
    <div class="embed-controls">
        <div class="input-group">
            <input type="url" 
                   class="form-control url-input" 
                   id="dataeaseUrl" 
                   placeholder="输入DataEase大屏URL"
                   value="http://localhost:8080">
            <button class="btn btn-primary" onclick="loadDashboard()">
                <i class="fas fa-external-link-alt me-1"></i>
                加载
            </button>
        </div>
        <div class="mt-2">
            <button class="btn btn-success btn-sm" onclick="toggleFullscreen()">
                <i class="fas fa-expand me-1"></i>
                全屏
            </button>
            <button class="btn btn-info btn-sm ms-2" onclick="refreshIframe()">
                <i class="fas fa-sync-alt me-1"></i>
                刷新
            </button>
        </div>
    </div>

    <!-- 全屏按钮 -->
    <button class="fullscreen-btn" onclick="toggleFullscreen()">
        <i class="fas fa-expand"></i>
    </button>

    <!-- 嵌入容器 -->
    <div class="embed-container">
        <div id="loadingIndicator" class="loading">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">加载中...</span>
            </div>
            <div class="ms-3">正在加载数据大屏...</div>
        </div>
        
        <iframe id="dataeaseFrame" 
                class="embed-iframe" 
                style="display: none;"
                onload="hideLoading()">
        </iframe>
        
        <div id="errorMessage" class="error-message" style="display: none;">
            <h5><i class="fas fa-exclamation-triangle me-2"></i>加载失败</h5>
            <p>无法加载DataEase数据大屏，请检查：</p>
            <ul>
                <li>DataEase服务是否正在运行</li>
                <li>URL地址是否正确</li>
                <li>网络连接是否正常</li>
                <li>是否有跨域访问限制</li>
            </ul>
            <button class="btn btn-primary" onclick="retryLoad()">
                <i class="fas fa-redo me-2"></i>
                重试
            </button>
        </div>
    </div>

    <!-- JavaScript -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 默认DataEase URL列表
        const defaultUrls = [
            'http://localhost:8080',
            'http://localhost:8080/dashboard',
            'https://dataease.io',
            'https://your-dataease-domain.com'
        ];
        
        // 从localStorage获取上次使用的URL
        let currentUrl = localStorage.getItem('dataeaseUrl') || 'http://localhost:8080';
        
        // 页面加载时初始化
        document.addEventListener('DOMContentLoaded', function() {
            document.getElementById('dataeaseUrl').value = currentUrl;
            loadDashboard();
        });
        
        // 加载数据大屏
        function loadDashboard() {
            const url = document.getElementById('dataeaseUrl').value.trim();
            
            if (!url) {
                showError('请输入DataEase数据大屏URL');
                return;
            }
            
            // 保存URL到localStorage
            localStorage.setItem('dataeaseUrl', url);
            
            // 显示加载状态
            showLoading();
            
            // 创建iframe并加载
            const iframe = document.getElementById('dataeaseFrame');
            iframe.src = url;
            
            // 设置超时检查
            setTimeout(() => {
                try {
                    // 尝试访问iframe内容
                    const iframeContent = iframe.contentWindow || iframe.contentDocument;
                    if (iframeContent) {
                        hideLoading();
                    }
                } catch (e) {
                    // 如果有跨域错误，但iframe可能仍然正常工作
                    console.log('跨域访问限制，但iframe可能正常工作');
                    setTimeout(hideLoading, 2000); // 延迟隐藏加载状态
                }
            }, 5000);
        }
        
        // 显示加载状态
        function showLoading() {
            document.getElementById('loadingIndicator').style.display = 'flex';
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('dataeaseFrame').style.display = 'none';
        }
        
        // 隐藏加载状态
        function hideLoading() {
            document.getElementById('loadingIndicator').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'none';
            document.getElementById('dataeaseFrame').style.display = 'block';
        }
        
        // 显示错误信息
        function showError(message) {
            document.getElementById('errorMessage').querySelector('p').textContent = message;
            document.getElementById('loadingIndicator').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'block';
            document.getElementById('dataeaseFrame').style.display = 'none';
        }
        
        // 重试加载
        function retryLoad() {
            loadDashboard();
        }
        
        // 刷新iframe
        function refreshIframe() {
            const iframe = document.getElementById('dataeaseFrame');
            const currentSrc = iframe.src;
            iframe.src = currentSrc; // 重新加载
        }
        
        // 全屏切换
        function toggleFullscreen() {
            const container = document.querySelector('.embed-container');
            const fullscreenBtn = document.querySelector('.fullscreen-btn');
            
            if (!document.fullscreenElement) {
                container.requestFullscreen().then(() => {
                    fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
                }).catch(err => {
                    console.error('无法进入全屏:', err);
                });
            } else {
                document.exitFullscreen().then(() => {
                    fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
                });
            }
        }
        
        // 监听全屏变化
        document.addEventListener('fullscreenchange', function() {
            const fullscreenBtn = document.querySelector('.fullscreen-btn');
            if (document.fullscreenElement) {
                fullscreenBtn.innerHTML = '<i class="fas fa-compress"></i>';
            } else {
                fullscreenBtn.innerHTML = '<i class="fas fa-expand"></i>';
            }
        });
        
        // 监听ESC键退出全屏
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && document.fullscreenElement) {
                document.exitFullscreen();
            }
        });
        
        // URL输入框回车事件
        document.getElementById('dataeaseUrl').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                loadDashboard();
            }
        });
        
        // 添加URL下拉建议
        function setupUrlSuggestions() {
            const input = document.getElementById('dataeaseUrl');
            const datalist = document.createElement('datalist');
            datalist.id = 'urlSuggestions';
            
            defaultUrls.forEach(url => {
                const option = document.createElement('option');
                option.value = url;
                datalist.appendChild(option);
            });
            
            input.setAttribute('list', 'urlSuggestions');
            input.parentNode.appendChild(datalist);
        }
        
        // 初始化URL建议
        setupUrlSuggestions();
        
        // 错误处理
        window.addEventListener('message', function(event) {
            // 监听来自iframe的消息
            if (event.data && event.data.type === 'error') {
                showError('数据大屏加载出错: ' + event.data.message);
            }
        });
        
        // iframe加载错误处理
        document.getElementById('dataeaseFrame').addEventListener('error', function() {
            showError('无法加载数据大屏，请检查URL是否正确');
        });
    </script>
</body>
</html>