import pandas as pd

def weighted_average(df, target_cols, weight_col):
    if isinstance(target_cols, str):
        # Single column
        return (df[target_cols] * df[weight_col]).sum() / df[weight_col].sum()
    else:
        # Multiple columns
        w = df[weight_col]
        return (df[target_cols].mul(w, axis=0).sum() / w.sum())

def weighted_average_group(df, group_cols, target_cols, weight_col):
    # If you just use .apply() wihtout then lambda, it will split it into each group and not a final single data set
    # Need to also add the mapping to the weighted average it wont take the same naming from the def
    # then x will act as a loop for x of groups:

    result = df.groupby(group_cols).apply(lambda x: weighted_average(x, target_cols=target_cols, weight_col=weight_col),include_groups=False).reset_index()
    result = result.rename(columns={col: f'WA_{col}' for col in target_cols}) #<- can use the for col in x then loop the rename

    return result


# # Dummy dataframe
# data = {
#     'balance': [10, 20, 30, 40],
#     'metric': [1, 2, 3, 4],
#     'WAL': [1.5, 2.5, 3.5, 4.5],
#     'grp': ['a', 'b', 'c', 'd'],
#     'grp2': ['hi', 'dddd', 'bye','dd']
# }
# df = pd.DataFrame(data)
#
# test = weighted_average_group(df, group_cols=['grp','grp2'], target_cols=["metric"], weight_col="balance")
# print(test)


