import pandas as pd

df = pd.DataFrame({
    "country": ["USA", "Canada", "USA", "Mexico"],
    "population": [1200000, 500000, 2000000, 800000]
})

print(df.head())

filter_dict = {"country":"USA", "population":"<1200001"}

def filtered_df(df, condition_dict):
    ## 1. start with all True - this is because the mask will then be updated to false when not true by a conditon, so reduction logic used

    mask = pd.Series(True, index=df.index) # settign all the data to true <- need the series to loop through all the data and get the TRUE / FALSE array

    ## 2. loop the dictionary
    #Basic Loop to print all the values in a dict, using just x will give the cols, and then [x] will loop the dict itself, think of series and dataframe
    #for x in condition_dict:
    #    print(condition_dict[x])

    ##Adding in the naming to show what the conditions are, col = both columns, condito is both rows(thiking more table logic than dict) i.e df[col] is both country then pop /
    ## the cond part would be both USA and >10K.

    #for col, cond, in condition_dict.items():
    #    print("Column", col)
    #    print("Condition", cond)

    ##First case - need ot use the cond as string, as say >1000
    # for col, cond in condition_dict.items():
    #     # Detect comparison vs exact match
    #     if isinstance(cond, str) and cond[0] in [">", "<"]:
    #         print(col, "is a comparison condition:", cond)
    #     else:
    #         print(col, "is an exact-match condition:", cond)

    # Loop through each column and its condition
    for col, cond in condition_dict.items(): #.items() to loop through the actual parts of the dict

        # Step 2a: Check if the condition is a comparison (starts with > or <)
        if isinstance(cond, str) and cond[0] in [">", "<"]:
            operator = cond[0]  # Extract operator - this is the first value of the string
            value = float(cond[1:])  # Extract numeric value - this takes anything past the first value so the numeric (wont work if >= then)

            # Apply the comparison and update the mask
            ## READ FUTURE ANDY --> &= updates the mask --> mask &= df[col] == cond is shorthand for: mask = mask & (df[col] == cond)

            if operator == ">":
                mask &= df[col] > value  # Keep rows where column > value
            elif operator == "<":
                mask &= df[col] < value  # Keep rows where column < value

        # Step 2b: Otherwise it's an exact match
        else:
            mask &= df[col] == cond  # Keep rows where column == value

        # Debug: Uncomment to see the mask after each condition
        print(f"After {col} filter, mask is:\n{mask}\n")

    # Step 3: Apply the final mask to the DataFrame
    filtered_df = df[mask]

    # Step 4: Return the filtered DataFrame
    return filtered_df


test = filtered_df(df, filter_dict)
print(test)