def generate_insights(kpis, trends):

    insights = []

    if kpis["Total Profit"] > 0:
        insights.append("Business is profitable")
    else:
        insights.append("Business is running at loss")

    if "Revenue increased" in trends:
        insights.append("Revenue growth detected")

    print("\nGenerated Insights")

    for i in insights:
        print("-", i)

    return insights