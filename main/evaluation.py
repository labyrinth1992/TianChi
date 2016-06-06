def evaluate(result):
    print "evaluate for %d artists" % len(result)
    pre_artist_id = result[0][0]
    ans = 0.
    now_var = 0.
    artist_num = 0.
    now_fi = 0.
    for artist_id, today_date, gold, prev in result:
        if gold == 0.:
            continue
        if artist_id != pre_artist_id:
            ans = ans + (1 - (now_var / artist_num) ** 0.5 ) * (now_fi ** 0.5)
            now_var = 0.
            now_fi = 0.
            artist_num = 0.
            pre_artist_id = artist_id
        now_var = now_var + ((gold - prev)/(gold * 1.0))**2
        now_fi = now_fi + gold
        artist_num = artist_num + 1.
    ans = ans + (1 - (now_var / artist_num) ** 0.5 ) * (now_fi ** 0.5)
    return ans

