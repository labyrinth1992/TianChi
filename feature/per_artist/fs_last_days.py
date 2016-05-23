from feature.feature_set import SQLFeatureSet
from datetime import timedelta
from io.sql import SQLClient


class FsSongLastDaysBasicStatistics(SQLFeatureSet):

    def features(self):
        return ["play", "download", "collect"]

    def __init__(self, params):
        SQLFeatureSet.__init__(self, "artist_last_%s_days_basic_statistics" % params["days"],
                               self.features(), "song_id")
        self.params = params

    def make(self, params):
        output_name = "fs_" + self.name
        last_day = str(params["last_day"] - timedelta(self.params["days"])).replace("-", "")
        sql = """
        CREATE TABLE %s AS
        SELECT song_id,
               count(if(action=0, 1, 0)) AS artist_last_%s_day_play,
               count(if(action=1, 1, 0)) AS artist_last_%s_day_download,
               count(if(action=2, 1, 0)) AS artist_last_%s_day_collect
        FROM %s
        GROUP BY artist_id
        WHERE ds > %s
       """ % (output_name, self.params["days"], self.params["days"], self.params["days"], params["src"], last_day)
        SQLClient.execute(sql)
        return output_name
