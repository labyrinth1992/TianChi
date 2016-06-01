import sys
sys.path.insert(0, "..")
from utils.sql import SQLClient


#SQLClient.set_mode(False)
SQLClient.create_table('user_actions_global_train',
                       'select * from user_actions where ds <= "20150630"', index="song_id")
SQLClient.create_table('user_actions_global_target',
                       'select * from user_actions where ds > "20150630"', index="song_id") 

songs = SQLClient.execute("select count(distinct song_id) from songs")[0][0]
SQLClient.create_table('tmp_local_song_ids_1',
                       'select song_id from songs order by rand() limit %d' % (songs*3/4), index="song_id")
SQLClient.create_table('tmp_local_song_ids_2',
                       '''select songs.song_id from songs
                       left join tmp_local_song_ids_1
                       on songs.song_id = tmp_local_song_ids_1.song_id
                       where tmp_local_song_ids_1.song_id is null
                    ''', index="song_id")

SQLClient.simple_join("tmp_user_actions_local_train", ["user_actions", "tmp_local_song_ids_1"], "song_id")
SQLClient.create_table('user_actions_local_train', 'select * from tmp_user_actions_local_train where ds <= "20150630"', index="song_id")
SQLClient.create_table('user_actions_local_target', 'select * from tmp_user_actions_local_train where ds > "20150630"', index="song_id")
SQLClient.simple_join("tmp_user_actions_local_test", ["user_actions", "tmp_local_song_ids_2"], "song_id")
SQLClient.create_table('user_actions_local_test', 'select * from tmp_user_actions_local_test where ds <= "20150630"', index="song_id")

SQLClient.create_table("artist_play_local", 
    """select artist_id, ds, sum(if(action_type=1,1,0)) 
       from tmp_user_actions_local_test as x inner join songs 
       on x.song_id = songs.song_id 
       where ds > "20150630" 
       group by artist_id, ds""")
