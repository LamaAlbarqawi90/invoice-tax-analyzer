import streamlit as st
from decimal import Decimal, ROUND_HALF_UP, getcontext
from itertools import combinations

# -------------------------
# Decimal configuration
# -------------------------
getcontext().prec = 12
ROUND_TO = Decimal("0.001")

def r(x):
    return x.quantize(ROUND_TO, rounding=ROUND_HALF_UP)

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Invoice Tax Analyzer", layout="centered")
st.title("Invoice Tax Analyzer")

st.write(
    "This tool finds **all valid tax breakdowns** that match the invoice total, "
    "tax total, and the selected tax rates. No assumptions or preferences are applied."
)

# -------------------------
# Inputs (text to preserve precision)
# -------------------------
invoice_str = st.text_input("Invoice amount (JOD)", placeholder="Example: 950")
tax_str = st.text_input("Total tax applied (JOD)", placeholder="Example: 82")

# -------------------------
# Tax rates as checkboxes
# -------------------------
available_rates = [
    Decimal("0.16"),
    Decimal("0.08"),
    Decimal("0.05"),
    Decimal("0.04"),
    Decimal("0.02"),
    Decimal("0.01"),
]

st.write("Select the tax rates to analyze:")

selected_rates = []
for rate in available_rates:
    if st.checkbox(f"{int(rate*100)}%", value=False):
        selected_rates.append(rate)

# -------------------------
# Analysis helpers
# -------------------------
def analyze_one_rate(invoice, tax, rate):
    solutions = []
    if r(invoice * rate) == r(tax):
        solutions.append([
            {"Tax Rate": f"{int(rate*100)}%", "Amount (JOD)": r(invoice), "Tax (JOD)": r(tax)}
        ])
    return solutions

def analyze_two_rates(invoice, tax, r1, r2):
    solutions = []
    a = (tax - invoice * r2) / (r1 - r2)
    if 0 <= a <= invoice:
        a = r(a)
        b = r(invoice - a)
        if r(a*r1 + b*r2) == r(tax):
            solutions.append([
                {"Tax Rate": f"{int(r1*100)}%", "Amount (JOD)": a, "Tax (JOD)": r(a*r1)},
                {"Tax Rate": f"{int(r2*100)}%", "Amount (JOD)": b, "Tax (JOD)": r(b*r2)},
            ])
    return solutions

def analyze_three_rates(invoice, tax, rates):
    solutions = []
    step = Decimal("1")  # 1 JOD granularity
    r1, r2, r3 = rates
    a = Decimal("0")
    while a <= invoice:
        b = Decimal("0")
        while a + b <= invoice:
            c = invoice - a - b
            total_tax = r(a*r1 + b*r2 + c*r3)
            if total_tax == r(tax):
                solutions.append([
                    {"Tax Rate": f"{int(r1*100)}%", "Amount (JOD)": r(a), "Tax (JOD)": r(a*r1)},
                    {"Tax Rate": f"{int(r2*100)}%", "Amount (JOD)": r(b), "Tax (JOD)": r(b*r2)},
                    {"Tax Rate": f"{int(r3*100)}%", "Amount (JOD)": r(c), "Tax (JOD)": r(c*r3)},
                ])
            b += step
        a += step
    return solutions

# -------------------------
# Run analysis
# -------------------------
if st.button("Analyze"):
    try:
        invoice = Decimal(invoice_str)
        tax = Decimal(tax_str)
    except:
        st.error("Please enter valid numeric values.")
        st.stop()

    if not selected_rates:
        st.error("Please select at least one tax rate.")
        st.stop()

    all_solutions = []

    # 1-rate
    if len(selected_rates) >= 1:
        for r1 in selected_rates:
            all_solutions.extend(analyze_one_rate(invoice, tax, r1))

    # 2-rate
    if len(selected_rates) >= 2:
        for r1, r2 in combinations(selected_rates, 2):
            all_solutions.extend(analyze_two_rates(invoice, tax, r1, r2))

    # 3-rate
    if len(selected_rates) >= 3:
        for r1, r2, r3 in combinations(selected_rates, 3):
            all_solutions.extend(analyze_three_rates(invoice, tax, (r1, r2, r3)))

    if not all_solutions:
        st.error("❌ No valid tax breakdowns found.")
    else:
        st.success(f"✅ Found {len(all_solutions)} valid solution(s)")
        for idx, solution in enumerate(all_solutions, start=1):
            st.write(f"### Solution {idx}")
            st.table(solution)

# -------------------------
# Footer
# -------------------------
st.caption("Rounding: 3 decimals, HALF-UP. Multiple solutions may exist.")
