from feature.feature_set import SQLFeatureSet
from datetime import timedelta
from io.sql import SQLClient


class FsSongFutureDaysBasicStatistics(SQLFeatureSet):

    def features(self):
        return ["play", "download", "collect"]

    def __init__(self, params):
        SQLFeatureSet.__init__(self, "song_future_%s_days_average_played_statistics" % params["days"],
                               self.features(), "song_id")
        self.params = params

    def make(self, params):
        output_name = "fs_" + self.name
        last_day = str(params["last_day"] + timedelta(self.params["days"])).replace("-", "")
        sql = """
        CREATE TABLE %s AS
        SELECT song_id,
               count(if(action = 0), 1, 0) / %s AS future_%s_days_average_played_person
        FROM %s
        GROUP BY song_id
        WHERE ds > %s and ds <= %s
       """ % (output_name, self.params["days"], self.params["days"], params["src"],
              params["last_day"], last_day)
        SQLClient.execute(sql)
        return output_name
