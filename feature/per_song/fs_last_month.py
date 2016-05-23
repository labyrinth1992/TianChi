from feature.feature_set import SQLFeatureSet
from io.sql import SQLClient

class FsSongLastMonthBasicStatistics(SQLFeatureSet):

    def features(self):
        return ["play", "download", "collect"]

    def __init__(self):
        SQLFeatureSet.__init__(self, "song_last_month_basic_statistics", self.features(), "song_id")

    def make(self, params):
        output_name = "fs_" + self.name
        sql = """
        CREATE TABLE %s AS
        SELECT song_id, count(if(action=0, 1, 0)) AS last_month_play,
                        count(if(action=1, 1, 0)) AS last_month_download,
                        count(if(action=2, 1, 0)) AS last_month_collect
        FROM %s
        GROUP BY song_id
        WHERE ds > 0 AND ds < 0
       """ % (output_name, params["src"])
        SQLClient.execute(sql)
        return output_name
