import json
import subprocess
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import asyncio
from pyrogram import filters
from pyrogram import filters, types
from pyrogram.errors.exceptions import ChannelInvalid
import datetime
import asyncpg
import pyrogram
from pyrogram import enums
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pyrogram import Client, filters
from pyrogram.types import Message
import psycopg2
import requests
import random 
from pyrogram.types import (InlineQueryResultArticle, InputTextMessageContent,
                            InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultPhoto)


api_id = 23780487
api_hash = "8e756a529aa577d1ae33859476ca4bf5"
bot_token = "7086463608:AAGa6jm-8vsrh2SI9x2bv2kzMlhChdNPHik"
allowed_user_id = 283212689

app = Client(
    "infor_bot",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)
def get_info(conn_project, cursor_project, user_id, column):
    try:
        # Перевіряємо, чи користувач user_id існує в базі даних
        if check_user(conn_project, cursor_project, user_id):
            # Виконуємо SQL-запит для отримання значення певного стовпця для користувача user_id
            cursor_project.execute(f"SELECT {column} FROM id_project WHERE id = %s", (user_id,))
            result = cursor_project.fetchone()
            if result:
                return result[0]  # Повертаємо значення з вибраного стовпця
            else:
                print(f"User with ID {user_id} not found.")
                return None
        else:
            print(f"User with ID {user_id} does not have permission to access information.")
            return None
    except Exception as e:
        print("Error getting user info:", e)
        return None
def get_country_info(country_name):
    url = f"https://restcountries.com/v3.1/name/{country_name}"
    response = requests.get(url)
    data = response.json()
    if data:
        country = data[0]
        # Отримання необхідної інформації про країну
        name = country.get("name", {}).get("common", "N/A")
        capital = country.get("capital", ["N/A"])[0]
        currency = list(country.get("currencies", {}).values())[0].get("name", "N/A")
        population = country.get("population", "N/A")
        flag_url = country.get("flags", {}).get("png", "N/A")
        # Створення тексту відповіді
        text = (
            f"Name: {name}\n"
            f"Capital: {capital}\n"
            f"Currency: {currency}\n"
            f"Population: {population}\n"
        )
        return text, flag_url
    else:
        return "Country not found", None
def delete_user(conn_project, cursor_project, user_id, delete_id):
    try:
        # Перевіряємо, чи користувач user_id існує в базі даних
        if user_id == allowed_user_id:
            # Виконуємо SQL-запит для видалення запису з таблиці id_project
            cursor_project.execute("DELETE FROM id_project WHERE id = %s", (delete_id,))
            # Зберігаємо зміни
            conn_project.commit()
            ans = f"User with ID {delete_id} deleted successfully."
            return ans
        else:
            print(f"User with ID {user_id} does not have permission to delete user with ID {delete_id}.")
    except Exception as e:
        print("Error deleting user:", e)

def add_user(conn_project, cursor_project, user_id):
    try:
        # Виконуємо SQL-запит для вставки користувача в базу даних з значеннями 0 для стовпців index і points
        cursor_project.execute("INSERT INTO id_project (id, index, points) VALUES (%s, 0, 0)", (user_id,))
        # Зберігаємо зміни
        conn_project.commit()
        print(f"User with ID {user_id} added successfully.")
    except Exception as e:
        print("Error adding user:", e)


def check_user(conn_project, cursor_project, user_id):
    try:
        # Виконуємо SQL-запит для перевірки наявності користувача в базі даних
        cursor_project.execute("SELECT * FROM id_project WHERE id = %s", (user_id,))
        # Перевіряємо, чи є результат запиту
        if cursor_project.fetchone():
            return True  # Користувач знайдений
        else:
            return False  # Користувача немає в базі
    except Exception as e:
        print("Error checking user:", e)

def change_info(conn_project, cursor_project, user_id, column, new_value):
    try:
        # Виконуємо SQL-запит для зміни інформації користувача
        cursor_project.execute(f"UPDATE id_project SET {column} = %s WHERE id = %s", (new_value, user_id))
        # Зберігаємо зміни
        conn_project.commit()
        print(f"User with ID {user_id} {column} changed to {new_value} successfully.")
    except Exception as e:
        print("Error changing user info:", e)
conn_project = psycopg2.connect(database="fyd", user="postgres", password="your_password", host="localhost", port="5432")
cursor_project = conn_project.cursor() 
@app.on_message(filters.command("start"))
def start_command(client, message):
    response = requests.get("https://restcountries.com/v3.1/all")
    countries_data = response.json()
    user_id = message.chat.id
    if check_user(conn_project, cursor_project, user_id) == False:
     add_user(conn_project, cursor_project, user_id)
     current_page = 0
     countries_per_page = 5
    else:
     current_page = get_info(conn_project, cursor_project, user_id, "index")
     countries_per_page = 5
    while True:
         start_index = current_page * countries_per_page
         end_index = min((current_page + 1) * countries_per_page, len(countries_data))
        
         reply_markup = InlineKeyboardMarkup([])
         for i in range(start_index, end_index):
            country = countries_data[i]
            country_button = InlineKeyboardButton(
                text=country["name"]["common"],
                callback_data=f"country_{i}"
            )
            reply_markup.inline_keyboard.append([country_button])
        
         if current_page > 0:
            previous_button = InlineKeyboardButton(
                text="⬅️ Previous",
                callback_data="previous"
            )
            reply_markup.inline_keyboard.append([previous_button])
        
         if end_index < len(countries_data):
            next_button = InlineKeyboardButton(
                text="➡️ Next",
                callback_data="next"
            )
            reply_markup.inline_keyboard.append([next_button])
        
         client.send_message(
            chat_id=message.chat.id,
            text="Please select a country:",
            reply_markup=reply_markup
         )
         break


@app.on_callback_query()
def callback_query_handler(client, query):
    data = query.data
    user_id = query.message.chat.id
    
    if data == "previous":
     current_page = get_info(conn_project, cursor_project, user_id, "index")
     current_page -= 1  # Зменшуємо поточну сторінку на 1
     change_info(conn_project, cursor_project, user_id, "index", current_page)  # Оновлюємо значення сторінки в базі даних

     response = requests.get("https://restcountries.com/v3.1/all")
     countries_data = response.json()
     start_index = current_page * 5
     end_index = min((current_page + 1) * 5, len(countries_data))
 
     reply_markup = InlineKeyboardMarkup([])
     for i in range(start_index, end_index):
        country = countries_data[i]
        country_button = InlineKeyboardButton(
            text=country["name"]["common"],
            callback_data=f"country_{i}"
        )
        reply_markup.inline_keyboard.append([country_button])

     if current_page > 0:
        previous_button = InlineKeyboardButton(
            text="⬅️ Previous",
            callback_data="previous"
        )
        reply_markup.inline_keyboard.append([previous_button])

     if end_index < len(countries_data):
        next_button = InlineKeyboardButton(
            text="➡️ Next",
            callback_data="next"
        )
        reply_markup.inline_keyboard.append([next_button])

     query.message.edit_text(
        text="Please select a country:",
        reply_markup=reply_markup
    )


    elif data == "next":
        current_page = get_info(conn_project, cursor_project, user_id, "index")
        current_page += 1  # Збільшуємо поточну сторінку на 1
        change_info(conn_project, cursor_project, user_id, "index", current_page)  # Оновлюємо значення сторінки в базі даних

        response = requests.get("https://restcountries.com/v3.1/all")
        countries_data = response.json()
        start_index = current_page * 5
        end_index = min((current_page + 1) * 5, len(countries_data))
        
        reply_markup = InlineKeyboardMarkup([])
        for i in range(start_index, end_index):
            country = countries_data[i]
            country_button = InlineKeyboardButton(
                text=country["name"]["common"],
                callback_data=f"country_{i}"
            )
            reply_markup.inline_keyboard.append([country_button])

        if current_page > 0:
            previous_button = InlineKeyboardButton(
                text="⬅️ Previous",
                callback_data="previous"
            )
            reply_markup.inline_keyboard.append([previous_button])

        if end_index < len(countries_data):
            next_button = InlineKeyboardButton(
                text="➡️ Next",
                callback_data="next"
            )
            reply_markup.inline_keyboard.append([next_button])

        query.message.edit_text(
            text="Please select a country:",
            reply_markup=reply_markup
        )
    elif data.startswith("country_"):
        index = int(data.split("_")[1])
        response = requests.get("https://restcountries.com/v3.1/all")
        countries_data = response.json()
        country = countries_data[index]
        
        country_name = country["name"]["common"] if "name" in country else "N/A"
        currency = list(country["currencies"].values())[0]["name"] if "currencies" in country else "N/A"
        languages = country["languages"] if "languages" in country else {}
        language = next(iter(languages.values())) if languages else "N/A"
        population = country["population"] if "population" in country else "N/A"
        flag_url = country["flags"]["png"] if "flags" in country and "png" in country["flags"] else "N/A"
        capital = country["capital"][0] if "capital" in country and country["capital"] else "N/A"
        google_maps_url = country["maps"]["googleMaps"] if "maps" in country and "googleMaps" in country["maps"] else "N/A"


        text = (
            f"Country: {country_name}\n"
            f"Currency: {currency}\n"
            f"Language: {language}\n"
            f"Population: {population}\n"
            f"Capital city: {capital}\n"
        )
        client.send_photo(
            chat_id=query.message.chat.id,
            photo=flag_url,
            caption=text,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Open in Google Maps", url=google_maps_url)]]
            )
        )
@app.on_message(filters.command("delete"))
def delete_command(client, message):
    # Перевіряємо, чи коректно вказано параметр команди
    if len(message.command) != 2:
        message.reply_text("Usage: /delete <user_id>")
        return
    
    user_id_to_delete = message.command[1]
    current_user_id = message.chat.id
    
    if current_user_id == allowed_user_id:
        delete_result = delete_user(conn_project, cursor_project, current_user_id, user_id_to_delete)
        if delete_result:
            message.reply_text(delete_result)
        else:
            message.reply_text(f"Error deleting user with ID {user_id_to_delete}.")
    else:
        message.reply_text("You do not have permission to delete users.")
def reset_points(user_id):
    try:
        cursor_project.execute("UPDATE id_project SET points = 0 WHERE id = %s", (user_id,))
        conn_project.commit()
        print(f"Points reset for user with ID {user_id}.")
    except Exception as e:
        print("Error resetting points:", e)

# Функція для створення питання та варіантів відповідей
def get_random_country():
    response = requests.get("https://restcountries.com/v3.1/all")
    countries_data = response.json()
    return random.choice(countries_data)

def quiz_message():
    country = get_random_country()
    country_name = list(country["name"].values())[0]
    capital = country.get("capital", ["N/A"])[0]
    currency = list(country["currencies"].values())[0]["name"]
    language = list(country["languages"].values())[0]
    
    question = f"Country: {country_name}\n\nQuiz:\n1. What is the capital of this country?\n2. What is the currency of this country?\n3. What language is spoken in this country?"
    return question, capital, currency, language

@app.on_message(filters.command("quiz"))
def quiz_command(client, message):
    response = requests.get("https://restcountries.com/v3.1/all")
    countries_data = response.json()
    random_country = random.choice(countries_data)
    country_name = random_country.get("name", {}).get("common", "N/A")
    capital = random_country.get("capital", ["N/A"])[0]
    currency = list(random_country.get("currencies", {}).values())[0].get("name", "N/A")
    languages = random_country.get("languages", {})
    language = next(iter(languages.values()), "N/A")

    question_text = f"Country: {country_name}\n\n1. What is the capital of this country? ||{capital}||\n2. What is the currency of this country? ||{currency}||\n3. What language is spoken in this country? ||{language}||"
    
    
    client.send_message(message.chat.id, text=question_text, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_inline_query()
async def answer(client, inline_query):
    country_name = inline_query.query.strip()  # Отримання запиту користувача
    if country_name:
        # Отримання інформації про країну
        text, flag_url = get_country_info(country_name)
        # Створення результату для відповіді на інлайн-запит
        result = [
            InlineQueryResultPhoto(
                title=country_name,
                photo_url=flag_url,
                description=country_name,
                caption = text 
            )
        ]
        await inline_query.answer(results=result, cache_time=0)
    else:
        # Якщо не вказано жодної країни, нічого не робити
        pass


# Запуск клієнта Pyrogram
@app.on_message(filters.command("help"))
async def help_command(client, message):
    # Текст довідки
    help_text = (
        "Цей бот допомагає отримувати інформацію про різні країни. Оскільки API, звідки взято країни не підтримує українську мову, весь бот крім цієї команди на англійській мові\n"
        "Доступні команди:\n"
        "/start - початок роботи з ботом\n"
        "/help - це довідкове повідомлення\n"
        "/quiz - вікторина з рандомної країни\n"
        "@CountriesFindBot назва країни - інформація про конкретну країну"
    )
    # Відправляємо довідкове повідомлення
    await message.reply_text(help_text)

# Запускаємо клієнт Pyrogram
app.run()

app.run()
