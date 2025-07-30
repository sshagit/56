"""
web_ui.py - Streamlit web interface for the 56 Card Game
"""

import streamlit as st
import time
from typing import Optional, List
from game import Game56, GamePhase
from player import Player, Team
from card import Card, Suit
from bidding import BidAction

# Configure the page
st.set_page_config(
    page_title="56 Card Game",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.card {
    background: linear-gradient(145deg, #ffffff, #f0f0f0);
    border: 2px solid #ddd;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    text-align: center;
    display: inline-block;
    min-width: 80px;
}

.trump-card {
    background: linear-gradient(145deg, #ffd700, #ffed4e);
    border: 2px solid #ffc107;
    font-weight: bold;
}

.winning-card {
    background: linear-gradient(145deg, #90EE90, #98FB98);
    border: 2px solid #32CD32;
    font-weight: bold;
}

.team-score {
    font-size: 1.5em;
    font-weight: bold;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    margin: 10px 0;
}

.north-south {
    background: linear-gradient(145deg, #e3f2fd, #bbdefb);
    border: 2px solid #2196f3;
    color: #1976d2;
}

.east-west {
    background: linear-gradient(145deg, #fff3e0, #ffcc80);
    border: 2px solid #ff9800;
    color: #f57c00;
}

.bidding-team {
    background: linear-gradient(145deg, #f3e5f5, #ce93d8);
    border: 2px solid #9c27b0;
    color: #7b1fa2;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'game' not in st.session_state:
        st.session_state.game = None
    if 'current_round' not in st.session_state:
        st.session_state.current_round = None
    if 'game_phase' not in st.session_state:
        st.session_state.game_phase = GamePhase.SETUP
    if 'auto_play' not in st.session_state:
        st.session_state.auto_play = False
    if 'trick_delay' not in st.session_state:
        st.session_state.trick_delay = 2.0

def display_card(card: Card, is_trump: bool = False, is_winner: bool = False) -> str:
    """Display a card with appropriate styling"""
    suit_symbols = {
        "Hearts": "♥️",
        "Diamonds": "♦️",
        "Clubs": "♣️",
        "Spades": "♠️"
    }
    
    suit_symbol = suit_symbols.get(card.suit.value, card.suit.value)
    card_class = "card"
    
    if is_trump:
        card_class += " trump-card"
    if is_winner:
        card_class += " winning-card"
    
    return f'<div class="{card_class}">{card.rank.display_name}{suit_symbol}<br><small>{card.points} pts</small></div>'

def display_team_scores(game: Game56):
    """Display team scores with styling"""
    for team in game.teams:
        score_class = "team-score north-south" if "North" in team.name else "team-score east-west"
        if team.is_bidding_team:
            score_class += " bidding-team"
        
        st.markdown(f"""
        <div class="{score_class}">
            <strong>{team.name}</strong><br>
            Game Score: {game.game_scores[team]} points<br>
            {"🎯 Bidding Team" if team.is_bidding_team else "🛡️ Defending Team"}
            {f"<br>Bid: {team.bid}" if team.is_bidding_team else ""}
        </div>
        """, unsafe_allow_html=True)

def setup_new_game():
    """Setup a new game"""
    st.header("🎮 New Game Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Player Names")
        north = st.text_input("North Player", value="North")
        east = st.text_input("East Player", value="East")
        south = st.text_input("South Player", value="South")
        west = st.text_input("West Player", value="West")
        
        player_names = [north, east, south, west]
    
    with col2:
        st.subheader("Game Settings")
        target_score = st.number_input("Target Score", min_value=50, max_value=1000, value=500, step=50)
        st.session_state.auto_play = st.checkbox("Auto-play tricks", value=True)
        if st.session_state.auto_play:
            st.session_state.trick_delay = st.slider("Delay between tricks (seconds)", 0.5, 5.0, 2.0, 0.5)
    
    if st.button("Start Game", type="primary"):
        st.session_state.game = Game56(player_names, target_score)
        st.session_state.game_phase = GamePhase.DEALING
        st.rerun()

def display_player_hands(round_obj):
    """Display player hands"""
    st.subheader("👥 Player Hands")
    
    cols = st.columns(4)
    for i, player in enumerate(round_obj.players):
        with cols[i]:
            st.write(f"**{player.name}**")
            st.write(f"Hand Points: {player.get_hand_points()}")
            
            # Show first few cards as preview
            hand_preview = ""
            for card in player.hand[:3]:  # Show first 3 cards
                hand_preview += display_card(card)
            hand_preview += f"<br><small>...and {len(player.hand)-3} more cards</small>" if len(player.hand) > 3 else ""
            st.markdown(hand_preview, unsafe_allow_html=True)

def display_bidding_phase(round_obj):
    """Display bidding phase"""
    st.subheader("🔨 Bidding Phase")
    
    if round_obj.bidding_round:
        # Show bidding history
        st.write("**Bidding History:**")
        for bid in round_obj.bidding_round.bids:
            if bid.action == BidAction.BID:
                st.write(f"• {bid.player.name} bids **{bid.amount}**")
            else:
                st.write(f"• {bid.player.name} passes")
        
        if round_obj.bidding_round.is_complete and round_obj.bidding_round.winning_bid:
            st.success(f"🎯 Winning bid: **{round_obj.bidding_round.winning_bid.amount}** by **{round_obj.bidding_round.winning_team.name}**")

def display_trump_selection(round_obj):
    """Display trump selection"""
    if round_obj.trump_suit:
        suit_symbols = {
            "Hearts": "♥️",
            "Diamonds": "♦️", 
            "Clubs": "♣️",
            "Spades": "♠️"
        }
        trump_symbol = suit_symbols.get(round_obj.trump_suit.value, "")
        st.subheader(f"🎺 Trump Suit: {trump_symbol} {round_obj.trump_suit.value}")

def display_tricks(round_obj):
    """Display tricks being played"""
    st.subheader("🃏 Trick Play")
    
    if round_obj.trick_manager and round_obj.trick_manager.tricks:
        # Show completed tricks
        for trick in round_obj.trick_manager.tricks[-3:]:  # Show last 3 tricks
            st.write(f"**Trick {trick.trick_number}** (Led by {trick.leading_player.name})")
            
            trick_cards = ""
            for trick_card in trick.cards_played:
                is_trump = trick_card.card.suit == round_obj.trump_suit
                is_winner = trick_card.player == trick.winner
                trick_cards += f"{trick_card.player.name}: {display_card(trick_card.card, is_trump, is_winner)} "
            
            st.markdown(trick_cards, unsafe_allow_html=True)
            st.write(f"Winner: **{trick.winner.name}** ({trick.get_points()} points)")
            st.write("---")
    
    # Show current trick points
    if round_obj.trick_manager:
        team_points = round_obj.trick_manager.get_team_points()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("North-South Points", team_points.get(round_obj.teams[0], 0))
        with col2:
            st.metric("East-West Points", team_points.get(round_obj.teams[1], 0))

def play_game():
    """Main game play interface"""
    game = st.session_state.game
    
    # Display game header
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.title("🃏 56 Card Game")
    with col2:
        if st.button("New Game", type="secondary"):
            st.session_state.game = None
            st.rerun()
    with col3:
        st.write(f"**Target Score:** {game.target_score}")
    
    # Display team scores
    col1, col2 = st.columns(2)
    with col1:
        display_team_scores(game)
    
    # Game controls
    st.sidebar.header("🎮 Game Controls")
    
    if not game.game_complete:
        if st.sidebar.button("Play Next Round", type="primary"):
            with st.spinner("Playing round..."):
                current_round = game.play_round()
                st.session_state.current_round = current_round
            st.rerun()
        
        if st.sidebar.button("Auto-Play Full Game"):
            with st.spinner("Playing full game..."):
                while not game.game_complete:
                    game.play_round()
                    time.sleep(0.5)  # Brief delay for visual effect
            st.rerun()
    
    # Display current round information
    if hasattr(st.session_state, 'current_round') and st.session_state.current_round:
        round_obj = st.session_state.current_round
        
        st.header(f"Round {round_obj.round_number}")
        st.write(f"**Dealer:** {round_obj.dealer.name}")
        
        # Show different phases
        if round_obj.bidding_round:
            display_bidding_phase(round_obj)
        
        if round_obj.trump_suit:
            display_trump_selection(round_obj)
        
        if round_obj.round_complete:
            display_tricks(round_obj)
            
            # Show round results
            st.subheader("📊 Round Results")
            if round_obj.trick_manager:
                team_points = round_obj.trick_manager.get_team_points()
                scores = round_obj.calculate_scores()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Points from Tricks:**")
                    for team, points in team_points.items():
                        st.write(f"• {team.name}: {points} points")
                
                with col2:
                    st.write("**Round Scores:**")
                    for team, score in scores.items():
                        st.write(f"• {team.name}: {score} points")
                
                if round_obj.winning_team:
                    st.success(f"🏆 Round Winner: **{round_obj.winning_team.name}**")
        else:
            display_player_hands(round_obj)
    
    # Display game completion
    if game.game_complete:
        st.balloons()
        st.header("🏆 Game Complete!")
        st.success(f"**Winner: {game.winning_team.name}**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Final Scores:**")
            for team, score in game.game_scores.items():
                st.write(f"• {team.name}: {score} points")
        with col2:
            st.write(f"**Rounds Played:** {len(game.rounds)}")

def show_rules():
    """Display game rules"""
    st.header("📖 Game Rules")
    
    st.markdown("""
    ### 🎯 Objective
    Be the first team to reach the target score (usually 500 points).
    
    ### 👥 Players & Teams
    - **4 players** in **2 teams** of 2
    - **North-South** vs **East-West** (partners sit opposite)
    
    ### 🃏 Deck & Cards
    - **48 cards** total (2 standard 24-card decks)
    - Cards: **9, 10, J, Q, K, A** from each suit
    
    ### 💰 Card Values
    - **Jack (J)**: 3 points
    - **Nine (9)**: 2 points
    - **Ace (A)**: 1 point
    - **Ten (10)**: 1 point
    - **King (K), Queen (Q)**: 0 points
    
    **Total**: 56 points per round (hence the name!)
    
    ### 🔨 Bidding
    - Starts at **28**, can go up to **56**
    - Players bid in rotation or pass
    - **Highest bidder** chooses trump suit
    - Bidding team must win **at least their bid** in tricks
    
    ### 🎮 Gameplay
    1. Deal 12 cards to each player
    2. Conduct bidding round
    3. Winning bidder declares trump
    4. Play 12 tricks (4 cards each)
    5. Must follow suit if possible
    6. Trump cards beat non-trump cards
    7. Highest card of led suit wins (if no trump played)
    
    ### 📊 Scoring
    - **Bidding team makes bid**: Gets bid points
    - **Bidding team fails**: Opponents get 56 points
    - Game continues until target score reached
    
    ### 🧠 Strategy Tips
    - Strong hands with **Jacks and 9s** enable higher bids
    - **Count points** as tricks are played
    - **Communicate** with partner through legal gameplay
    - Consider **trump suit** when bidding
    """)

def main():
    """Main application"""
    initialize_session_state()
    
    # Sidebar navigation
    st.sidebar.title("🃏 56 Card Game")
    page = st.sidebar.selectbox("Choose Page", ["Game", "Rules", "About"])
    
    if page == "Game":
        if st.session_state.game is None:
            setup_new_game()
        else:
            play_game()
    
    elif page == "Rules":
        show_rules()
    
    elif page == "About":
        st.header("ℹ️ About")
        st.markdown("""
        ### 56 Card Game - Digital Implementation
        
        This is a complete digital implementation of the traditional card game "56" (Fifty-Six).
        
        **Features:**
        - Full game logic with proper bidding and trick-taking
        - Visual web interface
        - Team-based gameplay
        - Auto-play options for quick games
        - Detailed scoring and statistics
        
        **Built with:**
        - Python 3.8+
        - Streamlit for web interface
        - Modular game engine
        
        **Source Code:**
        The game consists of several modules:
        - `card.py` - Card and deck logic
        - `player.py` - Player and team management
        - `bidding.py` - Bidding system
        - `trick.py` - Trick-taking logic
        - `game.py` - Main game engine
        - `web_ui.py` - This web interface
        
        Enjoy playing 56! 🎮
        """)

if __name__ == "__main__":
    main()
