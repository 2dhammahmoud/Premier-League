# =======================
# 📦 Imports & Setup
# =======================
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# Setup Streamlit
st.set_page_config(page_title="Premier League Dashboard", layout="wide")

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["premier_league"]

# Load collections
teams_data = pd.DataFrame(list(db.teams.find()))
players_data = pd.DataFrame(list(db.players.find()))
match_data_db = pd.DataFrame(list(db.match_results.find()))
fixtures_data = pd.DataFrame(list(db.fixtures.find()))

# Clean ObjectIDs
for df in [teams_data, players_data, match_data_db, fixtures_data]:
    if '_id' in df.columns:
        df['_id'] = df['_id'].astype(str)

# =======================
# 📁 Load CSV for Model & Viz
# =======================
df = pd.read_csv("cleaned_team_stats.csv")
df_goals = pd.read_csv("goals_stats.csv")
df_match = pd.read_csv("match.csv")

# =======================
# 🔖 Tabs Layout
# =======================
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Stats Explorer", "🤖 Match Prediction", "⚔️ Player Comparison", "📈 Visualizations"
])

# ============================================================
# TAB 1: 📊 Stats Explorer
# ============================================================
with tab1:
    st.header("📌 Explore Team & Player Stats")
    
    st.subheader("Select a Team")
    selected_team = st.selectbox("Choose a Team", sorted(teams_data["Team"].unique()))
    team_stats = teams_data[teams_data["Team"] == selected_team]
    st.dataframe(team_stats)

    st.subheader("Top 10 Goal Scorers")
    top_scorers = players_data.sort_values("Goals", ascending=False).head(10)
    st.table(top_scorers[["Player", "Goals", "Assists", "Appearances"]])

# ============================================================
# TAB 2: 🤖 Match Prediction
# ============================================================
with tab2:
    st.title("⚽ Football Match Predictor")

    # Prepare features
    df['result'] = np.random.choice([0, 1, 2], size=len(df))
    label_encoder = LabelEncoder()
    df['Team_encoded'] = label_encoder.fit_transform(df['Team'])
    base_features = ['Goals For', 'Goals Against', 'Points', 'Team_encoded']

    # Create combined features
    match_data = []
    for i in range(len(df)):
        for j in range(len(df)):
            if i != j:
                home = df.iloc[i][base_features].tolist()
                away = df.iloc[j][base_features].tolist()
                label = np.random.choice([0, 1, 2])
                match_data.append(home + away + [label])

    Xy = pd.DataFrame(match_data, columns=[f"{f}_home" for f in base_features] + [f"{f}_away" for f in base_features] + ['result'])
    X, y = Xy.drop("result", axis=1), Xy["result"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    def predict_match(home_team, away_team):
        h_code = label_encoder.transform([home_team])[0]
        a_code = label_encoder.transform([away_team])[0]
        h_data = df[df['Team_encoded'] == h_code][base_features].iloc[0].tolist()
        a_data = df[df['Team_encoded'] == a_code][base_features].iloc[0].tolist()
        input_df = pd.DataFrame([h_data + a_data], columns=X.columns)
        return model.predict(input_df)[0]

    teams = sorted(df["Team"].unique())
    home_team = st.selectbox("Select Home Team", teams)
    away_team = st.selectbox("Select Away Team", [t for t in teams if t != home_team])

    user_home_goals = st.number_input(f"{home_team} Goals", min_value=0, max_value=10, step=1)
    user_away_goals = st.number_input(f"{away_team} Goals", min_value=0, max_value=10, step=1)

    if st.button("Submit My Prediction"):
        st.success(f"✅ You predicted: {home_team} {user_home_goals} - {user_away_goals} {away_team}")

    prediction = predict_match(home_team, away_team)
    st.markdown("### 🤖 Model Prediction")
    if prediction == 1:
        st.info(f"📊 Model predicts: Home team **{home_team}** wins!")
    elif prediction == 0:
        st.info(f"📊 Model predicts: Away team **{away_team}** wins!")
    else:
        st.info("📊 Model predicts: It's a draw!")

    st.markdown("### 🆚 Your Prediction vs Model Prediction")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Your Prediction", f"{home_team} {user_home_goals} - {user_away_goals} {away_team}")
    with col2:
        result_label = "Win" if prediction == 1 else "Loss" if prediction == 0 else "Draw"
        st.metric("Model Prediction", f"{home_team} - {result_label} - {away_team}")

# ============================================================
# TAB 3: ⚔️ Player Comparison
# ============================================================
with tab3:
    st.header("⚔️ Compare Two Players")

    player1 = st.selectbox("Player 1", sorted(players_data["Player"].unique()))
    player2 = st.selectbox("Player 2", sorted(players_data["Player"].unique()))

    p1 = players_data[players_data["Player"] == player1].iloc[0]
    p2 = players_data[players_data["Player"] == player2].iloc[0]

    comparison_df = pd.DataFrame({
        "Metric": ["Goals", "Assists", "Appearances"],
        player1: [p1["Goals"], p1["Assists"], p1["Appearances"]],
        player2: [p2["Goals"], p2["Assists"], p2["Appearances"]],
    })
    st.table(comparison_df)

# ============================================================
# TAB 4: 📈 Visualizations
# ============================================================
with tab4:
    st.header("📊 Top 10 Goal Scorers")
    top_scorers = df_goals.sort_values('Goals', ascending=False).head(10)
    fig1, ax1 = plt.subplots()
    sns.barplot(x='Goals', y='Player', data=top_scorers, palette='viridis', ax=ax1)
    ax1.set_title('Top 10 Scorers of the Season')
    ax1.set_xlabel('Goals Scored')
    ax1.set_ylabel('Player')
    st.pyplot(fig1)

    st.header("📈 Total Points by Team")

    df_teams = pd.read_csv("cleaned_team_stats.csv")
    df_teams[['Played', 'Won', 'Drawn', 'Lost', 'Goals For', 'Goals Against']] = df_teams[['Played', 'Won', 'Drawn', 'Lost', 'Goals For', 'Goals Against']].apply(pd.to_numeric, errors='coerce')
    df_teams['Points'] = pd.to_numeric(df_teams['Points'], errors='coerce')
    df_teams_sorted = df_teams.sort_values('Points', ascending=False)
    fig2, ax2 = plt.subplots()
    sns.scatterplot(data=df_teams_sorted, x='Team', y='Points', hue='Team', palette='tab20', s=100, ax=ax2)
    ax2.set_title('All 20 Teams - Total Points')
    ax2.set_xlabel("")            
    ax2.set_xticks([])           
    ax2.set_xticklabels([])      

    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    st.pyplot(fig2)


    st.header("🔥 Heatmap: Home vs Away Goals by Team")
    home_goals = df_match.groupby('HomeTeam')['HomeTeamScore'].sum()
    away_goals = df_match.groupby('AwayTeam')['AwayTeamScore'].sum()
    venue_data = pd.DataFrame({'Home Goals': home_goals, 'Away Goals': away_goals}).fillna(0)
    fig3, ax3 = plt.subplots(figsize=(10, 8))
    sns.heatmap(venue_data, annot=True, cmap='YlGnBu', fmt='.0f', linewidths=0.5, ax=ax3)
    ax3.set_title("Home vs Away Goals (Venue-wise)")
    st.pyplot(fig3)

    st.header("📅 Weekly Goals Heatmap by Team")
    weekly_home = df_match.groupby(['RoundNumber', 'HomeTeam'])['HomeTeamScore'].sum().reset_index()
    weekly_home.columns = ['RoundNumber', 'Team', 'Goals']
    weekly_away = df_match.groupby(['RoundNumber', 'AwayTeam'])['AwayTeamScore'].sum().reset_index()
    weekly_away.columns = ['RoundNumber', 'Team', 'Goals']
    all_goals = pd.concat([weekly_home, weekly_away])
    heatmap_data = all_goals.pivot_table(index='Team', columns='RoundNumber', values='Goals', aggfunc='sum', fill_value=0)
    fig4, ax4 = plt.subplots(figsize=(12, 8))
    sns.heatmap(heatmap_data, cmap='YlGnBu', annot=True, fmt='.0f', linewidths=0.5, ax=ax4)
    ax4.set_title("Goals Scored per Gameweek")
    st.pyplot(fig4)
