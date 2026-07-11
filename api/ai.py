from fastapi import APIRouter
from pydantic import BaseModel
from google import genai
from api.database import get_connection
import re
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Gemini Client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Request Schema
class AIQuestion(BaseModel):
    question: str


@router.post("/ai/chat")
def chat(data: AIQuestion):

    # Prompt for Gemini
    prompt = f"""
You are a PostgreSQL SQL Expert.

Database Table:
pan_india_jobs

Columns:
- job_id
- rating
- company_name
- job_title
- salary
- salaries_reported
- location
- employment_status
- job_roles

Rules:
1. Generate ONLY PostgreSQL SELECT query.
2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE.
3. Return ONLY SQL query.
4. Table name is pan_india_jobs.
5. Do not return markdown or explanation.
6. If the question cannot be answered from the table, generate the best possible SELECT query.

7. If no matching data exists, generate a valid SELECT query that returns an empty result.



User Question:
{data.question}
"""

    # Generate SQL
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    sql = response.text.strip()

    # Remove markdown if present
    sql = re.sub(r"```sql|```", "", sql).strip()
    
    blocked_words = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "GRANT",
    "REVOKE"
]

    upper_sql = sql.upper()

    for word in blocked_words:
        if word in upper_sql:
            return {
                "error": f"{word} queries are not allowed."
            }

    print(sql)

    # Security Check

    if sql.count(";") > 1:
     return {
          "error": "Multiple SQL statements are not allowed."
    }

    if "PAN_INDIA_JOBS" not in upper_sql:
     return {
              
            "error": "Only pan_india_jobs table is allowed."
    }

    if not sql.upper().startswith("SELECT"):
     return {
            "error": "Only SELECT queries are allowed."
}
    
    # Execute SQL
    # Execute SQL
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()
       # Explain result using Gemini
    

    explain_prompt = f"""
    You are an AI Job Market Analyst.

    User Question:
    {data.question}

    SQL Result:
    {result}

    Instructions:
    - Give concise answers.
    - Use bullet points if multiple records are returned.
    - Do not mention SQL.
    - If the SQL result is empty, politely say that no matching jobs were found.

    Answer:
"""

    try:
        explanation = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=explain_prompt
        )

        return {
            "sql": sql,
            "answer": explanation.text
        }

    except Exception as e:
        return {
            "sql": sql,
            "result": result,
            "error": str(e)
        }