from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np


def svm(data):
    df = pd.read_csv('dataset.csv')

    X = df.drop(['index', 'Result'], axis='columns')
    Y = df['Result']

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.3)

    model = SVC(gamma='auto', kernel='rbf')
    model.fit(X_train, Y_train)
    print(model.score(X_test, Y_test))
    data = np.array(data).reshape(1, -1)
    print(model.predict(data))
