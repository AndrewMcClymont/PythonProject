import pandas as pd
import yaml

def load_boe_mapping(filepath="/Users/andrewmcclymont/PycharmProjects/PythonProject/European_RMBS_Model/Config/Mappings.yaml"):
    import yaml
    with open(filepath) as f:
        return yaml.safe_load(f)

def apply_boe_mapping(df,column_mapping, mappings, default_value=999):
    for df_col, yaml_key in column_mapping.items():
        if df_col in df.columns and yaml_key in mappings:
            df[df_col + "_mapped"] = df[df_col].map(mappings[yaml_key]).fillna(default_value)
        else:
            print(f"Warning: column '{df_col}' or mapping '{yaml_key}' not found")
    return df