// 健康饮食推荐系统 - 推荐结果页面JavaScript

// 营养指标颜色配置
const NUTRIENT_COLORS = {
    'calories': '#4CAF50',
    'protein': '#2196F3',
    'fat': '#FF9800',
    'carbs': '#9C27B0',
    'fiber': '#00BCD4',
    'sodium': '#E91E63'
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function () {
    loadRecommendationData();
});

// 从本地存储加载推荐数据
function loadRecommendationData() {
    const recommendationData = JSON.parse(localStorage.getItem('recommendationData'));

    if (!recommendationData) {
        showNoDataError();
        return;
    }

    // 隐藏加载动画
    document.getElementById('loading').style.display = 'none';

    // 更新用户信息
    document.getElementById('disease-name').textContent = recommendationData.diseaseInfo.diseaseName;
    document.getElementById('severity-level').textContent = recommendationData.diseaseInfo.severity;
    document.getElementById('generation-time').textContent = new Date().toLocaleString();

    // 渲染推荐菜品
    renderRecommendedDishes(recommendationData.recommendedDishes);

    // 渲染需要特别注意的菜品
    renderSpecialAttentionDishes(recommendationData.specialAttentionDishes);

    // 渲染优化套餐
    renderMealPlan(recommendationData.optimizedMealPlan);

    // 更新营养分析 - 使用后端计算的达标率
    updateNutritionAnalysis(
        recommendationData.nutritionAnalysis,
        recommendationData.nutritionTargets,
        recommendationData.nutritionRates
    );

    // 显示所有部分
    showAllSections();
}

// 显示无数据错误
function showNoDataError() {
    document.getElementById('loading').innerHTML = `
        <div class="empty-state">
            <i>❌</i>
            <h3>未找到推荐数据</h3>
            <p>请返回首页重新填写信息生成推荐</p>
            <button class="btn btn-primary" onclick="window.location.href='/'">返回首页</button>
        </div>
    `;
}

// 渲染推荐菜品
function renderRecommendedDishes(dishes) {
    const container = document.getElementById('recommended-dishes');

    if (!dishes || dishes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i>🍽️</i>
                <h3>暂无推荐菜品</h3>
                <p>请尝试调整您的偏好设置</p>
            </div>
        `;
        return;
    }

    container.innerHTML = dishes.map(dish => `
        <div class="dish-card">
            <div class="dish-header">
                <div class="dish-name">${dish.name}</div>
                <div class="dish-score">${dish.score.toFixed(1)}</div>
            </div>
            <div class="dish-body">
                <div class="ingredients">食材: ${dish.ingredients.join(', ')}</div>
                ${dish.isLiked ? '<span class="dish-tag">❤ 您喜欢的</span>' : ''}
                <span class="dish-tag">推荐指数: ${dish.score.toFixed(1)}/4.0</span>
            </div>
        </div>
    `).join('');
}

// 渲染需要特别注意的菜品
function renderSpecialAttentionDishes(dishes) {
    const container = document.getElementById('special-attention-dishes');

    if (!dishes || dishes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i>✅</i>
                <h3>无需特别注意的菜品</h3>
                <p>您的饮食偏好与健康状况较为匹配</p>
            </div>
        `;
        return;
    }

    container.innerHTML = dishes.map(dish => `
        <div class="dish-card special-attention">
            <div class="dish-header">
                <div class="dish-name">${dish.name}</div>
                <div class="dish-score">${dish.score.toFixed(1)}</div>
            </div>
            <div class="dish-body">
                <div class="ingredients">食材: ${dish.ingredients.join(', ')}</div>
                ${dish.isLiked ? '<span class="dish-tag">❤ 您喜欢的</span>' : ''}
                <span class="dish-tag" style="background:#FFE0B2;color:#E65100;">需特别注意</span>
            </div>
        </div>
    `).join('');
}

// 渲染优化套餐
function renderMealPlan(mealPlan) {
    const container = document.getElementById('meal-dishes');
    const scoreElement = document.getElementById('meal-score');

    if (!mealPlan || !mealPlan.dishes || mealPlan.dishes.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>暂无套餐推荐数据</p></div>';
        scoreElement.textContent = '0.00';
        return;
    }

    scoreElement.textContent = mealPlan.totalScore.toFixed(2);

    container.innerHTML = mealPlan.dishes.map(dish => `
        <div class="meal-dish">
            <div>
                <strong>${dish.name}</strong>
                ${dish.isLiked ? '<span style="color:#E91E63; margin-left:8px;">❤</span>' : ''}
            </div>
            <div>${dish.amount.toFixed(1)} 份</div>
        </div>
    `).join('');
}

// 更新营养分析
function updateNutritionAnalysis(nutrition, targets, nutritionRates) {
    if (!nutrition) {
        console.log('没有营养数据');
        return;
    }

    console.log('更新营养分析数据:', nutrition);
    console.log('营养目标数据:', targets);
    console.log('营养达标率数据:', nutritionRates);

    // 初始化营养卡片
    initializeNutrientCards();

    // 使用后端计算的达标率数据
    if (nutritionRates && nutritionRates.length > 0) {
        nutritionRates.forEach(rate => {
            const [name, target, actual, percentage] = rate;
            const nutrientId = mapNutritionNameToId(name);

            if (nutrientId) {
                updateNutrientDisplay(nutrientId, actual, target, percentage);
                setTimeout(() => animateNutrientProgress(nutrientId), 300);
            }
        });
    }

    // 初始化六边形数据图
    initHexagonChartFromRates(nutritionRates || []);
}

// 映射营养名称到ID
function mapNutritionNameToId(name) {
    const mapping = {
        '热量': 'calories',
        '蛋白质': 'protein',
        '脂肪': 'fat',
        '碳水化合物': 'carbs',
        '纤维素': 'fiber',
        '钠': 'sodium'
    };
    return mapping[name];
}

// 初始化营养卡片
function initializeNutrientCards() {
    Object.keys(NUTRIENT_COLORS).forEach(nutrientId => {
        const progressElement = document.getElementById(`${nutrientId}-progress`);
        if (progressElement) {
            progressElement.style.setProperty('--nutrient-color', NUTRIENT_COLORS[nutrientId]);
        }
    });

    document.querySelectorAll('.nutrient-progress-card').forEach(card => {
        card.addEventListener('mouseenter', () => {
            const nutrientId = card.id.replace('-card', '');
            animateNutrientProgress(nutrientId);
        });
    });
}

// 更新营养指标显示
function updateNutrientDisplay(nutrientId, currentValue, goalValue, percentage) {
    const elements = {
        display: document.getElementById(`${nutrientId}-display`),
        goal: document.getElementById(`${nutrientId}-goal`),
        percentage: document.getElementById(`${nutrientId}-percentage`),
        status: document.getElementById(`${nutrientId}-status`)
    };

    if (elements.display) elements.display.textContent = currentValue.toFixed(nutrientId === 'calories' ? 0 : 1);
    if (elements.goal) elements.goal.textContent = goalValue.toFixed(0);
    if (elements.percentage) elements.percentage.textContent = percentage.toFixed(1) + '%';

    if (elements.status) {
        let statusText = `已完成 ${percentage.toFixed(1)}%`;
        let bgColor = '#f5f5f5';
        let textColor = '#666';

        if (percentage >= 100) {
            statusText = '恭喜！目标已完成！';
            bgColor = '#e8f5e9';
            textColor = '#2e7d32';
        } else if (percentage >= 80) {
            statusText = `已完成 ${percentage.toFixed(1)}%，接近目标！`;
            bgColor = '#fff3e0';
            textColor = '#ef6c00';
        } else if (percentage >= 50) {
            statusText = `已完成 ${percentage.toFixed(1)}%，继续努力！`;
            bgColor = '#e3f2fd';
            textColor = '#1565c0';
        }

        elements.status.textContent = statusText;
        elements.status.style.backgroundColor = bgColor;
        elements.status.style.color = textColor;
    }
}

// 动画效果
function animateNutrientProgress(nutrientId) {
    const progressFill = document.getElementById(`${nutrientId}-progress`);
    if (!progressFill) return;

    progressFill.style.setProperty('--progress', '0%');

    requestAnimationFrame(() => {
        const displayElement = document.getElementById(`${nutrientId}-display`);
        const goalElement = document.getElementById(`${nutrientId}-goal`);

        if (displayElement && goalElement) {
            const currentValue = parseFloat(displayElement.textContent) || 0;
            const goalValue = parseFloat(goalElement.textContent) || 1;
            let targetProgress = (currentValue / goalValue) * 100;
            targetProgress = Math.min(targetProgress, 100);

            progressFill.style.setProperty('--progress', `${targetProgress}%`);
        }
    });
}

// 六边形数据图
function initHexagonChartFromRates(nutritionRates) {
    if (!nutritionRates || nutritionRates.length === 0) return;

    const nutritionData = {};
    nutritionRates.forEach(rate => {
        const [name, target, actual, percentage] = rate;
        const key = mapNutritionNameToId(name);
        if (key) {
            nutritionData[key] = percentage;
        }
    });

    // 更新图例数值
    const legendIds = ['calories', 'protein', 'fat', 'carbs', 'fiber', 'sodium'];
    legendIds.forEach(id => {
        const legendElement = document.getElementById(`legend-${id}`);
        if (legendElement) {
            legendElement.textContent = (nutritionData[id] || 0).toFixed(1) + '%';
        }
    });

    drawHexagonChart(nutritionData);
}

// 绘制六边形数据图（保持原有实现）
function drawHexagonChart(data) {
    // ... 保持原有的六边形图表绘制代码 ...
}

// 显示所有内容部分
function showAllSections() {
    ['recommended-section', 'special-attention-section', 'meal-plan-section', 'nutrition-section'].forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'block';
    });
}

// 重新生成推荐
function regenerateRecommendation() {
    localStorage.removeItem('recommendationData');
    window.location.href = '/';
}

// 打印功能优化
window.onbeforeprint = function () {
    document.body.classList.add('printing');
};

window.onafterprint = function () {
    document.body.classList.remove('printing');
};