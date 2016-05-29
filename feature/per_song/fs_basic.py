from feature.feature_set import SQLFeatureSet
from utils.sql import SQLClient


class FsSongBasicStatistics(SQLFeatureSet):

    def features(self):
        return ["song_initial_plays", "publish_time"]

    def __init__(self):
        SQLFeatureSet.__init__(self, "fs_song_basic_statistics",
                               self.features(), "song_id")

    def make(self, params):
        sql = """
        SELECT song_initial_plays,
            datediff("%s", publish_time) as publish_time
        FROM %s
       """ % (params["last_day"], params["songs"])
        SQLClient.create_table(self.name, sql)
        return self.name
