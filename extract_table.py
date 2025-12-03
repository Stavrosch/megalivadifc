"""
Extract league table data from sheet.htm and save as JSON
"""

import json
import re
from bs4 import BeautifulSoup
import os

def extract_table_data():
    try:
        # Read the HTML file
        with open('sheet.htm', 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all table rows
        rows = soup.find_all('tr')
        teams = []
        
        # Process rows from 6 to 16 (where team data is located)
        for i in range(6, 17):  # 6 to 16 inclusive
            if i >= len(rows):
                break
                
            row = rows[i]
            cells = row.find_all('td')
            
            if len(cells) >= 11:
                position = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                team_name = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                
                # Only process rows with valid data
                if position and team_name and position.isdigit():
                    team_data = {
                        'position': int(position),
                        'team': clean_team_name(team_name),
                        'played': safe_int(cells[3].get_text(strip=True)),
                        'won': safe_int(cells[4].get_text(strip=True)),
                        'drawn': safe_int(cells[5].get_text(strip=True)),
                        'lost': safe_int(cells[6].get_text(strip=True)),
                        'goalsFor': safe_int(cells[7].get_text(strip=True)),
                        'goalsAgainst': safe_int(cells[8].get_text(strip=True)),
                        'goalDifference': safe_int(cells[9].get_text(strip=True)),
                        'points': safe_int(cells[10].get_text(strip=True))
                    }
                    
                    teams.append(team_data)
        
        # Sort by position to ensure correct order
        teams.sort(key=lambda x: x['position'])
        
        # Save to JSON file
        output_data = {
            'last_updated': get_current_timestamp(),
            'teams': teams
        }
        
        with open('league_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(output_data, json_file, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully extracted data for {len(teams)} teams")
        print(f"📊 Our team position: {get_our_team_position(teams)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error extracting table data: {e}")
        return False

def clean_team_name(name):
    """Clean and standardize team names"""
    name_map = {
        'ΜΕΓΑΛΟ ΛΕΙΒΑΔΙ': 'Μεγάλο Λειβάδι FC',
        'ΜΕΓΑΛΟ ΛΕΙΒΑΔΙ FC': 'Μεγάλο Λειβάδι FC',
        'MINEIRO': 'Mineiro FC',
        'ΑΠΙΑΣΤΟΙ': 'Απιάστοι FC',
        'ΓΥΠΑΕΤΟΙ': 'Γυπαετοί FC',
        'ΠΑΡΑΓΚΑ': 'Παράγκα FC',
        'XAΣΟΜΕΡ CITY': 'Xασόμερ City',
        'WIND': 'Wind FC',
        'NEVERTON': 'Neverton FC',
        'ΑΣΤΕΡΑΣ ΕΞΑΡΧΕΙΩΝ': 'Αστέρας Εξαρχείων',
        'AMΠΑΛΟΙ F.C': 'Αμπαλοί FC',
        'ΠΤΩΜΑΤΑ F.C': 'Πτώματα FC',
        'GOTHAM CITY (-6β)': 'Gotham City'
    }
    
    clean_name = re.sub(r'\s+', ' ', name).strip()
    return name_map.get(clean_name, clean_name)

def safe_int(value, default=0):
    """Safely convert to integer"""
    try:
        # Remove any non-digit characters except minus sign
        cleaned = re.sub(r'[^\d-]', '', str(value))
        return int(cleaned) if cleaned else default
    except (ValueError, TypeError):
        return default

def get_current_timestamp():
    """Get current timestamp in readable format"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_our_team_position(teams):
    """Find our team's position"""
    for team in teams:
        if 'Μεγάλο Λειβάδι' in team['team']:
            return team['position']
    return "Not found"

if __name__ == "__main__":
    print("🔄 Extracting league table data from sheet.htm...")
    success = extract_table_data()
    
    if success:
        print("✅ Data extraction completed successfully!")
        print("📁 Data saved to: league_data.json")
    else:
        print("❌ Data extraction failed!")