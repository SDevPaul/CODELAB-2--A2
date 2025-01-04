import tkinter as tk
from PIL import Image, ImageTk
import requests
import io
from tkinter.scrolledtext import ScrolledText


class MealRecipeFinder:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1000x600')
        self.root.title('Meal Recipe Finder')
        self.root.resizable(False, False)
        self.root.iconbitmap('mealIcon.ico')

        # GUI Variables
        self.navbar_bg_color = '#D1602C'

        # Load background image
        self.background_image = Image.open("background.png")
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Initialize navigation bar
        self.initialize_navigation_bar()

        # Initialize main window frame
        self.main_window = tk.Frame(self.root, bg='orange')
        self.main_window.pack(side=tk.LEFT)
        self.main_window.pack_propagate(False)
        self.main_window.config(width=820, height=600)

        # Set start page
        self.set_start_page()

    # Navigation Bar Display
    def initialize_navigation_bar(self):
        self.navbar = tk.Frame(self.root, bg=self.navbar_bg_color, highlightbackground='white', highlightthickness=2)

        self.search_indicator = tk.Label(self.navbar, text="", bg=self.navbar_bg_color)
        self.search_indicator.place(x=10, y=240, width=5, height=54)
        self.search_button = tk.Button(self.navbar, text="Search", font=("Roboto", 20), bg=self.navbar_bg_color,
                                       fg="white", bd=0, relief="flat",
                                       command=lambda: self.show_indicator(self.search_indicator,
                                                                           self.display_search_page))
        self.search_button.place(x=25, y=240)

        self.surprise_indicator = tk.Label(self.navbar, text="", bg=self.navbar_bg_color)
        self.surprise_indicator.place(x=10, y=300, width=5, height=54)
        self.surprise_button = tk.Button(self.navbar, text="Surprise", font=("Roboto", 20), bg=self.navbar_bg_color,
                                         fg="white", bd=0, relief="flat",
                                         command=lambda: self.show_indicator(self.surprise_indicator,
                                                                             self.display_surprise_page))
        self.surprise_button.place(x=25, y=300)

        self.navbar.pack(side=tk.LEFT)
        self.navbar.pack_propagate(False)
        self.navbar.config(width=180, height=600)

    def set_start_page(self):
        self.start_page_canvas = tk.Canvas(self.main_window, width=self.background_image.width,
                                           height=self.background_image.width)
        self.start_page_canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
        self.start_page_canvas.place(x=0, y=0)
        self.start_page_canvas.create_text(370, 120, text="Welcome to the Meal Recipe Finder!", fill="white",
                                           font=("Arial", 27, "bold"))
        self.start_page_canvas.create_text(380, 270, text="This is where you can find meals with recipe\n\n"
                                                          "The Search button lets you search for the meals\n\n"
                                                          "the Surprise button gives you a random meal recipe!",
                                           fill="white", font=("Arial", 20, "bold"))

    def hide_all_indicators(self):
        self.search_indicator.config(bg=self.navbar_bg_color)
        self.surprise_indicator.config(bg=self.navbar_bg_color)

        for frame in self.main_window.winfo_children():
            frame.destroy()

    def show_indicator(self, selected_indicator, page_function):
        self.hide_all_indicators()
        selected_indicator.config(bg='white')
        page_function()

    def extract_ingredients_list(self, meal_data, ingredients_display_widget):
        def extract_ingredients():
            meal = meal_data["meals"][0]
            ingredients = []
            for i in range(1, 21):
                ingredient_name = meal.get(f"strIngredient{i}")
                measurement = meal.get(f"strMeasure{i}")
                if ingredient_name and ingredient_name.strip():
                    ingredients.append(f"{measurement} {ingredient_name}".strip())
            return ingredients

        ingredients = extract_ingredients()
        total_ingredients_text = f"TOTAL: {len(ingredients)} Ingredients\n"
        ingredients_display_widget.config(state=tk.NORMAL)
        ingredients_display_widget.insert(tk.END, total_ingredients_text)
        for ingredient in ingredients:
            ingredients_display_widget.insert(tk.END, f"• {ingredient}\n")
        ingredients_display_widget.config(state=tk.DISABLED)

    def display_recipe_instructions(self, instructions_display_widget, meal_data):
        instructions = meal_data['meals'][0]['strInstructions']
        instructions_display_widget.config(state=tk.NORMAL)
        instructions_display_widget.delete(1.0, tk.END)
        instructions_display_widget.insert(tk.END, instructions)
        instructions_display_widget.config(state=tk.DISABLED)

    def fetch_data_from_api(self, api_url):
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None

    def fetch_and_display_meal_image(self, meal_data, parent_frame):
        try:
            image_url = meal_data['meals'][0]['strMealThumb']
            response = requests.get(image_url)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
            image = image.resize((210, 210))
            image = ImageTk.PhotoImage(image)
            image_label = tk.Label(parent_frame, image=image)
            image_label.image = image
            image_label.place(x=580, y=120)
        except Exception:
            pass

    def setup_background(self, parent_frame, title_text):
        self.background_canvas = tk.Canvas(parent_frame, width=self.background_image.width,
                                           height=self.background_image.height)
        self.background_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_canvas.create_image(0, 0, image=self.background_photo, anchor="nw")
        self.background_canvas.create_text(50, 50, text=title_text, fill='white', font=("Arial", 27, "bold"), width=780,
                                           anchor='nw')

    def display_recipe_details(self, meal_data, parent_frame):
        meal_name = meal_data['meals'][0]['strMeal']
        self.setup_background(parent_frame, meal_name)
        self.background_canvas.create_text(50, 150, text=f"Ingredients", fill='white', font=("Arial", 22, "bold"),
                                           anchor='w')
        self.background_canvas.create_text(50, 350, text="Instructions", fill='white', font=("Arial", 22, "bold"),
                                           anchor='w')
        self.fetch_and_display_meal_image(meal_data, parent_frame)

        ingredients_display_widget = ScrolledText(parent_frame, wrap=tk.WORD, width=30, height=10, font=("Arial", 9),
                                                  padx=10)
        ingredients_display_widget.place(x=50, y=250, anchor='w')
        ingredients_display_widget.config(state=tk.DISABLED)
        self.extract_ingredients_list(meal_data, ingredients_display_widget)

        instructions_display_widget = ScrolledText(parent_frame, wrap=tk.WORD, width=103, height=12, font=("Arial", 9),
                                                   padx=5)
        instructions_display_widget.place(x=50, y=380, anchor='nw')
        instructions_display_widget.config(state=tk.DISABLED)
        self.display_recipe_instructions(instructions_display_widget, meal_data)

    def display_search_page(self):
        def update_results_listbox(data):
            results_listbox.delete(0, tk.END)
            for item in data:
                results_listbox.insert(tk.END, item)

        def fetch_and_display_selected_meal():
            search_query = search_box.get()
            if search_query == '':
                results_listbox.delete(0, tk.END)
                results_listbox.insert(tk.END, 'No Item Searched. Please start typing!')
            else:
                formatted_query = search_query.strip().replace(" ", "_")
                api_url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={formatted_query}"
                meal_data = self.fetch_data_from_api(api_url)
                if meal_data:
                    self.display_recipe_details(meal_data, search_frame)

        def autofill_search_box(event):
            search_box.delete(0, tk.END)
            search_box.insert(0, results_listbox.get(tk.ANCHOR))

        def filter_results(event):
            typed_text = search_box.get()
            if typed_text == '':
                available_meals.clear()
                filtered_data = available_meals
            else:
                if not available_meals:
                    filtered_data = []
                    api_url = f"https://www.themealdb.com/api/json/v1/1/search.php?f={typed_text}"
                    fetched_meals = self.fetch_data_from_api(api_url)
                    if fetched_meals:
                        for item in fetched_meals['meals']:
                            filtered_data.append(item["strMeal"])
                            available_meals.append(item['strMeal'])
                else:
                    filtered_data = [item for item in available_meals if typed_text.lower() in item.lower()]

            update_results_listbox(filtered_data)

        search_frame = tk.Frame(self.main_window)
        search_frame.pack(fill="both", expand=True)
        self.setup_background(search_frame, 'Search')
        self.background_canvas.create_text(50, 170, text=f"Results", fill='white', font=("Arial", 22, "bold"),
                                           anchor='w')

        search_box = tk.Entry(search_frame, font=("Arial", 18), width=30, bd=0)
        search_box.place(x=50, y=100, anchor='nw')
        confirm_button = tk.Button(search_frame, text='Confirm', font=("Arial", 11), width=8,
                                   command=fetch_and_display_selected_meal)
        confirm_button.place(x=450, y=100, anchor='nw')

        results_listbox = tk.Listbox(search_frame, width=63, height=10, font=("Arial", 14))
        results_listbox.place(x=50, y=195, anchor='nw')
        available_meals = []
        results_listbox.bind("<<ListboxSelect>>", autofill_search_box)
        search_box.bind("<KeyRelease>", filter_results)

    def display_surprise_page(self):
        surprise_frame = tk.Frame(self.main_window)
        surprise_frame.pack(fill="both", expand=True)
        meal_data = self.fetch_data_from_api(f"https://www.themealdb.com/api/json/v1/1/random.php")
        if meal_data:
            self.display_recipe_details(meal_data, surprise_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = MealRecipeFinder(root)
    root.mainloop()
