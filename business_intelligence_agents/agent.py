from langchain.tools import tool
from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq

from tools.data_loader import load_business_data
from tools.kpi_calculator import calculate_kpis
from tools.trend_analyzer import analyze_trends
from tools.competitor_analyzer import analyze_competitors
from tools.insight_generator import generate_insights


@tool
def business_analysis(file_path: str):
    """
    Analyze business dataset and generate insights
    """

    data = load_business_data(file_path)

    kpis = calculate_kpis(data)

    trends = analyze_trends(data)

    competitor_report = analyze_competitors(data)

    insights = generate_insights(kpis, trends)

    return {
        "KPIs": kpis,
        "Trends": trends,
        "Competitor Analysis": competitor_report,
        "Insights": insights
    }


tools = [business_analysis]


llm = ChatGroq(
    model="llama3-70b-8192"
)


agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)


if __name__ == "__main__":

    file_path = input("Enter dataset path: ")

    response = agent.run(
        f"Analyze the business performance using the dataset {file_path}"
    )

    print("\nFinal Report:\n", response)