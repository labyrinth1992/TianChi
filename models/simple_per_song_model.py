import numpy
from models.model import Model
from utils.sql import SQLClient
from sklearn.ensemble import RandomForestRegressor


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

    def make_train_data(self, params):
        sql = "select * from " + self.feature_set.make(params, output_table=self.feature_set.name + "_train")
        data = SQLClient.execute(sql)
        self.x = [_[1:-1] for _ in data]
        self.y = [_[-1] for _ in data]

    def train(self):
        self.x = numpy.asarray(self.x)
        self.clf = RandomForestRegressor(n_estimators=100, min_samples_leaf=2)
        self.clf.fit(self.x, self.y)

    def make_predict_data(self, params):
        sql = "select * from " + self.feature_set.make(params, output_table=self.feature_set.name + "_predict")
        data = SQLClient.execute(sql)
        self.test_x = [_[1:-1] for _ in data]
        self.test_y = [_[-1] for _ in data]

    def predict(self):
        test_x = self.clf.fit_transform(self.test_x)
        self.predict_res = self.clf.predict(test_x)
        print self.predict_res

