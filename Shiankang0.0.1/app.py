# -*- coding: utf-8 -*-
import os
import sys
import json
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import numpy as np
from scipy.optimize import minimize, LinearConstraint, Bounds
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import traceback
from datetime import datetime

# ========== 路径设置 ==========
current_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(current_dir, 'templates')
static_dir = os.path.join(current_dir, 'static')
DATA_DIR = os.path.join(current_dir, 'data')  # 用户数据存储目录

# 确保目录存在
os.makedirs(template_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

print(f"当前目录: {current_dir}")
print(f"模板目录: {template_dir}")
print(f"静态文件目录: {static_dir}")
print(f"用户数据目录: {DATA_DIR}")

app = Flask(__name__, 
            template_folder=template_dir,
            static_folder=static_dir)
CORS(app)

# ========== 用户数据文件操作 ==========
def load_user_data(username):
    """加载指定用户的 JSON 数据，不存在则返回 None"""
    filepath = os.path.join(DATA_DIR, f"{username}.json")
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_user_data(username, data):
    """保存用户数据到 JSON 文件"""
    filepath = os.path.join(DATA_DIR, f"{username}.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ========== 算法常量 ==========
a_vectors = np.array([
    [320, 0, 20, 0, 25, 15, 0.5, 550],   # 1.红烧肉
    [220, 5, 18, 0, 18, 12, 2, 450],     # 2.番茄炒蛋
    [120, 32, 0, 0, 8, 83, 101, 320],    # 3.蒜蓉上海青
    [150, 41, 0, 0, 10, 256, 2.5, 450],  # 4.酸辣土豆丝
    [350, 30, 25, 0, 25, 221, 5, 750],   # 5.鱼香肉丝
    [380, 20, 30, 0, 22, 248, 4, 680],   # 6.宫保鸡丁
    [280, 0, 6, 15, 12, 187, 3, 520],    # 7.麻婆豆腐
    [280, 0, 22, 0, 10, 32, 0, 450],     # 8.清蒸鲈鱼
    [250, 85, 0, 0, 15, 354, 4.2, 520],  # 9.地三鲜
    [320, 0, 25, 0, 20, 203, 2, 780],    # 10.京酱肉丝
    [300, 0, 30, 0, 22, 85, 1.5, 520],   # 11.葱油手撕鸡
    [380, 0, 20, 0, 25, 428, 2.8, 650],  # 12.糖醋里脊
    [220, 0, 20, 0, 8, 89, 0, 350],      # 13.清炒虾仁
    [150, 78, 0, 0, 8, 125, 7, 280],     # 14.蒜蓉西兰花
    [320, 10, 20, 0, 18, 189, 3.5, 580], # 15.木须肉
    [120, 10, 8, 0, 5, 128, 1.2, 320],   # 16.西红柿鸡蛋汤
    [220, 0, 20, 15, 10, 68, 2, 350],    # 17.鲫鱼豆腐汤
    [180, 0, 15, 0, 8, 125, 3.8, 480],   # 18.冬瓜肉丸汤
    [280, 12, 10, 0, 15, 289, 8, 520],   # 19.红烧茄子
    [350, 0, 25, 0, 20, 158, 2.2, 550],  # 20.葱爆羊肉
    [350, 0, 0, 0, 1, 150, 2, 100]       # 21.主食
])

k_target = np.array([1200, 40, 40, 20, 30, 300, 15, 600])

# ========== 数据类和枚举 ==========
@dataclass
class Food:
    category: str
    name: str
    gout: str
    diabetes: str
    hypertension: str
    cardio: str

@dataclass
class DishIngredient:
    foodName: str
    proportion: float

@dataclass
class Dish:
    name: str
    ingredients: List[DishIngredient]
    score: float = 0.0

class DiseaseType(Enum):
    GOUT = 0
    DIABETES = 1
    HYPERTENSION = 2
    CARDIO = 3

class SeverityLevel(Enum):
    MILD = 0
    MODERATE = 1
    SEVERE = 2

# ========== 类型转换函数 ==========
def deep_convert_numpy_types(obj):
    """
    递归地将所有NumPy类型转换为Python原生类型
    """
    if obj is None:
        return None
    elif isinstance(obj, (np.integer, np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return [deep_convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (list, tuple)):
        return [deep_convert_numpy_types(item) for item in obj]
    elif isinstance(obj, dict):
        return {str(key): deep_convert_numpy_types(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        return deep_convert_numpy_types(obj.__dict__)
    else:
        return obj

def safe_json_serialize(obj):
    """安全的JSON序列化，确保所有类型都是可序列化的"""
    return json.loads(json.dumps(obj, default=lambda x: float(x) if isinstance(x, (np.integer, np.floating)) else str(x)))

# ========== 算法函数 ==========
_rear_prefs = None
_w_like = 0.0
_w_dislike = 0.0
_front_weight_ratio = None

def _init_fast_random_params():
    global _rear_prefs, _w_like, _w_dislike, _front_weight_ratio
    _rear_prefs = np.random.choice([0, 1, 2], size=16, p=[0.2, 0.4, 0.4])
    _w_like = np.random.uniform(0.15, 0.25)
    _w_dislike = np.random.uniform(0.25, 0.35)
    _front_weight_ratio = np.random.uniform(0, 1, 5)
    _front_weight_ratio /= np.sum(_front_weight_ratio)

def solve_fast_top_three():
    _init_fast_random_params()

    def objective(x):
        residual = np.sum(np.abs(a_vectors.T @ x - k_target))
        front_weight = _w_like * np.sum(_front_weight_ratio / (x[:5] + 1e-3))
        rear_x = x[5:]
        rear_weight = _w_like * np.sum((_rear_prefs == 1) / (rear_x + 1e-3)) + \
                      _w_dislike * np.sum((_rear_prefs == 2) * rear_x)
        return residual + front_weight + rear_weight

    dish_constraint = LinearConstraint(np.ones(21), lb=3, ub=6)
    x0 = np.zeros(21)
    x0[np.random.choice(21, size=3, replace=False)] = 0.5
    bounds = Bounds(lb=0, ub=3)

    result = minimize(
        objective,
        x0,
        bounds=bounds,
        constraints=[dish_constraint],
        method='SLSQP',
        options={
            'maxiter': 800,
            'ftol': 1e-3,
            'eps': 1e-2
        }
    )

    if result.success:
        x_raw = result.x
        top5_idx = np.argsort(x_raw)[-5:]
        x_top5 = np.zeros_like(x_raw)
        x_top5[top5_idx] = x_raw[top5_idx]
        x_top5[x_top5 < 0.05] = 0
        
        # 转换为Python原生类型
        x_top5_python = [float(x) for x in x_top5]
        nutrition_result = [float(x) for x in (a_vectors.T @ x_top5)]
        
        return x_top5_python, nutrition_result
    else:
        try:
            return solve_fast_top_three()
        except:
            # 返回默认解
            default_solution = [0.0] * 21
            default_solution[0] = 1.0
            nutrition_default = [float(x) for x in (a_vectors.T @ np.array(default_solution))]
            return default_solution, nutrition_default

def calculate_nutrition_rate(nutrition_actual: list, nutrition_target: list) -> List[tuple]:
    """计算营养达标率"""
    nutrition_rates = []
    display_indices = [
        (0, "热量"),
        (-1, "蛋白质"),
        (4, "脂肪"),
        (5, "碳水化合物"),
        (6, "纤维素"),
        (7, "钠")
    ]

    protein_actual = 0.0
    if len(nutrition_actual) >= 4:
        protein_actual = nutrition_actual[1] + nutrition_actual[2] + nutrition_actual[3]
    protein_target = 100.0

    for idx, name in display_indices:
        if name == "蛋白质":
            target = protein_target
            actual = protein_actual
        else:
            original_idx = idx
            target = nutrition_target[original_idx]
            actual = nutrition_actual[original_idx] if original_idx < len(nutrition_actual) else 0.0

        if target == 0:
            rate = 0.0
        else:
            rate = (actual / target) * 100
            rate = max(0.0, min(rate, 100.0))

        nutrition_rates.append((name, float(target), float(actual), float(rate)))
    return nutrition_rates

def get_food_data() -> List[Food]:
    return [
        Food("蔬菜类", "上海青", "特别推荐", "特别推荐", "特别推荐", "特别推荐"),
        Food("蔬菜类", "西红柿", "特别推荐", "特别推荐", "建议食用", "特别推荐"),
        Food("蛋类", "鸡蛋", "建议食用", "建议食用", "建议食用", "建议食用"),
        Food("肉禽类", "猪肉(瘦)", "建议食用", "建议食用", "建议食用", "建议食用"),
        Food("肉禽类", "鸡肉(鸡胸)", "建议食用", "建议食用", "特别推荐", "特别推荐"),
        Food("水产类", "鲈鱼", "适量食用", "特别推荐", "特别推荐", "建议食用"),
        Food("豆类及制品", "豆腐(北豆腐)", "建议食用", "避免食用", "适量食用", "建议食用"),
        Food("谷物及制品", "粳米(标一)", "特别推荐", "避免食用", "适量食用", "特别推荐"),
        Food("蔬菜类", "菠菜(鲜)", "特别推荐", "特别推荐", "特别推荐", "特别推荐"),
        Food("水果类", "苹果", "特别推荐", "建议食用", "适量食用", "特别推荐"),
        Food("蔬菜类", "西兰花", "特别推荐", "特别推荐", "特别推荐", "特别推荐"),
        Food("蔬菜类", "黄瓜", "特别推荐", "特别推荐", "适量食用", "特别推荐"),
        Food("蔬菜类", "芹菜", "特别推荐", "特别推荐", "建议食用", "建议食用"),
        Food("蔬菜类", "胡萝卜", "特别推荐", "特别推荐", "建议食用", "特别推荐"),
        Food("蔬菜类", "木耳", "特别推荐", "特别推荐", "特别推荐", "特别推荐"),
        Food("蔬菜类", "山药", "特别推荐", "建议食用", "建议食用", "特别推荐"),
        Food("蔬菜类", "冬瓜", "特别推荐", "特别推荐", "适量食用", "特别推荐"),
        Food("肉禽类", "牛肉(瘦)", "建议食用", "建议食用", "建议食用", "特别推荐"),
        Food("肉禽类", "羊肉(瘦)", "建议食用", "建议食用", "建议食用", "建议食用"),
        Food("水产类", "虾", "适量食用", "特别推荐", "建议食用", "建议食用")
    ]

def get_dish_data() -> List[Dish]:
    return [
        Dish("红烧肉", [DishIngredient("猪肉(瘦)", 0.5), DishIngredient("冰糖", 0.05)]),
        Dish("番茄炒蛋", [DishIngredient("西红柿", 0.45), DishIngredient("鸡蛋", 0.35)]),
        Dish("蒜蓉上海青", [DishIngredient("上海青", 0.75), DishIngredient("大蒜", 0.04)]),
        Dish("酸辣土豆丝", [DishIngredient("土豆", 0.8), DishIngredient("干辣椒", 0.01)]),
        Dish("鱼香肉丝", [DishIngredient("猪肉(瘦)", 0.35), DishIngredient("木耳", 0.03)]),
        Dish("宫保鸡丁", [DishIngredient("鸡肉(鸡胸)", 0.4), DishIngredient("花生", 0.1)]),
        Dish("麻婆豆腐", [DishIngredient("豆腐(北豆腐)", 0.6), DishIngredient("猪肉(瘦)", 0.1)]),
        Dish("清蒸鲈鱼", [DishIngredient("鲈鱼", 0.75), DishIngredient("姜", 0.03)]),
        Dish("地三鲜", [DishIngredient("茄子", 0.35), DishIngredient("土豆", 0.35)]),
        Dish("京酱肉丝", [DishIngredient("猪肉(瘦)", 0.4), DishIngredient("甜面酱", 0.08)]),
        Dish("葱油手撕鸡", [DishIngredient("鸡肉(鸡胸)", 0.7), DishIngredient("大葱", 0.12)]),
        Dish("糖醋里脊", [DishIngredient("猪肉(瘦)", 0.4), DishIngredient("鸡蛋", 0.1)]),
        Dish("清炒虾仁", [DishIngredient("虾", 0.6), DishIngredient("黄瓜", 0.2)]),
        Dish("蒜蓉西兰花", [DishIngredient("西兰花", 0.65), DishIngredient("大蒜", 0.05)]),
        Dish("木须肉", [DishIngredient("猪肉(瘦)", 0.3), DishIngredient("鸡蛋", 0.2)]),
        Dish("西红柿鸡蛋汤", [DishIngredient("西红柿", 0.35), DishIngredient("鸡蛋", 0.15)]),
        Dish("鲫鱼豆腐汤", [DishIngredient("鲫鱼", 0.55), DishIngredient("豆腐(北豆腐)", 0.35)]),
        Dish("冬瓜肉丸汤", [DishIngredient("猪肉(瘦)", 0.35), DishIngredient("冬瓜", 0.4)]),
        Dish("红烧茄子", [DishIngredient("茄子", 0.6), DishIngredient("猪肉(瘦)", 0.15)]),
        Dish("葱爆羊肉", [DishIngredient("羊肉(瘦)", 0.6), DishIngredient("大葱", 0.25)])
    ]

def recommendation_to_score(recommendation: str) -> int:
    if recommendation == "特别推荐":
        return 4
    elif recommendation == "建议食用":
        return 3
    elif recommendation == "适量食用":
        return 2
    elif recommendation == "避免食用":
        return 1
    else:
        return 2

def get_recommendation(food: Food, disease: DiseaseType) -> str:
    if disease == DiseaseType.GOUT:
        return food.gout
    elif disease == DiseaseType.DIABETES:
        return food.diabetes
    elif disease == DiseaseType.HYPERTENSION:
        return food.hypertension
    elif disease == DiseaseType.CARDIO:
        return food.cardio
    else:
        return "适量食用"

def calculate_dish_score(dish: Dish, foods: List[Food], disease: DiseaseType) -> float:
    total_score = 0.0
    total_proportion = 0.0

    for ingredient in dish.ingredients:
        found_food = None
        for food in foods:
            if food.name == ingredient.foodName:
                found_food = food
                break

        if found_food:
            recommendation = get_recommendation(found_food, disease)
            score = recommendation_to_score(recommendation)
            total_score += ingredient.proportion * score
            total_proportion += ingredient.proportion
        else:
            total_score += ingredient.proportion * 2
            total_proportion += ingredient.proportion

    if total_proportion > 0:
        return total_score / total_proportion
    return 0.0

def should_recommend_dish(dish_score: float, severity: SeverityLevel) -> bool:
    if severity == SeverityLevel.MILD:
        return dish_score >= 2.0
    elif severity == SeverityLevel.MODERATE:
        return dish_score >= 2.5
    else:
        return dish_score >= 3.0

# ========== 推荐API类 ==========
class RecommendationAPI:
    def __init__(self):
        self.foods = get_food_data()
        self.dishes = get_dish_data()
        self.dish_names = [
            "红烧肉", "番茄炒蛋", "蒜蓉上海青", "酸辣土豆丝", "鱼香肉丝",
            "宫保鸡丁", "麻婆豆腐", "清蒸鲈鱼", "地三鲜", "京酱肉丝",
            "葱油手撕鸡", "糖醋里脊", "清炒虾仁", "蒜蓉西兰花", "木须肉",
            "西红柿鸡蛋汤", "鲫鱼豆腐汤", "冬瓜肉丸汤", "红烧茄子", "葱爆羊肉",
            "主食（米饭/面/面包）"
        ]
    
    def map_disease_name(self, disease_name: str) -> DiseaseType:
        disease_mapping = {
            "痛风": DiseaseType.GOUT,
            "糖尿病": DiseaseType.DIABETES,
            "高血压": DiseaseType.HYPERTENSION,
            "心脑血管疾病": DiseaseType.CARDIO
        }
        return disease_mapping.get(disease_name, DiseaseType.GOUT)
    
    def map_severity_name(self, severity_name: str) -> SeverityLevel:
        severity_mapping = {
            "轻度": SeverityLevel.MILD,
            "中度": SeverityLevel.MODERATE,
            "重度": SeverityLevel.SEVERE
        }
        return severity_mapping.get(severity_name, SeverityLevel.MILD)
    
    def calculate_dish_ingredients_list(self, dish: Dish) -> List[str]:
        return [ingredient.foodName for ingredient in dish.ingredients[:3]]
    
    def generate_optimized_meal_plan(self, liked_dishes: List[str], disliked_dishes: List[str]) -> tuple:
        try:
            x_opt, nutrition_result = solve_fast_top_three()
            
            optimized_dishes = []
            for i, amount in enumerate(x_opt):
                if amount > 0.05:
                    dish_name = self.dish_names[i]
                    if dish_name not in disliked_dishes:
                        optimized_dishes.append({
                            "name": dish_name,
                            "amount": float(amount),
                            "isLiked": dish_name in liked_dishes
                        })
            
            total_amount = sum(dish["amount"] for dish in optimized_dishes)
            total_score = 0.0
            for dish_info in optimized_dishes:
                for dish in self.dishes:
                    if dish.name == dish_info["name"]:
                        proportion = dish_info["amount"] / total_amount if total_amount > 0 else 0
                        total_score += dish.score * proportion
                        break
            
            meal_plan = {
                "dishes": optimized_dishes,
                "totalAmount": float(total_amount),
                "totalScore": float(total_score)
            }
            
            return deep_convert_numpy_types(meal_plan), nutrition_result
            
        except Exception as e:
            print(f"套餐优化失败: {str(e)}")
            default_plan = {
                "dishes": [
                    {"name": "蒜蓉西兰花", "amount": 1.2, "isLiked": True},
                    {"name": "清蒸鲈鱼", "amount": 1.0, "isLiked": False}
                ],
                "totalAmount": 2.2,
                "totalScore": 3.5
            }
            return deep_convert_numpy_types(default_plan), []
    
    def calculate_nutrition_analysis(self, meal_plan: Dict[str, Any]) -> Dict[str, float]:
        if not meal_plan or not meal_plan['dishes']:
            return deep_convert_numpy_types({
                "calories": 650.0,
                "protein": 35.2,
                "fat": 22.8,
                "carbs": 68.5,
                "fiber": 8.5,
                "sodium": 450.0
            })
        
        total_amount = meal_plan['totalAmount']
        base_calories = 600 + total_amount * 100
        base_protein = 30 + total_amount * 5
        base_fat = 20 + total_amount * 3
        base_carbs = 60 + total_amount * 8
        base_fiber = 8 + total_amount * 2
        base_sodium = 400 + total_amount * 50
        
        return deep_convert_numpy_types({
            "calories": round(base_calories, 1),
            "protein": round(base_protein, 1),
            "fat": round(base_fat, 1),
            "carbs": round(base_carbs, 1),
            "fiber": round(base_fiber, 1),
            "sodium": round(base_sodium, 1)
        })

    def generate_recommendation(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            user_info = user_data['userInfo']
            liked_dishes = user_data.get('likedDishes', [])
            disliked_dishes = user_data.get('dislikedDishes', [])
            
            main_disease = user_info['diseases'][0] if user_info['diseases'] else "痛风"
            severity = user_info.get('symptomSeverity', "轻度")
            
            disease_type = self.map_disease_name(main_disease)
            severity_level = self.map_severity_name(severity)
            
            # 计算菜品评分
            for dish in self.dishes:
                dish.score = calculate_dish_score(dish, self.foods, disease_type)
            
            # 分类菜品
            recommended_dishes = []
            special_attention_dishes = []
            
            for dish in self.dishes:
                if dish.name in disliked_dishes:
                    continue
                    
                should_recommend = should_recommend_dish(dish.score, severity_level)
                is_liked = dish.name in liked_dishes
                
                dish_info = {
                    "name": dish.name,
                    "score": float(dish.score),
                    "ingredients": self.calculate_dish_ingredients_list(dish),
                    "isLiked": is_liked
                }
                
                if should_recommend:
                    recommended_dishes.append(dish_info)
                elif is_liked:
                    special_attention_dishes.append(dish_info)
            
            # 对推荐菜品排序
            recommended_dishes.sort(key=lambda x: (not x["isLiked"], -x["score"]))
            
            # 生成优化套餐和营养数据
            optimized_meal_plan, nutrition_actual = self.generate_optimized_meal_plan(liked_dishes, disliked_dishes)
            
            # 计算营养达标率
            nutrition_rates = []
            if nutrition_actual and len(nutrition_actual) > 0:
                nutrition_rates = calculate_nutrition_rate(nutrition_actual, [float(x) for x in k_target])
            
            result = {
                "diseaseInfo": {
                    "diseaseName": main_disease,
                    "severity": severity
                },
                "recommendedDishes": recommended_dishes,
                "specialAttentionDishes": special_attention_dishes,
                "optimizedMealPlan": optimized_meal_plan,
                "nutritionAnalysis": self.calculate_nutrition_analysis(optimized_meal_plan),
                "nutritionRates": nutrition_rates,
                "nutritionTargets": {
                    "calories": 1200,
                    "protein": 100,
                    "fat": 30,
                    "carbs": 300,
                    "fiber": 15,
                    "sodium": 600
                }
            }
            
            final_result = deep_convert_numpy_types(result)
            
            try:
                json_str = json.dumps(final_result, ensure_ascii=False)
                return json.loads(json_str)
            except Exception as e:
                print(f"最终序列化验证失败: {e}")
                return safe_json_serialize(final_result)
            
        except Exception as e:
            print(f"生成推荐时发生错误: {str(e)}")
            traceback.print_exc()
            return safe_json_serialize({
                "diseaseInfo": {"diseaseName": "错误", "severity": "未知"},
                "recommendedDishes": [],
                "specialAttentionDishes": [],
                "optimizedMealPlan": {"dishes": [], "totalAmount": 0, "totalScore": 0},
                "nutritionAnalysis": {},
                "nutritionRates": [],
                "nutritionTargets": {}
            })

# ========== Flask路由 ==========
recommendation_api = RecommendationAPI()

@app.route('/')
def home():
    """登录界面（根路径）"""
    return render_template('login.html')

@app.route('/questionnaire')
def questionnaire():
    """问卷页面"""
    return render_template('index.html')

@app.route('/recommend')
def recommend_page():
    """推荐结果页面"""
    return render_template('recommend.html')

@app.route('/game')
def game_page():
    """游戏界面"""
    return render_template('game.html')

@app.route('/api/recommend', methods=['POST'])
def recommend_meal():
    """API接口 - 处理推荐请求"""
    try:
        user_data = request.get_json()
        if not user_data:
            return jsonify({
                "success": False,
                "error": "未收到有效数据"
            }), 400
            
        print("收到用户数据:", user_data)
        
        recommendation = recommendation_api.generate_recommendation(user_data)
        
        # 如果请求中携带了用户名，更新该用户的问卷状态
        username = user_data.get('username')
        if username:
            user = load_user_data(username)
            if user and not user.get('hasCompletedQuestionnaire', False):
                user['hasCompletedQuestionnaire'] = True
                save_user_data(username, user)
                print(f"用户 {username} 问卷状态已更新为已完成")
        
        response_data = {
            "success": True,
            "recommendation": recommendation
        }
        
        try:
            json.dumps(response_data)
            return jsonify(response_data)
        except Exception as e:
            print(f"响应数据序列化失败: {e}")
            return jsonify({
                "success": False,
                "error": f"数据序列化错误: {str(e)}"
            }), 500
        
    except Exception as e:
        print(f"推荐生成错误: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}"
        }), 500

# ========== 用户注册/登录接口 ==========
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not username or not password or not email:
        return jsonify({"success": False, "error": "请填写完整信息"}), 400

    # 检查用户是否已存在
    if load_user_data(username):
        return jsonify({"success": False, "error": "用户名已存在"}), 400

    # 创建新用户数据（密码建议加密，此处简化）
    new_user = {
        "username": username,
        "password": password,  # 实际应使用哈希存储
        "email": email,
        "createdAt": str(datetime.now()),
        "hasCompletedQuestionnaire": False,
        "gameProgress": {
            "gold": 100,
            "healthPoints": 10,
            "atk": 15,
            "def": 10,
            "hp": 100,
            "maxHp": 100,
            "exp": 0,
            "expToNext": 100,
            "level": 1,
            "dailyPurchased": 0
        }
    }

    save_user_data(username, new_user)
    return jsonify({
        "success": True,
        "user": {
            "username": username,
            "hasCompletedQuestionnaire": False
        }
    })

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = load_user_data(username)
    if not user or user['password'] != password:  # 应使用哈希比较
        return jsonify({"success": False, "error": "用户名或密码错误"}), 401

    return jsonify({
        "success": True,
        "user": {
            "username": username,
            "hasCompletedQuestionnaire": user.get('hasCompletedQuestionnaire', False)
        }
    })

# ========== 游戏进度接口 ==========
@app.route('/api/save_progress', methods=['POST'])
def save_progress():
    """保存用户游戏进度"""
    data = request.get_json()
    username = data.get('username')
    progress = data.get('progress')

    user = load_user_data(username)
    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    user['gameProgress'] = progress
    save_user_data(username, user)
    return jsonify({"success": True})

@app.route('/api/load_progress/<username>', methods=['GET'])
def load_progress(username):
    """加载用户游戏进度"""
    user = load_user_data(username)
    if not user:
        return jsonify({"success": False, "error": "用户不存在"}), 404

    return jsonify({
        "success": True,
        "progress": user.get('gameProgress', {})
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy", 
        "message": "后端服务运行正常",
        "version": "完整整合版"
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    """静态文件服务"""
    return app.send_static_file(filename)

if __name__ == '__main__':
    print("=" * 50)
    print("健康饮食推荐系统 - 完整整合版")
    print("=" * 50)
    print("服务地址: http://localhost:5000")
    print("用户数据目录:", DATA_DIR)
    print("=" * 50)
    
    app.run(debug=True, port=5000, host='0.0.0.0')