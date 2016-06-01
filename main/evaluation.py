def evaluate(result):
    pre_artist_id = result[0][0]
    artist_var = []
    artist_fi = []
    now_var = 0.
    artist_num = 0.
    now_fi = 0.
    for artist_id, today_date, gold, prev in result:
        if artist_id != pre_artist_id:
            artist_var.add((now_var / artist_num**0.5))
            artist_fi.add((now_fi**0.5))
            now_var = 0.
            now_fi = 0.
            artist_num = 0.
            pre_artist_id = artist_id
        now_var = now_var + ((gold - prev)/(gold * 1.0))**2
        now_fi = now_fi + gold
        artist_num = artist_num + 1.

    ans = 0.
    for var, fi in zip(artist_var, artist_fi):
        ans = ans + (1 - var) * fi
    return ans

