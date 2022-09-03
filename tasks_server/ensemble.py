import yfinance as yf
import datetime
import pandas as pd
from finta import TA
import pickle, os
import numpy as np
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn import metrics






class TickerAnalysis():
    NUM_DAYS: int = 10000     # The number of days of historical data to retrieve
    INTERVAL: str = '1d'     # Sample rate of historical data
    dir: str = "analysis_model/"
    INDICATORS: list[str] = ['RSI', 'MACD', 'STOCH','ADL', 'ATR', 'MOM', 'MFI', 'ROC', 'OBV', 'CCI', 'EMV', 'VORTEX']
    def __init__(self,symbol):
        self.symbol = symbol
        self.__get_history()
        print( self.data.columns)   
        print( len(self.data.columns))
        print( self.data.columns)

    def __save__(self):
        with open (f'{self.dir}{self.symbol.replace(" ","").lower()}.pkl','wb') as model:
            pickle.dump(self.ensemble,model)
    
    def __load__(self):
        with open (f'{self.dir}{self.symbol.replace(" ","").lower()}.pkl','rb') as model:
#        with open (f'{self.dir}{self.symbol}.pkl','rb') as model:
            self.ensemble = pickle.load(model)

    def __check_file(self):
        if os.path.isfile(f'{self.dir}{self.symbol.replace(" ","").lower()}.pkl'):
            return True
        return False
    def __get_history(self):
        start = (datetime.date.today() - datetime.timedelta( self.NUM_DAYS ) )
        end = datetime.datetime.today()
        self.data = yf.download(self.symbol, start=start, end=end, interval=self.INTERVAL)
        self.data.rename(columns={"Close": 'close', "High": 'high', "Low": 'low', 'Volume': 'volume', 'Open': 'open'}, inplace=True)


    def __exponential_smooth(self, alpha):
        self.data = self.data.ewm(alpha=alpha).mean()

    def __get_indicator_data(self):
        for indicator in self.INDICATORS:
            ind_data = eval('TA.' + indicator + '(self.data)')
            if not isinstance(ind_data, pd.DataFrame):
                ind_data = ind_data.to_frame()
            self.data = self.data.merge(ind_data, left_index=True, right_index=True)

        self.data['ema50'] = self.data['close'] / self.data['close'].ewm(50).mean()
        self.data['ema21'] = self.data['close'] / self.data['close'].ewm(21).mean()
        self.data['ema15'] = self.data['close'] / self.data['close'].ewm(14).mean()
        self.data['ema5'] = self.data['close'] / self.data['close'].ewm(5).mean()
        
        self.data.rename(columns={"14 period EMV.": '14 period EMV'}, inplace=True)
        self.data['vol'] = self.data['volume'] / self.data['volume'].ewm(5).mean()
        del (self.data['open'])
        del (self.data['high'])
        del (self.data['low'])
        del (self.data['volume'])
        del (self.data['Adj Close'])
        
    def __produce_prediction(self, window = 10):
        prediction = (self.data.shift(-window)['close'] >= self.data['close'])
        prediction = prediction.iloc[:-window]
        self.data['pred'] = prediction.astype(int)
        del (self.data['close'])
        self.data = self.data.dropna()
        
    def __start_validation(self):
        num_train = 20
        len_train = 40 

        ensemble_RESULTS = []        
        i = 0
        rf = RandomForestClassifier(n_jobs=1,n_estimators=130,random_state=65)
        knn = KNeighborsClassifier()
        
        estimators=[('knn', knn), ('rf', rf)]
        ensemble = VotingClassifier(estimators, voting='soft')
        while True:
            df = self.data.iloc[i * num_train : (i * num_train) + len_train]
            i += 1
            print(i * num_train, (i * num_train) + len_train)
            if len(df) < 40:
                break
            y = df['pred']
            features = [x for x in df.columns if x not in ['pred']]
            X = df[features]
            X_train, X_test, y_train, y_test = train_test_split(X, y, train_size= 7 * len(X) // 10,shuffle=False)
            #rf = self.__train_rf(X_train,y_train,X_test,y_test)
            ensemble.fit(X_train,y_train)
            ensemble_prediction = ensemble.predict(X_test)
            print('ensemble prediction is ', ensemble_prediction)
            print('truth values are ', y_test.values)
            ensemble_accuracy = accuracy_score(y_test.values, ensemble_prediction)
            
            print( ensemble_accuracy)
            ensemble_RESULTS.append(ensemble_accuracy)
                    
        print('ENSEMBLE Accuracy = ' + str( sum(ensemble_RESULTS) / len(ensemble_RESULTS)))
        self.ensemble = ensemble

    def start(self):
        self.__exponential_smooth(alpha = 0.65)
        self.__get_indicator_data()
        live_data = self.data.tail(10)

        del(live_data['close'])
        self.__produce_prediction(window=10)
        count_col = len(self.data.columns)
        in_data = self.data.iloc[:,0:count_col-1]  # .values # выбираем все строки c 2 по 10 колонок и трансформируем в np-массив
        if (not self.__check_file()):
            self.__start_validation()
            self.__save__()
        else:
            try:
                self.__load__()
            except:
                self.__start_validation()
                self.__save__()

        predict =  self.ensemble.predict(live_data)
        answer: str = ''
        if sum(predict) >= len(predict)/2:
            answer = answer + f'Согласно ансамблевой модели обученной на котировках этой акции, за последние дни она преимущественно советует ПОКУПАТЬ акцию {self.symbol}.\nПрогноз на следующий (текующий не закрытый день) - '
        else:
            answer = answer + f'Согласно ансамблевой модели обученной на котировках этой акции, за последние дни она преимущественно советует ПРОДАВАТЬ акцию. {self.symbol}\nПрогноз на следующий (текующий не закрытый день) - '
        if predict[-1:] == 1:
            answer = answer + 'цена ВЫШЕ закрытия прошлого дня за интервал в 1 день.\n'
        else:
            answer = answer + 'цена НИЖЕ закрытия прошлого дня за интервал в 1 день.\n'

        return answer
    
def get_chart_analysis(symbol:str):
    try:
        tick = TickerAnalysis(symbol)
        return tick.start()
    except:
        print('Невозможно провести анализ указанной акции. Проверьте вводимый тикер или подождите до восстановления работы поставщика данных')
        raise Exception('Невозможно провести анализ указанной акции. Проверьте вводимый тикер или подождите до восстановления работы поставщика данных')

#if __name__ == '__main__':
#tick = TickerAnalysis('aapl')
#tick.start()

