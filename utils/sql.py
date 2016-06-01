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
        SQLClient.create_table(target, sql, override, index=key)
    
    @staticmethod
    def create_table(name, sql, override=False, index=None):
        with SQLClient.get_db() as db:
            exist = db.execute("select TABLE_NAME from INFORMATION_SCHEMA.TABLES where TABLE_NAME='%s'" % name) > 0
            if exist and (override or override_mode):
                db.execute("drop table if exists %s" % name)
                exist = False
            if exist:
                print "table '%s' already exists" % name
            else:
                sql = "CREATE TABLE IF NOT EXISTS %s AS \n%s" % (name, sql)
                print sql
                db.execute(sql)
                if index is not None:
                    db.execute("alter table %s add index(%s)" % (name, index))
            print

    @staticmethod
    def insert(name, schema, items):
        with SQLClient.get_db() as db:
            cols = ",".join([n + " " + t for n, t in schema])
            db.execute("CREATE TABLE IF NOT EXISTS %s (%s)" % (name, cols))
            db.executemany("INSERT INTO %s (%s) VALUES (%s)" % (name, ",".join([n for n, _ in schema]), ",".join(["%s" for _ in schema])), 
                           items)

    @staticmethod
    def execute(sql):
        print sql
        with SQLClient.get_db() as db:
            db.execute(sql)
            results = db.fetchall()
        print
        return results
