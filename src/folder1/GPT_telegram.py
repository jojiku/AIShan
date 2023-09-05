headers = {
   'Authorization': f'Bearer {api_key}',
   'Content-Type': 'application/json'
}

bot = telebot.TeleBot(TOKENTG)
@bot.message_handler(func = lambda _: True)

def handle_message(message):
    data = {
   'model': 'gpt-3.5-turbo',  # Specify the model you want to use
   'messages': [
       {'role': 'system', 'content': 'You are a helpful assistant.'},
       {'role': 'user', 'content': message.text}
   ]
    }
    response = requests.post(endpoint, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        bot.send_message(chat_id = message.from_user.id, text = result['choices'][0]['message']['content'])
    else:
        print(f"Error: {response.status_code}, {response.text}")
    

bot.polling()
