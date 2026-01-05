import streamlit as st
from decimal import Decimal, ROUND_HALF_UP, getcontext

getcontext().prec = 10

st.set_page_config(page_title="Invoice Tax Analyzer", layout="centered")
st.title("Invoice Tax Analyzer")

st.write("Enter invoice and tax amounts exactly as shown on the invoice.")

# -------------------------
# Inputs (TEXT, not number)
# -------------------------
invoice_str = st.text_input("Invoice amount (JOD)", placeholder="e.g. 336.214")
tax_str = st.text_input("Total tax applied (JOD)", placeholder="e.g. 33.951")

available_rates = [Decimal("0.16"), Decimal("0.08"), Decimal("0.05"),
                   Decimal("0.04"), Decimal("0.02"), Decimal("0.01")]

selected_rates = st.multiselect(
    "Select applicable tax rates (optional)",
    options=available_rates,
    format_func=lambda r: f"{int(r*100)}%",
)

ROUND = Decimal("0.001")

def r(value):
    return value.quantize(ROUND, rounding=ROUND_HALF_UP)

# -------------------------
# Analysis functions
# -------------------------
def analyze_single_rate(invoice, tax, rate):
    calc_tax = r(invoice * rate)
    if calc_tax == r(tax):
        return [{
            "Tax Rate": f"{int(rate*100)}%",
            "Amount (JOD)": r(invoice),
            "Tax (JOD)": calc_tax
        }]
    return None


def analyze_two_rates(invoice, tax, r1, r2):
    a = (tax - invoice * r2) / (r1 - r2)

    if a < 0 or a > invoice:
        return None

    part1 = r(a)
    part2 = r(invoice - part1)

    tax1 = r(part1 * r1)
    tax2 = r(part2 * r2)

    if r(tax1 + tax2) == r(tax):
        return [
            {"Tax Rate": f"{int(r1*100)}%", "Amount (JOD)": part1, "Tax (JOD)": tax1},
            {"Tax Rate": f"{int(r2*100)}%", "Amount (JOD)": part2, "Tax (JOD)": tax2},
        ]

    return None

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

    rates = selected_rates if selected_rates else available_rates
    found = False

    # Single rate
    for r_rate in rates:
        res = analyze_single_rate(invoice, tax, r_rate)
        if res:
            st.success("✅ Tax matches a single rate")
            st.table(res)
            found = True
            break

    # Two rates
    if not found and len(rates) >= 2:
        for i in range(len(rates)):
            for j in range(i + 1, len(rates)):
                res = analyze_two_rates(invoice, tax, rates[i], rates[j])
                if res:
                    st.success("✅ Tax matches two rates")
                    st.table(res)
                    found = True
                    break
            if found:
                break

    if not found:
        st.error(
            "❌ No valid tax breakdown found.\n\n"
            "Possible reasons:\n"
            "- Line-level rounding\n"
            "- More than two tax rates\n"
            "- Different rounding policy"
        )

st.caption("Rounding: 3 decimals, HALF-UP (standard accounting).")
