def analyze_competitors(data):
    """
    Analyze competitor metrics
    """

    avg_price = data["competitor_price"].mean()
    avg_growth = data["competitor_growth"].mean()

    report = {
        "Average Competitor Price": avg_price,
        "Average Competitor Growth": avg_growth
    }

    print("\nCompetitor Analysis")
    for k, v in report.items():
        print(k, ":", v)

    return report