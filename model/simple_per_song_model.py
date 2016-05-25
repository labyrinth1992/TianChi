from model.model import Model


class SimplePerSongModel(Model):

    def __init__(self, feature_set, predict_table_name):
        Model.__init__(self, feature_set)
        self.predict_table_name = predict_table_name

