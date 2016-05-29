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
        GROUP BY song_id
        WHERE ds > %s and action = 0
       """ % (self.days, params["table"], last_day)
        SQLClient.create_table(self.name, sql)
        return self.name

    def is_target_feature(self):
        return True
