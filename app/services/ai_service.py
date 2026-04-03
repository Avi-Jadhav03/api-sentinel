from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from sqlalchemy import text
from app.db.database import AsyncSessionLocal
import os
from dotenv import load_dotenv
load_dotenv()

# Initialize LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile",
    temperature=0
)

# Prompt Template
prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are a SQL expert for an API monitoring system.

This system tracks:
- API uptime
- response times
- failures
- health logs over time

Users may ask about:
- slow APIs
- failed APIs
- uptime statistics
- logs over time

Database schema:

Table: apis(id, name, url, created_at)
Table: health_logs(id, api_id, status_code, response_time, is_healthy, checked_at)

Rules:
- Only generate SELECT queries
- Use SQLite syntax
- No explanation, only SQL
- Always use JOIN with apis table to get API name instead of api_id

User Question:
{question}
"""
)

# Chain
chain = prompt | llm


async def is_valid_question(question: str):
    response = llm.invoke(f"""
You are a classifier.

Determine if the following question is related to API monitoring, uptime, logs, response time, failures, or system performance.

Answer only YES or NO.

Question: {question}
""")
    return "yes" in response.content.lower()


async def generate_sql(question: str):
    response = chain.invoke({"question": question})
    sql_query = response.content.strip()

    # remove markdown formatting if present
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    # extract only the SELECT query if extra text exists
    if "select" in sql_query.lower():
        sql_query = sql_query[sql_query.lower().index("select"):]

    return sql_query


async def execute_sql(sql_query: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(text(sql_query))
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]


async def ai_query(question: str):

    # Validate question relevance
    if not await is_valid_question(question):
        return {"answer": "Please ask a question related to API monitoring system."}

    sql = await generate_sql(question)

    # Safety check
    if not sql.lower().startswith("select"):
        return {"error": "Only SELECT queries allowed"}

    try:
        result = await execute_sql(sql)
    except Exception as e:
        return {"error": str(e), "generated_sql": sql}

    answer = await generate_answer(question, result)

    return {
        "answer": answer
    }

async def generate_answer(question: str, result: list):
    response = llm.invoke(f"""
You are an assistant.

User question: {question}

Database result:
{result}

Convert this into a clean natural language answer.
If result is empty, say no data found.
""")

    return response.content.strip()