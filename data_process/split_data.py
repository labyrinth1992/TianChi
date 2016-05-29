from io.sql import SQLClient


SQLClient.create_table('user_actions_global_train',
                       'select * from user_action where ds <= "2015630"')
SQLClient.create_table('user_actions_global_target',
                       'select * from user_action where ds > "2015630"')

SQLClient.create_table('tmp_local_song_ids_1',
                       'select song_id from songs order by rand()')
SQLClient.create_table('tmp_local_song_ids_2',
                       '''select songs.song_id from songs
                       left join tmp_local_song_ids_1
                       on songs.song_id = tmp_local_song_ids_1.song_id
                       where tmp_local_song_ids_1.song_id is null
                    ''')
SQLClient.create_table('user_actions_local_train',
                       '''select * from user_action
                       inner join tmp_local_song_ids_1
                       on user_action.song_id = tmp_local_song_ids_1.song_id
                       where ds <= "2015630"
                    ''')
SQLClient.create_table('user_actions_local_target',
                       '''select * from user_action
                       inner join tmp_local_song_ids_1
                       on user_action.song_id = tmp_local_song_ids_1.song_id
                       where ds > "2015630"
                    ''')
SQLClient.create_table('user_actions_local_test',
                       '''select * from user_action
                       inner join tmp_local_song_ids_2
                       on user_action.song_id = tmp_local_song_ids_2.song_id
                       where ds <= "2015630"
                    ''')
