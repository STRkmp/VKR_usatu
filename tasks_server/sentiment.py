import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.downloader.download('vader_lexicon')
from utils.stock_utils import get_news_stock


vader = SentimentIntensityAnalyzer()

def calc_sentiment_score(text: str):
    return vader.polarity_scores(text)['compound']

def num_of_scores(scores:list[float]):
    neg=pos=neu = 0
    for item in scores:
        if item > 0:
            pos = pos + 1
        if item < 0:
            neg = neg + 1
        if item == 0:
            neu = neu + 1
    return (neg,neu,pos)

def get_news_analysis(symbol: str, token: str) -> list[float]:
    data =  get_news_stock(symbol=symbol, token=token)
    news = []
    try:
        for new in data:
            if new["lang"] == "en" and not new["hasPaywall"]:
                news.append(
                    f"{new['headline']}"
                )
    except:
        for new in data:
            news.append(
                f"{new['title']}"
            )
    result = []
    for item in news:
        result.append(calc_sentiment_score(item))
    a = num_of_scores(result)
    text = f'Дали оценку заголовкам последних {len(news)} новостей\nОтрицательных = {a[0]}\nНейтральных = {a[1]}\nПоложительных = {a[2]}\nОбщая оценка = {sum(result)}'
    if sum(result) >= 0:
        verd = '\nСогласно анализу для данной акции преобладает положительный фон, который может сказаться хорошо на цене. Советуем изучить состояние фондового рынка, а также показания технических индикаторов'
    else:
        verd = '\nСогласно анализу новостей для данной акции преобладает негативный фон, который может сказаться на цене не очень хорошо. В любом случае, советуем Вам лично посмотреть состояние фондового рынка для принятия решений.'
    return text + verd