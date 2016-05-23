from feature.feature_set import SQLFeatureSet
from datetime import timedelta
from io.sql import SQLClient


class FsSongStatistics(SQLFeatureSet):

    def features(self):
        return ["play", "download", "collect"]

    def __init__(self, params):
        SQLFeatureSet.__init__(self, "song_basic_statistics",
                               self.features(), "song_id")
        self.params = params

    def make(self, params):
        output_name = "fs_" + self.name
        sql = """
        CREATE TABLE %s AS
        SELECT song_initial_plays,
            datediff(%s, publish_time) as publish_time
        FROM %s
       """ % (output_name, params["last_days"])
        SQLClient.execute(sql)
        return output_name
