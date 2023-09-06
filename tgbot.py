import asyncio
import logging
import config
from aiogram import Bot, Dispatcher, types
from aiogram.utils.markdown import text, bold
from aiogram.types import ParseMode
from aiogram.types.message import ContentType
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from pathlib import Path

import os
from langchain.document_loaders import TextLoader

# used to create the retriever
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# used to create the retriever
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# used to create the retrieval tool
from langchain.agents import tool

# used to create the memory
from langchain.memory import ConversationBufferMemory

# used to create the agent executor
from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor

# used to create the prompt template
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.schema import SystemMessage
from langchain.prompts import MessagesPlaceholder

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

# retriever part
os.environ["OPENAI_API_KEY"] = config.openai_api_key
# This is needed for both the memory and the prompt
memory_key = "history"
loader = TextLoader(Path("data/raw_data/faq.txt"), encoding='utf8')
data = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(data)
embeddings = OpenAIEmbeddings()
db = FAISS.from_documents(texts, embeddings)
retriever = db.as_retriever()
@tool
def tool(query):
    "Searches and returns documents regarding the llm powered autonomous agents blog"
    docs = retriever.get_relevant_documents(query)
    return docs

tools = [tool]
memory = ConversationBufferMemory(memory_key=memory_key, return_messages=True)
system_message = SystemMessage(
        content=(
            "Ты помощник Ашана. Старайся отвечать на все поставленные вопросы. "
            "Для этого в первую очередь используй предоставленные данные Ашана."
        )
)
prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=system_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)]
    )
llm = ChatOpenAI(temperature = 0)
agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True)


token = config.token
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
TEL_REGEXP = r'^\+79[\d]{9}$'

def make_keyboard(menu):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for menu_point in menu:
        keyboard.add(menu_point)
    return keyboard

class UserStates(StatesGroup):
    person = State()
    ask_tel = State()
    tel = State()
    name = State()
    ready = State()
    
@dp.message_handler(lambda message: message.text == "Вызов оператора", state=UserStates.person)
@dp.message_handler(lambda message: message.text == "Мои заказы", state=UserStates.person)
@dp.message_handler(lambda message: message.text == "Регистрация пластиковой карты", state=UserStates.person)
@dp.message_handler(lambda message: message.text == "Регистрация виртуальной карты", state=UserStates.person)
@dp.message_handler(lambda message: message.text == "Получить социальный статус", state=UserStates.person)
@dp.message_handler(lambda message: message.text == "У меня не получилось накопить", state=UserStates.person)
@dp.message_handler(lambda message: message.text == "У меня не получилось потратить", state=UserStates.person)
@dp.message_handler(lambda message: message.text == "Какой у меня баланс", state=UserStates.person)
async def cmd_init(message: types.Message, state: FSMContext):
    await state.set_state(UserStates.ask_tel.state)
    menu_list = ["Главное меню"]
    msg = text("Укажите, пожалуйста, свой номер телефона  в формате +79ХХХХХХХХХ.\n\
Отправляя номер телефона, вы даете согласие на обработку персональных данных.\n\
Подробнее: https://www.auchan.ru/privacy-policy/")
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(filters.Regexp(TEL_REGEXP), state=UserStates.ask_tel)
async def cmd_save_person(message: types.Message, state: FSMContext):
    await state.update_data(telephone=message.text.lower())
    await state.set_state(UserStates.tel.state)
    menu_list = ["Продолжить", "Не согласен"]
    msg = text("Продолжая диалог, вы соглашаетесь с правилами лояльности, а также даете согласие на получение информации об акциях и скидках: https://www.auchan.ru/pl/\n\
Если вам не нужна информация о ваших скидках, пожалуйста, отправьте нам текстовое сообщение \"Не согласен\"")
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(lambda message: message.text == "Продолжить", state=UserStates.tel)
@dp.message_handler(lambda message: message.text == "Не согласен", state=UserStates.tel)
async def cmd_ask_name(message: types.Message, state: FSMContext):
    msg = text("Как вас зовут?")
    await state.set_state(UserStates.name.state)
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(state=UserStates.name)
async def cmd_save_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    msg = text("Приятно познакомиться, ", message.text,"🤗")
    await state.set_state(UserStates.ready.state)
    menu_list = ["Карта АШАН", "Мои покупки", "Акции", "Поиск магазина", "Вызов оператора"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(commands=['start'], state='*')
@dp.message_handler(lambda message: message.text == "Главное меню", state='*')
async def cmd_main_menu(message: types.Message, state: FSMContext):
    if await state.get_state() != UserStates.ready.state:
        await state.set_state(UserStates.person.state)

    menu_list = ["Карта АШАН", "Мои покупки", "Акции", "Поиск магазина", "Вызов оператора"]
    msg = text("Для продолжения, пожалуйста, выберите категорию запроса, и я с удовольствием вам помогу 🤗")
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))



@dp.message_handler(lambda message: message.text == "Карта АШАН", state="*")
async def cmd_card(message: types.Message, state: FSMContext):
    msg = text('💳 Регистрируйте карту АШАН и получайте море преимуществ!\
Возвращаем баллами до 70% от стоимости товаров со специальными ценниками\n\
Оплачивайте до 100% стоимости покупки баллами! И всё по честному курсу: 1 балл = 1 рубль!\
Подробнее: https://www.auchan.ru/karta-auchan/\n\
Что вы хотите узнать? 😉', sep='\n')
    menu_list = ["Какой у меня баланс", "Действия с баллами", "Социальный статус", "Регистрация карты", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))



@dp.message_handler(lambda message: message.text == "Какой у меня баланс", state=UserStates.ready)
async def cmd_get_balance(message: types.Message, state: FSMContext):
    #ПОТЕНЦИАЛЬНО: обращение к бд
    msg = text('💳  Ваша карта активна. Сейчас на вашей карте: \n🟡 0 базовых баллов \n🔴 0 экспресс-баллов \n🎫 0 купонов', sep='\n')
    menu_list = ["Не согласен с суммой на балансе", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(lambda message: message.text == "Вызов оператора", state=UserStates.ready)
async def cmd_call_op(message: types.Message, state: FSMContext):
    #НУЖНО: обращение к оператору
    menu_list = ["Главное меню"]
    msg = text('Минуту, уже ищу свободного оператора. Пожалуйста, подождите')
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(lambda message: message.text == "Не согласен с суммой на балансе", state='*')
@dp.message_handler(lambda message: message.text == "У меня не получилось накопить", state='*')
@dp.message_handler(lambda message: message.text == "У меня не получилось потратить", state='*')
async def cmd_connect_op(message: types.Message, state: FSMContext):
    #НУЖНО: обращение к оператору
    menu_list = ["Главное меню"]
    msg = text('Мне потребуется подключить оператора. Он поможет решить вопрос')
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))
    




@dp.message_handler(lambda message: message.text == "Действия с баллами", state='*')
async def cmd_points(message: types.Message, state: FSMContext):
    msg = text('Пожалуйста, выберите вопрос, по которому вас проконсультировать:', sep='\n')
    menu_list = ["Как накопить баллы", "Как потратить баллы", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(lambda message: message.text == "Как накопить баллы", state='*')
async def cmd_gain_points(message: types.Message, state: FSMContext):
    msg = text('Получайте кешбэк баллами до 70% за покупку товаров со специальными ценниками.\
                Для накопления и списания баллов покажите карту на кассе перед оплатой покупки.\n\
                А еще дарим праздничный кешбэк 10% за неделю до и после Дня рождения.\n\
                Подробнее:  https://www.auchan.ru/personal-settings/loyalty/my-suggestions/darim-bally-na-den-rozhdeniya/', sep='\n')
    menu_list = ["У меня не получилось накопить", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(lambda message: message.text == "Как потратить баллы", state='*')
async def cmd_spend_points(message: types.Message, state: FSMContext):
    msg = text('Оплачивайте до 100% стоимости покупок баллами во всех магазинах АШАН.\n\
                Для списания баллов перед оплатой отсканируйте карту АШАН.\n\
                Обратите внимание, что списывать баллы можно только если карта зарегистрирована.\n\
                Баллы не списываются:\n\
                - На табак и табачную продукцию;\n\
                - На алкогольную продукцию;\n\
                - На покупку подарочных карт АШАН;\n\
                - На покупку карт лояльности АШАН.', sep='\n')
    menu_list = ["У меня не получилось потратить", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(lambda message: message.text == "Социальный статус", state='*')
async def cmd_ss(message: types.Message, state: FSMContext):
    msg = text('По будням с 7:00 до 12:00 начисляем дополнительный кешбэк 7% баллами клиентам с социальным статусом!\n\
                Как получать социальный кешбэк?\n\
                Зарегистрируйте карту АШАН\n\
                Получите социальный статус карты АШАН\n\
                Покажите карту сотруднику магазина перед оплатой покупки\n\
                Ознакомиться со списком категорий и документов можно здесь https://www.auchan.ru/karta-auchan/pravila-programmy/, пункт 4.2.1.', sep='\n')
    menu_list = ["Получить социальный статус", "Главное меню", "Вызов оператора"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(lambda message: message.text == "Получить социальный статус", state=UserStates.ready)
async def cmd_get_ss(message: types.Message, state: FSMContext):
    msg = text('Кому предоставляется?\n\
               Социальный статус предоставляется покупателям, относящимся к социальным категориям граждан. Информацию о льготах можно найти в Правилах Программы лояльности: https://www.auchan.ru/karta-auchan/pravila-programmy/?punkt=42\n\
                Как посмотреть, есть ли у меня социальный статус?\n\
                На сайте в личном кабинете по ссылке\
                https://www.auchan.ru/personal-settings/my-profile/\n\
                Как получить?\n\
                Для получения социального статуса необходимо отправить документ, подтверждающий право получения льготы.\
                Пришлите фото или скан-копию документа в ответ на это сообщение', sep='\n')
    menu_list = ["Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(lambda message: message.text == "Регистрация карты", state='*')
async def cmd_card_reg(message: types.Message, state: FSMContext):
    msg = text('Выберите тип карты', sep='\n')
    menu_list = ["Регистрация пластиковой карты", "Регистрация виртуальной карты", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(lambda message: message.text == "Регистрация пластиковой карты", state=UserStates.ready)
async def cmd_plastic_card_reg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = text(data['name'],', пожалуйста, напишите номер вашей карты АШАН', sep='\n')
    menu_list = ["Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(lambda message: message.text == "Регистрация виртуальной карты", state=UserStates.ready)
async def cmd_virt_card_reg(message: types.Message, state: FSMContext):

    data = await state.get_data()
    msg = text(data['name'],', для регистрации карты АШАН, пожалуйста, скачайте приложение Мой АШАН по ссылке: https://mobile.auchan.ru/newapp/ \
               Или просто перейдите в раздел "Карта Ашан" на сайте https://www.auchan.ru/personal-settings/loyalty/my-card/\n', sep='\n')
    menu_list = ["Вызов оператора", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(lambda message: message.text == "Мои покупки", state='*')
async def cmd_purchases(message: types.Message, state: FSMContext):
    msg = text('Пока я могу проконсультировать вас только по интернет-заказам. Информацию о покупках в магазинах АШАН и АТАК можно увидеть в личном кабинете на сайте  https://www.auchan.ru/personal-settings/my-purchases/\n\
Выберите пункт меню', sep='\n')
    menu_list = ["Мои заказы", "Возвраты", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(lambda message: message.text == "Мои заказы", state=UserStates.ready)
async def cmd_orders(message: types.Message, state: FSMContext):
    #ПОТЕНЦИАЛЬНО: обращение к бд, поиск заказов клиента 
    msg = text('По указанному номеру телефона заказов не найдено', sep='\n')
    menu_list = ["Возвраты", "Главное меню", "Вызов оператора"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(lambda message: message.text == "Возвраты", state='*')
async def cmd_returns(message: types.Message, state: FSMContext):
    msg = text('Выберите интересующий вас пункт меню', sep='\n')
    menu_list = ["Условия возврата товара", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))
 
@dp.message_handler(lambda message: message.text == "Условия возврата товара", state='*')
async def cmd_return_terms(message: types.Message, state: FSMContext):
    msg = text('Вернуть товар — ЛЕГКО!\
                В магазинах АШАН и АТАК:\
                При покупке в гипермаркете - обратитесь в любой гипермаркет на Пункт обслуживания клиентов.\
                Купили товар в супермаркете? Верните в том же магазине. Обратитесь, пожалуйста, к сотруднику касс.\
                Не забудьте взять с собой чек и банковскую карту, с которой производилась оплата\
                В интернет-магазине Ашан.ру:\
                просто вызовите оператора по кнопке здесь или обратитесь на пункт обслуживания клиентов в ближайший гипермаркет АШАН.\
                Обратите, пожалуйста, внимание, что есть некоторые законодательные ограничения на возврат товаров. Пожалуйста, ознакомьтесь: https://www.auchan.ru/help/service/vozvrat/', sep='\n')
    menu_list = ["Вызов оператора", "Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))
 
@dp.message_handler(lambda message: message.text == "Акции", state='*')
async def cmd_promotions(message: types.Message, state: FSMContext):
    msg = text('Тысячи товаров для вас по суперценам https://www.auchan.ru/superceny/', sep='\n')
    menu_list = ["Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(lambda message: message.text == "Поиск магазина", state='*')
async def cmd_shop_search(message: types.Message, state: FSMContext):
    msg = text('Выберите способ', sep='\n')
    menu_list = ["По геолокации", "Главное меню"]
    keyboard = make_keyboard(menu_list)
    keyboard['keyboard'][0] = [{"text": "По геолокации", "request_location": True}]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)

@dp.message_handler(content_types=['location'], state='*')
async def cmd_shop_search_by_geo(message: types.Message, state: FSMContext):
    #ПОТЕНЦИАЛЬНО: обращение к бд, поиск ближайшего магазина
    lat = message.location.latitude
    lon = message.location.longitude
    msg = text(f'АШАН около точки ({lon}, {lat}), https://yandex.ru/maps/?ll={lon},{lat}&pt={lon},{lat}&z=12&l=map', sep='\n')
    menu_list = ["Главное меню"]
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


@dp.message_handler(state=UserStates.ask_tel)
async def cmd_check_person(message: types.Message, state: FSMContext):
    menu_list = ["Главное меню"]
    msg = text("Неправильный формат номера. Попробуйте ещё раз")
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))

@dp.message_handler(content_types=ContentType.ANY, state='*')
async def unknown_message(message: types.Message, state: FSMContext):
    menu_list = ["Главное меню"]
    result = agent_executor({"input": message.text})
    msg = text(result["output"])
    await message.answer(msg, parse_mode=ParseMode.MARKDOWN, reply_markup=make_keyboard(menu_list))


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())