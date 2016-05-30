import MySQLdb


override_mode = False


class SQLClient:

    def __init__(self):
        pass
   
    @staticmethod
    def set_mode(override):
        global override_mode
        override_mode = override        

    @staticmethod
    def get_db():
        return MySQLdb.connect(
            host="localhost", user="bxq", passwd="mengtaigu7", db="tianchi")

    @staticmethod
    def simple_join(target, tables, key, override=False):
        columns_set = set()
        columns = []
        for table in tables:
            with SQLClient.get_db() as db:
                db.execute("""
                    select column_name from information_schema.columns 
                    where table_name="%s" """ % table)
                cols = db.fetchall()
                for col in cols:
                    col = col[0]
                    if col == key:
                        continue
                    elif col in columns_set:
                        raise Exception("duplicate column '%s'" % col)
                    else:
                        columns.append(col)
                        columns_set.add(col)
        sql = "SELECT " + tables[0] + "." + key + "," + ",".join(columns) + "\n"
        sql += "FROM " + tables[0]
        for table in tables[1:]:
            sql += " INNER JOIN %s ON %s.%s=%s.%s " % (table, table, key, tables[0], key)
        SQLClient.create_table(target, sql, override)
    
    @staticmethod
    def create_table(name, sql, override=False, index=None):
        if override or override_mode:
            with SQLClient.get_db() as db:
                db.execute("drop table if exists %s" % name)
        sql = "CREATE TABLE IF NOT EXISTS %s AS \n%s" % (name, sql)
        SQLClient.execute(sql)
        if index is not None:
            with SQLClient.get_db() as db:
                db.execute("alter table %s add primary key(%s)" % (name, index))

    @staticmethod
    def execute(sql):
        print sql
        with SQLClient.get_db() as db:
            db.execute(sql)
            return db.fetchall()
        print
        print
