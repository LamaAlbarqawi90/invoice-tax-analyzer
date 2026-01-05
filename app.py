import streamlit as st

st.set_page_config(page_title="Invoice Tax Analyzer", layout="centered")

st.title("Invoice Tax Analyzer")
st.write(
    "Analyze how tax was calculated on an invoice using selected tax rates. "
    "Supports exact accounting-style rounding."
)

# -------------------------
# Inputs
# -------------------------
invoice = st.number_input(
    "Invoice amount (JOD)",
    min_value=0.0,
    step=0.001,
    format="%.3f"
)

tax = st.number_input(
    "Total tax applied (JOD)",
    min_value=0.0,
    step=0.001,
    format="%.3f"
)

available_rates = [0.16, 0.08, 0.05, 0.04, 0.02, 0.01]

selected_rates = st.multiselect(
    "Select applicable tax rates (optional)",
    options=available_rates,
    format_func=lambda r: f"{int(r*100)}%",
)

rounding = 3

# -------------------------
# Helper functions
# -------------------------
def analyze_single_rate(invoice, tax, rate):
    calculated_tax = round(invoice * rate, rounding)
    if calculated_tax == round(tax, rounding):
        return [{
            "Tax Rate": f"{int(rate*100)}%",
            "Amount (JOD)": round(invoice, 3),
            "Tax (JOD)": calculated_tax
        }]
    return None


def analyze_two_rates(invoice, tax, r1, r2):
    # Algebraic solution:
    # a*r1 + (invoice - a)*r2 = tax
    try:
        a = (tax - invoice * r2) / (r1 - r2)
    except ZeroDivisionError:
        return None

    if not (0 <= a <= invoice):
        return None

    part1 = round(a, 3)
    part2 = round(invoice - part1, 3)

    tax1 = round(part1 * r1, rounding)
    tax2 = round(part2 * r2, rounding)

    if round(tax1 + tax2, rounding) == round(tax, rounding):
        return [
            {"Tax Rate": f"{int(r1*100)}%", "Amount (JOD)": part1, "Tax (JOD)": tax1},
            {"Tax Rate": f"{int(r2*100)}%", "Amount (JOD)": part2, "Tax (JOD)": tax2},
        ]

    return None


# -------------------------
# Analysis
# -------------------------
if st.button("Analyze"):
    if invoice == 0 or tax == 0:
        st.warning("Please enter both invoice amount and tax.")
    else:
        rates_to_use = selected_rates if selected_rates else available_rates
        results_found = False

        # ---- Single rate check
        for r in rates_to_use:
            result = analyze_single_rate(invoice, tax, r)
            if result:
                st.success("✅ Tax matches a single tax rate")
                st.table(result)
                results_found = True
                break

        # ---- Two-rate check
        if not results_found and len(rates_to_use) >= 2:
            for i in range(len(rates_to_use)):
                for j in range(i + 1, len(rates_to_use)):
                    r1, r2 = rates_to_use[i], rates_to_use[j]
                    result = analyze_two_rates(invoice, tax, r1, r2)
                    if result:
                        st.success("✅ Tax matches a combination of two rates")
                        st.table(result)
                        results_found = True
                        break
                if results_found:
                    break

        if not results_found:
            st.error(
                "❌ No valid tax breakdown found using the selected rates.\n\n"
                "Possible reasons:\n"
                "- Different rounding rules\n"
                "- More than two tax rates applied\n"
                "- Line-level rather than invoice-level tax"
            )

# -------------------------
# Footer
# -------------------------
st.caption("Rounding applied to 3 decimal places (standard accounting practice).")
