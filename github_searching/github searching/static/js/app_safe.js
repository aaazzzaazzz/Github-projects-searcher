// GitHub项目智能搜索引擎 - 前端JavaScript代码（安全版本）

// 全局变量
let currentPage = 1;
let currentQuery = '';
let currentSortBy = 'relevance';
let currentFilters = {};

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    loadPopularProjects();
});

// 初始化事件监听器
function initializeEventListeners() {
    // 搜索表单提交
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearch);
    }
    
    // 高级搜索切换 - 检查元素是否存在
    const toggleAdvancedElement = document.getElementById('toggleAdvanced');
    if (toggleAdvancedElement) {
        toggleAdvancedElement.addEventListener('click', toggleAdvancedSearch);
    }
    
    // 搜索建议点击
    const suggestionLinks = document.querySelectorAll('.suggestion-link');
    suggestionLinks.forEach(link => {
        if (link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const query = this.getAttribute('data-query');
                const searchQuery = document.getElementById('searchQuery');
                if (searchQuery) {
                    searchQuery.value = query;
                    handleSearch(e);
                }
            });
        }
    });
    
    // 高级搜索选项变化 - 检查元素是否存在
    ['sortBy', 'language', 'activityLevel', 'contributorType'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', handleFilterChange);
        }
    });
}

// 处理搜索
async function handleSearch(e) {
    e.preventDefault();
    
    const searchQuery = document.getElementById('searchQuery');
    if (!searchQuery) {
        showError('搜索框未找到');
        return;
    }
    
    const query = searchQuery.value.trim();
    if (!query) {
        showError('请输入搜索关键词');
        return;
    }
    
    currentQuery = query;
    currentPage = 1;
    
    showLoading(true);
    
    try {
        const results = await searchProjects(query, currentPage, currentSortBy, currentFilters);
        displaySearchResults(results, query);
        
        // 显示AI搜索解释
        if (results.explanation) {
            displayAIExplanation(results.explanation);
        }
        
        // 显示搜索参数
        if (results.search_params) {
            displaySearchParams(results.search_params);
        }
        
    } catch (error) {
        console.error('搜索错误:', error);
        showError('搜索失败，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 搜索项目
async function searchProjects(query, page = 1, sortBy = 'relevance', filters = {}) {
    const params = new URLSearchParams({
        q: query,
        page: page.toString(),
        page_size: '20',
        sort_by: sortBy
    });
    
    // 添加过滤参数
    Object.entries(filters).forEach(([key, value]) => {
        if (value) {
            params.append(key, value);
        }
    });
    
    const response = await fetch(`/api/search?${params}`);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// 显示搜索结果
function displaySearchResults(data, query) {
    const resultsSection = document.getElementById('searchResults');
    const resultsList = document.getElementById('resultsList');
    const resultCount = document.getElementById('resultCount');
    
    if (!data.success || !data.results || !data.results.results) {
        showError('搜索结果格式错误');
        return;
    }
    
    const projects = data.results.results;
    const totalCount = data.results.total_count || 0;
    
    // 显示结果数量
    if (resultCount) {
        resultCount.textContent = `找到 ${totalCount} 个项目`;
    }
    
    // 生成项目列表HTML
    if (resultsList) {
        resultsList.innerHTML = projects.map(project => createProjectCard(project)).join('');
    }
    
    // 显示分页
    if (totalCount > 20) {
        displayPagination(data.results.total_pages, currentPage);
    }
    
    // 显示搜索结果区域
    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
}

// 创建项目卡片HTML
function createProjectCard(project) {
    // 使用正确的字段名，处理null值
    const projectName = project.project_name || project.name || '未知项目';
    const description = project.description !== null ? project.description : '暂无描述';
    const language = project.language !== null ? project.language : '未知';
    const stars = project.stars || 0;
    const forks = project.forks || 0;
    const updatedAt = project.updated_at || project.last_pushed || '未知';
    let projectKey = project.project_key || project.key || '';
    const activityScore = project.activity_score || 0;
    
    console.log('创建项目卡片 - 原始数据:', {
        name: projectName,
        project_key: project.project_key,
        key: project.key,
        description: description,
        language: language,
        stars: stars,
        forks: forks,
        activityScore: activityScore
    });
    
    // 确保projectKey不为空
    if (!projectKey) {
        console.warn('项目key为空，使用项目名称作为备选:', projectName);
        // 如果project_key为空，尝试使用其他字段
        projectKey = projectName || 'unknown';
    }
    
    console.log('创建项目卡片 - 最终使用的projectKey:', projectKey);
    
    // 转义projectKey以防止HTML注入 - 修复版本
    const escapedProjectKey = String(projectKey)
        .replace(/'/g, "\\'")
        .replace(/"/g, '\\"');
    
    return `
        <div class="card mb-3 project-card" onclick="showProjectDetails('${escapedProjectKey}')">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-8">
                        <h5 class="card-title">
                            <i class="fab fa-github me-2"></i>
                            ${projectName}
                            <!-- 移除活跃度徽章 -->
                        </h5>
                        <p class="card-text text-muted">${description}</p>
                        <div class="project-meta">
                            <span class="badge bg-secondary me-2">${language}</span>
                            <span class="text-muted me-3">
                                <i class="fas fa-star"></i> ${formatNumber(stars)}
                            </span>
                            <span class="text-muted me-3">
                                <i class="fas fa-code-branch"></i> ${formatNumber(forks)}
                            </span>
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="activity-score">
                            <small class="text-muted">活跃度评分</small>
                            <div class="score-value">${activityScore.toFixed(1)}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// 显示项目详情
async function showProjectDetails(projectKey) {
    console.log('显示项目详情，传入的projectKey:', projectKey);
    console.log('projectKey类型:', typeof projectKey);
    console.log('projectKey值:', projectKey);
    
    // 检查projectKey是否有效
    if (!projectKey || projectKey === 'undefined' || projectKey === 'null' || projectKey === 'unknown') {
        console.error('无效的项目key:', projectKey);
        showError('无效的项目标识符');
        return;
    }
    
    showLoading(true);
    
    try {
        const url = `/api/projects/${encodeURIComponent(projectKey)}`;
        console.log('请求项目详情URL:', url);
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (!data.success) {
            throw new Error(data.error || '获取项目详情失败');
        }
        
        displayProjectDetails(data);
        
        // 显示模态框
        const modal = new bootstrap.Modal(document.getElementById('projectModal'));
        if (modal) {
            modal.show();
        }
        
    } catch (error) {
        console.error('获取项目详情错误:', error);
        showError('获取项目详情失败，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 显示项目详情内容
function displayProjectDetails(data) {
    const detailsContainer = document.getElementById('projectDetails');
    const project = data.project_details.project;
    const summary = data.summary;
    const relatedProjects = data.related_projects;
    
    // 修正数据提取路径 - 从project_details中获取数据
    const topContributors = data.project_details.top_contributors || [];
    const activityStats = data.project_details.activity_stats || {};
    const contributorStats = data.project_details.contributor_stats || {};
    const contributorMetrics = data.project_details.contributor_metrics || {};
    const issueMetrics = data.project_details.issue_metrics || {};
    
    console.log('=== 调试信息 ===');
    console.log('完整API响应数据:', data);
    console.log('project_details:', data.project_details);
    console.log('项目详情数据:', project);
    console.log('顶级贡献者数据:', topContributors);
    console.log('活动统计数据:', activityStats);
    console.log('贡献者统计数据:', contributorStats);
    console.log('贡献者指标数据:', contributorMetrics);
    console.log('contributorMetrics.new_contributors_latest:', contributorMetrics.new_contributors_latest);
    console.log('contributorMetrics.new_contributors_average:', contributorMetrics.new_contributors_average);
    console.log('contributorMetrics.inactive_contributors_latest:', contributorMetrics.inactive_contributors_latest);
    console.log('contributorMetrics.inactive_contributors_average:', contributorMetrics.inactive_contributors_average);
    console.log('Issue指标数据:', issueMetrics);
    
    // 确保数据存在
    if (!project) {
        if (detailsContainer) {
            detailsContainer.innerHTML = '<div class="alert alert-danger">项目数据不存在</div>';
        }
        return;
    }
    
    // 解析JSON字段
    let attentionData = null;
    let metricsData = null;
    
    try {
        console.log('尝试解析attention数据:', project.attention);
        if (project.attention) {
            if (typeof project.attention === 'string') {
                // 修复包含NaN值的JSON字符串 - 更全面的替换
                let jsonString = project.attention
                    .replace(/:NaN/g, ':null')
                    .replace(/:\s*NaN/g, ':null')
                    .replace(/,NaN/g, ',null')
                    .replace(/,\s*NaN/g, ',null')
                    .replace(/\bNaN\b/g, 'null');
                console.log('修复后的attention JSON字符串:', jsonString);
                attentionData = JSON.parse(jsonString);
                console.log('attention数据解析成功:', attentionData);
            } else {
                attentionData = project.attention;
                console.log('attention数据已经是对象:', attentionData);
            }
        }
    } catch (e) {
        console.error('解析attention数据失败:', e);
        console.error('原始attention数据:', project.attention);
        // 如果解析失败，设置为null
        attentionData = null;
    }
    
    try {
        console.log('尝试解析metrics_data数据:', project.metrics_data);
        if (project.metrics_data) {
            if (typeof project.metrics_data === 'string') {
                // 修复包含NaN值的JSON字符串 - 更全面的替换
                let jsonString = project.metrics_data
                    .replace(/:NaN/g, ':null')
                    .replace(/:\s*NaN/g, ':null')
                    .replace(/,NaN/g, ',null')
                    .replace(/,\s*NaN/g, ',null')
                    .replace(/\bNaN\b/g, 'null');
                console.log('修复后的metrics_data JSON字符串:', jsonString);
                metricsData = JSON.parse(jsonString);
                console.log('metrics_data数据解析成功:', metricsData);
            } else {
                metricsData = project.metrics_data;
                console.log('metrics_data数据已经是对象:', metricsData);
            }
        }
    } catch (e) {
        console.error('解析metrics_data数据失败:', e);
        console.error('原始metrics_data数据:', project.metrics_data);
        // 如果解析失败，设置为null
        metricsData = null;
    }
    
    console.log('解析后的attention数据:', attentionData);
    console.log('解析后的metrics_data数据:', metricsData);
    
    // 生成项目详情HTML
    const detailsHTML = `
        <div class="project-details">
            <!-- 基本信息 -->
            <div class="row mb-4">
                <div class="col-md-8">
                    <h3>
                        <i class="fab fa-github me-2"></i>
                        ${project.project_name || project.name || '未知项目'}
                    </h3>
                    <p class="text-muted">${project.description !== null ? project.description : '暂无描述'}</p>
                    <div class="project-meta mb-3">
                        <span class="badge bg-primary me-2">${project.language !== null ? project.language : '未知'}</span>
                        <span class="text-muted me-3">
                            <i class="fas fa-star"></i> ${formatNumber(project.stars || 0)}
                        </span>
                        <span class="text-muted me-3">
                            <i class="fas fa-code-branch"></i> ${formatNumber(project.forks || 0)}
                        </span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-body text-center">
                            <h6>活跃度评分</h6>
                            <div class="score-display">
                                <span class="score-value">${(project.activity_score || data.project_details.project.activity_score || 0).toFixed(1)}</span>
                                <div class="activity-level">${getActivityLevel(project.activity_score)}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 项目指标 -->
            <div class="row">
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-chart-line me-2"></i>项目健康度指标</h6>
                        </div>
                        <div class="card-body">
                            ${formatHealthMetrics(metricsData)}
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-eye me-2"></i>关注度指标</h6>
                        </div>
                        <div class="card-body">
                            ${formatAttentionMetrics(attentionData)}
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-bug me-2"></i>Issue指标</h6>
                        </div>
                        <div class="card-body">
                            ${formatIssueMetrics(issueMetrics)}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 贡献者统计 -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-users me-2"></i>贡献者指标（来自metrics_data）</h6>
                        </div>
                        <div class="card-body">
                            <div class="metrics-grid">
                                <div class="metric-item text-center">
                                    <div class="metric-value">${contributorMetrics.new_contributors_latest || 0}</div>
                                    <div class="metric-label">新增贡献者（最新）</div>
                                    <div class="metric-desc">当前周期新增贡献者数量</div>
                                </div>
                                <div class="metric-item text-center">
                                    <div class="metric-value">${contributorMetrics.new_contributors_average || 0}</div>
                                    <div class="metric-label">新增贡献者（平均）</div>
                                    <div class="metric-desc">历史平均新增贡献者数量</div>
                                </div>
                                <div class="metric-item text-center">
                                    <div class="metric-value">${contributorMetrics.inactive_contributors_latest || 0}</div>
                                    <div class="metric-label">非活跃贡献者（最新）</div>
                                    <div class="metric-desc">当前周期非活跃贡献者数量</div>
                                </div>
                                <div class="metric-item text-center">
                                    <div class="metric-value">${contributorMetrics.inactive_contributors_average || 0}</div>
                                    <div class="metric-label">非活跃贡献者（平均）</div>
                                    <div class="metric-desc">历史平均非活跃贡献者数量</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- AI分析 -->
            ${summary ? `
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-robot me-2"></i>AI项目分析</h6>
                        </div>
                        <div class="card-body">
                            <p>${summary}</p>
                        </div>
                    </div>
                </div>
            </div>
            ` : ''}
            
            <!-- 相关项目 -->
            ${relatedProjects && relatedProjects.length > 0 ? `
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h6><i class="fas fa-link me-2"></i>相关项目推荐</h6>
                        </div>
                        <div class="card-body">
                            ${relatedProjects.map(p => {
                                // 处理字符串类型的项目数据
                                const projectKey = typeof p === 'string' ? p : (p.project_key || p.key);
                                const projectName = typeof p === 'string' ? p : (p.project_name || p.name);
                                const description = typeof p === 'string' ? '暂无描述' : (p.description || '暂无描述');
                                
                                return `
                                <div class="related-project mb-2">
                                    <a href="#" onclick="showProjectDetails('${projectKey}'); return false;">
                                        ${projectName}
                                    </a>
                                </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                </div>
            </div>
            ` : ''}
        </div>
    `;
    
    if (detailsContainer) {
        detailsContainer.innerHTML = detailsHTML;
    }
}

// 格式化健康度指标
function formatHealthMetrics(metricsData) {
    console.log('formatHealthMetrics被调用，参数:', metricsData);
    
    if (!metricsData) {
        console.log('metricsData为空，返回警告信息');
        return '<div class="alert alert-warning">健康度指标数据不可用</div>';
    }
    
    try {
        console.log('格式化健康度指标，原始数据:', metricsData);
        console.log('metricsData类型:', typeof metricsData);
        console.log('是否为数组:', Array.isArray(metricsData));
        
        // 确保metricsData是对象
        if (typeof metricsData !== 'object' || Array.isArray(metricsData)) {
            console.warn('健康度指标数据格式不正确，不是对象:', typeof metricsData);
            return '<div class="alert alert-warning">健康度指标数据格式不正确</div>';
        }
        
        let html = '<div class="metrics-grid">';
        let hasValidMetrics = false;
        
        // 首先检查Project_Health_Metrics
        if (metricsData.Project_Health_Metrics) {
            console.log('找到Project_Health_Metrics:', metricsData.Project_Health_Metrics);
            const healthMetrics = metricsData.Project_Health_Metrics;
            
            // Bus Factor
            if (healthMetrics.bus_factor_Latest !== undefined && healthMetrics.bus_factor_Latest !== null) {
                const busFactor = parseFloat(healthMetrics.bus_factor_Latest);
                if (!isNaN(busFactor)) {
                    hasValidMetrics = true;
                    html += `
                        <div class="metric-item">
                            <div class="metric-label">Bus Factor</div>
                            <div class="metric-value">${busFactor.toFixed(2)}</div>
                            <div class="metric-desc">项目依赖关键开发者数量</div>
                        </div>
                    `;
                    console.log('添加Bus Factor指标:', busFactor);
                }
            }
            
            // OpenRank
            if (healthMetrics.openrank_Latest !== undefined && healthMetrics.openrank_Latest !== null) {
                const openRank = parseFloat(healthMetrics.openrank_Latest);
                if (!isNaN(openRank)) {
                    hasValidMetrics = true;
                    html += `
                        <div class="metric-item">
                            <div class="metric-label">OpenRank</div>
                            <div class="metric-value">${openRank.toFixed(2)}</div>
                            <div class="metric-desc">项目开放排名分数</div>
                        </div>
                    `;
                    console.log('添加OpenRank指标:', openRank);
                }
            }
            
            // Technical Fork
            if (healthMetrics.technical_fork_Latest !== undefined && healthMetrics.technical_fork_Latest !== null) {
                const technicalFork = parseFloat(healthMetrics.technical_fork_Latest);
                if (!isNaN(technicalFork)) {
                    hasValidMetrics = true;
                    html += `
                        <div class="metric-item">
                            <div class="metric-label">Technical Fork</div>
                            <div class="metric-value">${technicalFork.toFixed(2)}</div>
                            <div class="metric-desc">技术分叉活跃度</div>
                        </div>
                    `;
                    console.log('添加Technical Fork指标:', technicalFork);
                }
            }
        } else {
            console.log('未找到Project_Health_Metrics，检查顶级字段');
            // 如果没有Project_Health_Metrics，尝试直接检查顶级字段
            // Bus Factor
            if (metricsData.bus_factor_Latest !== undefined && metricsData.bus_factor_Latest !== null) {
                const busFactor = parseFloat(metricsData.bus_factor_Latest);
                if (!isNaN(busFactor)) {
                    hasValidMetrics = true;
                    html += `
                        <div class="metric-item">
                            <div class="metric-label">Bus Factor</div>
                            <div class="metric-value">${busFactor.toFixed(2)}</div>
                            <div class="metric-desc">项目依赖关键开发者数量</div>
                        </div>
                    `;
                    console.log('添加顶级Bus Factor指标:', busFactor);
                }
            }
            
            // OpenRank
            if (metricsData.openrank_Latest !== undefined && metricsData.openrank_Latest !== null) {
                const openRank = parseFloat(metricsData.openrank_Latest);
                if (!isNaN(openRank)) {
                    hasValidMetrics = true;
                    html += `
                        <div class="metric-item">
                            <div class="metric-label">OpenRank</div>
                            <div class="metric-value">${openRank.toFixed(2)}</div>
                            <div class="metric-desc">项目开放排名分数</div>
                        </div>
                    `;
                    console.log('添加顶级OpenRank指标:', openRank);
                }
            }
            
            // Technical Fork
            if (metricsData.technical_fork_Latest !== undefined && metricsData.technical_fork_Latest !== null) {
                const technicalFork = parseFloat(metricsData.technical_fork_Latest);
                if (!isNaN(technicalFork)) {
                    hasValidMetrics = true;
                    html += `
                        <div class="metric-item">
                            <div class="metric-label">Technical Fork</div>
                            <div class="metric-value">${technicalFork.toFixed(2)}</div>
                            <div class="metric-desc">技术分叉活跃度</div>
                        </div>
                    `;
                    console.log('添加顶级Technical Fork指标:', technicalFork);
                }
            }
        }
        
        // 如果没有任何有效指标
        if (!hasValidMetrics) {
            html += '<div class="alert alert-info">暂无健康度指标数据</div>';
            console.log('没有找到有效的健康度指标');
        }
        
        html += '</div>';
        console.log('生成的健康度指标HTML:', html);
        return html;
        
    } catch (error) {
        console.error('格式化健康度指标时出错:', error);
        return `<div class="alert alert-danger">健康度指标解析失败: ${error.message}</div>`;
    }
}

// 格式化关注度指标
function formatAttentionMetrics(attentionData) {
    if (!attentionData) {
        return '<div class="alert alert-warning">关注度指标数据不可用</div>';
    }
    
    try {
        console.log('格式化关注度指标，原始数据:', attentionData);
        
        // 确保attentionData是对象
        if (typeof attentionData !== 'object' || Array.isArray(attentionData)) {
            console.warn('关注度指标数据格式不正确，不是对象:', typeof attentionData);
            return '<div class="alert alert-warning">关注度指标数据格式不正确</div>';
        }
        
        let html = '<div class="metrics-grid">';
        
        // 检查各种可能的关注度指标字段
        const attentionFields = [
            { key: 'attention_Latest', label: '关注度', desc: '项目整体关注度分数' },
            { key: 'attention', label: '关注度', desc: '项目整体关注度分数' },
            { key: 'attention_score', label: '关注度评分', desc: '项目关注度评分' },
            { key: 'community_attention', label: '社区关注度', desc: '社区对项目的关注度' },
            { key: 'developer_attention', label: '开发者关注度', desc: '开发者对项目的关注度' },
            { key: 'user_attention', label: '用户关注度', desc: '用户对项目的关注度' }
        ];
        
        let hasValidMetrics = false;
        
        attentionFields.forEach(field => {
            if (attentionData[field.key] !== undefined && attentionData[field.key] !== null) {
                const value = parseFloat(attentionData[field.key]);
                if (!isNaN(value)) {
                    hasValidMetrics = true;
                    html += `
                        <div class="metric-item">
                            <div class="metric-label">${field.label}</div>
                            <div class="metric-value">${value.toFixed(2)}</div>
                            <div class="metric-desc">${field.desc}</div>
                        </div>
                    `;
                }
            }
        });
        
        // 如果没有找到任何指标，尝试显示所有可用的字段
        if (!hasValidMetrics && typeof attentionData === 'object') {
            html += '<div class="alert alert-info">可用字段: ' + Object.keys(attentionData).join(', ') + '</div>';
        }
        
        // 如果没有任何有效指标
        if (!hasValidMetrics) {
            html += '<div class="alert alert-info">暂无关注度指标数据</div>';
        }
        
        html += '</div>';
        console.log('生成的关注度指标HTML:', html);
        return html;
        
    } catch (error) {
        console.error('格式化关注度指标时出错:', error);
        return `<div class="alert alert-danger">关注度指标解析失败: ${error.message}</div>`;
    }
}

// 格式化Issue指标数据
function formatIssueMetrics(data) {
    if (!data) {
        return '<div class="alert alert-info">暂无Issue指标数据</div>';
    }

    let html = '<div class="metrics-grid">';

    // Issues新建
    html += `
        <div class="metric-item">
            <div class="metric-label">Issues新建 (最新)</div>
            <div class="metric-value">${formatNumber(data.issues_new_latest)}</div>
            <div class="metric-desc">历史平均: ${formatNumber(data.issues_new_average)}</div>
        </div>
    `;

    // Issues关闭
    html += `
        <div class="metric-item">
            <div class="metric-label">Issues关闭 (最新)</div>
            <div class="metric-value">${formatNumber(data.issues_closed_latest)}</div>
            <div class="metric-desc">历史平均: ${formatNumber(data.issues_closed_average)}</div>
        </div>
    `;

    // Issue评论
    html += `
        <div class="metric-item">
            <div class="metric-label">Issue评论 (最新)</div>
            <div class="metric-value">${formatNumber(data.issue_comments_latest)}</div>
            <div class="metric-desc">历史平均: ${formatNumber(data.issue_comments_average)}</div>
        </div>
    `;

    // Issues和Change Request活跃
    html += `
        <div class="metric-item">
            <div class="metric-label">Issues和Change Request活跃 (最新)</div>
            <div class="metric-value">${formatNumber(data.issues_and_change_request_active_latest)}</div>
            <div class="metric-desc">历史平均: ${formatNumber(data.issues_and_change_request_active_average)}</div>
        </div>
    `;

    html += '</div>';
    return html;
}

// 获取活跃度级别 - 与后端动态阈值保持一致
function getActivityLevel(score) {
    // 这里使用与后端相同的逻辑，但需要动态获取阈值
    // 由于前端无法直接获取动态阈值，使用合理的固定阈值
    if (score >= 1000) return '高活跃度';      // 约30%的项目
    if (score >= 300) return '中等活跃度';       // 约40%的项目
    return '低活跃度';                    // 约30%的项目
}


// 格式化数字
function formatNumber(num) {
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '未知';
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('zh-CN');
    } catch (error) {
        return dateString;
    }
}

// 显示AI搜索解释
function displayAIExplanation(explanation) {
    const explanationDiv = document.getElementById('aiExplanation');
    const explanationText = document.getElementById('explanationText');
    
    if (explanationDiv && explanationText) {
        explanationText.textContent = explanation;
        explanationDiv.style.display = 'block';
    }
}

// 显示搜索参数
function displaySearchParams(params) {
    const paramsDiv = document.getElementById('searchParams');
    const paramsDisplay = document.getElementById('paramsDisplay');
    
    if (paramsDiv && paramsDisplay) {
        let paramsHTML = '';
        
        if (params.keywords && params.keywords.length > 0) {
            paramsHTML += `<div><strong>关键词:</strong> ${params.keywords.join(', ')}</div>`;
        }
        
        if (params.languages && params.languages.length > 0) {
            paramsHTML += `<div><strong>编程语言:</strong> ${params.languages.join(', ')}</div>`;
        }
        
        if (params.activity_level) {
            paramsHTML += `<div><strong>活跃度:</strong> ${params.activity_level}</div>`;
        }
        
        if (params.contributor_type && params.contributor_type !== 'all') {
            paramsHTML += `<div><strong>贡献者类型:</strong> ${params.contributor_type}</div>`;
        }
        
        if (paramsHTML) {
            paramsDisplay.innerHTML = paramsHTML;
            paramsDiv.style.display = 'block';
        }
    }
}

// 显示分页
function displayPagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;
    
    const paginationList = pagination.querySelector('ul');
    if (!paginationList) return;
    
    let paginationHTML = '';
    
    // 上一页
    if (currentPage > 1) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${currentPage - 1}); return false;">
                    上一页
                </a>
            </li>
        `;
    }
    
    // 页码
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        paginationHTML += `
            <li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="changePage(${i}); return false;">
                    ${i}
                </a>
            </li>
        `;
    }
    
    // 下一页
    if (currentPage < totalPages) {
        paginationHTML += `
            <li class="page-item">
                <a class="page-link" href="#" onclick="changePage(${currentPage + 1}); return false;">
                    下一页
                </a>
            </li>
        `;
    }
    
    paginationList.innerHTML = paginationHTML;
    pagination.style.display = 'block';
}

// 切换页面
async function changePage(page) {
    currentPage = page;
    
    showLoading(true);
    
    try {
        const results = await searchProjects(currentQuery, currentPage, currentSortBy, currentFilters);
        displaySearchResults(results, currentQuery);
        
        // 滚动到搜索结果顶部
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            searchResults.scrollIntoView({ behavior: 'smooth' });
        }
        
    } catch (error) {
        console.error('切换页面错误:', error);
        showError('切换页面失败，请稍后重试');
    } finally {
        showLoading(false);
    }
}

// 切换高级搜索
function toggleAdvancedSearch() {
    const advancedSearch = document.getElementById('advancedSearch');
    if (advancedSearch) {
        advancedSearch.style.display = advancedSearch.style.display === 'none' ? 'block' : 'none';
    }
}

// 处理过滤器变化
function handleFilterChange() {
    const sortByElement = document.getElementById('sortBy');
    const languageElement = document.getElementById('language');
    const activityLevelElement = document.getElementById('activityLevel');
    const contributorTypeElement = document.getElementById('contributorType');
    
    currentFilters = {
        language: languageElement ? languageElement.value : '',
        activityLevel: activityLevelElement ? activityLevelElement.value : '',
        contributorType: contributorTypeElement ? contributorTypeElement.value : ''
    };
    
    if (sortByElement) {
        currentSortBy = sortByElement.value;
    }
    
    // 如果有当前查询，重新搜索
    if (currentQuery) {
        currentPage = 1;
        handleSearch(new Event('submit'));
    }
}

// 显示加载状态
function showLoading(show) {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.style.display = show ? 'flex' : 'none';
    }
}

// 显示错误信息
function showError(message) {
    // 创建错误提示
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    errorDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 400px;';
    errorDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(errorDiv);
    
    // 3秒后自动移除
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 3000);
}

// 关闭模态框
function closeModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('projectModal'));
    if (modal) {
        modal.hide();
    }
}

// 加载热门项目
async function loadPopularProjects() {
    try {
        const response = await fetch('/api/projects?page=1&page_size=6&sort_by=stars');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.success && data.results && data.results.results) {
            // 可以在这里显示一些热门项目
            console.log('加载了', data.results.results.length, '个热门项目');
        }
    } catch (error) {
        console.error('加载热门项目失败:', error);
    }
}