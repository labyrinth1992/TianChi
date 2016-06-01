import sys
sys.path.insert(0, "..")
from feature.per_song.fs_basic import FsSongBasicStatistics
from feature.per_song.fs_future_days import FsSongFutureDaysPlay
from feature.per_song.fs_combine import FsSimplePerSongLongRange, FsSimplePerSongShortRange
from feature.feature_set import SQLJoinFeatureSet
from models.simple_per_song_model import SimplePerSongModel
from utils.sql import SQLClient
from datetime import date, timedelta
from evaluation import evaluate


# parameters
#SQLClient.set_mode(True)
stage = 3
for_online = False
if for_online:
    train_action_table = "user_actions_global_train"
    target_action_table = "user_actions_global_target"
    test_action_table = "user_actions"
    test_target_table = None
    predict_table_prefix = "simple_per_song_global_predict"
    last_day = date(2015, 8, 30)
    train_last_day = date(2015, 6, 30)
else:
    train_action_table = "user_actions_local_train"
    target_action_table = "user_actions_local_target"
    test_action_table = "user_actions_local_test"
    test_target_table = "artist_play_local"
    predict_table_prefix = "simple_per_song_local_predict"
    last_day = date(2015, 6, 30)
    train_last_day = date(2015, 6, 30)


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
if stage < 1:
    params = {"last_day": train_last_day, "songs": "songs",
              "table": train_action_table, "target_table": target_action_table}
    for model in models:
        model.make_train_data(params)
        model.train()


# model predicting
if stage < 2:
    params = {"last_day": last_day, "songs": "songs", 
              "unknown_target": True, "table": test_action_table}
    for model in models:
        model.make_predict_data(params)
        model.predict()


# from song to artist
if stage < 3:
    SQLClient.create_table(
        name="tmp_per_model_predict",
        sql="""
        SELECT artist_id,
               sum(predict_1) AS predict_1,
               sum(predict_7) AS predict_7,
               sum(predict_60) AS predict_60
        FROM (
            SELECT artist_id, songs.song_id, %s.predict as predict_1, %s.predict as predict_7, %s.predict as predict_60 
            FROM songs INNER JOIN
                %s ON %s.song_id = songs.song_id INNER JOIN
                %s ON %s.song_id = songs.song_id INNER JOIN
                %s ON %s.song_id = songs.song_id
        ) AS x
        GROUP BY artist_id
        """ %
        (model_1_day.predict_table_name, model_7_day.predict_table_name, model_60_day.predict_table_name,
         model_1_day.predict_table_name, model_1_day.predict_table_name,
         model_7_day.predict_table_name, model_7_day.predict_table_name,
         model_60_day.predict_table_name, model_60_day.predict_table_name)
    )


# output phase with model averaging
if stage < 4:
    predicts = SQLClient.execute("SELECT * from tmp_per_model_predict")
    results = {}
    for predict in predicts:
        for days in range(1, 61):
            weights = [1.0 / (abs(days - c) + 1) for c in [1, 7, 20]]
            for i in range(3):
                weights[i] /= sum(weights)

            result = int(weights[0] * float(predict[1]) + weights[1] * float(predict[2]) + weights[2] * float(predict[3]))
            cur_date = last_day + timedelta(days)
            results[predict[0] + " " + str(cur_date).replace("-", "")] = result

    if for_online:
        pass
    else:
        goldens = SQLClient.execute("SELECT * from " + test_target_table)
        to_eval = {}
        for artist_id, d, golden in goldens:
            key = artist_id + " " + d
            if key not in results:
                continue
            to_eval[key] = (float(golden), results[key])
        to_eval = [(k.split(" ")[0], k.split(" ")[1], v[0], v[1]) for k, v in to_eval.items()]
        print evaluate(to_eval)
