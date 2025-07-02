import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly.express as px
from fpdf import FPDF
import base64

# ----------- Enhanced Constants & Configuration ------------

PASSCODE = "1512"
DATA_FILE = "fitness_diary_data.json"

# Enhanced theme configuration
st.set_page_config(
    page_title="💪 FitTracker Pro", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💪"
)

# Custom CSS for better UI
def load_custom_css():
    st.markdown("""
    <style>
    /* Main theme colors */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    .food-section {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 10px 10px 0;
    }
    
    .success-box {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: linear-gradient(90deg, #f12711 0%, #f5af19 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* Progress bars */
    .progress-bar {
        background: #e0e0e0;
        border-radius: 10px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill.completed {
        background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%);
        box-shadow: 0 0 10px rgba(46, 204, 113, 0.5);
    }
    </style>
    """, unsafe_allow_html=True)

# Enhanced Food Database organized by meals with correct values
FOOD_DATA = {
    # Meal 1 Foods
    "Oats": {"unit": "g", "base": 45, "cal": 170, "protein": 10, "fat": 0, "meal": "Meal 1"},
    "Whey Protein": {"unit": "g", "base": 33, "cal": 120, "protein": 25, "fat": 0, "meal": "Meal 1"},
    "Skim Milk Powder": {"unit": "g", "base": 46, "cal": 160, "protein": 16, "fat": 0, "meal": "Meal 1"},
    "PB Powder": {"unit": "g", "base": 16, "cal": 80, "protein": 7, "fat": 0, "meal": "Meal 1"},
    "Nuts": {"unit": "g", "base": 15, "cal": 100, "protein": 2, "fat": 9, "meal": "Meal 1"},
    
    # Meal 2 Foods
    "White Rice": {"unit": "g", "base": 150, "cal": 210, "protein": 5, "fat": 0.5, "meal": "Meal 2"},
    "Tomato": {"unit": "count", "base": 1, "cal": 25, "protein": 0.5, "fat": 0, "meal": "Meal 2"},
    "Onion": {"unit": "count", "base": 1, "cal": 25, "protein": 0.5, "fat": 0, "meal": "Meal 2"},
    "Yogurt": {"unit": "g", "base": 170, "cal": 90, "protein": 18, "fat": 0, "meal": "Meal 2"},
    "Tortilla": {"unit": "count", "base": 1, "cal": 70, "protein": 5, "fat": 2, "meal": "Meal 2"},
    "Soya Chunks": {"unit": "g", "base": 50, "cal": 155, "protein": 27, "fat": 1, "meal": "Meal 2"},
    
    # Meal 3 Foods
    "Whey Protein Shake": {"unit": "g", "base": 33, "cal": 120, "protein": 25, "fat": 0, "meal": "Meal 3"},
}

# Enhanced exercise data
EXERCISE_DATA = {
    "Chest": {"intensity_1": 100, "intensity_2": 150, "intensity_3": 200, "icon": "💪"},
    "Back": {"intensity_1": 100, "intensity_2": 150, "intensity_3": 200, "icon": "🏋️"},
    "Bicep": {"intensity_1": 80, "intensity_2": 120, "intensity_3": 160, "icon": "💪"},
    "Tricep": {"intensity_1": 80, "intensity_2": 120, "intensity_3": 160, "icon": "💪"},
    "Shoulder": {"intensity_1": 90, "intensity_2": 135, "intensity_3": 180, "icon": "🏋️"},
    "Legs": {"intensity_1": 120, "intensity_2": 180, "intensity_3": 240, "icon": "🦵"},
    "Cardio": {"intensity_1": 200, "intensity_2": 300, "intensity_3": 400, "icon": "🏃"},
    "Full Body": {"intensity_1": 150, "intensity_2": 225, "intensity_3": 300, "icon": "💥"},
}

# Dynamic fitness goals based on workout day
def get_daily_goals(is_gym_day=True):
    if is_gym_day:
        return {
            "calories": {"min": 1300, "max": 1400, "optimal": 1350},
            "protein": {"min": 140, "max": 145, "optimal": 142},
            "water": {"min": 2000, "max": 4000, "optimal": 3000},
            "steps": {"min": 8000, "max": 15000, "optimal": 10000},
        }
    else:
        return {
            "calories": {"min": 1100, "max": 1200, "optimal": 1150},
            "protein": {"min": 100, "max": 120, "optimal": 110},
            "water": {"min": 2000, "max": 4000, "optimal": 3000},
            "steps": {"min": 8000, "max": 15000, "optimal": 10000},
        }

STEPS_PER_MILE = 1200
CAL_PER_MILE = 100

# ------------ Enhanced Utility Functions --------------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def calculate_macros(food_inputs):
    """Calculate total macros from food input dict."""
    total = {"cal": 0, "protein": 0, "fat": 0}
    
    for food, qty in food_inputs.items():
        if qty is None or qty == 0:
            continue
        info = FOOD_DATA.get(food)
        if not info:
            continue
            
        if info["unit"] == "g":
            ratio = qty / info["base"]
            total["cal"] += info["cal"] * ratio
            total["protein"] += info["protein"] * ratio
            total["fat"] += info["fat"] * ratio
        elif info["unit"] == "count":
            total["cal"] += info["cal"] * qty
            total["protein"] += info["protein"] * qty
            total["fat"] += info["fat"] * qty
    
    return total

def calculate_bmi(weight, height_cm):
    if weight is None or height_cm is None or weight <= 0 or height_cm <= 0:
        return None
    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)

def get_bmi_category(bmi):
    if bmi is None:
        return "Unknown", "gray"
    elif bmi < 18.5:
        return "Underweight", "#3498db"
    elif bmi < 25:
        return "Normal", "#2ecc71"
    elif bmi < 30:
        return "Overweight", "#f39c12"
    else:
        return "Obese", "#e74c3c"

def steps_to_miles_calories(steps):
    miles = steps / STEPS_PER_MILE
    cal_burned = miles * CAL_PER_MILE
    return round(miles, 2), round(cal_burned, 1)

def get_today_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def create_progress_bar(current, goal, label, color="#667eea", completed=False):
    percentage = min((current / goal) * 100, 100) if goal > 0 else 0
    is_complete = percentage >= 100
    bar_class = "completed" if is_complete else ""
    
    return f"""
    <div style="margin: 10px 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-weight: bold; color: {'#2ecc71' if is_complete else '#333'};">
                {label} {'✅' if is_complete else ''}
            </span>
            <span style="color: {'#2ecc71' if is_complete else '#666'};">{current:.1f} / {goal}</span>
        </div>
        <div style="background: #e0e0e0; border-radius: 10px; overflow: hidden;">
            <div class="progress-fill {bar_class}" style="height: 20px; width: {percentage}%; background: {'linear-gradient(90deg, #2ecc71 0%, #27ae60 100%)' if is_complete else color}; transition: width 0.3s ease;"></div>
        </div>
        <div style="text-align: right; font-size: 12px; margin-top: 2px; color: {'#2ecc71' if is_complete else '#666'};">
            {percentage:.1f}% {'🎉 GOAL ACHIEVED!' if is_complete else ''}
        </div>
    </div>
    """

def create_metric_card(title, value, unit, icon, color="#667eea"):
    return f"""
    <div style="
        background: linear-gradient(135deg, {color}20 0%, {color}10 100%);
        border-left: 4px solid {color};
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div>
                <h3 style="margin: 0; color: {color}; font-size: 14px;">{title}</h3>
                <h2 style="margin: 5px 0 0 0; color: #333;">{value} <span style="font-size: 16px; color: #666;">{unit}</span></h2>
            </div>
            <div style="font-size: 24px;">{icon}</div>
        </div>
    </div>
    """

def plot_enhanced_trends(data, key, title, ylabel, color="#667eea"):
    dates = sorted(data.keys())
    values = [data[d].get(key, None) for d in dates]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, 
        y=values, 
        mode='lines+markers',
        name=title,
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color),
        hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=18, color='#333')),
        xaxis_title='Date',
        yaxis_title=ylabel,
        height=350,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial", size=12),
        hovermode='x',
        showlegend=False
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig

# ----------- Enhanced Streamlit App -----------------

# Load custom CSS
load_custom_css()

# Enhanced Authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="main-header">
        <h1>💪 FitTracker Pro</h1>
        <p>Your Personal Fitness & Nutrition Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Enter Your Secure Passcode")
        password_input = st.text_input("", type="password", placeholder="Enter passcode...")
        
        if st.button("🚀 Access My Diary", use_container_width=True):
            if password_input == PASSCODE:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.markdown('<div class="warning-box">❌ Incorrect passcode! Please try again.</div>', unsafe_allow_html=True)
    st.stop()

# Load data
data = load_data()

# Enhanced Header
st.markdown("""
<div class="main-header">
    <h1>💪 FitTracker Pro Dashboard</h1>
    <p>Track • Analyze • Achieve Your Fitness Goals</p>
</div>
""", unsafe_allow_html=True)

# Enhanced Sidebar
st.sidebar.markdown("### 🎯 Navigation")
page = st.sidebar.radio(
    "",
    ["📝 Daily Entry", "📊 Analytics", "📈 Progress", "📋 History", "📄 Reports", "⚙️ Settings"],
    key="navigation"
)

# Enhanced Date Selection
st.sidebar.markdown("---")
st.sidebar.markdown("### 📅 Date Selection")
if "selected_date" not in st.session_state:
    st.session_state.selected_date = get_today_date_str()

selected_date = st.sidebar.date_input(
    "Select Date", 
    datetime.strptime(st.session_state.selected_date, "%Y-%m-%d")
)
selected_date_str = selected_date.strftime("%Y-%m-%d")
st.session_state.selected_date = selected_date_str

# Quick Stats in Sidebar
if data and selected_date_str in data:
    entry = data[selected_date_str]
    st.sidebar.markdown("### 📊 Quick Stats")
    st.sidebar.metric("Calories", f"{entry.get('total_calories', 0):.0f}", "kcal")
    st.sidebar.metric("Protein", f"{entry.get('total_protein', 0):.1f}", "g")
    st.sidebar.metric("Steps", f"{entry.get('steps', 0):,}")

# Helper function for entries
def get_entry(date_str):
    return data.get(date_str, {
        "date": date_str,
        "weight": None,
        "height": 181.0,  # Default height
        "age": 24,        # Default age
        "bmi": None,
        "steps": 0,
        "workout_notes": "",
        "food": {},
        "additional_meals": [],
        "exercises": [],
        "total_calories": 0,
        "total_protein": 0,
        "net_calories": 0,
        "is_gym_day": True,  # New field for workout day
    })

entry = get_entry(selected_date_str)

# ----- PAGE: Daily Entry -----
if page == "📝 Daily Entry":
    st.markdown(f"### 📝 Daily Entry - {selected_date_str}")
    
    # Gym Day Toggle
    is_gym_day = st.toggle("🏋️ Gym Day", value=entry.get("is_gym_day", True))
    DAILY_GOALS = get_daily_goals(is_gym_day)
    
    # Clickable Daily Goals Overview
    st.markdown("### 🎯 Daily Goals (Click to Highlight Achievement)")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate current values for goal checking
    current_cal = entry.get("total_calories", 0)
    current_protein = entry.get("total_protein", 0)
    current_steps = entry.get("steps", 0)
    
    with col1:
        cal_achieved = current_cal >= DAILY_GOALS["calories"]["optimal"] * 0.9
        if st.button("🎯 Calorie Goal", key="cal_goal"):
            st.balloons() if cal_achieved else None
        goal_color = "#2ecc71" if cal_achieved else "#e74c3c"
        st.markdown(f"""
        <div style="background: {goal_color}; color: white; padding: 10px; border-radius: 8px; text-align: center; margin: 5px 0;">
            <strong>{DAILY_GOALS["calories"]["optimal"]} kcal</strong><br>
            Current: {current_cal:.0f} {'✅' if cal_achieved else '❌'}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        protein_achieved = current_protein >= DAILY_GOALS["protein"]["optimal"] * 0.9
        if st.button("💪 Protein Goal", key="protein_goal"):
            st.balloons() if protein_achieved else None
        goal_color = "#2ecc71" if protein_achieved else "#e74c3c"
        st.markdown(f"""
        <div style="background: {goal_color}; color: white; padding: 10px; border-radius: 8px; text-align: center; margin: 5px 0;">
            <strong>{DAILY_GOALS["protein"]["optimal"]} g</strong><br>
            Current: {current_protein:.0f} {'✅' if protein_achieved else '❌'}
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        steps_achieved = current_steps >= DAILY_GOALS["steps"]["optimal"] * 0.9
        if st.button("👟 Step Goal", key="steps_goal"):
            st.balloons() if steps_achieved else None
        goal_color = "#2ecc71" if steps_achieved else "#f39c12"
        st.markdown(f"""
        <div style="background: {goal_color}; color: white; padding: 10px; border-radius: 8px; text-align: center; margin: 5px 0;">
            <strong>{DAILY_GOALS["steps"]["optimal"]} steps</strong><br>
            Current: {current_steps:,} {'✅' if steps_achieved else '❌'}
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        bmi = entry.get("bmi")
        bmi_normal = (18.5 <= bmi <= 25) if bmi is not None else False
        if st.button("⚖️ BMI Status", key="bmi_goal"):
            st.balloons() if bmi_normal else None
        goal_color = "#2ecc71" if bmi_normal else "#f39c12"
        bmi_display = f"{bmi:.1f}" if bmi else "0.0"
        st.markdown(f"""
        <div style="background: {goal_color}; color: white; padding: 10px; border-radius: 8px; text-align: center; margin: 5px 0;">
            <strong>BMI Status</strong><br>
            Current: {bmi_display} {'✅' if bmi_normal else '❌'}
        </div>
        """, unsafe_allow_html=True)

    # Enhanced Food Input organized by Meals
    st.markdown("## 🍽️ Nutrition Tracking")
    
    # Group foods by meal
    meal_foods = {
        "Meal 1": [],
        "Meal 2": [],
        "Meal 3": []
    }
    
    for food, info in FOOD_DATA.items():
        meal = info.get("meal", "Meal 1")
        meal_foods[meal].append(food)
    
    food_inputs = {}
    
    # Meal 1
    with st.expander("🌅 Meal 1 (Morning)", expanded=True):
        cols = st.columns(2)
        for i, food in enumerate(meal_foods["Meal 1"]):
            with cols[i % 2]:
                info = FOOD_DATA[food]
                unit_text = "grams" if info["unit"] == "g" else "count"
                default_val = info["base"] if food in ["Oats", "Whey Protein", "Skim Milk Powder", "PB Powder", "Nuts"] else 0
                food_inputs[food] = st.number_input(
                    f"{food} ({unit_text})",
                    min_value=0.0,
                    max_value=1000.0,
                    step=1.0,
                    value=float(entry["food"].get(food, default_val)),
                    key=f"food_{food}",
                    help=f"Calories per {info['base']}{info['unit'] if info['unit'] == 'g' else ' piece'}: {info['cal']}"
                )
    
    # Meal 2
    with st.expander("🌞 Meal 2 (Afternoon)", expanded=True):
        cols = st.columns(2)
        for i, food in enumerate(meal_foods["Meal 2"]):
            with cols[i % 2]:
                info = FOOD_DATA[food]
                unit_text = "grams" if info["unit"] == "g" else "count"
                default_val = info["base"] if food in ["White Rice", "Yogurt", "Soya Chunks"] else (1 if info["unit"] == "count" else 0)
                food_inputs[food] = st.number_input(
                    f"{food} ({unit_text})",
                    min_value=0.0,
                    max_value=1000.0,
                    step=1.0,
                    value=float(entry["food"].get(food, default_val)),
                    key=f"food_{food}",
                    help=f"Calories per {info['base']}{info['unit'] if info['unit'] == 'g' else ' piece'}: {info['cal']}"
                )
    
    # Meal 3
    with st.expander("🌙 Meal 3 (Evening)", expanded=True):
        cols = st.columns(2)
        for i, food in enumerate(meal_foods["Meal 3"]):
            with cols[i % 2]:
                info = FOOD_DATA[food]
                unit_text = "grams" if info["unit"] == "g" else "count"
                default_val = info["base"] if food == "Whey Protein Shake" else 0
                food_inputs[food] = st.number_input(
                    f"{food} ({unit_text})",
                    min_value=0.0,
                    max_value=1000.0,
                    step=1.0,
                    value=float(entry["food"].get(food, default_val)),
                    key=f"food_{food}",
                    help=f"Calories per {info['base']}{info['unit'] if info['unit'] == 'g' else ' piece'}: {info['cal']}"
                )

    # Additional Meals Section
    with st.expander("➕ Additional Meals", expanded=False):
        additional_meals = entry.get("additional_meals", [])
        new_additional_meals = []
        
        for i in range(len(additional_meals)):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                name = st.text_input(f"Meal Name #{i+1}", value=additional_meals[i].get("name", ""), key=f"add_meal_name_{i}")
            with col2:
                cal = st.number_input(f"Calories #{i+1}", min_value=0.0, value=additional_meals[i].get("calories", 0.0), key=f"add_meal_cal_{i}")
            with col3:
                if st.button("❌", key=f"remove_add_meal_{i}"):
                    continue
            new_additional_meals.append({"name": name, "calories": cal})
        
        if st.button("➕ Add Additional Meal"):
            new_additional_meals.append({"name": "", "calories": 0.0})
        
        additional_meals = new_additional_meals

    # Calculate and Show Current Totals
    st.markdown("## 📊 Current Meal Summary")
    
    # Add Calculate Button
    if st.button("🧮 Calculate Current Intake", type="secondary", use_container_width=True):
        # Calculate current macros
        current_macros = calculate_macros(food_inputs)
        additional_cal = sum(item.get("calories", 0) for item in additional_meals)
        total_current_cal = current_macros["cal"] + additional_cal
        total_current_protein = current_macros["protein"]
        
        # Store in session state to display
        st.session_state.current_cal = total_current_cal
        st.session_state.current_protein = total_current_protein
        st.session_state.calorie_progress = (total_current_cal / DAILY_GOALS["calories"]["optimal"]) * 100
        
        st.success("✅ Intake calculated successfully!")
    
    # Display current totals if calculated
    if hasattr(st.session_state, 'current_cal'):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Calories", f"{st.session_state.current_cal:.0f}", "kcal")
        with col2:
            st.metric("Current Protein", f"{st.session_state.current_protein:.1f}", "g")
        with col3:
            st.metric("Goal Progress", f"{st.session_state.calorie_progress:.1f}%", "of daily goal")
    else:
        st.info("👆 Click 'Calculate Current Intake' to see your meal totals")

    # Body Metrics & Exercise Tracking
    st.markdown("## 🏃‍♂️ Body Metrics & Exercise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📏 Quick Body Check")
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, step=0.1, value=entry.get("weight") if entry.get("weight") is not None else 70.0)
        
        # Auto-calculate and show BMI
        height = entry.get("height", 181.0)
        age = entry.get("age", 24)
        bmi = calculate_bmi(weight, height)
        
        if bmi is not None:
            bmi_cat, bmi_color = get_bmi_category(bmi)
            st.markdown(f"""
            <div style="background: {bmi_color}20; border-left: 4px solid {bmi_color}; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <strong>BMI: {bmi}</strong> ({bmi_cat})<br>
                <small>Height: {height}cm | Age: {age}</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Enter weight to calculate BMI")
        
    with col2:
        st.markdown("### 🚶‍♂️ Activity Tracking")
        
        # Step Count Input
        steps = st.number_input("Steps Today", min_value=0, max_value=100000, step=100, value=entry.get("steps", 0))
        
        # Calculate calories from steps
        if steps > 0:
            miles, step_calories = steps_to_miles_calories(steps)
            st.info(f"🔥 Steps burned: {step_calories:.0f} calories ({miles:.1f} miles)")

    # Enhanced Exercise Tracking
    st.markdown("### 🏋️‍♂️ Workout Tracking")
    exercises = entry.get("exercises", [])
    new_exercises = []
    
    for i, exercise in enumerate(exercises):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
        with col1:
            workout_type = st.text_input(f"Workout #{i+1}", value=exercise.get("type", ""), key=f"workout_type_{i}", placeholder="e.g., Chest, Back, Cardio")
        with col2:
            intensity = st.selectbox(f"Intensity #{i+1}", [1, 2, 3], 
                                   index=exercise.get("intensity", 1)-1, 
                                   key=f"intensity_{i}",
                                   help="1=Light(100cal), 2=Medium(150cal), 3=Heavy(200cal)")
        with col3:
            # Calculate calories based on intensity
            base_cal = {1: 100, 2: 150, 3: 200}
            calories = base_cal.get(intensity, 100)
            st.metric("Calories", f"{calories}")
        with col4:
            if st.button("❌", key=f"remove_workout_{i}"):
                continue
        new_exercises.append({"type": workout_type, "intensity": intensity, "calories": calories})
    
    if st.button("➕ Add Workout"):
        new_exercises.append({"type": "", "intensity": 1, "calories": 100})
    
    exercises = new_exercises
    
    # OR Direct Calorie Input
    st.markdown("#### 🔥 Or Enter Calories Burned Directly")
    direct_calories = st.number_input("Total Workout Calories", min_value=0, max_value=2000, step=10, value=0)
    
    # Workout Notes
    workout_notes = st.text_area("📝 Workout Notes", value=entry.get("workout_notes", ""), height=80)

    # Enhanced Save Button
    if st.button("💾 Save Daily Entry", type="primary", use_container_width=True):
        # Calculate all metrics
        macros = calculate_macros(food_inputs)
        additional_cal = sum(item.get("calories", 0) for item in additional_meals)
        exercise_cal = sum(ex.get("calories", 0) for ex in exercises) + direct_calories
        
        total_calories = macros["cal"] + additional_cal
        total_protein = macros["protein"]
        
        miles, step_calories = steps_to_miles_calories(steps)
        total_calories_burned = step_calories + exercise_cal
        net_calories = total_calories - total_calories_burned
        
        bmi = calculate_bmi(weight, 181.0)  # Use fixed height
        
        # Update entry
        entry.update({
            "food": food_inputs,
            "additional_meals": additional_meals,
            "exercises": exercises,
            "weight": weight,
            "height": 181.0,  # Fixed height
            "age": 24,        # Fixed age
            "steps": steps,
            "workout_notes": workout_notes,
            "direct_calories": direct_calories,
            "is_gym_day": is_gym_day,
            "bmi": bmi,
            "total_calories": round(total_calories, 1),
            "total_protein": round(total_protein, 1),
            "total_calories_burned": round(total_calories_burned, 1),
            "net_calories": round(net_calories, 1),
            "miles_walked": miles,
            "date": selected_date_str
        })
        
        data[selected_date_str] = entry
        save_data(data)
        
        st.markdown('<div class="success-box">✅ Entry saved successfully!</div>', unsafe_allow_html=True)
        
        # Show summary after saving
        st.markdown("### 📊 Saved Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Calories", f"{total_calories:.0f}", "kcal")
        with col2:
            st.metric("Total Protein", f"{total_protein:.1f}", "g")
        with col3:
            st.metric("Net Calories", f"{net_calories:.0f}", "after exercise")

# ----- PAGE: Analytics -----
elif page == "📊 Analytics":
    st.markdown("### 📊 Today's Analytics")
    
    if entry.get("total_calories"):
        # Current Progress
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 🎯 Daily Goals Progress")
            
            # Get current goals
            is_gym_day = entry.get("is_gym_day", True)
            DAILY_GOALS = get_daily_goals(is_gym_day)
            
            # Progress bars
            cal_progress = create_progress_bar(
                entry.get("total_calories", 0), 
                DAILY_GOALS["calories"]["optimal"], 
                "Calories", 
                "#e74c3c"
            )
            st.markdown(cal_progress, unsafe_allow_html=True)
            
            protein_progress = create_progress_bar(
                entry.get("total_protein", 0), 
                DAILY_GOALS["protein"]["optimal"], 
                "Protein (g)", 
                "#2ecc71"
            )
            st.markdown(protein_progress, unsafe_allow_html=True)
            
            steps_progress = create_progress_bar(
                entry.get("steps", 0), 
                DAILY_GOALS["steps"]["optimal"], 
                "Steps", 
                "#f39c12"
            )
            st.markdown(steps_progress, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📋 Quick Stats")
            
            # BMI Analysis
            bmi = entry.get("bmi")
            if bmi:
                bmi_cat, bmi_color = get_bmi_category(bmi)
                st.markdown(create_metric_card("BMI", f"{bmi}", bmi_cat, "⚖️", bmi_color), unsafe_allow_html=True)
            
            # Net Calories
            net_cal = entry.get("net_calories", 0)
            net_color = "#2ecc71" if net_cal > 0 else "#e74c3c"
            st.markdown(create_metric_card("Net Calories", f"{net_cal:.0f}", "kcal", "⚡", net_color), unsafe_allow_html=True)

        # Daily Goals Achievement
        if entry.get("total_calories", 0) > 0:
            st.markdown("#### 🥘 Daily Goals Achievement")
            
            # Check if all goals are met
            goals_met = 0
            total_goals = 3
            
            cal_achieved = entry.get("total_calories", 0) >= DAILY_GOALS["calories"]["optimal"] * 0.9
            protein_achieved = entry.get("total_protein", 0) >= DAILY_GOALS["protein"]["optimal"] * 0.9
            steps_achieved = entry.get("steps", 0) >= DAILY_GOALS["steps"]["optimal"] * 0.9
            
            if cal_achieved: goals_met += 1
            if protein_achieved: goals_met += 1
            if steps_achieved: goals_met += 1
            
            if goals_met == total_goals:
                st.markdown("""
                <div style="background: linear-gradient(90deg, #2ecc71 0%, #27ae60 100%); 
                           padding: 20px; border-radius: 10px; text-align: center; 
                           color: white; margin: 20px 0;">
                    <h2>🎉 DAILY GOALS ACHIEVED! 🎉</h2>
                    <p>Congratulations! You've met all your daily targets!</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background: linear-gradient(90deg, #f39c12 0%, #e67e22 100%); 
                           padding: 15px; border-radius: 10px; text-align: center; 
                           color: white; margin: 20px 0;">
                    <h3>📊 Daily Progress: {goals_met}/{total_goals} Goals Met</h3>
                    <p>Keep going! You're making great progress!</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Exercise Summary
        if entry.get("exercises"):
            st.markdown("#### 🏋️‍♂️ Exercise Summary")
            exercise_df = pd.DataFrame(entry["exercises"])
            st.dataframe(exercise_df[["type", "intensity", "calories"]], use_container_width=True)
            
    else:
        st.info("📝 No data available for today. Please enter your daily data first!")

# ----- PAGE: Progress -----
elif page == "📈 Progress":
    st.markdown("### 📈 Progress Tracking")
    
    if len(data) < 2:
        st.info("📊 Need at least 2 days of data to show progress trends.")
    else:
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            days_back = st.selectbox("Time Period", [7, 14, 30, 60, 90], index=0)
        with col2:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
        
        # Filter data
        filtered_data = {
            k: v for k, v in data.items() 
            if start_date.strftime("%Y-%m-%d") <= k <= end_date.strftime("%Y-%m-%d")
        }
        
        if filtered_data:
            # Weight Progress
            weight_fig = plot_enhanced_trends(filtered_data, "weight", "Weight Progress (kg)", "Weight (kg)", "#e74c3c")
            st.plotly_chart(weight_fig, use_container_width=True)
            
            # Calories Trend
            cal_fig = plot_enhanced_trends(filtered_data, "total_calories", "Calorie Intake Trend", "Calories", "#f39c12")
            st.plotly_chart(cal_fig, use_container_width=True)
            
            # Protein Trend
            protein_fig = plot_enhanced_trends(filtered_data, "total_protein", "Protein Intake Trend", "Protein (g)", "#2ecc71")
            st.plotly_chart(protein_fig, use_container_width=True)
            
            # Steps Trend
            steps_fig = plot_enhanced_trends(filtered_data, "steps", "Daily Steps Trend", "Steps", "#3498db")
            st.plotly_chart(steps_fig, use_container_width=True)

# ----- PAGE: History -----
elif page == "📋 History":
    st.markdown("### 📋 Historical Data")
    
    if not data:
        st.info("📝 No historical data available yet.")
    else:
        # Date selector
        dates_sorted = sorted(data.keys(), reverse=True)
        selected_history_date = st.selectbox("Select Date", dates_sorted, index=0)
        
        if selected_history_date:
            hist_entry = data[selected_history_date]
            
            # Display historical data in organized format
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📊 Metrics")
                metrics_df = pd.DataFrame({
                    "Metric": ["Weight", "BMI", "Calories", "Protein", "Steps"],
                    "Value": [
                        f"{hist_entry.get('weight', 'N/A')} kg",
                        hist_entry.get('bmi', 'N/A'),
                        f"{hist_entry.get('total_calories', 0):.0f} kcal",
                        f"{hist_entry.get('total_protein', 0):.1f} g",
                        f"{hist_entry.get('steps', 0):,}",
                    ]
                })
                st.dataframe(metrics_df, use_container_width=True)
            
            with col2:
                st.markdown("#### 🍽️ Food Intake")
                food_data = hist_entry.get("food", {})
                if food_data:
                    food_df = pd.DataFrame(list(food_data.items()), columns=["Food", "Quantity"])
                    food_df = food_df[food_df["Quantity"] > 0]  # Only show consumed foods
                    st.dataframe(food_df, use_container_width=True)
                else:
                    st.info("No food data recorded")
            
            # Exercise data
            if hist_entry.get("exercises"):
                st.markdown("#### 🏋️‍♂️ Exercise Data")
                exercise_df = pd.DataFrame(hist_entry["exercises"])
                st.dataframe(exercise_df, use_container_width=True)
            
            # Notes
            if hist_entry.get("workout_notes"):
                st.markdown("#### 📝 Notes")
                st.text_area("Workout Notes", hist_entry["workout_notes"], disabled=True)

# ----- PAGE: Reports -----
elif page == "📄 Reports":
    st.markdown("### 📄 Reports & Export")
    
    if len(data) == 0:
        st.info("📊 No data available to generate reports.")
    else:
        report_type = st.selectbox("Report Type", ["Weekly Summary", "Monthly Overview", "Custom Range"])
        
        if report_type == "Weekly Summary":
            # Last 7 days report logic (existing functionality enhanced)
            pass
        
        # Add download buttons for different formats
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 Download Excel Report"):
                # Create Excel export functionality
                pass
        with col2:
            if st.button("📄 Download PDF Report"):
                # Enhanced PDF report
                pass
        with col3:
            if st.button("📈 Download CSV Data"):
                # CSV export functionality
                pass

# ----- PAGE: Settings -----
elif page == "⚙️ Settings":
    st.markdown("### ⚙️ Settings & Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Goals Configuration")
        # Get current goals
        is_gym_day = st.toggle("🏋️ Gym Day Goals", value=True)
        current_goals = get_daily_goals(is_gym_day)
        
        new_cal_goal = st.number_input("Daily Calorie Goal", min_value=1000, max_value=5000, value=current_goals["calories"]["optimal"])
        new_protein_goal = st.number_input("Daily Protein Goal (g)", min_value=50, max_value=300, value=current_goals["protein"]["optimal"])
        new_steps_goal = st.number_input("Daily Steps Goal", min_value=5000, max_value=25000, value=current_goals["steps"]["optimal"])
    
    with col2:
        st.markdown("#### 🔐 Security")
        if st.button("🔑 Change Passcode"):
            st.info("Feature coming soon!")
        
        st.markdown("#### 📱 Data Management")
        if st.button("📤 Export All Data"):
            st.info("Feature coming soon!")
        
        if st.button("🗑️ Clear All Data", type="secondary"):
            st.info("Feature coming soon!")

# Logout button
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state.authenticated = False
    st.rerun()