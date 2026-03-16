def calculate_kpis(data):
    """
    Calculate basic business KPIs
    """

    revenue = data["revenue"].sum()
    cost = data["cost"].sum()

    profit = revenue - cost
    profit_margin = (profit / revenue) * 100

    kpis = {
        "Total Revenue": revenue,
        "Total Cost": cost,
        "Total Profit": profit,
        "Profit Margin %": round(profit_margin, 2)
    }

    print("\nKPI Results")
    for k, v in kpis.items():
        print(k, ":", v)

    return kpis