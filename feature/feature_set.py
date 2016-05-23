class FeatureSet:
    def features(self):
        return []

    def __init__(self, name, features):
        self.name = name
        self.features = features


class SQLFeatureSet(FeatureSet):
    def __int__(self, name, features, key):
        FeatureSet.__init__(self, name, features)


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
        SQLFeatureSet.__init__(name, features, key)
        self.sub_feature_sets = sub_feature_sets

    def make(self, tables):
        input_tables = []
        for fs in self.sub_feature_sets:
            input_tables.append(fs.make(tables))










