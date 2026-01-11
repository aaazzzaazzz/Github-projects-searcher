# DataEase数据大屏快速连接

## 🎯 目标
将您在DataEase上创建的数据大屏连接到本地运行的GitHub项目搜索引擎API。

## 🚀 快速连接步骤

### 1. 确保API服务运行
```bash
# 检查服务状态
curl http://localhost:8000/api/health
```

### 2. 登录DataEase
- 访问您的DataEase管理界面
- 用户名: `admin`
- 密码: `dataease`

### 3. 添加API数据源
在DataEase中添加数据源：
- **名称**: GitHub项目搜索API
- **类型**: API
- **基础URL**: `http://localhost:8000/api/dataease`
- **请求头**: `Content-Type: application/json`

### 4. 配置数据大屏
在您的数据大屏中：
- 选择组件
- 设置数据源为刚创建的API数据源
- 配置API路径：
  - 词云: `/wordcloud/activity`
  - 统计: `/dashboard/stats`

## 📊 可用API端点

```
词云数据:
http://localhost:8000/api/dataease/wordcloud/activity
http://localhost:8000/api/dataease/wordcloud/participants
http://localhost:8000/api/dataease/wordcloud/attention
http://localhost:8000/api/dataease/wordcloud/change_requests
http://localhost:8000/api/dataease/wordcloud/issues_active
http://localhost:8000/api/dataease/wordcloud/new_contributors
http://localhost:8000/api/dataease/wordcloud/openrank
http://localhost:8000/api/dataease/wordcloud/stars
http://localhost:8000/api/dataease/wordcloud/technical_fork

统计数据:
http://localhost:8000/api/dataease/dashboard/stats
```

## 🔧 数据格式示例

### 词云数据响应
```json
{
  "success": true,
  "metric_type": "activity",
  "data": [
    {"name": "project1", "value": 100},
    {"name": "project2", "value": 85}
  ]
}
```

### 统计数据响应
```json
{
  "success": true,
  "data": {
    "total_projects": 300,
    "total_events": 50000,
    "total_contributors": 1500
  }
}
```

## 🎉 完成

现在您可以在DataEase中查看实时GitHub项目数据了！

## 🆘 遇到问题？

1. **API连接失败**: 检查 `http://localhost:8000/api/health`
2. **数据不显示**: 检查API路径配置
3. **跨域错误**: 确保CORS配置正确
4. **详细帮助**: 查看 `DATASEASE_CONNECTION_GUIDE.md`