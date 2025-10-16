// load-table.js

class TableLoader {
    constructor() {
        this.leagueData = null;
    }

    // Load data from JSON file
    async loadTableData() {
        try {
            console.log('Loading league data from JSON...');
            
            const response = await fetch('league_data.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            this.leagueData = await response.json();
            console.log('League data loaded successfully:', this.leagueData);
            
            this.updateCompleteLeagueTable();
            this.updateLastUpdated();
            
            return this.leagueData;
        } catch (error) {
            console.error('Error loading league data:', error);
            this.showError();
            return null;
        }
    }

    // Update the complete league table
    updateCompleteLeagueTable() {
        const tableBody = document.getElementById('league-table');
        if (!tableBody || !this.leagueData) return;

        // Clear existing content
        tableBody.innerHTML = '';

        // Add all teams to the table
        this.leagueData.teams.forEach(team => {
            const row = document.createElement('tr');
            
            // Highlight our team
            if (team.team.includes('Μεγάλο Λειβάδι')) {
                row.style.backgroundColor = '#fff3cd';
                row.style.fontWeight = '600';
            } else {
                row.style.backgroundColor = '#f9f9f9';
            }
            
            row.innerHTML = `
                <td style="padding: 12px 15px; font-weight: 700; text-align: center;">${team.position}</td>
                <td style="padding: 12px 15px;">${team.team}</td>
                <td style="padding: 12px 15px; text-align: center;">${team.played}</td>
                <td style="padding: 12px 15px; text-align: center;">${team.won}</td>
                <td style="padding: 12px 15px; text-align: center;">${team.drawn}</td>
                <td style="padding: 12px 15px; text-align: center;">${team.lost}</td>
                <td style="padding: 12px 15px; text-align: center;">${team.goalsFor}</td>
                <td style="padding: 12px 15px; text-align: center;">${team.goalsAgainst}</td>
                <td style="padding: 12px 15px; text-align: center;">${team.goalDifference}</td>
                <td style="padding: 12px 15px; text-align: center; font-weight: 700;">${team.points}</td>
            `;
            
            tableBody.appendChild(row);
        });

        // Update team stats
        this.updateTeamStats();
    }

    // Update team statistics
    updateTeamStats() {
        const ourTeam = this.leagueData.teams.find(team => 
            team.team.includes('Μεγάλο Λειβάδι')
        );
        
        if (!ourTeam) return;

        // Update matches won
        const matchesWonElement = document.getElementById('matches-won');
        if (matchesWonElement) matchesWonElement.textContent = ourTeam.won;
        
        // Update goals scored
        const goalsScoredElement = document.getElementById('goals-scored');
        if (goalsScoredElement) goalsScoredElement.textContent = ourTeam.goalsFor;
        
        // Update clean sheets (you might need to calculate this)
        const cleanSheetsElement = document.getElementById('clean-sheets');
        if (cleanSheetsElement) cleanSheetsElement.textContent = '0'; // Placeholder
        
        // Update league position
        const leaguePositionElement = document.getElementById('league-position');
        if (leaguePositionElement) {
            leaguePositionElement.textContent = this.getOrdinalSuffix(ourTeam.position);
        }
    }

    // Update last updated timestamp
    updateLastUpdated() {
        const timestampElement = document.getElementById('last-updated');
        if (timestampElement && this.leagueData.last_updated) {
            timestampElement.textContent = this.leagueData.last_updated;
        }
    }

    // Show error message
    showError() {
        const tableBody = document.getElementById('league-table');
        if (tableBody) {
            tableBody.innerHTML = `
                <tr style="background-color: #f9f9f9;">
                    <td colspan="10" style="padding: 20px; text-align: center; color: #dc3545;">
                        Error loading league table data. Please try again later.
                    </td>
                </tr>
            `;
        }
    }

    // Helper function for ordinal suffixes
    getOrdinalSuffix(number) {
        if (number % 100 >= 11 && number % 100 <= 13) {
            return number + 'th';
        }
        switch (number % 10) {
            case 1: return number + 'st';
            case 2: return number + 'nd';
            case 3: return number + 'rd';
            default: return number + 'th';
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const tableLoader = new TableLoader();
    tableLoader.loadTableData();
});