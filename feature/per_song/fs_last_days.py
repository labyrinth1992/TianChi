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
               sum(if(action_type=1, 1, 0)) AS last_%s_day_play,
               sum(if(action_type=2, 1, 0)) AS last_%s_day_download,
               sum(if(action_type=3, 1, 0)) AS last_%s_day_collect
        FROM %s
        WHERE ds > "%s"  
        GROUP BY song_id 
       """ % (self.days, self.days, self.days, params["table"], last_day)
        SQLClient.create_table(self.name, sql, index=self.key)
        return self.name
