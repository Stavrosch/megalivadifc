import pandas as pd
import json
import os
from datetime import datetime

def extract_player_data_from_excel(file_path):
    """
    Extract player data from all sheets in the Excel file
    """
    try:
        # Read all three sheets
        df_sheet1 = pd.read_excel(file_path, sheet_name='Φύλλο1')
        df_sheet2 = pd.read_excel(file_path, sheet_name='Φύλλο2')
        df_static = pd.read_excel(file_path, sheet_name='Static Info')
        
        players = {}
        
        # Extract stats from Sheet2 (summary table)
        for index, row in df_static.iterrows():
            # Check if this row contains the summary table headers
            if (len(row) > 11 and 
                row.iloc[7] == 'Names' and 
                row.iloc[8] == 'APPS' and 
                row.iloc[9] == 'GOALS' and 
                row.iloc[10] == 'ASSIST' and 
                row.iloc[11] == 'POM'):
                
                # Process the next rows until we hit empty data
                for next_index in range(index + 1, len(df_sheet2)):
                    summary_row = df_sheet2.iloc[next_index]
                    if len(summary_row) <= 7:
                        continue
                        
                    player_name = summary_row.iloc[7]  # Names column
                    
                    # Stop when we hit empty player name
                    if pd.isna(player_name) or player_name == '':
                        break
                    
                    # Extract player stats from summary table
                    players[player_name] = {
                        'apps': int(summary_row.iloc[8]) if not pd.isna(summary_row.iloc[8]) else 0,
                        'goals': int(summary_row.iloc[9]) if not pd.isna(summary_row.iloc[9]) else 0,
                        'assists': int(summary_row.iloc[10]) if not pd.isna(summary_row.iloc[10]) else 0,
                        'pom': int(summary_row.iloc[11]) if not pd.isna(summary_row.iloc[11]) else 0
                    }
                break
        
        # Add static information from Static Info sheet
        for index, row in df_static.iterrows():
            player_name = row.get('Name')
            
            if pd.isna(player_name) or player_name == 'Name' or player_name == 'Static Info':
                continue
                
            if player_name in players:
                players[player_name]['jersey_number'] = int(row.get('#', 0)) if not pd.isna(row.get('#')) else 0
                players[player_name]['age'] = int(row.get('Age', 0)) if not pd.isna(row.get('Age')) else 0
                players[player_name]['height'] = f"{int(row.get('Height', 0))}cm" if not pd.isna(row.get('Height')) else "N/A"
                players[player_name]['position'] = str(row.get('Position', ''))
        
        return players
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return {}

def create_player_json(players_data, output_path='players.json'):
    """
    Create JSON file with player data
    """
    # Add metadata
    output_data = {
        'metadata': {
            'last_updated': datetime.now().isoformat(),
            'total_players': len(players_data),
            'source_file': 'ΜΕΓΑ ΛΙΒΑΔΙ FC.xlsx'
        },
        'players': players_data
    }
    
    # Write to JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON file created successfully: {output_path}")
    print(f"Total players processed: {len(players_data)}")

def update_player_json(excel_file_path, json_file_path='players.json'):
    """
    Update existing JSON file with new data from Excel
    """
    # Read existing JSON if it exists
    existing_data = {}
    if os.path.exists(json_file_path):
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print(f"Found existing JSON file: {json_file_path}")
        except Exception as e:
            print(f"Error reading existing JSON file: {e}")
    
    # Extract new data from Excel
    new_players_data = extract_player_data_from_excel(excel_file_path)
    
    # Merge with existing data
    if 'players' in existing_data:
        for player_name, player_data in new_players_data.items():
            # Update existing player or add new one
            existing_data['players'][player_name] = player_data
    else:
        existing_data['players'] = new_players_data
        
    if existing_data['players']:
        top_scorer = max(existing_data['players'].items(), key=lambda x: x[1].get('goals', 0))
        top_assister = max(existing_data['players'].items(), key=lambda x: x[1].get('assists', 0))
        
        existing_data['top_performers'] = {
            'top_scorer': {
                'name': top_scorer[0],
                'goals': top_scorer[1].get('goals', 0)
            },
            'top_assister': {
                'name': top_assister[0],
                'assists': top_assister[1].get('assists', 0)
            }
        }    
    
    # Update metadata
    existing_data['metadata'] = {
        'last_updated': datetime.now().isoformat(),
        'total_players': len(existing_data['players']),
        'source_file': 'ΜΕΓΑ ΛΙΒΑΔΙ FC.xlsx',
        'previous_update': existing_data.get('metadata', {}).get('last_updated')
    }
    
    # Write updated JSON
    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON file updated successfully: {json_file_path}")
    print(f"Total players: {len(existing_data['players'])}")

# Main execution
if __name__ == "__main__":
    excel_file = "ΜΕΓΑ ΛΙΒΑΔΙ FC.xlsx"
    json_file = "players.json"
    
    # Check if Excel file exists
    if not os.path.exists(excel_file):
        print(f"Error: Excel file '{excel_file}' not found!")
        exit(1)
    
    # Update JSON file
    update_player_json(excel_file, json_file)
    
    # Print the data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("\nPlayer data extracted:")
        print("=" * 80)
        for player, stats in data['players'].items():
            print(f"{player}:")
            print(f"  Position: {stats.get('position', 'N/A')}")
            print(f"  Age: {stats.get('age', 'N/A')}")
            print(f"  Height: {stats.get('height', 'N/A')}")
            print(f"  Jersey: #{stats.get('jersey_number', stats.get('number', 'N/A'))}")
            print(f"  Stats: APPS={stats.get('apps', 0)}, GOALS={stats.get('goals', 0)}, ASSISTS={stats.get('assists', 0)}, POM={stats.get('pom', 0)}")
            print("-" * 40)
            
        print("\nTop Performers:")
        print("=" * 40)

        # Find top goalscorer
        top_scorer = max(data['players'].items(), key=lambda x: x[1].get('goals', 0))
        print(f"Top Goalscorer: {top_scorer[0]}")
        print(f"  Goals: {top_scorer[1].get('goals', 0)}")

        # Find top assister  
        top_assister = max(data['players'].items(), key=lambda x: x[1].get('assists', 0))
        print(f"Top Assister: {top_assister[0]}")
        print(f"  Assists: {top_assister[1].get('assists', 0)}")
            