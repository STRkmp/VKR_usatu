import os
import pickle
from threading import Thread

from pydantic import BaseSettings

from utils.stock_utils import *
#
from qmanager.qmanager_factory import QueueManagerFactory
from models import *
from sentiment import get_news_analysis
from configparser import RawConfigParser, ExtendedInterpolation
from qmanager.qmanager_config import QManagerSettings
from ensemble import get_chart_analysis

WORKERS: int = os.environ.get('WORKERS')
Indicators: list[str] = ['rsi', 'macd', 'stoch', 'mom', 'roc']
iex_token: str = os.environ.get('IEX') #pk_fc28bb9a68aa470f91daf030b4831308
##   basic functions

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
    return QManagerSettings.parse_obj(app_config[name])

def get_holders(client: ClientRequest) -> ClientResponse:
    """
    Запрос-роутер. Служит неким декоратором запроса для составления ответа и вызова необходимой функции из utils.
    Args:
        client (ClientRequest): Десериализованный запрос пользователя, который был сформирован ботом и отправлен с помощью очереди сообщений серверу

    Returns:
        ClientResponse: Сформированный ответ для одного пользователя по одному запросу. Именно данный файл потом сериализутся и отправляется с помощью Qmanager frontend части.
    """
    Answer : ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
    Answer.description['holders'] = get_holders_stock(client.symbol)
    return Answer

def get_info(client: ClientRequest) -> ClientResponse:
    """
    Запрос-роутер. Служит неким декоратором запроса для составления ответа и вызова необходимой функции из utils.
    Args:
        client (ClientRequest): Десериализованный запрос пользователя, который был сформирован ботом и отправлен с помощью очереди сообщений серверу

    Returns:
        ClientResponse: Сформированный ответ для одного пользователя по одному запросу. Именно данный файл потом сериализутся и отправляется с помощью Qmanager frontend части.
    """
    Answer : ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
    Answer.description['info'] = get_info_stock(client.symbol)
    return Answer

def get_news(client: ClientRequest) -> ClientResponse:
    """
    Запрос-роутер. Служит неким декоратором запроса для составления ответа и вызова необходимой функции из utils.
    Args:
        client (ClientRequest): Десериализованный запрос пользователя, который был сформирован ботом и отправлен с помощью очереди сообщений серверу

    Returns:
        ClientResponse: Сформированный ответ для одного пользователя по одному запросу. Именно данный файл потом сериализутся и отправляется с помощью Qmanager frontend части.
    """
    Answer: ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
    data = get_news_stock(client.symbol,iex_token)

    line = []
    try:
        for news in data:
            if news["lang"] == "en" and not news["hasPaywall"]:
                line.append(
                    f'{news["source"]}: <a href="{news["url"]}">{news["headline"]}</a> \n'
                )
    except:
        line.append(''.join([str(count+1)+ ') '+'<a href="'+ item['link'] +'">'+item['title']+'</a> - ' + item['publisher'] + '\n'  for count,item in enumerate(data)]))
    Answer.description['news'] = ''.join(line)
    return Answer

def news_analysis(client: ClientRequest) -> ClientResponse:
    Answer: ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
    Answer.description['news_Analysis'] = get_news_analysis(client.symbol,iex_token)
    return Answer

def chart_analysis(client: ClientRequest) -> ClientResponse:
    Answer: ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
    Answer.description['chart_analysis'] = get_chart_analysis(client.symbol)
    return Answer

def get_dividend(client: ClientRequest) -> ClientResponse:
    """
    Запрос-роутер. Служит неким декоратором запроса для составления ответа и вызова необходимой функции из utils.
    Args:
        client (ClientRequest): Десериализованный запрос пользователя, который был сформирован ботом и отправлен с помощью очереди сообщений серверу

    Returns:
        ClientResponse: Сформированный ответ для одного пользователя по одному запросу. Именно данный файл потом сериализутся и отправляется с помощью Qmanager frontend части.
    """
    Answer: ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
    Answer.description['dividend'] = get_dividend_stock(client.symbol)
    return Answer

def get_chart(client:ClientRequest) -> ClientResponse:
    """
    Метод получения котировок акций, составления графика + объёмов торгов, очищение данных от нулевых значений (ввиду праздников и выходных).
    График переводится в изображение + html, но сохраняется в буфере и кодируются b64.
    Все данные заполняются в финальный ответ и отправляются через очередь сообщений 
    Args:
        client (ClientRequest): Десериализованный запрос пользователя, который был сформирован ботом и отправлен с помощью очереди сообщений серверу

    Returns:
        ClientResponse: Сформированный ответ для одного пользователя по одному запросу. Именно данный файл потом сериализутся и отправляется с помощью Qmanager frontend части.
    """
    delta = client.add_info.split(' ',1)
    prices = get_price_stock(client.symbol,timedelta= int(delta[0]))
    if len(prices) == 0:
        raise Exception('Неовозможно получить данные. Возможно Вы ввели неверный тикер')
    Needed_ind: list[str] = []
    fail: list[str] = []
    if len(delta) == 2:
        Needed_ind = list(set(delta[1].lower().replace(' ','').split(',')) & set(Indicators))
        fail = list(set(delta[1].lower().replace(' ','').split(',')) - set(Indicators))
    pl = plot_graph(prices,client.symbol,subplots = 2 + len(Needed_ind))
    pl = add_MA(prices,pl)
    for index,indicator in enumerate(Needed_ind):
        info = eval(indicator + '(prices)')
        pl = eval('add_' + indicator + f'(info,pl,{3+index})')
    html = fig_2_html64(pl)
    image = fig_2_img64(pl)
    Answer: ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
    Answer.images[client.symbol] = image
    Answer.images['html'] = html
    a = ''
    if len(fail) > 0:
        a = 'Мы не смогли построить следующие индикаторы, они не реализованы либо не существуют : ' + ','.join(fail).upper() + '\n' 
    add: str = ''
    if ('-' not in client.symbol):
        add = get_analysis_TA(client.symbol)
    Answer.description[client.symbol] = a + add
    return Answer
##################################

class ThreadedConsume(Thread):
    def __init__(self, settings: BaseSettings):
        Thread.__init__(self)
        self.qmanager = QueueManagerFactory(settings).get_instance(callback_func=self.process_request)

    def run(self):
        print(f'{self.name} Consuming...')
        self.qmanager.consume()

    def process_request(self,data: bytes, headers: dict = None) -> None:
    #        
    #Callback функция прослушивания интерфейса очередей qmanager. Вызывается, когда очередь сообщений находит в прослушиваемой директории или бд очередной бинарник. В данном случае содержит блоки try - except для отлова запросов пользователя которые не смогли выполниться и требуется проинформировать инициатора.
    #Args:
    #    data (bytes): Сериализованные данные. предполагается что там находится объект класса ClientResponse
    #    headers (dict, optional): Словарь заголовков объекта. Находится UUID запросов, можно добавить свои метки. Рекомендуется добавить шифрование sha256.
    #    
    #чтение и получение цен
        try:
            request: ClientRequest = pickle.loads(data)
            print(f'Новый запрос от {request.id} по тикеру {request.symbol} с функцией {request.type[0]}')
            answers : list = []
            for item in request.type:
                answers.append(functions[item](request))
            #TODO объединение ответов
            for answer in answers:
                print(f'Ответ пользователю {answer.id} публикуется.')
                self.qmanager.publish(data = pickle.dumps(answer),queue_name="out")
        except Exception as e:
            print(f'Получил ошибку в ходе выполнения функции {request.type[0]}\n{e}')
            answer = ClientResponse(id=request.id, message_id = request.message_id,symbol=request.symbol, description= {'exception' : f'Получил ошибку в ходе выполнения функции {request.type[0]}\n{e}'})
            self.qmanager.publish(data=pickle.dumps(answer),queue_name='out')






functions: dict = {'info' : get_info,
                   'chart': get_chart,
                   'dividend': get_dividend,
                   'news':get_news,
                   'holders':get_holders,
                   'news_analysis': news_analysis,
                   'chart_analysis': chart_analysis} 

if __name__ == '__main__':
    for i in range(WORKERS):
        print(f'Начал {i}')
        th = ThreadedConsume(get_qmanager(name = 'QueueManager_server')).start()