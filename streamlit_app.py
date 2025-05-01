import streamlit as st
import pandas as pd
from pymongo import MongoClient

# -------------------- MongoDB Connection --------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["premier_league"]

# -------------------- Load Data from MongoDB --------------------
# Fetch data from MongoDB collections
teams_data = pd.DataFrame(list(db.teams.find()))
players_data = pd.DataFrame(list(db.players.find()))
match_data = pd.DataFrame(list(db.match_results.find()))
fixtures_data = pd.DataFrame(list(db.fixtures.find()))

# -------------------- Ensure ObjectId Handling --------------------
# Convert _id field to string (to avoid serialization issues)
if '_id' in teams_data.columns:
    teams_data['_id'] = teams_data['_id'].apply(str)
if '_id' in players_data.columns:
    players_data['_id'] = players_data['_id'].apply(str)
if '_id' in match_data.columns:
    match_data['_id'] = match_data['_id'].apply(str)
if '_id' in fixtures_data.columns:
    fixtures_data['_id'] = fixtures_data['_id'].apply(str)

# -------------------- Streamlit Configuration --------------------
st.set_page_config(page_title="Premier League Dashboard", layout="wide")
st.title("🏆 Premier League Interactive Dashboard")

# -------------------- Streamlit Tabs --------------------
tab1, tab2, tab3 = st.tabs(["📊 Stats Explorer", "🤖 Match Prediction", "⚔️ Player Comparison"])

# ======================================================
# 📊 TAB 1 - Stats Explorer
# ======================================================
with tab1:
    st.header("📌 Explore Team & Player Stats")

    st.subheader("Select a Team to View Stats")
    selected_team = st.selectbox("Choose a Team", sorted(teams_data["Team"].unique()))
    team_stats = teams_data[teams_data["Team"] == selected_team]
    st.dataframe(team_stats)

    st.subheader("Top 10 Goal Scorers")
    top_scorers = players_data.sort_values("Goals", ascending=False).head(10)
    st.table(top_scorers[["Player", "Goals", "Assists", "Appearances"]])

# ======================================================
# 🤖 TAB 2 - Match Prediction & User Input
# ======================================================
with tab2:
    st.header("⚽ Predict a Match")

    teams = sorted(teams_data["Team"].unique())
    col1, col2 = st.columns(2)
    with col1:
        home_team = st.selectbox("Home Team", teams)
    with col2:
        away_team = st.selectbox("Away Team", [team for team in teams if team != home_team])

    st.subheader("🧍 Your Prediction")
    user_home_goals = st.number_input(f"{home_team} Goals", min_value=0, max_value=10, step=1)
    user_away_goals = st.number_input(f"{away_team} Goals", min_value=0, max_value=10, step=1)

    if st.button("Submit My Prediction"):
        st.success(f"✅ You predicted: {home_team} {user_home_goals} - {user_away_goals} {away_team}")

    st.markdown("### 🤖 Model Prediction (Mocked)")

    # ⚠️ Replace this with your actual model and input features
    prediction = "2 - 1"  # Placeholder

    st.info(f"📊 Model predicts: {home_team} {prediction} {away_team}")

    # Comparison
    st.markdown("### 🆚 Your Prediction vs Model")
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Your Prediction", f"{home_team} \n {user_home_goals} - {user_away_goals} {away_team}")
    with col4:
        st.metric("Model Prediction", f"{home_team} \n {prediction} {away_team}")

# ======================================================
# ⚔️ TAB 3 - Player Comparison
# ======================================================
with tab3:
    st.header("⚔️ Compare Two Players")

    player1 = st.selectbox("Player 1", sorted(players_data["Player"].unique()))
    player2 = st.selectbox("Player 2", sorted(players_data["Player"].unique()))

    p1_stats = players_data[players_data["Player"] == player1].iloc[0]
    p2_stats = players_data[players_data["Player"] == player2].iloc[0]

    st.subheader("📊 Side-by-Side Comparison")
    comparison_df = pd.DataFrame({
        "Metric": ["Goals", "Assists", "Appearances"],
        player1: [p1_stats["Goals"], p1_stats["Assists"], p1_stats["Appearances"]],
        player2: [p2_stats["Goals"], p2_stats["Assists"], p2_stats["Appearances"]],
    })

    st.table(comparison_df)
