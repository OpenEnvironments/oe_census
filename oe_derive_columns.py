import sys
import pandas as pd
import numpy as np
from io import StringIO
from contextlib import redirect_stdout

def oe_derive_columns(df, rules):
    """
    This function calculates new columns in a dataframe dfd on a set of rules.

    :param df: the original dataframe providing the columns upon which derivation rules are applied.
    :type df: dataframe

    :param rules: the derivation rules as a list of text
        to be executed on a generic dataframe named "df"
        using pandas or numpy functions
    :type rules: list

    :returns df: the original dataframe with new derived columns.
    :type df: dataframe

    :returns rulestatus: The "passed" or "failed" result of each rule applied.
    :type rulestatus: list

    """

    # parameter testing
    if not isinstance(df, pd.DataFrame):
            sys.exit("The first parameter (df) has an invalid type. Expecting a pandas dataframe.")
    if not isinstance(rules, list):
            sys.exit("The second parameter (rules) has an invalid type. Expecting a list of rules.")

    print("Applying",len(rules),"rules to the dataset:")
    rulestatus = {}
    old_stdout = sys.stdout
    count = 0
    try: 
        f = StringIO()
        for rule in rules:
            if rule[0] != "#":  # allow for comment lines
                count += 1
                print(str(count)+",", end="")
                try:
                    with redirect_stdout(f):
                        exec(rule)
                        rulestatus[rule] = "passed"
                except:
                    rulestatus[rule] = "failed"
    except:
        sys.stdout = old_stdout
    sys.stdout = old_stdout
    print()
    print()
    return df, rulestatus
