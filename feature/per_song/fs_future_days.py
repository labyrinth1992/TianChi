from feature.feature_set import SQLFeatureSet
from datetime import timedelta
from utils.sql import SQLClient


class FsSongFutureDaysPlay(SQLFeatureSet):

    def __init__(self, days):
        SQLFeatureSet.__init__(self, "fs_song_future_%s_days_average_play" % days, "days", "song_id")
        self.days = days

    def make(self, params):
        last_day = str(params["last_day"] + timedelta(self.days)).replace("-", "")
        sql = """
        SELECT song_id,
               sum(if(action_type = 1, 1.0, 0))/%s AS future_%s_days_average_play 
        FROM %s 
        WHERE ds <= "%s" 
        GROUP BY song_id
       """ % (self.days, self.days, params["target_table"],  last_day)
        SQLClient.create_table(self.name, sql)
        return self.name
