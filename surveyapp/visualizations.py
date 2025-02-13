import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from django.db.models import Count
from datetime import date

def generate_demographic_pie_chart(respondents): 
    """Generate pie chart for gender distribution"""
    
    # Correct aggregation: Count total respondents per gender
    gender_counts = respondents.values('gender').annotate(count=Count('id'))  
    print(list(gender_counts))  # Debugging output

    df = pd.DataFrame(list(gender_counts))
    
    # Define the allowed gender categories
    allowed_genders = {"Male", "Female", "Other"}
    
    # Filter out unexpected gender values
    df = df[df['gender'].isin(allowed_genders)]

    # Ensure count is an integer (avoids unexpected issues)
    df['count'] = df['count'].astype(int)

    print(df)  # Debugging output to check correctness

    if df.empty:
        return "<p>No demographic data available</p>"

    # Create Pie Chart
    fig = px.pie(
        df, 
        values='count', 
        names='gender', 
        title='Respondent Gender Distribution',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    
    fig.update_layout(
        title_x=0.5,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs=False)


def generate_education_bar_chart(respondents):
    """Generate bar chart for education levels"""
    education_counts = respondents.values('education').annotate(count=Count('education'))
    df = pd.DataFrame(list(education_counts)).sort_values('count', ascending=False)
    
    if df.empty:
        return "<p>No education data available</p>"
    
    fig = px.bar(
        df, 
        x='education', 
        y='count', 
        title='Respondent Education Levels',
        labels={'count': 'Number of Respondents', 'education': 'Education Level'},
        color='education',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        title_x=0.5,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    print(df)
    return fig.to_html(full_html=False, include_plotlyjs=False)

def generate_age_distribution(respondents):
    """Generate age distribution histogram"""
    def calculate_age(born):
        today = date.today()
        try:
            return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        except:
            return None

    # Filter out None and invalid ages
    ages = [calculate_age(r.dob) for r in respondents if r.dob]
    ages = [age for age in ages if age is not None and 0 < age < 100]
    
    if not ages:
        return "<p>No age data available</p>"
    
    fig = go.Figure(data=[go.Histogram(x=ages, nbinsx=20)])
    fig.update_layout(
        title='Respondent Age Distribution',
        xaxis_title='Age',
        yaxis_title='Number of Respondents',
        title_x=0.5,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)