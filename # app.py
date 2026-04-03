# app.py
import streamlit as st
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

# 🔌 PostgreSQL Connection
conn = psycopg2.connect(
    host="localhost",
    database="ai_churn_chatbot",
    user="username",       # <-- Your DB username
    password="password"        # <-- Your DB password
)

# 🤖 Rule-based SQL Generator
def generate_sql(user_query):
    user_query = user_query.lower()

    if "churn count by contract" in user_query:
        return """
        SELECT contract, COUNT(*) AS churn_count
        FROM customers
        WHERE churn = 'Yes'
        GROUP BY contract;
        """

    elif "churn count by gender" in user_query:
        return """
        SELECT gender, COUNT(*) AS churn_count
        FROM customers
        WHERE churn='Yes'
        GROUP BY gender;
        """

    elif "total customers" in user_query:
        return "SELECT COUNT(*) AS total_customers FROM customers;"

    elif "average monthly charges" in user_query:
        return "SELECT AVG(monthly_charges) AS avg_monthly_charges FROM customers;"

    elif "average tenure by churn" in user_query:
        return "SELECT churn, AVG(tenure) AS avg_tenure FROM customers GROUP BY churn;"

    elif "total monthly charges by contract" in user_query:
        return "SELECT contract, SUM(monthly_charges) AS total_charges FROM customers GROUP BY contract;"

    elif "churn percentage by gender" in user_query:
        return """
        SELECT gender, 
               ROUND(100.0 * SUM(CASE WHEN churn='Yes' THEN 1 ELSE 0 END)/COUNT(*),2) AS churn_percentage
        FROM customers
        GROUP BY gender;
        """

    else:
        return "SELECT * FROM customers LIMIT 10;"

# 🎨 Streamlit UI
st.set_page_config(page_title="AI Customer Churn Chatbot", layout="wide")
st.title("📊 AI Customer Churn Chatbot")

user_input = st.text_input("Ask your question about the customers dataset:")

if st.button("Run Query"):

    sql_query = generate_sql(user_input)
    st.write("### 🧾 Generated SQL Query:")
    st.code(sql_query)

    # Run SQL
    try:
        df = pd.read_sql(sql_query, conn)
    except Exception as e:
        st.error(f"SQL Execution Error: {e}")
        df = pd.DataFrame()

    if not df.empty:
        st.write("### 📋 Result:")
        st.dataframe(df)

        # 📊 Charts
        if len(df.columns) >= 2:
            st.write("### 📈 Chart:")
            st.bar_chart(df.set_index(df.columns[0]))

        # 💡 Basic Insight (optional)
        if "churn_count" in df.columns:
            max_churn = df[df.columns[1]].max()
            best_group = df[df.columns[1]] == max_churn
            st.write(f"💡 Insight: Highest churn in **{df[df.columns[0]][best_group].values[0]}** group")
    else:
        st.warning("No data returned from query. Try another question!")