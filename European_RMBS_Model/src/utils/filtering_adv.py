import pandas as pd

def filter_df(df, condition_dict):
    """
    Filters a DataFrame based on a dictionary of conditions.

    Args:
        df (pd.DataFrame): Input DataFrame
        condition_dict (dict): Dictionary of filters
                               key = column name
                               value = condition
                               condition can be:
                               - Exact match: "USA"
                               - Comparison: ">1000", "<=50", etc.

    Returns:
        pd.DataFrame: Filtered DataFrame
    """

    # Step 1: Start with a mask of all True
    # Hint: use pd.Series with index=df.index
    mask = pd.Series(data=True, index=df.index)

    # Step 2: Loop through the condition dictionary
    for col, cond in filter_dict.items():
        print('Column',col)
        print('Condition',cond)

        # Check if the first two characters are a >= or <= -- using the isinstance to make sure the string part is due to >, could jsut be 10, which is where the last else is used

        if isinstance(cond,str) and cond[0:2] in ['<=','>=']:
            operator = cond[:2]
            value = float(cond[2:])
        elif isinstance(cond,str) and cond[0:1] in ['<','>']:
            operator = cond[0:1] #or could state 0
            value = float(cond[1:])
        else:
            operator = '=='
            value = cond

        if operator == '<':
            mask &= df[col] < value
        elif operator == '>':
            mask &= df[col] > value
        elif operator == '<=':
            mask &= df[col] <= value
        elif operator == '>=':
            mask &= df[col] >= value
        else:
            mask &= df[col] == cond #need to make equal to cond here as if no operator the value would be null

        # Optional: print mask after each condition to debug
        print(mask)

    filtered_df = df[mask]

    return filtered_df


# # Example DataFrame
# df = pd.DataFrame({
#     "country": ["USA", "Canada", "USA", "Mexico"],
#     "population": [1200000, 500000, 2000000, 800000]
# })
#
# # Example filter dictionary
# filter_dict = {"country": "USA", "population": ">=1000000"}
# test = filter_df(df, filter_dict)
# print(test)
