import streamlit as st
import pandas as pd
from pathlib import Path
from src.consultants.recipe_consultant import RecipeConsultant
from data.raw_data.raw_products import products_row
import random
import re

from dataclasses import dataclass

n_cards_per_row = 3
smart_consultant = RecipeConsultant()
initial_massage = [{"role": "assistant", "content": "Здравствуйте! Меня зовут Мария, я консультант по приготовлению еды в магазине Ашан. Какие пожелания у вас в еде? Что вы предпочитаете?"}]

st.sidebar.title("Попроси помощи с покупками у персонального ассистента")

chat_container = st.sidebar.container()


@st.cache_data
def read_csv(path):
    df = pd.read_csv(path, index_col=0)

    return df

recipe_db = read_csv(Path("data/raw_data/recepies.csv"))

@dataclass
class Product:
    name: str
    photo_link: str

    def render(self, add_button="add"):
        st.write(self.name)
        st.image(self.photo_link)
        if add_button == "add":
            st.button("Добавить в корзину", on_click=add_to_backet, args=(self, True), key=self.name+"_add_button")
        if add_button == "delete":
            st.button("Удалить из корзины", on_click=delete_from_backet, args=(self, True), key=self.name+"_delete_button")

all_products = [Product(name, link) for name, link in products_row]


def delete_from_backet(product, is_update_advice=False):
    st.session_state["basket"].remove(product)
    if is_update_advice:
        update_advice()

def add_to_backet(product, is_update_advice=False):
    if product.name not in [i.name for i in st.session_state["basket"]]:
        st.session_state["basket"].append(product)
        if is_update_advice:
            update_advice()

def update_advice():

    try: 
        ingridients, recipe_name, recipe = find_recipe(st.session_state["basket"])

        message = f"Вы добавили {', '.join([i.name for i in st.session_state['basket']])} в корзину. \n \
                    Приготовь из этого {recipe_name}! \n"
        
        link = "https://i.artfile.ru/2880x1800_954014_[www.ArtFile.ru].jpg" # Заглушка
    except:
        message = "У нас не получилось придумать рецепт, простите 😞. \n\n Мы чиним"

        ingridients, recipe = "", ""
        
        link = "https://i.yapx.cc/VakAF.gif"

    st.session_state["advice"] = (message, ingridients, recipe, link)

def show_recipe(recipe, ingridients):

    st.chat_message("assistant").write(re.sub(r"\d[.] ", "\n {}) ", recipe).format(*range(1, 100)))

    ask_to_add_to_basket(ingridients, False)


def find_recipe(products: list):
  
    products = [i.name.lower().replace(" ", "_") for i in products]

    data = recipe_db

    spice_df = pd.DataFrame(dict((spice, data.composition.str.contains(spice, re.IGNORECASE)) for spice in products))
    selection = spice_df.query('|'.join(products))
    index_selection = random.choice(selection.index)
    name = data.name[index_selection]
    recipe = data.Инструкции[index_selection]
    compositions = data.composition[index_selection]
    link = data.source[index_selection]

    return eval(compositions), name, recipe



def add_message(role: str, content: str) -> None:
    st.session_state["messages"].append({"role": role, "content": content})

def display_chat(chat: list):

    for msg in chat:
        st.chat_message(msg["role"]).write(msg["content"])
    
    if "ask_chat_bot" in st.session_state:
        if st.session_state["ask_chat_bot"]:
            with st.spinner("Ассистент думает"):
                answer = smart_consultant.get_answer(initial_massage + st.session_state["messages"])
            add_message(role = "assistant", content = answer)
            st.chat_message("assistant").write(answer)

            with st.spinner("Ассистент думает"):
                ingridients = smart_consultant.find_ingridients(answer) 

            ask_to_add_to_basket(ingridients.split(", "))                    


            st.session_state["ask_chat_bot"] = False


def ask_to_add_to_basket(ingridients: list, is_add_message=True):
    
    ingridients_to_advice = []

    for product in all_products:
        for i in ingridients:
            if product.name.lower() == i.lower() and product.name.lower() not in [i.name.lower() for i in st.session_state["basket"]]:
                ingridients_to_advice.append(product)

    advice = ("Для приготовления вам нужно добавить в корзину: \n\n" + 
              "\n\n".join([f" ✅ {i.name}" for i in ingridients_to_advice]) + " \n\n " + 
              "Добавить в корзину?")
    
    st.chat_message("assistant").write(advice)
    if is_add_message:
        add_message("assistant", advice)

    make_design(ingridients_to_advice)    
    

def make_design(ingridients_to_advice):
    col1, col2 = st.columns(2)
    
    col1.button("Да", on_click=add_to_backet_list, args=(ingridients_to_advice, ))
    col2.button("Нет")

def add_to_backet_list(products):
    for p in products:
        add_to_backet(p, is_update_advice=True)


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if "basket" not in st.session_state:
        st.session_state["basket"] = []

def update_chat():
    if "chat_input" in st.session_state:
        if st.session_state["chat_input"]:
            add_message(role = "user", content = st.session_state["chat_input"])
            st.session_state["ask_chat_bot"] = True
            
        st.session_state["chat_input"] = ""

def display_sidebar():
    with st.sidebar:

        st.text_input("Ответ", label_visibility='hidden', placeholder="Посоветуй что-нибудь на ужин", key="chat_input")

        if st.button("Очистить чат"):
            st.session_state["messages"] = []

        with chat_container:
            display_chat(st.session_state["messages"][-10:])

def display_basket():
    with st.expander("Корзина"):
        st.title("Ваша корзина")

        display_products(st.session_state["basket"], add_button="delete")

def display_advices():
    with st.expander("Советы по корзине", expanded=True):
        st.title("Советы на основе вашей корзины")

        if "advice" in st.session_state:

            message, ingridients, recipe, link = st.session_state["advice"]

            st.chat_message("assistant").write(message)

            st.image(link)

            if recipe:

                st.chat_message("assistant").write("Показать рецепт?")

                col1, col2 = st.columns(2)

                if col1.button("Да", key="67890"):
                    show_recipe(recipe, ingridients)
                col2.button("Нет", key="7890987")
        else:
            st.chat_message("assistant").write("Добавте продукты, чтобы получить советы")


def display_market():
    st.title("Товары")

    text_to_search = st.text_input('Введите название товара')

    if text_to_search:
        products_to_show = [i for i in all_products if text_to_search.lower() in i.name.lower()]
    else:
        products_to_show = all_products

    display_products(products_to_show, add_button="add")


def display_products(products: list, add_button = "add"):
    

    for i, product in enumerate(products):

        n_col = i%n_cards_per_row

        if n_col == 0:
            st.write("---")
            cols = st.columns(n_cards_per_row)

        with cols[n_col]:
            product.render(add_button=add_button)



if __name__ == "__main__":
    init_session_state()

    update_chat()

    display_sidebar()

    display_basket()

    display_advices()

    display_market()
