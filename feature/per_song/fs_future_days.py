from feature.feature_set import SQLFeatureSet
from datetime import timedelta
from io.sql import SQLClient


class FsSongFutureDaysPlay(SQLFeatureSet):

    def __init__(self, days):
        SQLFeatureSet.__init__(self, "fs_song_future_%s_days_average_play" % days, "days", "song_id")
        self.days = days

    def make(self, params):
        last_day = str(params["last_day"] + timedelta(self.days)).replace("-", "")
        sql = """
        SELECT song_id,
               count(if(action = 0), 1, 0) / %s AS future_%s_days_average_play
        FROM %s
        GROUP BY song_id
        WHERE ds > %s
       """ % (self.days, self.days, params["target_table"],  last_day)
        SQLClient.create_table(self.name, sql)
        return self.name