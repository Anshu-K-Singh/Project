import plotly.express as px
import pandas as pd
from django.db.models import Count
from datetime import date

def calculate_age(dob):
    today = date.today()
    return today.year - dob.year if dob else None

def generate_demographic_pie_chart(respondents):
    data = respondents.values('gender').annotate(count=Count('gender'))
    df = pd.DataFrame(list(data))

    if df.empty:
        return None  # No data to plot

    fig = px.pie(df, names='gender', values='count', title="Gender Distribution")
    return fig.to_html(full_html=False)

def generate_education_bar_chart(respondents):
    data = respondents.values('education').annotate(count=Count('education'))
    df = pd.DataFrame(list(data))

    if df.empty:
        return None

    fig = px.bar(df, x='education', y='count', title="Education Levels", text_auto=True)
    return fig.to_html(full_html=False)

def generate_age_distribution(respondents):
    ages = [calculate_age(res.dob) for res in respondents if res.dob]
    
    if not ages:
        return None

    df = pd.DataFrame(ages, columns=['Age'])
    fig = px.histogram(df, x='Age', nbins=10, title="Age Distribution")
    return fig.to_html(full_html=False)
