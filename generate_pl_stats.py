import pandas as pd

# Top Scorers Data (Name, Team, Appearances, Goals)

top_scorers_data = [
    [1, "Mohamed Salah", "Liverpool", 34, 28],
    [2, "Alexander Isak", "Newcastle United", 31, 22],
    [3, "Erling Haaland", "Manchester City", 28, 21],
    [4, "Chris Wood", "Nottingham Forest", 31, 19],
    [5, "Bryan Mbeumo", "Brentford", 33, 18],
    [6, "Yoane Wissa", "Brentford", 30, 16],
    [7, "Ollie Watkins", "Aston Villa", 34, 15],
    [7, "Matheus Cunha", "Wolverhampton Wanderers", 29, 15],
    [9, "Cole Palmer", "Chelsea", 33, 14],
    [9, "Jean-Philippe Mateta", "Crystal Palace", 33, 14],
    [11, "Jørgen Strand Larsen", "Wolverhampton Wanderers", 32, 13],
    [12, "Liam Delap", "Ipswich Town", 33, 12],
    [12, "Luis Díaz", "Liverpool", 33, 12],
    [12, "Justin Kluivert", "AFC Bournemouth", 30, 12],
    [15, "Brennan Johnson", "Tottenham Hotspur", 31, 11],
    [16, "Raúl Jiménez", "Fulham", 34, 10],
    [16, "Nicolas Jackson", "Chelsea", 28, 10],
    [16, "João Pedro", "Brighton & Hove Albion", 27, 10],
    [19, "Alex Iwobi", "Fulham", 34, 9],
    [19, "Antoine Semenyo", "AFC Bournemouth", 33, 9],
    [19, "Kaoru Mitoma", "Brighton & Hove Albion", 33, 9],
    [19, "James Maddison", "Tottenham Hotspur", 31, 9],
    [19, "Cody Gakpo", "Liverpool", 31, 9],
    [19, "Jarrod Bowen", "West Ham United", 30, 9],
    [19, "Harvey Barnes", "Newcastle United", 29, 9],
    [19, "Evanilson", "AFC Bournemouth", 27, 9],
    [19, "Danny Welbeck", "Brighton & Hove Albion", 27, 9],
    [19, "Kai Havertz", "Arsenal", 21, 9],
    [29, "Leandro Trossard", "Arsenal", 34, 8],
    [29, "Bruno Fernandes", "Manchester United", 33, 8],
    [29, "Morgan Rogers", "Aston Villa", 33, 8],
    [29, "Tomás Soucek", "West Ham United", 31, 8],
    [29, "Jacob Murphy", "Newcastle United", 31, 8],
    [29, "Rodrigo Muniz", "Fulham", 31, 8],
    [29, "Dominic Solanke", "Tottenham Hotspur", 25, 8],
    [36, "Ismaïla Sarr", "Crystal Palace", 34, 7],
    [36, "Kevin Schade", "Brentford", 33, 7],
    [36, "Jamie Vardy", "Leicester City", 32, 7],
    [36, "Dango Ouattara", "AFC Bournemouth", 31, 7],
    [36, "Dejan Kulusevski", "Tottenham Hotspur", 30, 7],
    [36, "Iliman Ndiaye", "Everton", 29, 7],
    [36, "Gabriel Martinelli", "Arsenal", 29, 7],
    [36, "Son Heung-Min", "Tottenham Hotspur", 28, 7],
    [36, "Noni Madueke", "Chelsea", 28, 7],
    [36, "Phil Foden", "Manchester City", 25, 7],
    [36, "Jhon Durán", "Aston Villa", 20, 7],
    [47, "Anthony Elanga", "Nottingham Forest", 33, 6],
    [47, "Anthony Gordon", "Newcastle United", 30, 6],
    [47, "Emile Smith Rowe", "Fulham", 30, 6],
    [47, "Mateo Kovacic", "Manchester City", 28, 6],
]




# Top Assists Data (Name, Team, Appearances, Assists)
top_assists_data = [
    [1, "Mohamed Salah", "Liverpool", 34, 18],
    [2, "Jacob Murphy", "Newcastle United", 31, 11],
    [3, "Antonee Robinson", "Fulham", 33, 10],
    [3, "Mikkel Damsgaard", "Brentford", 33, 10],
    [3, "Anthony Elanga", "Nottingham Forest", 33, 10],
    [3, "Bukayo Saka", "Arsenal", 21, 10],
    [7, "Ollie Watkins", "Aston Villa", 34, 9],
    [7, "Bruno Fernandes", "Manchester United", 33, 9],
    [7, "Son Heung-Min", "Tottenham Hotspur", 28, 9],
    [10, "Cole Palmer", "Chelsea", 33, 8],
    [10, "Morgan Rogers", "Aston Villa", 33, 8],
    [10, "Eberechi Eze", "Crystal Palace", 30, 8],
    [10, "Savinho", "Manchester City", 27, 8],
    [14, "Youri Tielemans", "Aston Villa", 34, 7],
    [14, "Rayan Aït-Nouri", "Wolverhampton Wanderers", 33, 7],
    [14, "Declan Rice", "Arsenal", 32, 7],
    [14, "Enzo Fernández", "Chelsea", 32, 7],
    [14, "Elliot Anderson", "Nottingham Forest", 32, 7],
    [14, "Adama Traoré", "Fulham", 32, 7],
    [14, "James Maddison", "Tottenham Hotspur", 31, 7],
    [14, "Jarrod Bowen", "West Ham United", 30, 7],
    [14, "Morgan Gibbs-White", "Nottingham Forest", 29, 7],
    [14, "Kevin De Bruyne", "Manchester City", 24, 7],
    [24, "Bruno Guimarães", "Newcastle United", 34, 6],
    [24, "Alex Iwobi", "Fulham", 34, 6],
    [24, "Bryan Mbeumo", "Brentford", 33, 6],
    [24, "Dominik Szoboszlai", "Liverpool", 32, 6],
    [24, "Alexander Isak", "Newcastle United", 31, 6],
    [24, "Pedro Porro", "Tottenham Hotspur", 31, 6],
    [24, "Jean-Ricner Bellegarde", "Wolverhampton Wanderers", 31, 6],
    [24, "Trent Alexander-Arnold", "Liverpool", 30, 6],
    [24, "Justin Kluivert", "AFC Bournemouth", 30, 6],
    [24, "Matheus Cunha", "Wolverhampton Wanderers", 29, 6],
    [24, "Nicolas Jackson", "Chelsea", 28, 6],
    [24, "João Pedro", "Brighton & Hove Albion", 27, 6],
    [24, "Martin Ødegaard", "Arsenal", 26, 6],
    [24, "Amad", "Manchester United", 22, 6],
    [38, "Milos Kerkez", "AFC Bournemouth", 34, 5],
    [38, "Leandro Trossard", "Arsenal", 34, 5],
    [38, "Luis Díaz", "Liverpool", 33, 5],
    [38, "Anthony Gordon", "Newcastle United", 30, 5],
    [38, "Ilkay Gündogan", "Manchester City", 30, 5],
    [38, "Gabriel Martinelli", "Arsenal", 29, 5],
    [38, "Marcus Tavernier", "AFC Bournemouth", 25, 5],
    [38, "Jérémy Doku", "Manchester City", 25, 5],
    [38, "Matheus Nunes", "Manchester City", 23, 5],
    [38, "Dwight McNeil", "Everton", 17, 5],
    [48, "Ryan Gravenberch", "Liverpool", 34, 4],
    [48, "Tyrick Mitchell", "Crystal Palace", 34, 4],
    [48, "Ismaïla Sarr", "Crystal Palace", 34, 4],
]


# Column names
columns = ["RK", "Name", "Team", "Appearances", "Goals"]
assist_columns = ["RK", "Name", "Team", "Appearances", "Assists"]

# Create DataFrames with column names
df_top_scorers = pd.DataFrame(top_scorers_data, columns=columns)
df_top_assists = pd.DataFrame(top_assists_data, columns=assist_columns)

# Save DataFrames as CSV files
df_top_scorers.to_csv("top_scorers.csv", index=False)
df_top_assists.to_csv("top_assists.csv", index=False)

print("CSV files created: top_scorers.csv and top_assists.csv")

