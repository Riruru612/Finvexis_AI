# Project Description

# Finvexis AI – A Smart Multi-agent Platform for Finance, Business & Sales

**Finvexis AI is the intelligent A.I.powered platform to manage finance, operations, sales & hiring all at one place for businesses.** It utilises Agentic AI system: A new approach of multiple specialised agents, which collaborate under the auspices of one central controller (orchestrator) to address business problems.

Today, most businesses use different tools for invoicing, tax calculation, KPI tracking, lead management, and hiring. Because these tools are separate, it becomes difficult to make fast and informed decisions. Finvexis AI solves this problem by combining everything into one intelligent system where AI agents collaborate to provide insights and automation.

The platform is divided into three main areas:

# 1. Finance Agents

This section focuses on handling financial tasks and giving smart financial suggestions.It includes:

• **Invoice Generator Agent** – This automatically generates invoice

• **Tax Calculator Agent** - Predicts taxes on income and expense.

• **Investment Risk Agent** – Estimates the risk involved in different financial choices

• **AI Financial Advisor** – Recommends actions to improve budget and financial health

The agents help business owners make better use of their money, lower the business costs and increase profits.

# 2. Business Intelligence Agents

This section explains why it's good for companies to know more about how well they're doing. It includes:

• **Business KPI Tracker** – A tracker for business key performance indicators including revenue, profit and growth.

• **Market Research Analyst** – Analyzes competitors, market trends and industry patterns.

• **Forecasting Agent** – Predicts future trends based on historical data and market signals.

• **Strategy Agent** – Generates strategic recommendations based on KPI, market, and forecast analysis.

These agents convert raw data into actionable insights, enabling businesses to make more informed decisions.

# 3. Sales & HR Agents

This part will also impact hiring and sales processes. It includes:

• **Lead Qualification Agent** – Ranks potential leads and pinpoint those that are best

• **CRM Integration Agent** - Consolidates customer information to keep them up-to-date.

• **Resume Screener** – Pre-screens job applicants.

• **HR Chat Assistant** : Answer regarding employee-related questions and policy-based inquiries

The Master Orchestrator Agent is at the heart of the system. This agent has the capability to grasp the user’s intention, mediate with which agents should be activated and co-communicate among them. Rather than acting in isolation, the agents share their responsibilities to complete VP tasks. For instance, when a user request business health analysis the system can consolidate tracking of KPIs, financial analysis and evaluation of risk to generate a comprehensive report.

It is achieved by making the use of large language models (LLMs), tool integration with structure, and systems memory to design scalable and intelligent workflows. It is designed to grow and support more business functions in the future.

Finvexis AI shows how Agentic AI can go beyond simple chatbots and become a powerful decision-support system. By combining automation, reasoning, and domain expertise, the platform helps businesses reduce manual work and make better, data-driven decisions.

---

# Running the Platform

## Frontend (React + TypeScript + Tailwind CSS)

```bash
# Navigate to the UI directory
cd c:\Users\pande\Agentic_AI\src_ui_ux

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:8080`

## Finance Agents (Streamlit)

```bash
# From project root
cd c:\Users\pande\Agentic_AI
streamlit run finance/app.py
```

## Business Intelligence Agents

```bash
# From project root
cd c:\Users\pande\Agentic_AI
python "Business Intelligence Agents/src_ai/graph/orchestrator.py"
```

## Sales & HR Agents

```bash
# From project root
cd c:\Users\pande\Agentic_AI
python sales_hr/main.py
```
