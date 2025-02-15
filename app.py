import requests
import streamlit as st

SPOONACULAR_API_KEY = "e625149e9e744f1b9e183b07e9465940"
SPOONACULAR_BASE_URL = "https://api.spoonacular.com/recipes/complexSearch"

class MealPlanner:
    def __init__(self):
        self.protein_sources = []
        self.healthy_fats = []
        self.fiber_rich_foods = []
        self.dietary_filters = []
        self.pantry_items = {}
        self.meal_plan = {}
        self.side_dishes = []

    def set_preferences(self, proteins, fats, fibers, filters, sides=[]):
        self.protein_sources = proteins
        self.healthy_fats = fats
        self.fiber_rich_foods = fibers
        self.dietary_filters = filters
        self.side_dishes = sides
    
    def add_pantry_item(self, item, quantity):
        self.pantry_items[item] = quantity

    def generate_meal_plan(self):
        meals = {"breakfast": [], "lunch": [], "dinner": []}
        for meal in meals.keys():
            meals[meal] = self.get_recipes(meal)
        self.meal_plan = meals
        return meals
    
    def get_recipes(self, meal_type):
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "type": meal_type,
            "includeIngredients": ",".join(self.protein_sources + self.healthy_fats + self.fiber_rich_foods),
            "diet": "".join(self.dietary_filters),
            "number": 5
        }
        response = requests.get(SPOONACULAR_BASE_URL, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []
    
    def get_side_dishes(self):
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "type": "side dish",
            "includeIngredients": ",".join(self.side_dishes),
            "number": 5
        }
        response = requests.get(SPOONACULAR_BASE_URL, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []
    
    def create_grocery_list(self):
        grocery_list = {}
        for meal, recipes in self.meal_plan.items():
            for recipe in recipes:
                ingredients = self.get_recipe_ingredients(recipe['id'])
                for item, qty in ingredients.items():
                    if item not in self.pantry_items:
                        grocery_list[item] = qty
        return grocery_list
    
    def get_recipe_ingredients(self, recipe_id):
        url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
        params = {"apiKey": SPOONACULAR_API_KEY}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            ingredients = response.json().get("extendedIngredients", [])
            return {ingredient['name']: ingredient['amount'] for ingredient in ingredients}
        return {}

# Streamlit UI
st.title("Meal Planner App")

protein_options = ["Chicken", "Beef", "Tofu", "Fish", "Eggs", "Lentils"]
fat_options = ["Avocado", "Olive Oil", "Nuts", "Seeds", "Cheese"]
fiber_options = ["Broccoli", "Oats", "Beans", "Chia Seeds", "Flaxseeds"]
dietary_options = ["Gluten-Free", "Vegan", "Keto", "Paleo"]
side_dish_options = ["Spinach", "Carrots", "Kale", "Cucumber", "Bell Peppers"]

selected_proteins = st.multiselect("Select protein sources:", protein_options)
selected_fats = st.multiselect("Select healthy fats:", fat_options)
selected_fibers = st.multiselect("Select fiber-rich foods:", fiber_options)
selected_filters = st.multiselect("Select dietary filters:", dietary_options)
selected_sides = st.multiselect("Select side dishes:", side_dish_options)

planner = MealPlanner()

if st.button("Generate Meal Plan"):
    planner.set_preferences(
        selected_proteins,
        selected_fats,
        selected_fibers,
        selected_filters,
        selected_sides
    )
    meal_plan = planner.generate_meal_plan()
    side_dishes = planner.get_side_dishes()
    grocery_list = planner.create_grocery_list()
    
    st.subheader("Meal Plan")
    st.write(meal_plan)
    
    st.subheader("Side Dishes")
    st.write(side_dishes)
    
    st.subheader("Grocery List")
    st.write(grocery_list)

st.subheader("Pantry")
pantry_item_input = st.text_input("Enter pantry item")
pantry_quantity_input = st.number_input("Quantity", min_value=1, value=1)

if st.button("Add Pantry Item"):
    planner.add_pantry_item(pantry_item_input, pantry_quantity_input)
    st.success(f"Added to pantry: {pantry_item_input} - {pantry_quantity_input}")
