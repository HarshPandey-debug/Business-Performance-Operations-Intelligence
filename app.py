
import os
import json

import streamlit as st
from dotenv import load_dotenv
from google import genai

# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Business Insights AI",
    page_icon="📊",
    layout="wide",
)

load_dotenv()

# --------------------------------------------------
# Load business metrics
# --------------------------------------------------

try:
    with open("business_metrics.json", "r", encoding="utf-8") as file:
        metrics = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    st.error(
        "Unable to load business_metrics.json. "
        "Check that the file exists and contains valid JSON."
    )
    st.stop()

# --------------------------------------------------
# Custom styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    .hero {
        padding: 1.5rem;
        border-radius: 16px;
        background: linear-gradient(120deg, #172554, #1e40af);
        color: white;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        color: white;
        margin-bottom: 0.4rem;
        font-size: 2rem;
    }

    .hero p {
        color: #dbeafe;
        margin-bottom: 0;
    }

    .section-label {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Header
# --------------------------------------------------

st.markdown(
    """
    <div class="hero">
        <h1>Business Insights AI</h1>
        <p>
            Business performance analytics and AI-assisted
            management reporting.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.caption(
    "Built with Python, Streamlit, Power BI, and Google Gemini"
)

# --------------------------------------------------
# Sidebar: business metrics
# --------------------------------------------------

with st.sidebar:
    st.header("⚙️ Analysis Settings")
    st.write("Review the metrics used to generate the report.")

    sales = st.number_input(
        "Total Sales",
        min_value=0.0,
        value=float(metrics["total_sales"]),
        step=1000.0,
        format="%.2f",
    )

    profit = st.number_input(
        "Total Profit",
        value=float(metrics["total_profit"]),
        step=1000.0,
        format="%.2f",
    )

    profit_margin = st.number_input(
        "Profit Margin (%)",
        value=float(metrics["profit_margin_pct"]),
        step=0.1,
        format="%.2f",
    )

    sales_growth = st.number_input(
        "Latest Sales Growth (%)",
        value=float(metrics["yearly_sales_growth_pct"]["2014"]),
        step=0.1,
        format="%.2f",
    )

    st.divider()

    st.caption(
        "These values come from business_metrics.json. "
        "Changes here apply to this analysis only."
    )

# --------------------------------------------------
# KPI overview
# --------------------------------------------------

st.markdown(
    '<p class="section-label">Performance Overview</p>',
    unsafe_allow_html=True,
)

kpi1, kpi2, kpi3 = st.columns(3)

with kpi1:
    st.metric(
        "Total Sales",
        f"{sales:,.2f}",
    )

with kpi2:
    st.metric(
        "Total Profit",
        f"{profit:,.2f}",
    )

with kpi3:
    st.metric(
        "Profit Margin",
        f"{profit_margin:.2f}%",
    )

st.divider()

# --------------------------------------------------
# Generate AI analysis
# --------------------------------------------------

st.markdown(
    '<p class="section-label">AI-Powered Reporting</p>',
    unsafe_allow_html=True,
)

st.subheader("Management Insights")
st.write(
    "Generate a concise report covering performance, "
    "business risks, and areas for further investigation."
)

if st.button("✨ Generate AI Insights", type="primary"):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error(
            "GEMINI_API_KEY was not found. Check your .env file."
        )

    else:
        try:
            client = genai.Client(api_key=api_key)

            discount_bands = ", ".join(
                metrics["negative_profit_discount_bands"]
            )

            yearly_growth = ", ".join(
                f"{year}: {growth:.2f}%"
                for year, growth in
                metrics["yearly_sales_growth_pct"].items()
            )

            prompt = f"""
You are a careful business analyst.

Analyze these supplied metrics:
- Total sales: {sales:,.2f}
- Total profit: {profit:,.2f}
- Profit margin: {profit_margin:.2f}%
- Latest year-over-year sales growth: {sales_growth:.2f}%
- Yearly sales growth: {yearly_growth}
- Discount bands associated with negative total profit: {discount_bands}

The discount chart shows an association between these discount
bands and negative total profit. It does not establish causation.

Write a concise management report using these sections:

## Overall Assessment
Summarize the overall performance in 1–2 sentences.

## 1. Key Observations
Provide three observations supported by the supplied metrics.

## 2. Areas for Further Investigation
Provide two specific questions for further analysis.

## 3. Actionable Recommendations
Provide two practical recommendations, distinguishing evidence
from hypotheses.

## 4. Limitations and Additional Data Needed
Explain relevant limitations and the value of more detailed
cost and transaction-level data.

Rules:
- Use clean Markdown headings and bullet points.
- Bold only short descriptive labels.
- Do not bold or insert formatting markers inside numbers.
- Format numerical values with commas and two decimal places.
- Do not invent data, causes, or numerical results.
- Do not claim that discounts caused losses.
- Acknowledge changing growth rates where relevant.
- Avoid repeating the same figures unnecessarily.
- Flag apparent inconsistencies in the supplied metrics.
"""

            with st.spinner("Analyzing business performance..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                )

            if response.text:
                st.success("Analysis generated successfully.")

                with st.container(border=True):
                    st.markdown(
                        """
                        <style>
                        .report-content {
                        font-size: 1rem;
                        line-height: 1.7;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    st.markdown(response.text)

                st.caption(
                    "AI-generated analysis. Validate conclusions "
                    "against the underlying business data."
                )
            else:
                st.warning(
                    "Gemini returned no text. Please try again."
                )

        except Exception:
            st.error(
                "The AI request failed. Check your connection, "
                "Gemini API key, API access, and model availability."
            )

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "Business Insights AI · Exploratory analytics, "
    "not a substitute for validated financial reporting."
)
