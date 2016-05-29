from utils.sql import SQLClient


class FeatureSet:
    def features(self):
        return []

    def __init__(self, name, features):
        self.name = name
        if isinstance(features, str):
            features = [features]
        self.sub_features = features

    def is_target_feature(self):
        return False


class SQLFeatureSet(FeatureSet):
    def __init__(self, name, features, key):
        FeatureSet.__init__(self, name, features)
        self.key = key


class SQLJoinFeatureSet(SQLFeatureSet):
    def __init__(self, name, sub_feature_sets):
        features = []
        key = None
        for fs in sub_feature_sets:
            if key is None:
                key = fs.key
            elif key != fs.key:
                raise Exception("sub SQLFeatureSets have inconsistent key column")
            for f in fs.features():
                features.append(fs.name + "." + f)
        SQLFeatureSet.__init__(self, name, features, key)
        self.sub_feature_sets = sub_feature_sets

    def make(self, params):
        input_tables = []

        def dfs(sub_feature_sets):
            for fs in sub_feature_sets:
                if fs.is_target_feature() and params.get("unknown_target", False):
                    continue
                elif isinstance(fs, SQLJoinFeatureSet):
                    dfs(fs)
                else:
                    input_tables.append(fs.make(params))
        dfs(self.sub_feature_sets)

        columns = set()
        for table in input_tables:
            cols = SQLClient.execute('select column_names from information_schema.columns '
                                     'where table_name="%s"' % table)
            for col in cols:
                if col == self.key:
                    continue
                elif col in columns:
                    raise Exception("duplicate column '%s'" % col)
                else:
                    columns.add(col)
        sql = "CREATE TABLE %s AS SELECT " % self.name
        sql += input_tables[0] + "." + self.key + ","
        sql += ",".join(columns)
        sql += " FROM " + input_tables[0]
        for table in input_tables[1:]:
            sql += " INNER JOIN %s ON %s.%s=%s.%s " % (table, table, self.key, input_tables[0], self.key)
        sql += ";"
        SQLClient.execute(sql)
        return self.name











