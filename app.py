import streamlit as st
from itertools import combinations

# ---------------- Page Setup ----------------
st.set_page_config(
    page_title="Invoice Tax Analyzer",
    layout="centered"
)

# ---------------- Core Algebra Engine ----------------
def solve_algebra(invoice, tax, allowed_rates, exact_only):

    invoice = round(invoice, 3)
    tax = round(tax, 3)

    tolerance = 0 if exact_only else 0.001
    solutions = []

    # ---------- 1 RATE (Unlimited) ----------
    for r in allowed_rates:
        rate = r / 100
        if abs(invoice * rate - tax) <= tolerance:
            solutions.append([
                {
                    "Tax Rate": f"{r}%",
                    "Amount (JOD)": round(invoice, 3),
                    "Tax (JOD)": round(tax, 3)
                }
            ])

    # ---------- 2 RATES (Unlimited) ----------
    for r1, r2 in combinations(allowed_rates, 2):

        d1, d2 = r1/100, r2/100

        if abs(d1 - d2) < 1e-12:
            continue

        # Solve:
        # x + y = invoice
        # d1*x + d2*y = tax

        x = (tax - invoice * d2) / (d1 - d2)
        y = invoice - x

        if x >= -tolerance and y >= -tolerance:
            if abs(d1*x + d2*y - tax) <= tolerance:
                solutions.append([
                    {
                        "Tax Rate": f"{r1}%",
                        "Amount (JOD)": round(x, 3),
                        "Tax (JOD)": round(x*d1, 3)
                    },
                    {
                        "Tax Rate": f"{r2}%",
                        "Amount (JOD)": round(y, 3),
                        "Tax (JOD)": round(y*d2, 3)
                    }
                ])

    # ---------- 3 RATES (LIMIT TO 25) ----------
    max_three_rate = 25
    three_rate_count = 0

    step = 0.001  # mil precision

    for r1, r2, r3 in combinations(allowed_rates, 3):

        d1, d2, d3 = r1/100, r2/100, r3/100

        x = 0.0
        while x <= invoice:

            remaining_invoice = invoice - x
            remaining_tax = tax - d1 * x

            if abs(d2 - d3) > 1e-12:

                y = (remaining_tax - remaining_invoice * d3) / (d2 - d3)
                z = remaining_invoice - y

                if y >= -tolerance and z >= -tolerance:
                    if abs(d2*y + d3*z - remaining_tax) <= tolerance:

                        solutions.append([
                            {
                                "Tax Rate": f"{r1}%",
                                "Amount (JOD)": round(x, 3),
                                "Tax (JOD)": round(x*d1, 3)
                            },
                            {
                                "Tax Rate": f"{r2}%",
                                "Amount (JOD)": round(y, 3),
                                "Tax (JOD)": round(y*d2, 3)
                            },
                            {
                                "Tax Rate": f"{r3}%",
                                "Amount (JOD)": round(z, 3),
                                "Tax (JOD)": round(z*d3, 3)
                            }
                        ])

                        three_rate_count += 1

                        if three_rate_count >= max_three_rate:
                            return solutions

            x = round(x + step, 3)

    return solutions


# ---------------- UI ----------------
st.title("🧾 Invoice Tax Analyzer")
st.caption("Explain how mixed tax rates could produce the total tax on an invoice.")

invoice = st.number_input(
    "Invoice amount (before tax)",
    min_value=0.0,
    step=0.001,
    format="%.3f"
)

tax = st.number_input(
    "Total tax applied",
    min_value=0.0,
    step=0.001,
    format="%.3f"
)

st.subheader("Applicable tax rates (optional)")
st.caption("Leave all unchecked to try all standard rates.")

available_rates = [16, 10, 5, 4, 2, 1]

selected_rates = [
    r for r in available_rates
    if st.checkbox(f"{r}%")
]

allowed_rates = selected_rates if selected_rates else available_rates

st.divider()

exact_only = st.checkbox("Exact solution only (0 cent tolerance)")

if st.button("Analyze invoice"):

    if invoice <= 0:
        st.warning("Please enter a valid invoice amount.")
    elif tax <= 0:
        st.warning("Please enter a valid tax amount.")
    else:
        results = solve_algebra(invoice, tax, allowed_rates, exact_only)

        if not results:
            st.error("No valid tax breakdown found.")
        else:
            st.success(
                f"Possible explanation(s) for {tax:.3f} JOD tax "
                f"on a {invoice:.3f} JOD invoice:"
            )

            for i, solution in enumerate(results, 1):
                st.markdown(f"### Option {i}")
                st.table(solution)
