import sys
sys.path.insert(0, "..")
from feature.per_song.fs_basic import FsSongBasicStatistics
from feature.per_song.fs_future_days import FsSongFutureDaysPlay
from feature.per_song.fs_combine import FsSimplePerSongLongRange, FsSimplePerSongShortRange
from feature.feature_set import SQLJoinFeatureSet
from models.simple_per_song_model import SimplePerSongModel
from utils.sql import SQLClient
from datetime import datetime, timedelta


# parameters
for_online = True
if for_online:
    train_action_table = "user_actions_global_train"
    target_action_table = "user_actions_global_target"
    test_action_table = "user_actions"
    test_target_table = None
    predict_table_prefix = "simple_per_song_global_predict"
    last_day = datetime(2015, 6, 30)
    train_last_day = datetime(2015, 6, 30)
else:
    train_action_table = "user_actions_local_train"
    target_action_table = "user_actions_local_target"
    test_action_table = "user_actions_local_test"
    test_target_table = "artist_play_local"
    predict_table_prefix = "simple_per_song_local_predict"
    last_day = datetime(2015, 8, 30)
    train_last_day = datetime(2015, 6, 30)


# make feature sets
basic_fs = FsSongBasicStatistics()
long_range_fs = FsSimplePerSongLongRange()
short_range_fs = FsSimplePerSongShortRange()
feature_set_1_day = SQLJoinFeatureSet("fs_1_day", [long_range_fs, short_range_fs, FsSongFutureDaysPlay(1)])
feature_set_7_day = SQLJoinFeatureSet("fs_7_day", [long_range_fs, short_range_fs, FsSongFutureDaysPlay(7)])
feature_set_60_day = SQLJoinFeatureSet("fs_60_day", [long_range_fs, FsSongFutureDaysPlay(60)])


# make models
model_1_day = SimplePerSongModel(feature_set_1_day, predict_table_name=predict_table_prefix + "_1")
model_7_day = SimplePerSongModel(feature_set_7_day, predict_table_name=predict_table_prefix + "_7")
model_60_day = SimplePerSongModel(feature_set_60_day, predict_table_name=predict_table_prefix + "_60")
models = {model_1_day, model_7_day, model_60_day}


# model training
params = {"last_day": train_last_day, "songs": "songs",
          "table": train_action_table, "target_table": target_action_table}
for model in models:
    model.make_train_data(params)
    model.train()


# model predicting
params = {"last_day": last_day, "songs": "songs", "unknown_target": True,
          "aim": for_online, "table": test_action_table}
for model in models:
    model.make_predict_data(params)
    model.predict()


# from song to artist
SQLClient.create_table(
    name="tmp_per_model_predict",
    sql="""
        SELECT artist_id,
               sum(%s.predict) AS predict_1,
               sum(%s.predict) AS predict_7,
               sum(%s.predict) AS predict_60
        FROM (
            SELECT artist_id, songs.song_id, %s.predict, %s.predict, %s.predict
            FROM songs INNER JOIN
                %s ON %s.song_id = songs.song_id INNER JOIN
                %s ON %s.song_id = songs.song_id INNER JOIN
                %s ON %s.song_id = songs.song_id
        )
        GROUP BY artist_id
    """ %
        (model_1_day.predict_table_name, model_7_day.predict_table_name, model_60_day.predict_table_name,
         model_1_day.predict_table_name, model_7_day.predict_table_name, model_60_day.predict_table_name,
         model_1_day.predict_table_name, model_1_day.predict_table_name,
         model_7_day.predict_table_name, model_7_day.predict_table_name,
         model_60_day.predict_table_name, model_60_day.predict_table_name)
)


# output phase with model averaging
predicts = SQLClient.execute("SELECT * from tmp_per_model_predict")
start_date = datetime(2015, 9, 1)
results = {}
for predict in predicts:
    for days in range(1, 61):

        weights = [1.0 / abs(days - c + 1) for c in [1, 7, 20]]
        for i in range(3):
            weights[i] /= sum(weights)

        result = int(weights[0] * predict[1] + weights[1] * predict[2] + weights[2] * predict[3])
        cur_date = start_date + timedelta(days)
        results[predict[0] + " " + str(cur_date).replace("-", "")] = result

if for_online:
    SQLClient.execute("""

    """)
else:
    goldens = SQLClient.execute("SELECT * from " + test_target_table)
    for golden in goldens:
        golden_play = golden[2]
        predict_play = results[predict[0] + " " + golden[1]]

