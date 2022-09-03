# VKR_usatu
Дипломная работа по теме "Программное обеспечение для мониторинга и анализа акций на фондовом рынке"
Цель работы: упрощение процесса мониторинга и анализа акций фондового рынка с помощью разработки программного обеспечения. 

ПО разделено на микросервисы, которые расположены в контейнерах docker.
Install:
1)В файле docker-compose.yml необходимо заменить
  BOT_TOKEN на токен полученный у BotFather в Telegram;
  IEX на токен, полученный на платформе https://iexcloud.io/

2)Разместить на сервере проект (тестировался на 4*2.3 CPU, 8 RAM, 80 SSD, Linux Ubuntu 22.04), создать контейнеры и запустить.
![image](https://user-images.githubusercontent.com/82835572/188265149-9d2cd5ba-732a-4e5c-8bde-09325f5e750d.png)

Дополнительная информация
![image](https://user-images.githubusercontent.com/82835572/188264743-a5019bd6-9d4d-4a5e-95f3-4dbb9f8b9cd4.png)
![image](https://user-images.githubusercontent.com/82835572/188264769-b836c942-3f4f-4142-823b-41c512dc6a4a.png)
![image](https://user-images.githubusercontent.com/82835572/188264755-f69f19f3-6f04-4d75-931f-08ec67b26c61.png)
![image](https://user-images.githubusercontent.com/82835572/188264763-149cedca-a355-4c7f-8fc2-c563d90c49c0.png)
![image](https://user-images.githubusercontent.com/82835572/188264766-f70d3ad7-182a-4805-af4d-982781eb914c.png)
![image](https://user-images.githubusercontent.com/82835572/188264810-2d2ac2ab-9166-4bba-a49a-554341948b4f.png)

P.S. 
  Данное ПО было "пробой пера", но надеюсь это пригодится кому-нибудь.
