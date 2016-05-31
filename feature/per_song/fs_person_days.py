from feature.feature_set import SQLFeatureSet
from datetime import timedelta
from utils.sql import SQLClient


class FsSongPersonLastDaysBasicStatistics(SQLFeatureSet):

    def features(self):
        return ["play", "download", "collect"]

    def __init__(self, days):
        SQLFeatureSet.__init__(self, "fs_song_last_%s_days_played_person_statistics" % days,
                               self.features(), "song_id")
        self.days = days

    def make(self, params):
        last_day = str(params["last_day"] - timedelta(self.days)).replace("-", "")
        sql = """
        SELECT song_id,
               count(distinct user_id) AS last_%s_days_played_person
        FROM %s 
        WHERE ds > "%s" and action_type = 1 
        GROUP BY song_id
       """ % (self.days, params["table"], last_day)
        SQLClient.create_table(self.name, sql, index=self.key)
        return self.name

