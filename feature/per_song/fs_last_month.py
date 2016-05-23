from feature.feature_set import SQLFeatureSet


class FsSongLastMonthBasicStatistics(SQLFeatureSet):

    def features(self):
        return ["play", "download", "collect"]

    def __init__(self):
        SQLFeatureSet.__init__(self, "song_last_month_basic_statistics", self.features(), "song_id")

    def make(self, tables):
        sql = """
        SELECT song_id, count(if(action=0, 1, 0)), count(if(action=1, 1, 0)), count(if(action=2, 1, 0))
        FROM %s
        GROUP BY song_id 
        WHERE time > 0
       """ % tables["src"]
