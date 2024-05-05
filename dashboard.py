import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import ast

# Set the page config for wide layout
st.set_page_config(layout="wide")

st.title('Data Science: Career Insights Dashboard')
st.markdown("""
<p style="font-size:16px;">CDS 492 - Spring 2024</p>
<p style="font-size:16px;">Nghia Pham</p>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data():
    data = pd.read_csv('cleaned_data.csv')
    data['Skill'] = data['Skill'].apply(ast.literal_eval)
    return data

# Unique values plus 'All' option function
def unique_sorted_values_plus_ALL(array):
    unique = sorted(array.unique().tolist())
    unique.insert(0, "All")
    return unique

# Loading data
data = load_data()

# Creating tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Top Job Titles", "Job Salaries", "Top Skills", "Skills Pay", "Map View"])

# Top Job Titles
with tab1:
    st.header('Top Data Science Job Titles')
    col1, col2 = st.columns(2)
    with col1:
        state_option = st.selectbox('Select a State', unique_sorted_values_plus_ALL(data['State']), key='state1')
    cities = unique_sorted_values_plus_ALL(data[data['State'] == state_option]['City']) if state_option != 'All' else unique_sorted_values_plus_ALL(data['City'])
    with col2:
        city_option = st.selectbox('Select a City', cities, key='city1')
    filtered_data = data
    if state_option != 'All':
        filtered_data = filtered_data[filtered_data['State'] == state_option]
    if city_option != 'All':
        filtered_data = filtered_data[filtered_data['City'] == city_option]

    job_counts = filtered_data['Job Title'].value_counts().head(10).reset_index()
    job_counts.columns = ['Job Title', 'Number of Openings']
    fig = px.bar(job_counts, y='Job Title', x='Number of Openings', orientation='h',
                 color='Number of Openings', color_continuous_scale='blues', title='Top 10 Job Titles with Most Openings')
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', 
                  yaxis={'categoryorder': 'total ascending', 'title': ''}, autosize=True)
    st.plotly_chart(fig, use_container_width=True)


# Job Salary
with tab2:
    st.header('Data Science Salary Overview')
    col1, col2, col3 = st.columns(3)
    with col1:
        state_option = st.selectbox('Select a State', unique_sorted_values_plus_ALL(data['State']), key='state2')
    with col2:
        city_option = st.selectbox('Select a City', unique_sorted_values_plus_ALL(data[data['State'] == state_option]['City']), key='city2')
    with col3:
        job_option = st.text_input('Enter a Job Title', key='job_input2')
    filtered_data = data
    if state_option != 'All':
        filtered_data = filtered_data[filtered_data['State'] == state_option]
    if city_option != 'All':
        filtered_data = filtered_data[filtered_data['City'] == city_option]
    if job_option:
        filtered_data = filtered_data[filtered_data['Job Title'].str.contains(job_option, case=False)]
    average_salary = filtered_data.groupby('Job Title')['Average Salary'].mean().nlargest(10).reset_index()
    fig = px.bar(average_salary, x='Average Salary', y='Job Title', title='Average Salary by Job Title',
                 labels={'Average Salary': 'Average Salary ($)'}, color='Average Salary', color_continuous_scale='greens')
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', yaxis={'categoryorder': 'total ascending', 'title': ''}, autosize=True)
    for i, (job_title, salary) in enumerate(zip(average_salary['Job Title'], average_salary['Average Salary'])):
        fig.add_annotation(x=salary, y=job_title, text=f'${salary:,.0f}', showarrow=False, font=dict(color='white'), xshift=25)
    st.plotly_chart(fig, use_container_width=True)


# Top Skills
with tab3:
    st.header('Most Demanding Skills')
    job_title_option = st.selectbox('Select a Job Title', unique_sorted_values_plus_ALL(data['Job Title']), key='job3')
    filtered_data = data[data['Job Title'] == job_title_option] if job_title_option != 'All' else data
    all_skills = [skill for skills in filtered_data['Skill'].dropna() for skill in skills]
    skill_counts = pd.Series(all_skills).value_counts().head(10).reset_index()
    skill_counts.columns = ['Skill', 'Frequency']
    fig = px.bar(skill_counts, y='Skill', x='Frequency', orientation='h', title=f'Top Skills for {job_title_option}', color='Frequency', color_continuous_scale='oranges')
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', yaxis={'categoryorder': 'total ascending', 'title': ''}, autosize=True)
    st.plotly_chart(fig, use_container_width=True)


# Skills Pay
with tab4:
    st.header('Skills Salary Overview')
    skills_salary = [{'Skill': skill, 'Salary': row['Average Salary']} for index, row in data.iterrows() for skill in row['Skill']]
    skills_salary_df = pd.DataFrame(skills_salary)
    average_salary = skills_salary_df.groupby('Skill')['Salary'].mean().reset_index()
    fig = px.bar(average_salary, x='Salary', y='Skill', title='Average Salary by Skill', labels={'Salary': 'Average Salary ($)'}, color='Salary', color_continuous_scale='Purples', height=600)
    fig.update_layout(plot_bgcolor='rgba(0, 0, 0, 0)', paper_bgcolor='rgba(0, 0, 0, 0)', yaxis={'categoryorder': 'total ascending', 'title': ''}, autosize=True)
    for i, (skill, salary) in enumerate(zip(average_salary['Skill'], average_salary['Salary'])):
        fig.add_annotation(x=salary, y=skill, text=f'${salary:,.0f}', showarrow=False, font=dict(color='white'), xshift=25)
    st.plotly_chart(fig, use_container_width=True)
    

# Map
with tab5:
    st.header('Map View')
    # Count the number of jobs in each state
    state_counts = data['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Number of Jobs']
    # If there are NaN values, fill them with 0
    state_counts['Number of Jobs'] = state_counts['Number of Jobs'].fillna(0)
    fig = go.Figure(
        data=go.Choropleth(
            locations=state_counts['State'],
            z=state_counts['Number of Jobs'],
            locationmode='USA-states',
            colorscale='reds',
            colorbar_title="Number of Jobs",
        ),
        layout=go.Layout(
            geo=dict(
                bgcolor='rgba(0,0,0,0)',
                lakecolor='#4E5D6C',
                landcolor='rgba(51,17,0,0.2)',
                subunitcolor='grey'
            ),
            title='Heatmap of Data Science Job Openings in the US',
            font=dict(size=9, color="White"),
            titlefont=dict(size=15, color="White"),
            geo_scope='usa',
            margin=dict(r=0, t=40, l=0, b=0),
            paper_bgcolor='rgba(0,0,0,0)',  # clear background
            plot_bgcolor='rgba(0,0,0,0)',  # clear background
        )
    )
    # Display the map within the Streamlit app
    st.plotly_chart(fig, use_container_width=True)