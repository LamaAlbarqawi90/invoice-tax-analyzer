import streamlit as st
from decimal import Decimal, ROUND_HALF_UP, getcontext

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
    "Enter the invoice total and tax exactly as shown on the invoice. "
    "This tool analyzes how the tax may have been calculated."
)

# -------------------------
# Inputs (TEXT INPUTS — SAFE)
# -------------------------
invoice_str = st.text_input(
    "Invoice amount (JOD)",
    placeholder="Example: 336.214"
)

tax_str = st.text_input(
    "Total tax applied (JOD)",
    placeholder="Example: 33.951"
)

# -------------------------
# Tax rates
# -------------------------
available_rates = [
    Decimal("0.16"),
    Decimal("0.08"),
    Decimal("0.05"),
    Decimal("0.04"),
    Decimal("0.02"),
    Decimal("0.01"),
]

selected_rates = st.multiselect(
    "Select applicable tax rates (optional)",
    options=available_rates,
    format_func=lambda r: f"{int(r * 100)}%",
)

# -------------------------
# Analysis functions
# -------------------------
def analyze_single_rate(invoice, tax, rate):
    calc_tax = r(invoice * rate)
    if calc_tax == r(tax):
        return [{
            "Tax Rate": f"{int(rate * 100)}%",
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
            {"Tax Rate": f"{int(r1 * 100)}%", "Amount (JOD)": part1, "Tax (JOD)": tax1},
            {"Tax Rate": f"{int(r2 * 100)}%", "Amount (JOD)": part2, "Tax (JOD)": tax2},
        ]

    return None

# -------------------------
# Run analysis
# -------------------------
if st.button("Analyze"):
    if not invoice_str or not tax_str:
        st.warning("Please enter both invoice amount and tax.")
        st.stop()

    if "," in invoice_str or "," in tax_str:
        st.error("Please use a dot (.) as the decimal separator.")
        st.stop()

    try:
        invoice = Decimal(invoice_str)
        tax = Decimal(tax_str)
    except:
        st.error("Invalid number format.")
        st.stop()

    rates = selected_rates if selected_rates else available_rates
    found = False

    # Single-rate check
    for rate in rates:
        result = analyze_single_rate(invoice, tax, rate)
        if result:
            st.success("✅ Tax matches a single tax rate")
            st.table(result)
            found = True
            break

    # Two-rate check
    if not found and len(rates) >= 2:
        for i in range(len(rates)):
            for j in range(i + 1, len(rates)):
                result = analyze_two_rates(invoice, tax, rates[i], rates[j])
                if result:
                    st.success("✅ Tax matches a combination of two rates")
                    st.table(result)
                    found = True
                    break
            if found:
                break

    if not found:
        st.error(
            "❌ No valid tax breakdown found.\n\n"
            "Possible reasons:\n"
            "- Line-level rounding\n"
            "- More than two tax rates applied\n"
            "- Different rounding rules"
        )

# -------------------------
# Footer
# -------------------------
st.caption("Rounding: 3 decimals, HALF-UP (standard accounting practice).")
