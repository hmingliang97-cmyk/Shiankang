// 健康饮食推荐系统 - 问卷页面JavaScript

// 菜品数据
const DISHES = [
    { id: 1, name: "红烧肉", description: "猪肉（五花）" },
    { id: 2, name: "番茄炒蛋", description: "西红柿，鸡蛋" },
    { id: 3, name: "蒜蓉上海青", description: "上海青" },
    { id: 4, name: "酸辣土豆丝", description: "土豆" },
    { id: 5, name: "鱼香肉丝", description: "猪肉（瘦），木耳，胡萝卜，莴笋" },
    { id: 6, name: "宫保鸡丁", description: "鸡肉（鸡胸），花生，干辣椒" },
    { id: 7, name: "麻婆豆腐", description: "豆腐（北豆腐），猪肉（瘦）" },
    { id: 8, name: "清蒸鲈鱼", description: "鲈鱼" },
    { id: 9, name: "地三鲜", description: "茄子，土豆，青椒" },
    { id: 10, name: "京酱肉丝", description: "猪肉（瘦），豆腐皮" },
    { id: 11, name: "葱油手撕鸡", description: "鸡肉（鸡腿）" },
    { id: 12, name: "糖醋里脊", description: "猪肉（瘦），鸡蛋" },
    { id: 13, name: "清炒虾仁", description: "虾（河虾），黄瓜，胡萝卜" },
    { id: 14, name: "蒜蓉西兰花", description: "西兰花" },
    { id: 15, name: "木须肉", description: "猪肉（瘦），鸡蛋，黄瓜，木耳" },
    { id: 16, name: "西红柿鸡蛋汤", description: "西红柿，鸡蛋" },
    { id: 17, name: "鲫鱼豆腐汤", description: "鲫鱼，豆腐（北豆腐）" },
    { id: 18, name: "冬瓜肉丸汤", description: "猪肉（瘦），冬瓜，鸡蛋" },
    { id: 19, name: "红烧茄子", description: "茄子，猪肉（瘦）" },
    { id: 20, name: "葱爆羊肉", description: "羊肉（瘦）" },
    { id: 21, name: "主食（米饭/面/面包）", description: "主食" }
];

// 全局状态
let selectedDishes = {
    liked: new Set(),
    disliked: new Set()
};

// 工具函数
function showLoading() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'block';
    }
    document.querySelectorAll('.btn').forEach(btn => {
        btn.disabled = true;
    });
}

function hideLoading() {
    const loadingElement = document.getElementById('loading');
    if (loadingElement) {
        loadingElement.style.display = 'none';
    }
    document.querySelectorAll('.btn').forEach(btn => {
        btn.disabled = false;
    });
}

function showError(message) {
    alert('错误: ' + message);
    console.error('错误信息:', message);
}

// 偏好管理
function togglePreference(id, type) {
    const dishId = parseInt(id);

    if (type === 'like') {
        selectedDishes.disliked.delete(dishId);
        selectedDishes.liked.add(dishId);
    } else {
        selectedDishes.liked.delete(dishId);
        selectedDishes.disliked.add(dishId);
    }

    updatePreferenceUI();
}

function removePreference(id) {
    const dishId = parseInt(id);
    selectedDishes.liked.delete(dishId);
    selectedDishes.disliked.delete(dishId);
    updatePreferenceUI();
}

function updatePreferenceUI() {
    // 更新按钮状态
    document.querySelectorAll('.preference-card').forEach(card => {
        const id = parseInt(card.dataset.id);
        const likeBtn = card.querySelector('.like-btn');
        const dislikeBtn = card.querySelector('.dislike-btn');

        likeBtn.classList.remove('selected');
        dislikeBtn.classList.remove('selected');

        if (selectedDishes.liked.has(id)) {
            likeBtn.classList.add('selected');
        } else if (selectedDishes.disliked.has(id)) {
            dislikeBtn.classList.add('selected');
        }
    });

    // 更新喜欢列表
    const likeList = document.getElementById('likeList');
    if (selectedDishes.liked.size === 0) {
        likeList.innerHTML = '<div class="empty-state">暂无喜欢的菜品</div>';
    } else {
        likeList.innerHTML = '';
        selectedDishes.liked.forEach(id => {
            const dish = DISHES.find(d => d.id === id);
            const prefItem = document.createElement('div');
            prefItem.className = 'preference-item';
            prefItem.innerHTML = `
                ${dish.name}
                <button class="remove-btn" data-id="${id}">×</button>
            `;
            prefItem.querySelector('.remove-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                removePreference(id);
            });
            likeList.appendChild(prefItem);
        });
    }

    // 更新不喜欢列表
    const dislikeList = document.getElementById('dislikeList');
    if (selectedDishes.disliked.size === 0) {
        dislikeList.innerHTML = '<div class="empty-state">暂无不喜欢菜品</div>';
    } else {
        dislikeList.innerHTML = '';
        selectedDishes.disliked.forEach(id => {
            const dish = DISHES.find(d => d.id === id);
            const prefItem = document.createElement('div');
            prefItem.className = 'preference-item';
            prefItem.innerHTML = `
                ${dish.name}
                <button class="remove-btn" data-id="${id}">×</button>
            `;
            prefItem.querySelector('.remove-btn').addEventListener('click', (e) => {
                e.stopPropagation();
                removePreference(id);
            });
            dislikeList.appendChild(prefItem);
        });
    }

    // 更新计数
    document.getElementById('likeCount').textContent = selectedDishes.liked.size;
    document.getElementById('dislikeCount').textContent = selectedDishes.disliked.size;

    updateSubmitButtonState();
}

// 搜索功能
function setupSearch() {
    const searchInput = document.getElementById('prefSearch');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            document.querySelectorAll('.preference-card').forEach(card => {
                const title = card.querySelector('.preference-title').textContent.toLowerCase();
                const description = card.querySelector('.option-description').textContent.toLowerCase();
                card.style.display = (title.includes(searchTerm) || description.includes(searchTerm)) ? 'block' : 'none';
            });
        });
    }
}

// 控制按钮
function setupControlButtons() {
    // 全选喜欢
    const selectAllBtn = document.getElementById('selectAllLikes');
    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', () => {
            DISHES.forEach(dish => {
                selectedDishes.liked.add(dish.id);
                selectedDishes.disliked.delete(dish.id);
            });
            updatePreferenceUI();
        });
    }

    // 清除偏好
    const clearBtn = document.getElementById('clearPreferences');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            selectedDishes.liked.clear();
            selectedDishes.disliked.clear();
            updatePreferenceUI();
        });
    }

    // 重置表单
    const resetBtn = document.getElementById('resetBtn');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetForm);
    }
}

// 偏好按钮事件
function setupPreferenceButtons() {
    document.querySelectorAll('.preference-card').forEach(card => {
        const likeBtn = card.querySelector('.like-btn');
        const dislikeBtn = card.querySelector('.dislike-btn');

        likeBtn.addEventListener('click', () => {
            togglePreference(card.dataset.id, 'like');
        });

        dislikeBtn.addEventListener('click', () => {
            togglePreference(card.dataset.id, 'dislike');
        });
    });
}

// 个人信息摘要
function updateInfoSummary() {
    const gender = document.querySelector('input[name="gender"]:checked');
    document.getElementById('genderSummary').textContent = gender ? (gender.value === 'male' ? '男' : '女') : '未选择';

    const age = document.querySelector('input[name="age"]:checked');
    document.getElementById('ageSummary').textContent = age ? (age.value === '18-64' ? '18~64岁' : '65岁及以上') : '未选择';

    const weight = document.getElementById('weight');
    document.getElementById('weightSummary').textContent = weight.value ? `${weight.value} 公斤` : '未输入';

    const diseases = Array.from(document.querySelectorAll('input[name="disease"]:checked')).map(d => d.value);
    document.getElementById('diseaseSummary').textContent = diseases.length > 0 ? diseases.join(', ') : '无';

    const severity = document.querySelector('input[name="severity"]:checked');
    document.getElementById('severitySummary').textContent = severity ? severity.value : '未选择';

    updateSubmitButtonState();
}

function setupPersonalInfoListeners() {
    // 监听所有个人信息输入
    const inputs = [
        ...document.querySelectorAll('input[name="gender"]'),
        ...document.querySelectorAll('input[name="age"]'),
        document.getElementById('weight'),
        ...document.querySelectorAll('input[name="disease"]'),
        ...document.querySelectorAll('input[name="severity"]')
    ];

    inputs.forEach(input => {
        if (input) {
            input.addEventListener('change', updateInfoSummary);
            input.addEventListener('input', updateInfoSummary);
        }
    });

    // 表单选项选中样式
    document.querySelectorAll('.form-option').forEach(option => {
        option.addEventListener('click', function () {
            const input = this.querySelector('input');
            if (input.type === 'radio') {
                document.querySelectorAll(`input[name="${input.name}"]`).forEach(radio => {
                    radio.closest('.form-option').classList.remove('selected');
                });
            }
            if (input.type === 'checkbox') {
                this.classList.toggle('selected', input.checked);
            } else {
                this.classList.add('selected');
            }
        });
    });
}

// 表单验证
function validateForm() {
    // 验证年龄
    const age = document.querySelector('input[name="age"]:checked');
    if (!age) {
        alert('请选择年龄组');
        return false;
    }

    // 验证体重
    const weight = parseFloat(document.getElementById('weight').value);
    if (!weight || weight < 5 || weight > 200) {
        alert('请输入有效的体重（5-200公斤）');
        return false;
    }

    // 验证疾病选择
    const diseases = document.querySelectorAll('input[name="disease"]:checked');
    if (diseases.length === 0) {
        alert('请选择慢性病类型');
        return false;
    }

    // 验证严重程度
    const severity = document.querySelector('input[name="severity"]:checked');
    if (!severity) {
        alert('请选择病情严重程度');
        return false;
    }

    // 验证偏好选择
    if (selectedDishes.liked.size === 0 && selectedDishes.disliked.size === 0) {
        alert('请至少选择一种菜品偏好');
        return false;
    }

    return true;
}

function updateSubmitButtonState() {
    const submitBtn = document.getElementById('submitBtn');
    if (!submitBtn) return;

    const gender = document.querySelector('input[name="gender"]:checked');
    const age = document.querySelector('input[name="age"]:checked');
    const weight = document.getElementById('weight').value;

    const isPersonalInfoComplete = gender && age && weight;
    const isPreferenceComplete = selectedDishes.liked.size > 0 || selectedDishes.disliked.size > 0;

    submitBtn.disabled = !(isPersonalInfoComplete && isPreferenceComplete);
}

// 表单提交
async function submitFormData(formData) {
    console.log('正在发送请求到 /api/recommend');
    console.log('发送的数据:', JSON.stringify(formData, null, 2));

    const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    });

    console.log('响应状态:', response.status);

    if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP错误! 状态: ${response.status}, 详情: ${errorText}`);
    }

    return await response.json();
}

function getFormData() {
    const gender = document.querySelector('input[name="gender"]:checked');
    const age = document.querySelector('input[name="age"]:checked');
    const weight = document.getElementById('weight');
    const diseases = Array.from(document.querySelectorAll('input[name="disease"]:checked')).map(d => d.value);
    const severity = document.querySelector('input[name="severity"]:checked');

    const likedItems = Array.from(selectedDishes.liked).map(id => {
        const dish = DISHES.find(d => d.id === id);
        return dish.name;
    });

    const dislikedItems = Array.from(selectedDishes.disliked).map(id => {
        const dish = DISHES.find(d => d.id === id);
        return dish.name;
    });

    return {
        userInfo: {
            age: age.value === '18-64' ? 35 : 70,
            gender: gender.value,
            weight: parseFloat(weight.value),
            diseases: diseases.length > 0 ? diseases : ["痛风"],
            symptomSeverity: severity.value,
            dietaryRestrictions: []
        },
        likedDishes: likedItems,
        dislikedDishes: dislikedItems
    };
}

async function handleFormSubmit(event) {
    event.preventDefault();

    if (!validateForm()) {
        return;
    }

    showLoading();

    try {
        const formData = getFormData();
        console.log('准备提交的表单数据:', formData);

        const response = await submitFormData(formData);

        if (response.success) {
            // 将推荐数据存储到localStorage，然后在新的推荐页面显示
            localStorage.setItem('recommendationData', JSON.stringify(response.recommendation));
            // 跳转到推荐结果页面
            window.location.href = '/recommend';
        } else {
            showError('推荐生成失败：' + (response.error || '未知错误'));
        }
    } catch (error) {
        console.error('提交错误:', error);
        showError('网络错误，请检查连接后重试: ' + error.message);
    } finally {
        hideLoading();
    }
}

function resetForm() {
    document.getElementById('healthForm').reset();
    selectedDishes.liked.clear();
    selectedDishes.disliked.clear();
    updatePreferenceUI();
    updateInfoSummary();
}

// 初始化
function initialize() {
    // 只在问卷页面初始化
    if (document.getElementById('healthForm')) {
        setupPreferenceButtons();
        setupSearch();
        setupControlButtons();
        setupPersonalInfoListeners();
        updateInfoSummary();

        // 表单提交事件
        const healthForm = document.getElementById('healthForm');
        if (healthForm) {
            healthForm.addEventListener('submit', handleFormSubmit);
        }

        console.log('问卷页面初始化完成');
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', initialize);