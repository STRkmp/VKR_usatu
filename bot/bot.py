import os
import  asyncio, pickle, base64
from messages import MESSAGES
from models import *
from aiogram import Bot, Dispatcher, types
from qmanager.qmanager_factory import QueueManagerFactory
from qmanager.qmanager import QueueManager
from configparser import RawConfigParser, ExtendedInterpolation
from qmanager.qmanager_config import QManagerSettings
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import re
from inline_keyboards import keyboard

def get_qmanager(name : str) -> QManagerSettings:
    """
    Получение настроек очереди сообщений в описанном конфигурационном файле. Принимает имя конфигурации, читает настройки и возвращает базовые настройки
    Именно в этом файле задается директории, где читать и куда записывать файлы, как с ними поступать, с какой периодичностью проверять папку, а также подача 
    логина и пароля для бд, путь к хосту. 
    Args:
        name (str): Имя конфигурации в файле settings.ini (например для бота это QueueBot)

    Returns:
        QManagerSettings: Модель наследуемая от pydantic.BaseSettings. Получает значения по ключам. 
    """
    app_config = RawConfigParser(interpolation=ExtendedInterpolation())
    app_config.read('settings/application.ini')
    print(f'Читаю конфинг Qmanager')
    return QManagerSettings.parse_obj(app_config[name])

BOT_TOKEN: str = os.environ.get('BOT_TOKEN')
storage = MemoryStorage()
bot: Bot = Bot(token=BOT_TOKEN)
dp: Dispatcher = Dispatcher(bot =bot, storage=storage)
sender_response: Bot = Bot(token=BOT_TOKEN)
indicators = ['rsi', 'macd', 'stoch', 'mom', 'roc']

def process_request(data: bytes, headers: dict = None) -> None:
    """
    Callback функция прослушивания интерфейса очередей qmanager. Вызывается, когда очередь сообщений находит в прослушиваемой директории или бд очередной бинарник.
    Args:
        data (bytes): Сериализованные данные. предполагается что там находится объект класса ClientResponse
        headers (dict, optional): Словарь заголовков объекта. Находится UUID запросов, можно добавить свои метки. Рекомендуется добавить шифрование sha256.
    """
    
    answer: ClientResponse = pickle.loads(data)
    print(f'Получили ответ для пользователя {answer.id}')
    if 'exception' in answer.description.keys():
        asyncio.run(send_message(answer.id,answer.symbol,error=answer.description['exception'],message_id = answer.message_id))
        return
    for item in answer.description.items():
        image = None
        if item[0] in answer.images.keys():
            image = answer.images[item[0]]
        
        asyncio.run(send_messsage(answer.id,answer.symbol,item[1], image,message_id=answer.message_id))
    if 'html' in answer.images.keys():
        asyncio.run(send_messsage(id = answer.id,symbol = answer.symbol,html = answer.images['html']))



def publish_req(id: int, symbol: str, type: list = [], add_info: str = '', message_id: int = 0, queue_name: str = 'in') -> None:
    """
    Запись запроса в БД или другую указанную директорию через интерфейс очереди сообщений
    Args:
     id (int): личный ID пользователя, не беседы!
     message_id (_type_): ID сообщения для его измены. 
     symbol (str): Название акции, по которой необходимо выполнить целевое действие
     type (list, optional): Целевое действие (например: "news" - получение новостей; "dividend" - получение информации о дивидендах). 
     Является списком, для возможного расширения функционала и составления "сложных" запросов. Defaults to [].
     add_info (str, optional): Дополнительная информация об запросе - период или даты получения цен, цена при достжении которой нужно уведомить пользователя. Defaults to ''.
     queue_name (str, optional): Место, куда нужно отправить запрос (смотря какой модуль что читает). Например папка in тут - запросы с tasks_server, а laert - alert_server.
     Стоит добавить словарь ключей значений по доставке. например destination = {'server' : 'in', 'alerts' : 'alert'}, это поможет быстрее распределять запросы между сервисами. Defaults to 'in'.
    """
    print(f'Публикуем запрос для других модулей через очередь сообщений от пользователя {id} по тикеру {symbol} с желанием {type[0]}')
    client : ClientRequest = ClientRequest(id= id, message_id = message_id, symbol= symbol, type=type, add_info=add_info)
    qmanager.publish(data= pickle.dumps(client), queue_name= queue_name)

qmanager : QueueManager = QueueManagerFactory(get_qmanager(name='QueueManager_bot')).get_instance(callback_func=process_request)
print('НУ ДАВАЙ ПРОЙДИ ДАЛЬШЕ')
    

async def send_messsage(id: int, symbol: str, answer: str = '', image: bytes = None, html:bytes = None,message_id : int = 0) -> None:
    """
    Функция отправки сообщений пользователям из Telegram, которым пришел ответ на запрос от других сервисов. 
    Args:
        id (int): личный ID пользователя
        symbol (str): Наименовании акции, которая была запрошена
        answer (str, optional): Здесь находится текст, который необходимо прислать пользователю вместе с картинкой или без неё. Defaults to ''.
        image (bytes, optional): Зашифрованное изображение (зачастую график акции). Defaults to None.
        html (bytes, optional): Зашифрованный .html файл (зачастую интерактивной график акции). Defaults to None.
        message_id (int, optional): id сообщения 
    """
    try:
        print(f'Отправляем сообщение пользователю {id} от сервера по тикеру {symbol}')
        if html is not None:
            await sender_response.send_document(id,(f'charts_{symbol}.html',base64.b64decode(html)))
            return
        if image is None:
            if message_id == 0:
                await sender_response.send_message(id, f'{answer}', parse_mode= types.ParseMode.HTML)
            else:
                await sender_response.delete_message(chat_id=id,message_id=message_id)
                await sender_response.send_message(chat_id = id,text = f'Тикер желаемой акции - {symbol}\n'+answer,reply_markup=keyboard, parse_mode= types.ParseMode.HTML)
            return
        else:
            photo = base64.b64decode(image)
            if message_id == 0:
                await sender_response.send_photo(chat_id=id,photo= photo,caption= answer)
            else:
                await sender_response.delete_message(chat_id=id,message_id=message_id)
                try:
                    await sender_response.send_photo(chat_id = id, caption =  f'Тикер желаемой акции - {symbol}\n'+answer, photo=photo,reply_markup=keyboard)
                except RuntimeError as e:
                    print('RuntimeError в ходе отправления графика, всё хорошо. Случилось из-за большого размера файла')
            return
    except Exception as e:
        print('опв')
        print(e)
async def send_message(id:int, symbol:str, error:str = '', message_id : int = 0):
    if message_id != 0:
        await sender_response.delete_message(chat_id=id, message_id =message_id)        
    await sender_response.send_message(id,f'Ошибка при запросе {symbol}. \n {error}')


class ChartInfo(StatesGroup):
    Symbol = State()
    DaysDelta = State()
    Indicators = State()

## DEFAULT
@dp.message_handler(commands=['start'])
async def start_handler(event: types.Message) -> None:
    """
    Первый запуск бота от пользователя, обратное сообщение заранее подготовлено в словаре MESSAGES.
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """
    print(f'Получил запрос от {event.from_user.id} на start')
    await event.answer(
        MESSAGES['start']
    )

@dp.message_handler(commands=['help'])
async def help_handler(event: types.Message) -> None:
    """
    Отправка пользователю всех функций бота, их описание и примеры вызовов
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """
    await event.reply(MESSAGES['help'])


##


@dp.message_handler(commands=['dividend']) 
async def dividend_handler(event: types.Message) -> None:
    """
    Функция /dividend $Symbol бота. проверка доп сообщения и отправка запроса серверу
    По сути все функции бота являются некоторой небольшой обёрткой для создания запроса
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """
    args: str = event.get_args()
    if args:
        publish_req(id=event.from_user.id,symbol=args, type=['dividend'])
        await event.answer(
            f'Пытаемся получить данные об дивидендах компании по тикеру {args}.'
         )
    else: 
        await event.answer(
            MESSAGES['dividend']
        )

@dp.message_handler(commands=['news'])
async def news_handler(event:types.Message) -> None:
    """
    Функция /news $Symbol бота. проверка доп сообщения и отправка запроса серверу
    По сути все функции бота являются некоторой небольшой обёрткой для создания запроса
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """
    args:str = event.get_args()
    if args:
        publish_req(id=event.from_user.id,symbol= args, type=['news'])
        await event.answer(
            f'Подготавливаем последний список новостей по тикеру {args}'
        )
    else: 
        await event.answer(
            MESSAGES['news']
        )

def is_digit(s:str) -> bool:
    """
    Функция проверяющая являются ли поступающая строка числом.
    Args:
        s (str): поступающая строка вида "123" , "fd23"
    Returns:
        bool: значение истинности: является ли полученная строка числом (можно ли его привести к нему).
    """
    if s.isdigit():
        return True if (int(s) < 1001 and int(s) > 29) else False
    return False

@dp.message_handler(state = ChartInfo.DaysDelta)
async def days_delta_choosen(event: types.Message, state: FSMContext)->None:
    """
    Функция получения ответов в системе диалогов (Конечные автоматы). Записывает за сколько дней необходимо получить и отобразить котировки акций
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
        state (FSMContext): Контекст состояния для пользователя. Уникальное состояние, которое заполняется по мере ответов пользователем для их дальнейшей отправки. Хранится лишь в ОЗУ.
    """
    if event.text == "Cancel":
        await event.answer('Возврат назад')
        await state.finish()
        return
    if not is_digit(event.text):
        await event.answer('Введите корректное число между 30 и 1000. Если желаете вернуться напишите "Cancel"')
        return
    await state.update_data(DaysDelta = event.text)
    await event.answer(f'Напишите какие индикаторы отобразить \n Список доступных: {",".join(indicators).upper()} \nЕсли индикаторы были введены неверно, то они не будут отображены\n macd, rsi')
    await ChartInfo.Indicators.set()

@dp.message_handler(state = ChartInfo.Indicators)
async def indicators_choosen(event: types.Message, state:FSMContext)-> None:
    """
    Функция получения информации от пользователей о требуемых технических индикаторов (их название), которые нужно вычислить и отобразить на графиках.
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
        state (FSMContext): Контекст состояния для пользователя. Уникальное состояние, которое заполняется по мере ответов пользователем для их дальнейшей отправки. Хранится лишь в ОЗУ.
    """
    await state.update_data(Indicators = event.text)
    data = await state.get_data()
    await state.finish()
    publish_req(id=event.from_user.id,symbol= data['Symbol'], type=['chart'],add_info=f'{data["DaysDelta"]} {data["Indicators"]}')
    await event.answer(
        f'Собираем данные по тикеру '
    )


@dp.message_handler(commands=['chart'])
async def chart_handler(event:types.Message) -> None:
    """
    Функция /chart $Symbol для получения цен акций и их отображение в графическом виде (японские свечи). Поддерживает выбор дней, за сколько нужно получить данные, а также выбор технических индикаторов. 
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """
    args: str = event.get_args()
    if args:
        await event.answer('Введите, пожалуйста, за сколько дней Вы желаете получить график (от 30 до 1000):')
        #await ChartInfo.Symbol.set()
        await ChartInfo.Symbol.set()
        state = Dispatcher.get_current().current_state()
        await state.update_data(Symbol = args)
        await ChartInfo.DaysDelta.set()
    else: 
        await event.answer(
            MESSAGES['chart']
        )

@dp.message_handler(commands=['info'])
async def info_handler(event:types.Message) -> None:
    """
    Функция /info $Symbol бота. проверка доп сообщения и отправка запроса серверу
    По сути все функции бота являются некоторой небольшой обёрткой для создания запроса
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """
    args:str = event.get_args()
    if args:
        publish_req(id=event.from_user.id,symbol=event.get_args(), type=['info'])
        await event.answer(
            f'Получение базовой информации по тикеру {event.get_args()}'
        )
    else: 
        await event.answer(
            MESSAGES['info']
        )

@dp.message_handler(commands=['holders'])
async def holders_handler(event:types.Message) -> None:
    """
    Функция /holders $Symbol бота. Отправляет пользователю информацию об институциональных держателях акций
    По сути все функции бота являются некоторой небольшой обёрткой для создания запроса
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """
    args:str = event.get_args()
    if args:
        publish_req(id=event.from_user.id,symbol=args, type=['holders'])
        await event.answer(
            f'Получение институциональных инвесторов по тикеру {args}'
        )
    else: 
        await event.answer(
            MESSAGES['holders']
        )

@dp.message_handler(commands=['alert'])
async def alert_handler(event:types.Message) -> None:
    """
    Функция /alert $Symbol > $Price (/alert aapl > 160) бота. Отправка запроса на модуль alert_server для создания уведомления на достижении цены конкретной акции.
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """
    if re.match('^[a-zA-Z]+.*[>|<].+\d+$',event.get_args()) and '-' not in event.get_args():
        args: list[str] = event.get_args().split(' ',1)
        if len(args) == 1:
            if '>' in event.get_args():
                args = event.get_args().split('>',1)
                args[1] = '> ' +args[1]
            else:
                args = event.get_args().split('<')
                args[1] = '< ' +args[1] 
                
        publish_req(id=event.from_user.id,symbol=args[0], type=['alert'],add_info = args[1], queue_name= 'tasks')
        await event.answer(
            f'Создал уведомление на достижение цены в  {event.get_args()}'
        )
    else: 
        await event.answer(
            MESSAGES['alert']
        )

#TODO графики нескольких акций одновременно!
@dp.message_handler()
async def echo_message(event: types.Message)-> None:
    """
    Обработчик сообщений для запросов, отправленных без специального символа '/'. В общем случае служит информационном бюро, выводящим информацию об технических индикаторов. Если ввели тикер - присылает клавиатуру для создания быстрых запросов.
    Args:
        event (types.Message): Обёртка сообщения от пользователя. От него получаем полное сообщение от пользователя. 
    """

    if event.text[0] == '/':
        return
    if event.text.upper() in MESSAGES.keys():
        await event.answer(
            MESSAGES[event.text.upper()]
        )
    else:
        await event.answer(
            f'Тикер желаемой акции - {event.text} \nЧто желаете получить?',reply_markup=keyboard
        )

@dp.callback_query_handler(text=["info","holders","chart","dividend","news",'news_analysis','chart_analysis'])
async def inline_check(call: types.CallbackQuery) -> None:
    """
    Функция динамического создания запросов с inline-клавиатуры. После отправки запроса клавиатура скрывается, так-как после получения ответа сообщения стирается или заменяется.
    Args:
        call (types.CallbackQuery): Входящий запрос от нажатой кнопки пользователем. Требуется получить от него ID сообщения, ID пользователя и необходимая функция.
    """
    print(f'Получил запрос от {call.from_user.id} через Inline-клавиатуру')
   
    symbol:str = call.message.html_text.split(' ',4)[4].split('\n')[0].lower().replace(' ','')
    add_info:str = ''
    if call.data == 'chart':
        add_info = '365'
    publish_req(id=call.from_user.id, message_id=call.message.message_id,symbol=symbol, type=[call.data],add_info=add_info)
    await bot.edit_message_reply_markup(chat_id = call.from_user.id, reply_markup=None,message_id=call.message.message_id)
    await bot.answer_callback_query(call.id, text='Отправлено')

@dp.callback_query_handler(text=['hide'])
async def inline_hide(call: types.CallbackQuery) -> None:
    """
    Функция для скрытия клавиатуры.
    Args:
        call (types.CallbackQuery): Входящий запрос от нажатой кнопки пользователем. Требуется получить от него ID сообщения, ID пользователя и необходимая функция.
    """
    await bot.edit_message_reply_markup(chat_id = call.from_user.id, reply_markup=None,message_id=call.message.message_id)
    await bot.answer_callback_query(call.id, text='Скрыто')

async def main() -> None:
    """
    Запуск асинхронного телеграм сервера
    Можно переписать полностью бота на веб сервер с чтением вебсокетов но имеет мало практического смысла, однако будет возможность деплоя html файлов к себе на сервер
    и отправка их пользователю с помощью WebApp Telegram SDK 6.0
    """
    try:
        
        task_bot = asyncio.create_task(dp.start_polling())
        await task_bot
    finally:
        await bot.close()

if __name__ == '__main__':
    print('Запуск системы')
    ThreadedConsumer(qmanager,'out').start()
    print('Запускаю асинхронное прослушивание')
    asyncio.run(main())

