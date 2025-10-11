// results.js
// Load match data from JSON
async function loadMatchData() {
    try {
        const response = await fetch('matches.json');
        if (!response.ok) {
            throw new Error('Failed to load match data');
        }
        const data = await response.json();
        displayMatches(data.matches);
    } catch (error) {
        console.error('Error loading match data:', error);
        document.getElementById('matches-container').innerHTML = 
            '<div class="loading">Error loading match data. Please try again later.</div>';
    }
}

// Display matches from JSON data
function displayMatches(matches) {
    const container = document.getElementById('matches-container');
    container.innerHTML = '';
    
    // Add pitch CSS only once
    if (!document.querySelector('#pitch-styles')) {
        const pitchStyles = document.createElement('style');
        pitchStyles.id = 'pitch-styles';
        pitchStyles.textContent = `
            .pitch-container {
                position: relative;
                width: 75%;
                height: 500px;
                background: linear-gradient(to bottom, #27ae60, #2ecc71);
                border: 2px solid #fff;
                border-radius: 10px;
                margin-top: 20px;
                overflow: hidden;
            }
            
            .player-on-pitch {
                position: absolute;
                width: 70px;
                height: 70px;
                background-color: #be1b1e;
                border: 2px solid #fff;
                border-radius: 50%;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.7rem;
                font-weight: bold;
                text-align: center;
                padding: 5px;
                box-sizing: border-box;
                cursor: pointer;
                transition: all 0.3s ease;
                z-index: 2;
                transform: translate(-50%, -50%);
            }
            
            .player-on-pitch:hover {
                transform: translate(-50%, -50%) scale(1.1) !important;
                z-index: 10;
                box-shadow: 0 0 10px rgba(0,0,0,0.5);
            }

            .stats-symbols {
                display: flex;
                justify-content: center;
                gap: 2px;
                margin-top: 2px;
                font-size: 8px;
                flex-wrap: wrap;
                max-width: 60px;
            }

            .bench-container {
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #6c757d;
            }

            .bench-title {
                font-weight: 600;
                color: #495057;
                margin-bottom: 10px;
                font-size: 1rem;
            }

            .bench-players {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }

            .bench-player {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                background: white;
                border-radius: 20px;
                border: 1px solid #dee2e6;
                font-size: 0.85rem;
            }

            .bench-player-number {
                font-weight: bold;
                color: #be1b1e;
                font-size: 0.8rem;
            }

            .bench-player-name {
                font-weight: 500;
            }

            .bench-stats-symbols {
                display: flex;
                gap: 3px;
                font-size: 0.75rem;
            }
        `;
        document.head.appendChild(pitchStyles);
    }
    
    // Sort matches by date (newest first)
    matches.sort((a, b) => new Date(b.date) - new Date(a.date));
    
    matches.forEach(match => {
        const accordion = document.createElement('div');
        accordion.className = 'accordion';
        
        // Format date
        const matchDate = new Date(match.date);
        const formattedDate = matchDate.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        // Determine status and score
        let statusClass, scoreText;
        if (match.result) {
            const [goalsFor, goalsAgainst] = match.result.split('-').map(Number);
            if (match.outcome === 'W') {
                statusClass = 'status-won';
                scoreText = `${goalsFor} - ${goalsAgainst}`;
            } else if (match.outcome === 'L') {
                statusClass = 'status-lost';
                scoreText = `${goalsFor} - ${goalsAgainst}`;
            } else {
                statusClass = 'status-draw';
                scoreText = `${goalsFor} - ${goalsAgainst}`;
            }
        } else {
            // If no result is available, show the outcome
            if (match.outcome === 'W') {
                statusClass = 'status-won';
                scoreText = 'W';
            } else if (match.outcome === 'L') {
                statusClass = 'status-lost';
                scoreText = 'L';
            } else {
                statusClass = 'status-draw';
                scoreText = 'D';
            }
        }
        
        // Create team order based on home/away
        let team1, team2;
        if (match.location === 'Home') {
            // Home match: Μεγάλο Λειβάδι vs Opponent
            team1 = `
                <div class="team">
                    <img src="logo_mg-1.png" alt="Μεγάλο Λειβάδι FC" class="team-badge">
                    <div class="team-name">Μεγάλο Λειβάδι FC</div>
                </div>
            `;
            team2 = `
                <div class="team">
                    <img src="club_placeholder.png" alt="${match.opponent}" class="team-badge">
                    <div class="team-name">${match.opponent}</div>
                </div>
            `;
        } else {
            // Away match: Opponent vs Μεγάλο Λειβάδι
            team1 = `
                <div class="team">
                    <img src="club_placeholder.png" alt="${match.opponent}" class="team-badge">
                    <div class="team-name">${match.opponent}</div>
                </div>
            `;
            team2 = `
                <div class="team">
                    <img src="logo_mg-1.png" alt="Μεγάλο Λειβάδι FC" class="team-badge">
                    <div class="team-name">Μεγάλο Λειβάδι FC</div>
                </div>
            `;
        }
        
        // Create accordion header
        const header = document.createElement('div');
        header.className = 'accordion-header';
        header.innerHTML = `
            <div class="match-card">
                <div class="match-date">
                    ${formattedDate}<br>
                    <small style="color: #be1b1e; font-weight: bold;">${match.location}</small>
                </div>
                ${team1}
                <div class="vs-container">
                    <div class="match-status ${statusClass}">${scoreText}</div>
                </div>
                ${team2}
            </div>
            <i class="fas fa-chevron-right"></i>
        `;
        
        // Create accordion content
        const content = document.createElement('div');
        content.className = 'accordion-content';

        // Add location info to match details
        const locationInfo = document.createElement('div');
        locationInfo.className = 'match-info';
        locationInfo.innerHTML = `<strong>Location:</strong> ${match.location} match`;
        content.appendChild(locationInfo);

        // Create lineup display
        const lineupHeader = document.createElement('div');
        lineupHeader.className = 'stats-header';
        lineupHeader.textContent = 'Starting Lineup';
        content.appendChild(lineupHeader);

        // Separate starting players and bench players
        const startingPlayers = match.players.filter(player => 
            player.position && player.position !== 'Bench'
        );

        const benchPlayers = match.players.filter(player => 
            player.position && player.position === 'Bench'
        );

        // Create football pitch container
        const pitchContainer = document.createElement('div');
        pitchContainer.className = 'pitch-container';

        // Add pitch markings
        const centerCircle = document.createElement('div');
        centerCircle.style.position = 'absolute';
        centerCircle.style.top = '50%';
        centerCircle.style.left = '50%';
        centerCircle.style.transform = 'translate(-50%, -50%)';
        centerCircle.style.width = '100px';
        centerCircle.style.height = '100px';
        centerCircle.style.border = '2px solid #fff';
        centerCircle.style.borderRadius = '50%';
        centerCircle.style.backgroundColor = 'transparent';
        centerCircle.style.zIndex = '1';
        pitchContainer.appendChild(centerCircle);

        const centerLine = document.createElement('div');
        centerLine.style.position = 'absolute';
        centerLine.style.top = '50%';
        centerLine.style.left = '50%';
        centerLine.style.transform = 'translateX(-50%)';
        centerLine.style.width = '100%';
        centerLine.style.height = '2px';
        centerLine.style.backgroundColor = '#fff';
        centerLine.style.zIndex = '1';
        pitchContainer.appendChild(centerLine);

        // Group players by position for better distribution
        const playersByPosition = {
            'Goalkeeper': [],
            'Defender': [],
            'Midfielder': [], 
            'Striker': []
        };

        // Group starting players
        startingPlayers.forEach(player => {
            const pos = player.position;
            if (pos === 'Goalkeeper') {
                playersByPosition.Goalkeeper.push(player);
            } else if (pos.includes('Defender') || pos === 'Defernder' || pos === 'Defenedr') {
                playersByPosition.Defender.push(player);
            } else if (pos === 'Midfielder') {
                playersByPosition.Midfielder.push(player);
            } else if (pos === 'Striker') {
                playersByPosition.Striker.push(player);
            }
        });

        // Define formation positions for proper distribution
        const formationPositions = {
            'Goalkeeper': [
                { top: '90%', left: '50%', posAbbr: 'GK' }
            ],
            'Defender': [
                { top: '60%', left: '25%', posAbbr: 'CB' },
                { top: '70%', left: '50%', posAbbr: 'CB' },
                { top: '60%', left: '75%', posAbbr: 'CB' }
            ],
            'Midfielder': [
                { top: '30%', left: '25%', posAbbr: 'LM' },
                { top: '40%', left: '50%', posAbbr: 'CM' },
                { top: '30%', left: '75%', posAbbr: 'RM' }
            ],
            'Striker': [
                { top: '8%', left: '50%', posAbbr: 'ST' }
            ]
        };

        // Function to create player stats symbols
        function createStatsSymbols(player, match) {
            const cleanName = player.name ? player.name.replace(' (C)', '').replace(' (Τ)', '').replace(' (Π)', '') : 'Unknown';
            const isPOM = match.player_of_match && cleanName && 
                (match.player_of_match.includes(cleanName) || cleanName.includes(match.player_of_match));
            
            const goals = player.goals || 0;
            const assists = player.assists || 0;
            const hasGoals = goals > 0;
            const hasAssists = assists > 0;

            let goalSymbols = '';
            let assistSymbols = '';

            if (hasGoals) {
                goalSymbols = '⚽'.repeat(goals);
            }

            if (hasAssists) {
                assistSymbols = '👟'.repeat(assists);
            }

            return {
                goalSymbols,
                assistSymbols,
                isPOM,
                goals,
                assists,
                cleanName
            };
        }

        // Place starting players on pitch
        Object.keys(playersByPosition).forEach(positionType => {
            const players = playersByPosition[positionType];
            const positions = formationPositions[positionType] || [];
            
            players.forEach((player, index) => {
                if (index < positions.length) {
                    const pos = positions[index];
                    const playerElement = document.createElement('div');
                    playerElement.className = 'player-on-pitch';
                    playerElement.style.top = pos.top;
                    playerElement.style.left = pos.left;

                    // Get player number safely (allow 0 as valid number)
                    const playerNumber = player.number != null ? player.number : '?';

                    // Use first name only for display
                    const displayName = player.name ? player.name.split(' ')[0] : 'Player';

                    // Create stats symbols
                    const stats = createStatsSymbols(player, match);

                    playerElement.innerHTML = `
                        <div style="font-size: 12px; font-weight: bold; margin-bottom: 2px;">${playerNumber}</div>
                        <div style="font-size: 10px; line-height: 1.1;">${displayName}</div>
                        <div style="font-size: 9px; margin-top: 2px; color: #ffeb3b;">${pos.posAbbr}</div>
                        <div class="stats-symbols">
                            ${stats.goalSymbols ? `<div style="color: #27ae60;" title="${stats.goals} goal${stats.goals > 1 ? 's' : ''}">${stats.goalSymbols}</div>` : ''}
                            ${stats.assistSymbols ? `<div style="color: #3498db;" title="${stats.assists} assist${stats.assists > 1 ? 's' : ''}">${stats.assistSymbols}</div>` : ''}
                            ${stats.isPOM ? '<div style="color: gold;" title="Player of the Match">⭐</div>' : ''}
                        </div>
                    `;

                    // Add hover tooltip with detailed stats
                    const tooltipStats = [];
                    if (stats.goals > 0) tooltipStats.push(`Goals: ${stats.goals}`);
                    if (stats.assists > 0) tooltipStats.push(`Assists: ${stats.assists}`);
                    if (stats.isPOM) tooltipStats.push('⭐ Player of the Match');

                    playerElement.title = `${stats.cleanName} (#${playerNumber}) - ${pos.posAbbr}${tooltipStats.length ? '\n' + tooltipStats.join('\n') : ''}`;

                    pitchContainer.appendChild(playerElement);
                }
            });
        });

        content.appendChild(pitchContainer);

        // Add formation info
        const formationInfo = document.createElement('div');
        formationInfo.style.textAlign = 'center';
        formationInfo.style.marginTop = '15px';
        formationInfo.style.fontSize = '0.9rem';
        formationInfo.style.color = '#333';
        formationInfo.innerHTML = `
            <div><strong>Formation: ${playersByPosition.Defender.length}-${playersByPosition.Midfielder.length}-${playersByPosition.Striker.length}</strong></div>
        `;
        content.appendChild(formationInfo);

        // Add bench players section
        if (benchPlayers.length > 0) {
            const benchContainer = document.createElement('div');
            benchContainer.className = 'bench-container';
            
            const benchTitle = document.createElement('div');
            benchTitle.className = 'bench-title';
            benchTitle.textContent = `Bench (${benchPlayers.length})`;
            benchContainer.appendChild(benchTitle);

            const benchPlayersContainer = document.createElement('div');
            benchPlayersContainer.className = 'bench-players';

            benchPlayers.forEach(player => {
                const benchPlayerElement = document.createElement('div');
                benchPlayerElement.className = 'bench-player';
                
                // Get player number safely (allow 0 as valid number)
                const playerNumber = player.number != null ? player.number : '?';
                
                // Clean name
                const cleanName = player.name ? player.name.replace(' (C)', '').replace(' (Τ)', '').replace(' (Π)', '') : 'Unknown';
                
                // Create stats symbols
                const stats = createStatsSymbols(player, match);

                benchPlayerElement.innerHTML = `
                    <div class="bench-player-number">#${playerNumber}</div>
                    <div class="bench-player-name">${cleanName}</div>
                    ${(stats.goalSymbols || stats.assistSymbols || stats.isPOM) ? `
                        <div class="bench-stats-symbols">
                            ${stats.goalSymbols ? `<div style="color: #27ae60;" title="${stats.goals} goal${stats.goals > 1 ? 's' : ''}">${stats.goalSymbols}</div>` : ''}
                            ${stats.assistSymbols ? `<div style="color: #3498db;" title="${stats.assists} assist${stats.assists > 1 ? 's' : ''}">${stats.assistSymbols}</div>` : ''}
                            ${stats.isPOM ? '<div style="color: gold;" title="Player of the Match">⭐</div>' : ''}
                        </div>
                    ` : ''}
                `;

                // Add hover tooltip
                const tooltipStats = [];
                if (stats.goals > 0) tooltipStats.push(`Goals: ${stats.goals}`);
                if (stats.assists > 0) tooltipStats.push(`Assists: ${stats.assists}`);
                if (stats.isPOM) tooltipStats.push('⭐ Player of the Match');

                benchPlayerElement.title = `${cleanName} (#${playerNumber}) - Bench${tooltipStats.length ? '\n' + tooltipStats.join('\n') : ''}`;

                benchPlayersContainer.appendChild(benchPlayerElement);
            });

            benchContainer.appendChild(benchPlayersContainer);
            content.appendChild(benchContainer);
        }
        
        // Assemble accordion
        accordion.appendChild(header);
        accordion.appendChild(content);
        container.appendChild(accordion);
    });
    
    // Reattach accordion toggle functionality
    attachAccordionToggle();
}

// Attach accordion toggle functionality
function attachAccordionToggle() {
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', () => {
            const accordion = header.parentElement;
            accordion.classList.toggle('open');
        });
    });
}

// Load match data when page loads
document.addEventListener('DOMContentLoaded', loadMatchData);