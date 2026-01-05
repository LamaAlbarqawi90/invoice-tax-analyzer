import streamlit as st
from itertools import product

# ---------------- Page Setup ----------------
st.set_page_config(
    page_title="Invoice Tax Analyzer",
    layout="centered"
)

# ---------------- Core Logic ----------------
def analyze_tax(invoice_amount, total_tax, allowed_rates, step):
    target_rate = total_tax / invoice_amount
    rates = [r / 100 for r in allowed_rates]
    chunks = int(invoice_amount // step)
    solutions = []

    for allocation in product(range(chunks + 1), repeat=len(rates)):
        if sum(allocation) != chunks:
            continue

        weighted_rate = sum(
            allocation[i] * rates[i] for i in range(len(rates))
        ) / chunks

        if abs(weighted_rate - target_rate) < 0.002:
            solution = []
            for i, units in enumerate(allocation):
                if units > 0:
                    amount = units * step
                    solution.append({
                        "Tax Rate": f"{allowed_rates[i]}%",
                        "Amount (JOD)": amount,
                        "Tax (JOD)": round(amount * rates[i], 2)
                    })
            solutions.append(solution)

    return solutions


def find_solutions(invoice, tax, allowed_rates):
    for step in [50, 25, 10]:
        results = analyze_tax(invoice, tax, allowed_rates, step)
        if results:
            return results
    return []


# ---------------- UI ----------------
st.title("🧾 Invoice Tax Analyzer")
st.caption(
    "Explain how mixed tax rates could produce the total tax on an invoice."
)

invoice = st.number_input(
    "Invoice amount (before tax)",
    min_value=0.0,
    step=50.0
)

tax = st.number_input(
    "Total tax applied",
    min_value=0.0,
    step=1.0
)

st.subheader("Applicable tax rates (optional)")
st.caption("Leave all unchecked to try all standard rates.")

available_rates = [16, 8, 5, 4, 2, 1]
selected_rates = [
    r for r in available_rates
    if st.checkbox(f"{r}%")
]

# If none selected, use all rates
allowed_rates = selected_rates if selected_rates else available_rates

if st.button("Analyze invoice"):
    if invoice <= 0:
        st.warning("Please enter a valid invoice amount.")
    elif tax <= 0:
        st.warning("Please enter a valid tax amount.")
    else:
        results = find_solutions(invoice, tax, allowed_rates)

        if not results:
            st.error(
                "No valid tax breakdown found using the selected tax rates."
            )
        else:
            st.success(
                f"Possible explanation(s) for {tax:.2f} JOD tax on a "
                f"{invoice:.2f} JOD invoice:"
            )

            for i, solution in enumerate(results, 1):
                st.markdown(f"### Option {i}")
                st.table(solution)
