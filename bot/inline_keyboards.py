from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ["Info","Holders","Chart","Dividend","News","News_Analyze","Chart_Analyze"]
buttons = [
#    InlineKeyboardButton(text='Анализ новостей',callback_data='News_Analyze'),
#    InlineKeyboardButton(text='Анализ графика',callback_data='Chart_Analyze'),
    InlineKeyboardButton(text='Информация',callback_data='info'),
    InlineKeyboardButton(text='Инвесторы',callback_data='holders'),
    InlineKeyboardButton(text='Дивиденды',callback_data='dividend'),
    InlineKeyboardButton(text='График',callback_data='chart'),
    InlineKeyboardButton(text='Новости',callback_data='news'),
]
keyboard = InlineKeyboardMarkup(row_width=3).add(*buttons)
keyboard.add(*[InlineKeyboardButton(text='Анализ графика',callback_data='chart_analysis'),
             InlineKeyboardButton(text='Анализ новостей',callback_data='news_analysis')])
keyboard.add(InlineKeyboardButton(text='Скрыть клавиатуру',callback_data='hide'))