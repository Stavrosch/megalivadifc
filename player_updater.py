import pandas as pd
import json
import os
from datetime import datetime

def extract_player_data_from_excel(file_path):
    """
    Extract player data from all sheets in the Excel file
    """
    try:
        # Read with openpyxl engine
        df_sheet1 = pd.read_excel(file_path, sheet_name='Φύλλο1', engine='openpyxl')
        df_sheet2 = pd.read_excel(file_path, sheet_name='Φύλλο2', engine='openpyxl')
        df_static = pd.read_excel(file_path, sheet_name='Static Info', engine='openpyxl')
        
        players = {}
        
        # FIRST: Get static information from Static Info sheet
        for index, row in df_static.iterrows():
            player_name = row.iloc[2] if len(row) > 2 else None  # Column C (Name)
            
            if pd.isna(player_name) or player_name in ['Name', 'Static Info', None]:
                continue
                
            players[player_name] = {
                'jersey_number': int(row.iloc[1]) if len(row) > 1 and not pd.isna(row.iloc[1]) else 0,
                'age': int(row.iloc[3]) if len(row) > 3 and not pd.isna(row.iloc[3]) else 0,
                'height': f"{int(row.iloc[4])}cm" if len(row) > 4 and not pd.isna(row.iloc[4]) else "N/A",
                'position': str(row.iloc[5]) if len(row) > 5 and not pd.isna(row.iloc[5]) else "N/A",
                'apps': 0,
                'goals': 0, 
                'assists': 0,
                'pom': 0
            }
        
        # MANUAL CALCULATION: Parse match data from Sheet2 to calculate stats
        print("Calculating stats from match data...")
        
        current_match_date = None
        pom_candidates = []
        match_players = set()
        
        for index, row in df_sheet2.iterrows():
            if len(row) < 3:
                continue
                
            if 'Date' in str(row.iloc[0]) and len(row) > 2:
                current_match_date = row.iloc[2]
                print(f"Found match date: {current_match_date}")
                match_players = set()  # Reset for new match
            
            # Check for Player of the Match
            elif 'Player of the Match' in str(row.iloc[0]) and len(row) > 3:
                pom_name = row.iloc[3]
                if pd.notna(pom_name) and pom_name != '' and pom_name != 'Player of the Match':
                    print(f"Found Player of the Match: {pom_name}")
                    if pom_name in players:
                        players[pom_name]['pom'] += 1
                        print(f"Awarded POM to: {pom_name}")
            
            elif (pd.notna(row.iloc[1]) and 
                  str(row.iloc[1]).isdigit() and 
                  pd.notna(row.iloc[2]) and 
                  isinstance(row.iloc[2], str) and
                  row.iloc[2] in players):
                
                player_name = row.iloc[2]
                played = row.iloc[3] if len(row) > 3 else None
                goals = row.iloc[4] if len(row) > 4 else 0
                assists = row.iloc[5] if len(row) > 5 else 0
                
                debug_info = f"Player: {player_name}, Played: {played}, Goals: {goals}, Assists: {assists}"
                
                if (pd.notna(played) and played != 0 and played != '0' and 
                    played != ''):
                    players[player_name]['apps'] += 1
                    match_players.add(player_name)
                    debug_info += f" → APPEARANCE (#{players[player_name]['apps']})"
                
                # Add goals
                if pd.notna(goals):
                    try:
                        goal_count = int(goals)
                        if goal_count > 0:
                            old_goals = players[player_name]['goals']
                            players[player_name]['goals'] += goal_count
                            debug_info += f" → +{goal_count} GOALS (total: {players[player_name]['goals']})"
                    except (ValueError, TypeError):
                        pass
                
                # Add assists  
                if pd.notna(assists):
                    try:
                        assist_count = int(assists)
                        if assist_count > 0:
                            old_assists = players[player_name]['assists']
                            players[player_name]['assists'] += assist_count
                            debug_info += f" → +{assist_count} ASSISTS (total: {players[player_name]['assists']})"
                    except (ValueError, TypeError):
                        pass
                
                print(debug_info)
        
        print(f"\nManual calculation completed for {len(players)} players")
        
        # Print summary of top performers
        print("\n=== CALCULATION SUMMARY ===")
        for player_name, stats in sorted(players.items(), key=lambda x: x[1]['goals'], reverse=True)[:5]:
            print(f"{player_name}: {stats['goals']} goals, {stats['assists']} assists, {stats['apps']} apps, {stats['pom']} POM")
        
        return players
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        import traceback
        traceback.print_exc()
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
    
    new_players_data = extract_player_data_from_excel(excel_file_path)
    
    if not new_players_data:
        print("ERROR: No player data extracted from Excel file!")
        return
    
    # Merge with existing data (preserve existing data if any)
    if 'players' in existing_data:
        # Update existing players with new data
        for player_name, player_data in new_players_data.items():
            existing_data['players'][player_name] = player_data
    else:
        existing_data['players'] = new_players_data
        
    # Update top performers
    if existing_data['players']:
        # Find top scorer (most goals)
        top_scorer = max(existing_data['players'].items(), key=lambda x: x[1].get('goals', 0))
        
        # Find top assister (most assists)
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
        
        print(f"\nTop Scorer: {top_scorer[0]} with {top_scorer[1].get('goals', 0)} goals")
        print(f"Top Assister: {top_assister[0]} with {top_assister[1].get('assists', 0)} assists")
    
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
    
    # Print the final data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print("\n" + "="*80)
        print("FINAL PLAYER DATA:")
        print("="*80)
        for player, stats in data['players'].items():
            print(f"{player}:")
            print(f"  Position: {stats.get('position', 'N/A')}")
            print(f"  Age: {stats.get('age', 'N/A')}")
            print(f"  Height: {stats.get('height', 'N/A')}")
            print(f"  Jersey: #{stats.get('jersey_number', 'N/A')}")
            print(f"  Stats: APPS={stats.get('apps', 0)}, GOALS={stats.get('goals', 0)}, ASSISTS={stats.get('assists', 0)}, POM={stats.get('pom', 0)}")
            print("-" * 40)
            
        print("\nTOP PERFORMERS:")
        print("=" * 40)
        if 'top_performers' in data:
            print(f"Top Goalscorer: {data['top_performers']['top_scorer']['name']}")
            print(f"  Goals: {data['top_performers']['top_scorer']['goals']}")
            print(f"Top Assister: {data['top_performers']['top_assister']['name']}")
            print(f"  Assists: {data['top_performers']['top_assister']['assists']}")