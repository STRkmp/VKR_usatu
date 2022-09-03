
MESSAGES = {
'start' : 'Категорически приветствую. \nДанный бот был разработан в рамках ВКР студента группы ПРО-421 Ястребова Данила.\n Воспользуйтесь /help для получения всех команд',
'help' : """
Thanks for using this bot.

**Commands**
- `/start - Регистрация пользователя (для отправки сообщений). 🎗️
- `/dividend [symbol]` Получение информации об дивидендах. 📅
- `/chart [symbol]` Построение котировок акций. 📊
- `/news [symbol]` Новости касающиеся компании. 📰
- `/info [symbol]` Основная информация о компании. ℹ️
- `/holders [symbol]` Институциональные держатели акций компании. 🔢
- `/alert [symbol] [<>] {price $}` Создание уведомления о достижении цены. 🆘
Например так 
`/alert aapl > 130`
- `/help` Get some help using the bot. 💬

Список доступных индикаторов для отображения: RSI, MACD, STOCH, MOM, ROC
Информация по дополнительным индикаторам: ADL, ATR, MFI, OBV, CCI, EMV, VORTEX
**Дисклеймер**
Информация о рынке предоставлена Yahoo! Finance (https://finance.yahoo.com), небольшая сводка информации от TradingView (https://ru.tradingview.com), библиотеки finta.
""",
'dividend':"""Боюсь Вы предоставили неверные данные или не предоставили их вовсе
Необходимо писать команды в данном стиле 
/dividend aapl""",
'news': """Боюсь Вы предоставили неверные данные или не предоставили их вовсе
Необходимо писать команды в данном стиле

/news aapl """,
'chart':'''Боюсь Вы предоставили неверные данные или не предоставили их вовсе
Необходимо записать подобно этому 

/chart aapl''',
'info':'''Боюсь Вы предоставили неверные данные или не предоставили их вовсе
Необходимо писать команды в данном стиле


/info aapl''',
'holders':'''Боюсь Вы предоставили неверные данные или не предоставили их вовсе
Необходимо писать команды в данном стиле


/holders aapl''',
'alert':'''Боюсь Вы предоставили неверные данные или не предоставили их вовсе
Необходимо писать команды в данном стиле

/alert aapl > 145 
/alert aapl < 130''',
'RSI':"""Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements.
RSI oscillates between zero and 100. Traditionally, and according to Wilder, RSI is considered overbought when above 70 and oversold when below 30.
Signals can also be generated by looking for divergences, failure swings and centerline crossovers.
RSI can also be used to identify the general trend.""",
'MACD':"""
MACD, MACD Signal and MACD difference.
The MACD Line oscillates above and below the zero line, which is also known as the centerline.
These crossovers signal that the 12-day EMA has crossed the 26-day EMA. The direction, of course, depends on the direction of the moving average cross.
Positive MACD indicates that the 12-day EMA is above the 26-day EMA. Positive values increase as the shorter EMA diverges further from the longer EMA.
This means upside momentum is increasing. Negative MACD values indicates that the 12-day EMA is below the 26-day EMA.
Negative values increase as the shorter EMA diverges further below the longer EMA. This means downside momentum is increasing.

Signal line crossovers are the most common MACD signals. The signal line is a 9-day EMA of the MACD Line.
As a moving average of the indicator, it trails the MACD and makes it easier to spot MACD turns.
A bullish crossover occurs when the MACD turns up and crosses above the signal line.
A bearish crossover occurs when the MACD turns down and crosses below the signal line.
""",
'STOCH': """Stochastic oscillator %K
The stochastic oscillator is a momentum indicator comparing the closing price of a security
to the range of its prices over a certain period of time.
The sensitivity of the oscillator to market movements is reducible by adjusting that time
period or by taking a moving average of the result.""",
'ADL':"""The accumulation/distribution line was created by Marc Chaikin to determine the flow of money into or out of a security.
It should not be confused with the advance/decline line. While their initials might be the same, these are entirely different indicators,
and their uses are different as well. Whereas the advance/decline line can provide insight into market movements,
the accumulation/distribution line is of use to traders looking to measure buy/sell pressure on a security or confirm the strength of a trend.""",
'ATR':"""Average True Range is moving average of True Range.""",
'MOM':"""Market momentum is measured by continually taking price differences for a fixed time interval.
To construct a 10-day momentum line, simply subtract the closing price 10 days ago from the last closing price.
This positive or negative value is then plotted around a zero line.""",
'MFI':"""The money flow index (MFI) is a momentum indicator that measures
the inflow and outflow of money into a security over a specific period of time.
MFI can be understood as RSI adjusted for volume.
The money flow indicator is one of the more reliable indicators of overbought and oversold conditions, perhaps partly because
it uses the higher readings of 80 and 20 as compared to the RSI's overbought/oversold readings of 70 and 30""",
'ROC':"""The Rate-of-Change (ROC) indicator, which is also referred to as simply Momentum,
is a pure momentum oscillator that measures the percent change in price from one period to the next.
The ROC calculation compares the current price with the price “n” periods ago.""",
'OBV':"""On Balance Volume (OBV) measures buying and selling pressure as a cumulative indicator that adds volume on up days and subtracts volume on down days.
OBV was developed by Joe Granville and introduced in his 1963 book, Granville's New Key to Stock Market Profits.
It was one of the first indicators to measure positive and negative volume flow.
Chartists can look for divergences between OBV and price to predict price movements or use OBV to confirm price trends.

source: https://en.wikipedia.org/wiki/On-balance_volume#The_formula""",
'CCI':"""Commodity Channel Index (CCI) is a versatile indicator that can be used to identify a new trend or warn of extreme conditions.
CCI measures the current price level relative to an average price level over a given period of time.
The CCI typically oscillates above and below a zero line. Normal oscillations will occur within the range of +100 and −100.
Readings above +100 imply an overbought condition, while readings below −100 imply an oversold condition.
As with other overbought/oversold indicators, this means that there is a large probability that the price will correct to more representative levels.

source: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:commodity_channel_index_cci""",
'EMV': """Ease of Movement (EMV) is a volume-based oscillator that fluctuates above and below the zero line.
As its name implies, it is designed to measure the 'ease' of price movement.
prices are advancing with relative ease when the oscillator is in positive territory.
Conversely, prices are declining with relative ease when the oscillator is in negative territory.""",
'VORTEX':"""The Vortex indicator plots two oscillating lines, one to identify positive trend movement and the other to identify negative price movement.
Indicator construction revolves around the highs and lows of the last two days or periods.
The distance from the current high to the prior low designates positive trend movement while the
distance between the current low and the prior high designates negative trend movement.
Strongly positive or negative trend movements will show a longer length between the two numbers while
weaker positive or negative trend movement will show a shorter length."""
}
