from sklearn.datasets import load_boston
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
from ensemble import stacking

# Prepare data
boston = load_boston()
X, y = boston.data, boston.target

# Make train/test split
# As usual in machine learning task we have X_train, y_train, and X_test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

print(X_train.shape)

# First-layer model
models_1 = [
    ExtraTreesRegressor(random_state=0, n_jobs=-1,
                        n_estimators=100, max_depth=3),

    RandomForestRegressor(random_state=0, n_jobs=-1,
                          n_estimators=100, max_depth=3),

    XGBRegressor(random_state=0, n_jobs=-1, learning_rate=0.1,
                 n_estimators=100, max_depth=3)
]
# Second-layer model
models_2 = [GradientBoostingRegressor(), SVR(), RandomForestRegressor()]

# Meta-layer model
meta_model = XGBRegressor(seed=0, n_jobs=-1, learning_rate=0.1, n_estimators=100, max_depth=3)

# Construct stacking
ensemble = stacking(X_train, y_train, X_test, bagged_pred=False,
                    regression=True,save_dir='.', metric=mean_absolute_error, n_folds=4,
                    shuffle=True, random_state=0, verbose=2)

# First layer
ensemble.add(models_1,propagate_features=[0, 1])

# we expect 5 columns as we propagate the 0 and 1 column of the first layer data
print(ensemble.next_train[:5])

if ensemble.next_train.shape[1] == 5:
    print("test the function of the propagate:")
    print("     pass the test!")

# Second layer
ensemble.add(models_2, subset=[0, 1], propagate_features=[0])
print("test the function of the subset")
print(ensemble.next_train[:5])

# Meta layer
y_pred = ensemble.add_meta(meta_model)

print('Final prediction score: [%.8f]' % mean_absolute_error(y_test, y_pred))

