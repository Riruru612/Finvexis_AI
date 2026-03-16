def analyze_trends(data):
    """
    Detect revenue trends
    """

    trends = []
    revenue_list = data["revenue"].tolist()

    for i in range(1, len(revenue_list)):
        change = revenue_list[i] - revenue_list[i-1]

        if change > 0:
            trends.append("Revenue increased")

        elif change < 0:
            trends.append("Revenue decreased")

        else:
            trends.append("Revenue stable")

    print("\nTrend Analysis")
    for t in trends:
        print(t)

    return trends