from feature.feature_set import SQLJoinFeatureSet
from feature.per_song.fs_last_days import FsSongLastDaysBasicStatistics
from feature.per_song.fs_person_days import FsSongPersonLastDaysBasicStatistics


class FsSimplePerSongShortRange(SQLJoinFeatureSet):

    def __init__(self):
        SQLJoinFeatureSet.__init__(
            self,
            "fs_simple_per_song_short_range",
            [
                FsSongLastDaysBasicStatistics(3),
                FsSongLastDaysBasicStatistics(7),
                FsSongPersonLastDaysBasicStatistics(3),
                FsSongPersonLastDaysBasicStatistics(7),
            ]
        )


class FsSimplePerSongLongRange(SQLJoinFeatureSet):

    def __init__(self):
        SQLJoinFeatureSet.__init__(
            self,
            "fs_simple_per_song_long_range",
            [
                FsSongLastDaysBasicStatistics(14),
                FsSongLastDaysBasicStatistics(30),
                FsSongLastDaysBasicStatistics(60),
                FsSongLastDaysBasicStatistics(120),
                FsSongPersonLastDaysBasicStatistics(14),
                FsSongPersonLastDaysBasicStatistics(30),
                FsSongPersonLastDaysBasicStatistics(60),
                FsSongPersonLastDaysBasicStatistics(120),
            ]
        )
