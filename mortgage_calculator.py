"""Advanced mortgage calculator — like Property Finder."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd


def calculate_mortgage(price, down_pct=20, years=20, rate=10):
    """Calculate monthly payment + full schedule."""
    down = price * (down_pct / 100)
    loan = price - down
    monthly_rate = (rate / 100) / 12
    n_months = years * 12

    if monthly_rate > 0:
        monthly = loan * (monthly_rate * (1 + monthly_rate) ** n_months) / ((1 + monthly_rate) ** n_months - 1)
    else:
        monthly = loan / n_months

    # Full schedule
    schedule = []
    balance = loan
    total_interest = 0
    total_principal = 0
    for m in range(1, n_months + 1):
        interest = balance * monthly_rate
        principal = monthly - interest
        balance -= principal
        total_interest += interest
        total_principal += principal
        if m <= 12 or m % 12 == 0:
            schedule.append({
                'month': m, 'year': (m - 1) // 12 + 1,
                'principal': principal, 'interest': interest,
                'balance': max(0, balance),
            })

    return {
        'monthly': monthly,
        'down': down,
        'loan': loan,
        'total_interest': total_interest,
        'total_paid': total_principal + total_interest,
        'total_cost': down + total_principal + total_interest,
        'schedule': schedule,
    }


def render_mortgage_calculator(price, lang="en"):
    """Advanced mortgage calculator with sliders + chart."""
    if lang == "ar":
        title = "🏦 حاسبة الرهن العقاري"
        subtitle = "احسب قسطك الشهري بالتفصيل"
        labels = {
            "down": "المقدم (%)", "years": "عدد السنوات",
            "rate": "نسبة الفايدة (%)", "monthly": "القسط الشهري",
            "down_amt": "قيمة المقدم", "loan_amt": "قيمة القرض",
            "interest": "إجمالي الفوايد", "total": "إجمالي المدفوع",
            "chart": "توزيع القسط على السنوات",
            "principal": "أصل القرض", "intr": "الفوايد",
            "schedule": "جدول السداد السنوي",
            "year": "السنة", "balance": "الرصيد المتبقي",
        }
    else:
        title = "🏦 Mortgage Calculator"
        subtitle = "Detailed monthly payment calculator"
        labels = {
            "down": "Down Payment (%)", "years": "Years",
            "rate": "Interest Rate (%)", "monthly": "Monthly Payment",
            "down_amt": "Down Payment", "loan_amt": "Loan Amount",
            "interest": "Total Interest", "total": "Total Paid",
            "chart": "Yearly Breakdown",
            "principal": "Principal", "intr": "Interest",
            "schedule": "Yearly Schedule",
            "year": "Year", "balance": "Balance",
        }

    st.markdown("## " + title)
    st.caption(subtitle)

    # Sliders
    c1, c2, c3 = st.columns(3)
    with c1:
        down_pct = st.slider(labels["down"], 5, 50, 20, 5, key="mort_down")
    with c2:
        years = st.slider(labels["years"], 5, 30, 20, 1, key="mort_years")
    with c3:
        rate = st.slider(labels["rate"], 3.0, 25.0, 10.0, 0.5, key="mort_rate")

    r = calculate_mortgage(price, down_pct, years, rate)

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(labels["monthly"], f"{r['monthly']:,.0f} EGP")
    k2.metric(labels["down_amt"], f"{r['down']:,.0f} EGP")
    k3.metric(labels["loan_amt"], f"{r['loan']:,.0f} EGP")
    k4.metric(labels["interest"], f"{r['total_interest']:,.0f} EGP")

    # Chart
    df = pd.DataFrame(r['schedule'])
    if not df.empty:
        yearly = df[df['month'] % 12 == 0].copy()
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=yearly['year'],
            y=yearly['principal'],
            name=labels["principal"],
            marker_color='#10b981',
        ))
        fig.add_trace(go.Bar(
            x=yearly['year'],
            y=yearly['interest'],
            name=labels["intr"],
            marker_color='#ef4444',
        ))
        fig.update_layout(
            barmode='stack', height=320,
            margin=dict(l=10, r=10, t=30, b=20),
            plot_bgcolor='white',
            xaxis_title=labels["year"],
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Table
        st.markdown("### " + labels["schedule"])
        table = yearly[['year', 'principal', 'interest', 'balance']].round(0)
        table.columns = [labels["year"], labels["principal"], labels["intr"], labels["balance"]]
        st.dataframe(table, use_container_width=True, hide_index=True)
