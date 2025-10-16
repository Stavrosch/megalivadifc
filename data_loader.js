// Function to load all dynamic data
async function loadAllData() {
    try {
        // Load players data for key players section
        await loadKeyPlayers();
        
        // Load matches data for results and team stats
        await loadMatchesData();
        
    } catch (error) {
        console.error('Error loading data:', error);
    }
}

// Function to load key players data
async function loadKeyPlayers() {
    try {
        const response = await fetch('players.json');
        if (!response.ok) {
            throw new Error('Failed to load player data');
        }
        const data = await response.json();
        
        // Update president stats based on team performance
        updatePresidentStats(data);
        
        // Update top performers
        updateTopPerformers(data);
        
    } catch (error) {
        console.error('Error loading key players data:', error);
    }
}

// Function to update president stats based on team performance
function updatePresidentStats(data) {
    let totalMatches = 0;
    
    // Calculate team stats from players data
    Object.values(data.players).forEach(player => {
        if (player.apps > totalMatches) {
            totalMatches = player.apps;
        }
    });
    
    // Update the president's stats
    const presidentMatches = document.getElementById('president-matches');
    const presidentWins = document.getElementById('president-wins');
    const presidentLosses = document.getElementById('president-losses');
    
    if (presidentMatches) presidentMatches.textContent = totalMatches;
    // Wins and losses will be updated from matches data
}

// Function to update top performers
function updateTopPerformers(data) {
    // Get top performers from the data
    const topScorerName = data.top_performers.top_scorer.name;
    const topAssisterName = data.top_performers.top_assister.name;
    
    // Find the player data for top scorer
    const topScorerData = data.players[topScorerName];
    if (topScorerData) {
        document.getElementById('top-scorer-card').style.display = 'block';
        document.getElementById('top-scorer-img').src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(topScorerName)}`;
        document.getElementById('top-scorer-name').textContent = topScorerName;
        document.getElementById('top-scorer-matches').textContent = topScorerData.apps || 0;
        document.getElementById('top-scorer-goals').textContent = topScorerData.goals || 0;
        document.getElementById('top-scorer-assists').textContent = topScorerData.assists || 0;
    }
    
    // Find the player data for top assister
    const topAssisterData = data.players[topAssisterName];
    if (topAssisterData) {
        document.getElementById('top-assister-card').style.display = 'block';
        document.getElementById('top-assister-img').src = `https://api.dicebear.com/7.x/avataaars/svg?seed=${encodeURIComponent(topAssisterName)}`;
        document.getElementById('top-assister-name').textContent = topAssisterName;
        document.getElementById('top-assister-matches').textContent = topAssisterData.apps || 0;
        document.getElementById('top-assister-goals').textContent = topAssisterData.goals || 0;
        document.getElementById('top-assister-assists').textContent = topAssisterData.assists || 0;
    }
}

// Function to load matches data
async function loadMatchesData() {
    try {
        const response = await fetch('matches.json');
        if (!response.ok) {
            throw new Error('Failed to load matches data');
        }
        const matchesData = await response.json();
        
        // Update recent results
        updateRecentResults(matchesData);
        
        // Update team statistics
        updateTeamStatistics(matchesData);
        
        // Update president wins/losses
        updatePresidentWinsLosses(matchesData);
        
    } catch (error) {
        console.error('Error loading matches data:', error);
        // Fallback to hardcoded data if matches.json doesn't exist
        useHardcodedMatchData();
    }
}

// Function to update recent results
function updateRecentResults(matchesData) {
    const matchesContainer = document.querySelector('#results .matches');
    if (!matchesContainer) return;
    
    // Clear existing content
    matchesContainer.innerHTML = '';
    
    // Sort matches by date (newest first) and get recent ones
    const recentMatches = matchesData.matches
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, 3); // Get 3 most recent matches
    
    recentMatches.forEach(match => {
        const matchCard = document.createElement('div');
        matchCard.className = 'card match-card';
        
        // Determine status based on outcome
        const statusClass = match.outcome === 'W' ? 'status-won' : 
                           match.outcome === 'L' ? 'status-lost' : 'status-upcoming';
        const statusText = match.outcome === 'W' ? 'Win' : 
                          match.outcome === 'L' ? 'Lost' : 'Upcoming';
        
        matchCard.innerHTML = `
            <div class="match-info">
                <div class="match-date">${formatDate(match.date)}</div>
                <div class="match-teams">
                    <div class="match-result">${match.result}</div>
                    <div>${match.opponent} vs Μεγάλο Λειβάδι FC</div>
                </div>
            </div>
            <div class="match-status ${statusClass}">${statusText}</div>
        `;
        
        matchesContainer.appendChild(matchCard);
    });
}

// Function to update team statistics
function updateTeamStatistics(matchesData) {
    // Use the summary data directly from matches.json
    const summary = matchesData.summary;
    
    // Update team stats cards
    const matchesWon = document.querySelector('.stat-card:nth-child(1) h3');
    const goalsScored = document.querySelector('.stat-card:nth-child(2) h3');
    const cleanSheets = document.querySelector('.stat-card:nth-child(3) h3');
    
    if (matchesWon) matchesWon.textContent = summary.wins;
    if (goalsScored) goalsScored.textContent = summary.goals_for;
    if (cleanSheets) cleanSheets.textContent = '0'; // You can calculate this from match data if available
}

// Function to update president wins/losses
function updatePresidentWinsLosses(matchesData) {
    const summary = matchesData.summary;
    
    const presidentWins = document.getElementById('president-wins');
    const presidentLosses = document.getElementById('president-losses');
    
    if (presidentWins) presidentWins.textContent = summary.wins;
    if (presidentLosses) presidentLosses.textContent = summary.losses;
}

// Function to format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Fallback function if matches.json doesn't exist
function useHardcodedMatchData() {
    // Update team stats based on hardcoded results
    document.querySelector('.stat-card:nth-child(1) h3').textContent = '1';
    document.querySelector('.stat-card:nth-child(2) h3').textContent = '5';
    
    // Update president wins/losses
    const presidentWins = document.getElementById('president-wins');
    const presidentLosses = document.getElementById('president-losses');
    if (presidentWins) presidentWins.textContent = '1';
    if (presidentLosses) presidentLosses.textContent = '2';
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    loadAllData();
});