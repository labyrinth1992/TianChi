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
                    dfs(fs.sub_feature_sets)
                else:
                    input_tables.append(fs.make(params))
        dfs(self.sub_feature_sets)

        SQLClient.simple_join(self.name, input_tables, self.key)
        return self.name











