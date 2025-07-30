"""
Interactive Web Interface for 56 Card Game
"""

from flask import Flask, render_template, jsonify, request, session
from interactive_game import InteractiveGame56, PlayerType
from card import Suit
import uuid
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Store active games
active_games = {}

@app.route('/')
def index():
    return render_template('interactive_game.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    """Start a new interactive game"""
    data = request.json
    player_name = data.get('player_name', 'You')
    target_score = data.get('target_score', 500)
    
    # Create new game
    game_id = str(uuid.uuid4())
    game = InteractiveGame56(player_name, target_score)
    active_games[game_id] = game
    
    # Store game ID in session
    session['game_id'] = game_id
    
    # Start first round
    result = game.start_new_round()
    
    return jsonify({
        'success': True,
        'game_id': game_id,
        'game_state': {
            'phase': 'dealing',
            'players': [p.name for p in game.players],
            'teams': {team.name: [p.name for p in team.players] for team in game.teams},
            'target_score': target_score,
            'current_scores': {team.name: score for team, score in game.game_scores.items()}
        },
        'round_info': result
    })

@app.route('/start_bidding', methods=['POST'])
def start_bidding():
    """Start the bidding phase"""
    game_id = session.get('game_id')
    if not game_id or game_id not in active_games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = active_games[game_id]
    if not game.current_round:
        return jsonify({'success': False, 'error': 'No active round'})
    
    # Start bidding
    result = game.current_round.conduct_interactive_bidding()
    
    return jsonify({
        'success': True,
        'bidding_state': result
    })

@app.route('/make_bid', methods=['POST'])
def make_bid():
    """Process human player's bid"""
    game_id = session.get('game_id')
    if not game_id or game_id not in active_games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    data = request.json
    action = data.get('action')  # 'bid' or 'pass'
    amount = data.get('amount', 0)
    
    game = active_games[game_id]
    result = game.current_round.process_human_bid(action, amount)
    
    return jsonify({
        'success': True,
        'bidding_state': result
    })

@app.route('/continue_bidding', methods=['POST'])
def continue_bidding():
    """Continue AI bidding process"""
    game_id = session.get('game_id')
    if not game_id or game_id not in active_games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = active_games[game_id]
    result = game.current_round.continue_ai_bidding()
    
    return jsonify({
        'success': True,
        'bidding_state': result
    })

@app.route('/set_trump', methods=['POST'])
def set_trump():
    """Set trump suit after winning bid"""
    game_id = session.get('game_id')
    if not game_id or game_id not in active_games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    data = request.json
    trump_suit_name = data.get('trump_suit')
    
    # Convert string to Suit enum
    trump_suit = None
    for suit in Suit:
        if suit.value.lower() == trump_suit_name.lower():
            trump_suit = suit
            break
    
    if not trump_suit:
        return jsonify({'success': False, 'error': 'Invalid trump suit'})
    
    game = active_games[game_id]
    game.current_round.trump_suit = trump_suit
    
    # Start trick-taking phase
    result = game.current_round.start_interactive_tricks()
    
    return jsonify({
        'success': True,
        'trump_suit': trump_suit.value,
        'trick_state': result
    })

@app.route('/play_card', methods=['POST'])
def play_card():
    """Process human player's card play"""
    game_id = session.get('game_id')
    if not game_id or game_id not in active_games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    data = request.json
    card_info = {
        'rank': data.get('rank'),
        'suit': data.get('suit')
    }
    
    game = active_games[game_id]
    result = game.current_round.process_human_card(card_info)
    
    # If trick is complete and round is not complete, start next trick
    if result.get('type') == 'trick_complete' and not result.get('round_complete'):
        next_leader_name = result.get('next_leader')
        next_leader = None
        for player in game.players:
            if player.name == next_leader_name:
                next_leader = player
                break
        
        if next_leader:
            next_trick_result = game.current_round.play_next_trick(next_leader)
            result['next_trick'] = next_trick_result
    
    # If round is complete, update game scores
    if result.get('round_complete'):
        # Add round to game
        game.rounds.append(game.current_round)
        
        # Update game scores
        for team, score in result['round_scores'].items():
            for game_team in game.teams:
                if game_team.name == team:
                    game.game_scores[game_team] += score
                    break
        
        # Check if game is complete
        for team, total_score in game.game_scores.items():
            if total_score >= game.target_score:
                game.game_complete = True
                game.winning_team = team
                break
        
        result['game_scores'] = {team.name: score for team, score in game.game_scores.items()}
        result['game_complete'] = game.game_complete
        if game.winning_team:
            result['winning_team'] = game.winning_team.name
    
    return jsonify({
        'success': True,
        'play_result': result
    })

@app.route('/start_next_round', methods=['POST'])
def start_next_round():
    """Start the next round"""
    game_id = session.get('game_id')
    if not game_id or game_id not in active_games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = active_games[game_id]
    if game.game_complete:
        return jsonify({'success': False, 'error': 'Game is already complete'})
    
    result = game.start_new_round()
    
    return jsonify({
        'success': True,
        'round_info': result,
        'game_scores': {team.name: score for team, score in game.game_scores.items()}
    })

@app.route('/get_game_state')
def get_game_state():
    """Get current game state"""
    game_id = session.get('game_id')
    if not game_id or game_id not in active_games:
        return jsonify({'success': False, 'error': 'Game not found'})
    
    game = active_games[game_id]
    
    state = {
        'success': True,
        'game_complete': game.game_complete,
        'current_scores': {team.name: score for team, score in game.game_scores.items()},
        'target_score': game.target_score,
        'round_number': len(game.rounds) + (1 if game.current_round else 0)
    }
    
    if game.winning_team:
        state['winning_team'] = game.winning_team.name
    
    return jsonify(state)

if __name__ == '__main__':
    print("*** Starting Interactive 56 Card Game Web Interface...")
    app.run(debug=True, host='0.0.0.0', port=5001)
