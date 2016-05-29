from feature.feature_set import SQLFeatureSet
from datetime import timedelta
from utils.sql import SQLClient


class FsSongLastDaysBasicStatistics(SQLFeatureSet):

    def features(self):
        return ["play", "download", "collect"]

    def __init__(self, days):
        SQLFeatureSet.__init__(self, "fs_song_last_%s_days_basic_statistics" % days,
                               self.features(), "song_id")
        self.days = days

    def make(self, params):
        last_day = str(params["last_day"] - timedelta(self.days)).replace("-", "")
        sql = """
        SELECT song_id,
               count(if(action=0, 1, 0)) AS last_%s_day_play,
               count(if(action=1, 1, 0)) AS last_%s_day_download,
               count(if(action=2, 1, 0)) AS last_%s_day_collect
        FROM %s
        GROUP BY song_id
        WHERE ds > %s
       """ % (self.days, self.days, self.days, params["table"], last_day)
        SQLClient.create_table(self.name, sql)
        return self.name
