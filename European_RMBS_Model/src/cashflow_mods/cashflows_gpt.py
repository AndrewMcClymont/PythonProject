# loan_engine.py

import numpy as np
import pandas as pd
import numpy_financial as npf

# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def make_vector(value, n):
    """Convert scalar to length-n vector."""
    if np.isscalar(value):
        return np.full(n, float(value))
    return np.asarray(value, dtype=float)

# =========================================================
# LOAN CLASS
# =========================================================

class Loan:
    """
    Represents a single mortgage loan capable of:
      - loading contractual inputs,
      - merging forward curve,
      - building contractual waterfall,
      - building scenario waterfall.
    """

    def __init__(self, loan_row: pd.Series, sonia_curve: pd.DataFrame,
                 CPR, CDR, Severity, recovery_lag):

        self.loan_row = loan_row
        self.sonia_curve = sonia_curve

        # Convert annual → monthly where needed
        self.SVR_0 = loan_row["current_interest_rate_svr"] / 100
        self.margin = loan_row["current_interest_rate_margin"]
        self.term = int(loan_row["remaining_term"])
        self.rate_type = loan_row["interest_rate_type_mapped"]
        self.fix_to_float_term = loan_row["reversion_term"]

        self.repayment_type = loan_row["repayment_method_mapped"]

        # Scenario inputs
        self.CPR = CPR / 100
        self.CDR = CDR / 100
        self.Severity = Severity / 100
        self.recovery_lag = recovery_lag

        self.SMM = (1 - (1 - self.CPR)**(1/12))
        self.MDR = (1 - (1 - self.CDR)**(1/12))

        # Storage for results
        self.contractual = None
        self.scenario = None

    # -----------------------------------------------------
    # CONTRACTUAL CASHFLOWS
    # -----------------------------------------------------
    def build_contractual(self):
        """
        Builds contractual BOP/EOP, amortisation, interest, principal.
        """
        n = self.term + 1
        df = pd.DataFrame({"period": range(n)})

        # merge forward curve
        df["compounded_sonia_forward"] = self.sonia_curve["compounded_sonia_forward"].iloc[:n].values

        df.loc[0, "SVR"] = self.SVR_0
        df["margin"] = self.margin
        df.loc[0, "EOP"] = self.loan_row["current_balance"]

        for t in range(1, n):
            df.loc[t, "BOP"] = df.loc[t-1, "EOP"]

            # Interest rate evolution
            df.loc[t, "SVR"] = df.loc[t-1, "SVR"] * (
                df.loc[t, "compounded_sonia_forward"] / df.loc[t-1, "compounded_sonia_forward"]
            )

            # Rate type
            if self.rate_type == "fix_to_float" and t < self.fix_to_float_term:
                df.loc[t, "interest_rate"] = self.loan_row["current_interest_rate"]
            else:
                df.loc[t, "interest_rate"] = df.loc[t, "SVR"] + df.loc[t, "margin"]

            # Cashflows
            if self.repayment_type == "interest_only":
                df.loc[t, "principal_pmt"] = 0
                if t == self.term:
                    df.loc[t, "principal_pmt"] = df.loc[t, "BOP"]

                df.loc[t, "interest_pmt"] = npf.ipmt(
                    rate=df.loc[t, "interest_rate"] / 12,
                    per=1,
                    nper=self.term,
                    pv=-df.loc[t, "BOP"]
                )
            else:
                df.loc[t, "principal_pmt"] = npf.ppmt(
                    rate=df.loc[t, "interest_rate"] / 12,
                    per=t,
                    nper=self.term,
                    pv=-df.loc[t, "BOP"]
                )

                df.loc[t, "interest_pmt"] = npf.ipmt(
                    rate=df.loc[t, "interest_rate"] / 12,
                    per=t,
                    nper=self.term,
                    pv=-df.loc[t, "BOP"]
                )

            df.loc[t, "EOP"] = df.loc[t, "BOP"] - df.loc[t, "principal_pmt"]

        df["amort_factor"] = df["EOP"] / df.loc[0, "EOP"]

        self.contractual = df
        return df

    # -----------------------------------------------------
    # SCENARIO CASHFLOWS (default + prepay + recovery)
    # -----------------------------------------------------
    def build_scenario(self):
        """
        Apply MDR, SMM, severity, recovery lag.
        Uses contractual amort factors.
        """
        if self.contractual is None:
            self.build_contractual()

        base = self.contractual.copy()
        n = len(base)

        MDR_vec = make_vector(self.MDR, n)
        SMM_vec = make_vector(self.SMM, n)

        base["default_rate"] = MDR_vec
        base["prepay_rate"] = SMM_vec

        # Initialise
        for t in range(1, n):
            base.loc[t, "BOP"] = base.loc[t-1, "EOP"]

            # Default
            base.loc[t, "default_amt"] = base.loc[t, "BOP"] * base.loc[t, "default_rate"]
            bop_after_default = base.loc[t, "BOP"] - base.loc[t, "default_amt"]

            # Prepay
            base.loc[t, "prepay_amt"] = bop_after_default * base.loc[t, "prepay_rate"]
            bop_after_both = bop_after_default - base.loc[t, "prepay_amt"]

            # Amortisation
            if base.loc[t-1, "amort_factor"] == 0:
                amort_delta = 0
            else:
                amort_delta = 1 - (base.loc[t, "amort_factor"] / base.loc[t-1, "amort_factor"])

            base.loc[t, "actual_principal_pmt"] = amort_delta * bop_after_both

            # Interest on post-default balance
            base.loc[t, "actual_interest_pmt"] = (base.loc[t, "interest_rate"] / 12) * bop_after_default

            # Recoveries
            if t < self.recovery_lag:
                base.loc[t, "recovery_pmt"] = 0
            else:
                base.loc[t, "recovery_pmt"] = (
                    base.loc[t - self.recovery_lag, "default_amt"] * (1 - self.Severity)
                )

            base.loc[t, "total_prin_pmt"] = base.loc[t, "actual_principal_pmt"] + base.loc[t, "prepay_amt"]
            base.loc[t, "total_int_pmt"] = base.loc[t, "actual_interest_pmt"] + base.loc[t, "recovery_pmt"]

            base.loc[t, "EOP"] = (
                base.loc[t, "BOP"]
                - base.loc[t, "default_amt"]
                - base.loc[t, "prepay_amt"]
                - base.loc[t, "actual_principal_pmt"]
            )

        self.scenario = base
        return base


# =========================================================
# PORTFOLIO CLASS
# =========================================================

class Portfolio:
    """
    Represents a collection of loans.
    Supports:
      - loan-by-loan modelling,
      - repline modelling,
      - portfolio aggregation,
      - future behavioural logic hooks.
    """

    def __init__(self, loan_tape: pd.DataFrame, sonia_curve: pd.DataFrame):
        self.loan_tape = loan_tape
        self.sonia_curve = sonia_curve
        self.loans = []

    # ------------------------------------------
    def build_loans(self, CPR, CDR, Severity, recovery_lag):
        """
        Instantiate Loan objects for each row in the tape.
        """
        self.loans = [
            Loan(row, self.sonia_curve, CPR, CDR, Severity, recovery_lag)
            for _, row in self.loan_tape.iterrows()
        ]

    # ------------------------------------------
    def run_loan_level(self):
        """
        Run contractual + scenario for each loan individually.
        """
        for loan in self.loans:
            loan.build_contractual()
            loan.build_scenario()

    # ------------------------------------------
    def aggregate_portfolio(self):
        """
        Sum all loan cashflows period-by-period.
        """
        agg = None
        for loan in self.loans:
            df = loan.scenario.copy()
            df["loan_id"] = loan.loan_row["loan_id"]
            if agg is None:
                agg = df
            else:
                agg = pd.concat([agg, df])

        portfolio_cf = agg.groupby("period").sum(numeric_only=True)
        return portfolio_cf

    # ------------------------------------------
    def run_repline(self, group_var: str):
        """
        Model at repline level (e.g., by LTV bucket, origination year, etc).
        You can later insert custom behavioural logic here.
        """
        results = {}
        groups = self.loan_tape.groupby(group_var)

        for name, group in groups:
            sub_port = Portfolio(group, self.sonia_curve)
            # You can inject special CPR/CDR assumptions here per repline
            results[name] = sub_port

        return results
