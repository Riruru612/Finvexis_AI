from sales_hr.agent import create_sales_hr_agent
import os
from dotenv import load_dotenv
load_dotenv()

groq_api_key = os.getenv("GROQ_API")
def main():

    agent = create_sales_hr_agent()

    print("Finvexis Sales & HR Agent Ready")


    while True:

        query = input("\nAsk something (type 'exit' to stop): ")

        if query.lower() == "exit":
            break

        response = agent.invoke(
            {"messages": [("user", query)]}
        )

        print("\nAgent Response:")
        print(response["messages"][-1].content)


if __name__ == "__main__":
    main()