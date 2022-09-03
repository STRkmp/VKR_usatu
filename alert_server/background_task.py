from datetime import timedelta
from threading import Thread
from pydantic import BaseSettings
from qmanager.qmanager_factory import QueueManagerFactory
from qmanager.qmanager import QueueManager
import pickle
from yahoo_fin import stock_info as si
from configparser import RawConfigParser, ExtendedInterpolation
from qmanager.qmanager_config import QManagerSettings

from models import *

WORKERS = 1

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


def check_date(date: datetime) -> bool:
    now: datetime = datetime.now()
    result : timedelta = now - date
    if result.days > 30:
        return False    # delete
    return True         # check price

class ThreadedPrice(Thread):
    def __init__(self, settings: BaseSettings):
        Thread.__init__(self)
        self.qmanager = QueueManagerFactory(settings).get_instance(callback_func=self.process_client)

    def run(self):
        print(f'{self.name} Consuming...')
        self.qmanager.consume()

    def process_client(self, data: bytes, headers: dict = None) -> None:

        
        client: ClientRequest = pickle.loads(data)
        print(f'{self.name} RECEIVED {headers}\n{type(data)} from {client.id} about {client.symbol}\n')
        try:
            if (check_date(client.date)):
                try:
                    price = si.get_live_price(client.symbol)
                except:
                    raise ('Такого тикера не существует.')
                add_info = client.add_info.replace(',','.').replace(' ','')
                eval = add_info[0]
                goal = add_info[1:]
                match eval:
                    case '<':
                        if price < float(goal):
                            Answer: ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
                            Answer.description['alert'] = f'🆘 ЦЕНА АКЦИИ ({client.symbol}) НИЖЕ {goal} 🆘  \n СЕЙЧАС: {"{:,}".format(price)} $'
                            self.qmanager.publish(pickle.dumps(Answer),queue_name='out')  
                            return
                    case '>':
                        if price > float(goal):
                            Answer: ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol)
                            Answer.description['alert'] = f'🆘 ЦЕНА АКЦИИ {client.symbol} БОЛЬШЕ {goal} 🆘 \n СЕЙЧАС: {"{:,}".format(price)} $'
                            self.qmanager.publish(pickle.dumps(Answer),queue_name='out')  
                            return
                self.qmanager.publish(data=data)
            else:
                Answer: ClientResponse = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol, description= {'alert':f'За 30 дней акции {client.symbol} не достигли указанной цены в {client.add_info}.'})
                self.qmanager.publish(pickle.dumps(Answer),queue_name='out')
        except Exception as e:
            print(f'Получил ошибку в ходе выполнения функции {client.type[0]}\n{e}')
            Answer = ClientResponse(id=client.id, message_id = client.message_id,symbol=client.symbol, description= {'exception' : f'Получил ошибку в ходе выполнения функции {client.type[0]}\n Возможно Вы указали несуществующую акцию, неверный символ или неверную цену'})
            self.qmanager.publish(data=pickle.dumps(Answer),queue_name='out')
            

        

if __name__ == '__main__':
    for instance in range(WORKERS):
        ThreadedPrice(get_qmanager(name='QueueManager_bg')).start()
