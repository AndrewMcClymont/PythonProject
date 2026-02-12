import yaml

#ChatGPT version for any yaml

def map_any_yaml(df, yaml_file, column_to_yaml_map, default_value=999):
    """
    Map any DataFrame columns to text labels using any YAML mapping.

    Args:
        df (pd.DataFrame): DataFrame to map
        yaml_file (str): path to YAML file with mappings
        column_to_yaml_map (dict): {df_col_name: yaml_section_key}
        default_value: value for codes not found in mapping (default 999)

    Returns:
        pd.DataFrame: DataFrame with new '_mapped' columns
    """
    # Load YAML once
    with open(yaml_file, "r") as f:
        mappings = yaml.safe_load(f)

    # Loop through each column mapping
    for df_col, yaml_key in column_to_yaml_map.items():
        if df_col in df.columns and yaml_key in mappings:
            df[df_col + "_mapped"] = df[df_col].map(mappings[yaml_key]).fillna(default_value)
        else:
            print(f"Warning: df column '{df_col}' or YAML section '{yaml_key}' not found")

    return df

import pandas as pd

# # Example DataFrame with weird column names
# df = pd.DataFrame({
#     "erveefer": [1, 2, 7, 99],
#     "int_type_col": [1, 2, 1, 5],
#     "index_col": [11, 12, 11, 13]
# })
#
# # Mapping of DataFrame columns to YAML sections
# column_to_yaml_map = {
#     "erveefer": "repayment_method",
#     "int_type_col": "interest_type",
#     "index_col": "index_mapping"
# }
#
# # Apply mappings from YAML
# df = map_any_yaml(df, "/path/to/Mappings.yaml", column_to_yaml_map, default_value=999)
#
# print(df)
