"""
simple_web.py - Simple Flask-based web interface for the 56 Card Game
"""

from flask import Flask, render_template, request, jsonify
import json
import os
from game import Game56

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Global game state (in production, use proper session management)
current_game = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_game', methods=['POST'])
def new_game():
    global current_game
    data = request.get_json()
    
    player_names = [
        data.get('north', 'North'),
        data.get('east', 'East'), 
        data.get('south', 'South'),
        data.get('west', 'West')
    ]
    target_score = int(data.get('target_score', 500))
    
    current_game = Game56(player_names, target_score)
    return jsonify({'success': True})

@app.route('/play_round', methods=['POST'])
def play_round():
    global current_game
    if current_game and not current_game.game_complete:
        round_obj = current_game.play_round()
        
        # Get detailed round information
        round_info = {
            'round_number': round_obj.round_number,
            'dealer': round_obj.dealer.name,
            'bidding_history': [],
            'winning_bid': None,
            'trump_suit': None,
            'tricks': [],
            'team_points': {},
            'round_scores': {}
        }
        
        # Bidding information
        if round_obj.bidding_round:
            for bid in round_obj.bidding_round.bids:
                round_info['bidding_history'].append({
                    'player': bid.player.name,
                    'action': bid.action.value,
                    'amount': bid.amount if bid.action.value == 'bid' else 0
                })
            
            if round_obj.bidding_round.winning_bid:
                round_info['winning_bid'] = {
                    'player': round_obj.bidding_round.winning_bid.player.name,
                    'amount': round_obj.bidding_round.winning_bid.amount,
                    'team': round_obj.bidding_round.winning_team.name
                }
        
        # Trump suit
        if round_obj.trump_suit:
            round_info['trump_suit'] = round_obj.trump_suit.value
        
        # Tricks information
        if round_obj.trick_manager:
            for trick in round_obj.trick_manager.tricks:
                trick_info = {
                    'number': trick.trick_number,
                    'leader': trick.leading_player.name,
                    'cards': [],
                    'winner': trick.winner.name if trick.winner else None,
                    'points': trick.get_points()
                }
                
                for trick_card in trick.cards_played:
                    trick_info['cards'].append({
                        'player': trick_card.player.name,
                        'card': f"{trick_card.card.rank.display_name} of {trick_card.card.suit.value}",
                        'points': trick_card.card.points,
                        'is_trump': trick_card.card.suit == round_obj.trump_suit
                    })
                
                round_info['tricks'].append(trick_info)
            
            # Team points from tricks
            team_points = round_obj.trick_manager.get_team_points()
            for team, points in team_points.items():
                round_info['team_points'][team.name] = points
        
        # Round scores
        if round_obj.round_complete:
            scores = round_obj.calculate_scores()
            for team, score in scores.items():
                round_info['round_scores'][team.name] = score
        
        return jsonify({
            'success': True,
            'game_complete': current_game.game_complete,
            'game_scores': {team.name: score for team, score in current_game.game_scores.items()},
            'winner': current_game.winning_team.name if current_game.winning_team else None,
            'round_info': round_info
        })
    return jsonify({'success': False})

@app.route('/game_status')
def game_status():
    if current_game:
        return jsonify({
            'exists': True,
            'complete': current_game.game_complete,
            'scores': {team.name: score for team, score in current_game.game_scores.items()},
            'target_score': current_game.target_score,
            'rounds_played': len(current_game.rounds),
            'winner': current_game.winning_team.name if current_game.winning_team else None
        })
    return jsonify({'exists': False})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create a comprehensive HTML template
    html_template = '''<!DOCTYPE html>
<html>
<head>
    <title>56 Card Game</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #333; margin-bottom: 30px; }
        .form-group { margin: 15px 0; }
        .form-row { display: flex; gap: 15px; }
        .form-row .form-group { flex: 1; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input { width: 100%; padding: 8px; border: 2px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { background: #007bff; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; margin: 10px 5px; }
        button:hover { background: #0056b3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .scores { display: flex; justify-content: space-around; margin: 20px 0; }
        .score-box { background: #e9ecef; padding: 15px; border-radius: 8px; text-align: center; min-width: 150px; border: 2px solid #ddd; }
        .score-box.winning { background: #d4edda; border-color: #28a745; }
        .winner { background: #d4edda; border: 2px solid #28a745; color: #155724; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }
        .game-info { background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .round-details { background: #fff; border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .trick { background: #f8f9fa; padding: 10px; margin: 5px 0; border-radius: 5px; }
        .card { display: inline-block; background: #fff; border: 1px solid #ccc; padding: 5px 8px; margin: 2px; border-radius: 3px; font-size: 12px; }
        .card.trump { background: #fff3cd; border-color: #ffc107; font-weight: bold; }
        .card.winner { background: #d1ecf1; border-color: #bee5eb; }
        .hidden { display: none; }
        .loading { text-align: center; color: #666; font-style: italic; }
        .bidding { background: #e3f2fd; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .trump-suit { background: #fff3e0; padding: 10px; border-radius: 5px; margin: 10px 0; text-align: center; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">♠♥♦♣ 56 Card Game ♣♦♥♠</h1>
        
        <div id="setup" class="setup-form">
            <h2>New Game Setup</h2>
            <div class="form-row">
                <div class="form-group">
                    <label>North Player:</label>
                    <input type="text" id="north" value="North">
                </div>
                <div class="form-group">
                    <label>East Player:</label>
                    <input type="text" id="east" value="East">
                </div>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>South Player:</label>
                    <input type="text" id="south" value="South">
                </div>
                <div class="form-group">
                    <label>West Player:</label>
                    <input type="text" id="west" value="West">
                </div>
            </div>
            <div class="form-group">
                <label>Target Score:</label>
                <input type="number" id="target_score" value="500" min="50" max="1000">
            </div>
            <button onclick="startNewGame()">Start Game</button>
        </div>
        
        <div id="game" class="hidden">
            <div class="game-info">
                <h2>Game in Progress</h2>
                <p><strong>Target Score:</strong> <span id="target"></span></p>
                <p><strong>Rounds Played:</strong> <span id="rounds"></span></p>
            </div>
            
            <div class="scores">
                <div class="score-box" id="team1-score">
                    <h3>North-South</h3>
                    <div class="score">0</div>
                </div>
                <div class="score-box" id="team2-score">
                    <h3>East-West</h3>
                    <div class="score">0</div>
                </div>
            </div>
            
            <div class="controls">
                <button onclick="playRound()" id="play-btn">Play Next Round</button>
                <button onclick="autoPlay()" id="auto-btn">Auto-Play Full Game</button>
                <button onclick="newGame()">New Game</button>
            </div>
            
            <div id="round-details"></div>
            
            <div id="winner" class="hidden winner">
                <h2>*** Game Complete! ***</h2>
                <p><strong>Winner:</strong> <span id="winner-name"></span></p>
            </div>
        </div>
    </div>

    <script>
        function startNewGame() {
            const data = {
                north: document.getElementById('north').value,
                east: document.getElementById('east').value,
                south: document.getElementById('south').value,
                west: document.getElementById('west').value,
                target_score: document.getElementById('target_score').value
            };
            
            fetch('/new_game', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    document.getElementById('setup').classList.add('hidden');
                    document.getElementById('game').classList.remove('hidden');
                    document.getElementById('target').textContent = document.getElementById('target_score').value;
                    updateGameStatus();
                }
            });
        }
        
        function playRound() {
            document.getElementById('play-btn').disabled = true;
            document.getElementById('auto-btn').disabled = true;
            
            const roundDetails = document.getElementById('round-details');
            roundDetails.innerHTML = '<div class="loading">Playing round...</div>';
            
            fetch('/play_round', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                document.getElementById('play-btn').disabled = false;
                document.getElementById('auto-btn').disabled = false;
                
                if (data.success) {
                    updateGameStatus();
                    displayRoundDetails(data.round_info);
                    
                    if (data.game_complete) {
                        showWinner(data.winner);
                    }
                }
            });
        }
        
        function displayRoundDetails(roundInfo) {
            const container = document.getElementById('round-details');
            
            let html = `<div class="round-details">
                <h3>Round ${roundInfo.round_number} (Dealer: ${roundInfo.dealer})</h3>`;
            
            // Bidding
            if (roundInfo.bidding_history.length > 0) {
                html += '<div class="bidding"><h4>Bidding:</h4>';
                roundInfo.bidding_history.forEach(bid => {
                    if (bid.action === 'bid') {
                        html += `<div>${bid.player} bids ${bid.amount}</div>`;
                    } else {
                        html += `<div>${bid.player} passes</div>`;
                    }
                });
                
                if (roundInfo.winning_bid) {
                    html += `<div><strong>Winning bid: ${roundInfo.winning_bid.amount} by ${roundInfo.winning_bid.team}</strong></div>`;
                }
                html += '</div>';
            }
            
            // Trump suit
            if (roundInfo.trump_suit) {
                html += `<div class="trump-suit">Trump Suit: ${roundInfo.trump_suit}</div>`;
            }
            
            // Tricks
            if (roundInfo.tricks.length > 0) {
                html += '<h4>Tricks:</h4>';
                roundInfo.tricks.forEach(trick => {
                    html += `<div class="trick">
                        <strong>Trick ${trick.number}</strong> (led by ${trick.leader}):
                        <div style="margin-top: 5px;">`;
                    
                    trick.cards.forEach(card => {
                        let cardClass = 'card';
                        if (card.is_trump) cardClass += ' trump';
                        if (card.player === trick.winner) cardClass += ' winner';
                        
                        html += `<span class="${cardClass}">${card.player}: ${card.card}</span>`;
                    });
                    
                    html += `</div>
                        <div style="margin-top: 5px;"><strong>Winner: ${trick.winner}</strong> (${trick.points} points)</div>
                    </div>`;
                });
            }
            
            // Round scores
            if (Object.keys(roundInfo.team_points).length > 0) {
                html += '<h4>Round Results:</h4>';
                html += '<div>Points from tricks:</div>';
                Object.entries(roundInfo.team_points).forEach(([team, points]) => {
                    html += `<div>${team}: ${points} points</div>`;
                });
                
                if (Object.keys(roundInfo.round_scores).length > 0) {
                    html += '<div style="margin-top: 10px;">Round scores:</div>';
                    Object.entries(roundInfo.round_scores).forEach(([team, score]) => {
                        html += `<div><strong>${team}: ${score} points</strong></div>`;
                    });
                }
            }
            
            html += '</div>';
            container.innerHTML = html;
        }
        
        function autoPlay() {
            document.getElementById('auto-btn').disabled = true;
            document.getElementById('play-btn').disabled = true;
            
            const playNext = () => {
                fetch('/play_round', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateGameStatus();
                        displayRoundDetails(data.round_info);
                        
                        if (data.game_complete) {
                            showWinner(data.winner);
                            document.getElementById('auto-btn').disabled = false;
                        } else {
                            setTimeout(playNext, 2000);
                        }
                    }
                });
            };
            playNext();
        }
        
        function updateGameStatus() {
            fetch('/game_status')
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    document.getElementById('rounds').textContent = data.rounds_played;
                    
                    const scores = data.scores;
                    const team1Box = document.getElementById('team1-score');
                    const team2Box = document.getElementById('team2-score');
                    
                    team1Box.querySelector('.score').textContent = scores['North-South'] || 0;
                    team2Box.querySelector('.score').textContent = scores['East-West'] || 0;
                    
                    // Highlight leading team
                    const team1Score = scores['North-South'] || 0;
                    const team2Score = scores['East-West'] || 0;
                    
                    team1Box.classList.toggle('winning', team1Score > team2Score);
                    team2Box.classList.toggle('winning', team2Score > team1Score);
                }
            });
        }
        
        function showWinner(winnerName) {
            document.getElementById('winner').classList.remove('hidden');
            document.getElementById('winner-name').textContent = winnerName;
            document.getElementById('play-btn').disabled = true;
            document.getElementById('auto-btn').disabled = true;
        }
        
        function newGame() {
            location.reload();
        }
        
        window.onload = function() {
            fetch('/game_status')
            .then(response => response.json())
            .then(data => {
                if (data.exists) {
                    document.getElementById('setup').classList.add('hidden');
                    document.getElementById('game').classList.remove('hidden');
                    updateGameStatus();
                    if (data.complete) {
                        showWinner(data.winner);
                    }
                }
            });
        };
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    print("*** Starting 56 Card Game Web Interface...")
    print("*** Open your browser and go to: http://localhost:5000")
    print("*** Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
