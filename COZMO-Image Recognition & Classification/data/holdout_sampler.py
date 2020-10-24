import pandas as pd
from sklearn.model_selection import train_test_split

# Paths to full dataset
X_WHOLE_PATH = "./whole_set/digits.csv"
Y_WHOLE_PATH = "./whole_set/labels.csv"

# Paths where subsets are to be saved
X_TRAIN_SUBSET_PATH = "./train/X_train.csv"
Y_TRAIN_SUBSET_PATH = "./train/y_train.csv"
X_TEST_SUBSET_PATH = "./test/X_test.csv"
Y_TEST_SUBSET_PATH = "./test/y_test.csv"
X_VAL_SUBSET_PATH = "./validate/X_val.csv"
Y_VAL_SUBSET_PATH = "./validate/y_val.csv"

# Load full dataset in DataFrames
x_data = pd.read_csv(X_WHOLE_PATH)
y_data = pd.read_csv(Y_WHOLE_PATH)

# Split full data set between training and holdout data
X_train, X_holdout, y_train, y_holdout = train_test_split(x_data, y_data, test_size=0.33, random_state=42)

# Split holdout data between test and validation
X_test, X_val, y_test, y_val = train_test_split(X_holdout, y_holdout, test_size=0.5, random_state=42)

print("X_train size : " + str(len(X_train)))
print("y_train size : " + str(len(y_train)))
print("X_test size : " + str(len(X_test)))
print("X_val size : " + str(len(X_val)))
print("y_test size : " + str(len(y_test)))
print("y_val size : " + str(len(y_val)))

total = len(X_train) + len(X_test) + len(X_val)
print("Total size : " + str(total))

# Save train data to csv
X_train.to_csv(X_TRAIN_SUBSET_PATH)
y_train.to_csv(Y_TRAIN_SUBSET_PATH)

# Save test data to csv
X_test.to_csv(X_TEST_SUBSET_PATH)
y_test.to_csv(Y_TEST_SUBSET_PATH)

# Save validation data to csv
X_val.to_csv(X_VAL_SUBSET_PATH)
y_val.to_csv(Y_VAL_SUBSET_PATH)
