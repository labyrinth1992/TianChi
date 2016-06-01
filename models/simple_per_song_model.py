import numpy
import os
from models.model import Model
from utils.sql import SQLClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction import DictVectorizer
from sklearn.externals import joblib
from sklearn.metrics import mean_squared_error

class SimplePerSongModel(Model):

    def __init__(self, feature_set, predict_table_name):
        Model.__init__(self, feature_set)
        self.predict_table_name = predict_table_name
        self.x = None
        self.y = None
        self.clf = None
        self.test_x = None
        self.test_y = None
        self.predict_res = None
        self.vectorizer = None

    def make_train_data(self, params):
        sql = "select * from " + self.feature_set.make(params, output_table=self.feature_set.name + "_train")
        data = SQLClient.execute(sql)
        self.x = [_[1:-1] for _ in data]
        self.y = [_[-1] for _ in data]

    def train(self):
        self.vectorizer = DictVectorizer()
        #self.x = self.vectorizer.fit_transform(self.x)
        self.clf = RandomForestRegressor(n_estimators=100, min_samples_leaf=2)
        self.clf.fit(self.x, self.y)
        if not os.path.exists(self.feature_set.name):
            os.mkdir(self.feature_set.name)
        joblib.dump(self.clf, self.feature_set.name+"/train_model.rf")

    def make_predict_data(self, params):
        sql = "select * from " + self.feature_set.make(params, output_table=self.feature_set.name + "_predict")
        data = SQLClient.execute(sql)
        self.test_x = [_[1:] for _ in data]
        #self.test_y = [_[] for_ in data]

    def predict(self):
        self.clf = joblib.load(self.feature_set.name + "/train_model.rf")
        #self.test_x = self.vectorizer.transform(self.test_x)
        self.predict_res = self.clf.predict(self.test_x)
        #print mean_squared_error(self.test_x, self.predict_res)




