import pickle
import argparse
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import RobustScaler, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.decomposition import PCA


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-d", "--data_path", default=".", type=str, help="train.csv directory"
    )
    argparser.add_argument(
        "-m", "--model_path", default=".", type=str, help="model directory"
    )
    args = argparser.parse_args()

    data_path = args.data_path
    model_path = args.model_path

    train_data = pd.read_csv(data_path + "/train.csv")
    X, y = train_data.drop(columns=["Survived"]), train_data["Survived"]

    # Слишком много пропусков
    X.drop(["Cabin"], axis=1, inplace=True)

    # Слишком мало полезности
    X.drop(["Ticket"], axis=1, inplace=True)

    X.drop(["Name"], axis=1, inplace=True)

    cat_cols = ["Embarked", "Sex", "Pclass"]
    cat_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse=False)),
            ("pca", PCA(n_components=8)),
        ]
    )

    num_cols = ["Age", "Fare"]
    num_transformer = Pipeline(
        steps=[("imputer", KNNImputer(n_neighbors=5)), ("scaler", RobustScaler())]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, num_cols),
            ("cat", cat_transformer, cat_cols),
        ]
    )

    clf = Pipeline(
        steps=[("preprocessor", preprocessor), ("classifier", RandomForestClassifier())]
    )

    num_transformer_dist = {
        "preprocessor__num__imputer__n_neighbors": list(range(2, 15)),
        "preprocessor__num__imputer__add_indicator": [True, False],
    }

    cat_transformer_dist = {
        "preprocessor__cat__imputer__strategy": ["most_frequent", "constant"],
        "preprocessor__cat__imputer__add_indicator": [True, False],
        "preprocessor__cat__pca__n_components": list(range(2, 8)),
    }

    random_forest_dist = {
        "classifier__n_estimators": list(range(50, 500)),
        "classifier__max_depth": list(range(2, 20)),
        "classifier__bootstrap": [True, False],
    }

    param_dist = {**num_transformer_dist, **cat_transformer_dist, **random_forest_dist}

    random_search = RandomizedSearchCV(
        clf, param_distributions=param_dist, n_iter=100, n_jobs=-1, scoring="accuracy"
    )

    random_search.fit(X, y)

    print(random_search.best_score_)

    full_path = f"{model_path}/serialized_model.sav"
    pickle.dump(random_search, open(full_path, "wb"))


if __name__ == "__main__":
    main()
