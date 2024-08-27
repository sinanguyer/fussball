import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize the database
def init_db():
    conn = sqlite3.connect('foosball.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS matches
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  teams TEXT,
                  scores TEXT,
                  comments TEXT)''')
    conn.commit()
    conn.close()

# Normalize team names
def normalize_team_names(teams):
    normalized_teams = []
    for team in teams:
        sorted_team = " ".join(sorted(team.split()))
        normalized_teams.append(sorted_team)
    return normalized_teams

# Add a new match to the database
def add_match(date, teams, scores, comments):
    normalized_teams = normalize_team_names(teams)
    teams_str = ', '.join(normalized_teams)
    scores_str = ', '.join(map(str, scores))
    comments_str = ', '.join(comments)
    
    conn = sqlite3.connect('foosball.db')
    c = conn.cursor()
    c.execute("INSERT INTO matches (date, teams, scores, comments) VALUES (?, ?, ?, ?)",
              (date, teams_str, scores_str, comments_str))
    conn.commit()
    conn.close()

# Get match data
def get_matches():
    conn = sqlite3.connect('foosball.db')
    df = pd.read_sql_query("SELECT * FROM matches ORDER BY date DESC", conn)
    conn.close()
    return df

# Calculate team statistics
def calculate_statistics(df):
    team_stats = {}
    for index, row in df.iterrows():
        teams = row['teams'].split(', ')
        scores = list(map(int, row['scores'].split(', ')))
        for team, score in zip(teams, scores):
            if team in team_stats:
                team_stats[team]['matches'] += 1
                team_stats[team]['total_score'] += score
            else:
                team_stats[team] = {'matches': 1, 'total_score': score}
    return team_stats

# Plot team statistics
def plot_team_statistics(stats):
    teams = list(stats.keys())
    matches_played = [stats[team]['matches'] for team in teams]
    total_scores = [stats[team]['total_score'] for team in teams]

    df_stats = pd.DataFrame({
        'Team': teams,
        'Matches Played': matches_played,
        'Total Score': total_scores
    })

    fig, ax = plt.subplots(1, 2, figsize=(16, 6))

    sns.barplot(data=df_stats, x='Team', y='Matches Played', ax=ax[0], palette='Blues_d')
    ax[0].set_title('Matches Played by Team')
    ax[0].set_ylabel('Matches Played')
    ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45, ha='right')

    sns.barplot(data=df_stats, x='Team', y='Total Score', ax=ax[1], palette='Oranges_d')
    ax[1].set_title('Total Scores by Team')
    ax[1].set_ylabel('Total Score')
    ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45, ha='right')

    st.pyplot(fig)

# Initialize the database
init_db()

# Streamlit UI
st.title("Foosball Match Tracker")

# Input Form
st.header("Add New Match")
with st.form(key='match_form'):
    date = st.date_input("Match Date")
    team1 = st.text_input("Team 1")
    score1 = st.number_input("Score 1", min_value=0, step=1)
    comment1 = st.text_input("Comment for Team 1")

    team2 = st.text_input("Team 2")
    score2 = st.number_input("Score 2", min_value=0, step=1)
    comment2 = st.text_input("Comment for Team 2")

    additional_teams = []
    while st.checkbox(f"Add another team?", key=f"team_{len(additional_teams) + 3}"):
        team_name = st.text_input(f"Team {len(additional_teams) + 3}")
        score = st.number_input(f"Score {len(additional_teams) + 3}", min_value=0, step=1)
        comment = st.text_input(f"Comment for Team {len(additional_teams) + 3}")
        additional_teams.append((team_name, score, comment))

    teams = [team1, team2] + [t[0] for t in additional_teams]
    scores = [score1, score2] + [t[1] for t[2] in additional_teams]
    comments = [comment1, comment2] + [t[2] for t in additional_teams]

    submit = st.form_submit_button(label="Submit Match")

    if submit:
        add_match(str(date), teams, scores, comments)
        st.success("Match added successfully!")

# Display match data
st.header("Match Data")
matches_df = get_matches()
st.dataframe(matches_df)

# Calculate and display team statistics
if not matches_df.empty:
    st.header("Team Statistics")
    team_stats = calculate_statistics(matches_df)

    st.header("Visualized Team Statistics")
    plot_team_statistics(team_stats)
