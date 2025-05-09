import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create directory for histograms if it doesn't exist
output_dir = 'histogram_result'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load the CSV file
df = pd.read_csv("results.csv")

# Convert relevant columns to numeric, handling errors
stats = ['Gls', 'Ast', 'xG', 'TklW', 'Lost', 'Sh']
for stat in stats:
    df[stat] = pd.to_numeric(df[stat], errors='coerce')

# Set up the plotting style
plt.style.use('ggplot')

# Get unique teams
teams = df['Team'].unique()

# Explanation text for player representation
player_explanation = (
    "This histogram shows the distribution of the statistic for players in the team. "
    "Each bar represents the number of players with values in a specific range, "
    "symbolizing their performance within the team."
)

# Generate a separate plot for each team and each statistic
for team in teams:
    # Filter data for the current team
    team_data = df[df['Team'] == team]
    
    # Create a separate figure for each statistic
    for stat in stats:
        plt.figure(figsize=(8, 6))
        sns.histplot(data=team_data, x=stat, kde=True, line_kws={'color': 'red'})
        plt.title(f'{stat} Distribution for {team}')
        plt.xlabel(stat)
        plt.ylabel('Count')
        
        # Add player representation explanation text
        plt.text(
            0.02, 0.98, player_explanation, 
            transform=plt.gca().transAxes, 
            fontsize=8, 
            verticalalignment='top', 
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8)
        )
        
        # Save the plot to the histogram_result folder
        safe_team_name = team.replace(' ', '_').replace('/', '_')  # Replace spaces and slashes for safe filenames
        plt.savefig(os.path.join(output_dir, f'{safe_team_name}_{stat}_histogram.png'))
        plt.close()  # Close the figure to free memory