"""
interactive_game.py - Interactive 56 Card Game with Human vs AI players
"""

from typing import List, Optional, Dict, Tuple
from enum import Enum
import random
from game import Game56, GameRound, GamePhase
from player import Player, Team, Position, GameSetup
from card import Card, Suit, Rank
from bidding import BiddingRound, BidAction, Bid
from trick import TrickManager, Trick


class PlayerType(Enum):
    HUMAN = "human"
    AI = "ai"


class InteractivePlayer(Player):
    """Extended Player class for interactive gameplay"""
    
    def __init__(self, name: str, position: Position, player_type: PlayerType = PlayerType.AI):
        super().__init__(name, position)
        self.player_type = player_type
        self.ai_personality = self._generate_ai_personality()
    
    def _generate_ai_personality(self) -> Dict:
        """Generate AI personality traits for more realistic bidding"""
        return {
            'aggressiveness': random.uniform(0.3, 0.9),  # How likely to bid high
            'conservatism': random.uniform(0.2, 0.8),    # How conservative in card play
            'bluffing': random.uniform(0.1, 0.6)         # Tendency to bluff in bidding
        }
    
    def should_bid(self, hand_points: int, min_bid: int, current_team_bid: bool) -> Tuple[bool, int]:
        """AI logic for bidding decisions"""
        if self.player_type == PlayerType.HUMAN:
            return False, 0  # Human decisions handled separately
        
        if current_team_bid:  # Don't outbid your own team
            return False, 0
        
        # More aggressive bidding logic
        personality_factor = self.ai_personality['aggressiveness']
        bluff_factor = random.random() < self.ai_personality['bluffing']
        
        # Base threshold for bidding (more generous)
        base_threshold = 12 + (min_bid - 28) * 0.3
        
        # Adjust threshold based on personality and bluffing
        threshold = base_threshold - (personality_factor * 4)
        if bluff_factor:
            threshold -= 2  # More likely to bid with weaker hand
        
        # More lenient bidding conditions
        should_make_bid = (hand_points >= threshold and min_bid <= 50) or \
                         (hand_points >= 16 and min_bid <= 40) or \
                         (hand_points >= 20 and min_bid <= 45) or \
                         (bluff_factor and hand_points >= 10 and min_bid <= 35)
        
        if should_make_bid:
            # Calculate bid amount based on hand strength
            if hand_points >= 22:
                bid_amount = min(min_bid + random.randint(2, 5), 56)
            elif hand_points >= 18:
                bid_amount = min(min_bid + random.randint(1, 4), 56)
            elif hand_points >= 14:
                bid_amount = min(min_bid + random.randint(1, 3), 56)
            else:
                bid_amount = min(min_bid + random.randint(0, 2), 56)
            
            return True, bid_amount
        
        return False, 0
    
    def choose_card_to_play(self, valid_cards: List[Card], led_suit: Optional[Suit], 
                           trump_suit: Suit, trick_cards: List[Card]) -> Card:
        """AI logic for card selection"""
        if self.player_type == PlayerType.HUMAN:
            return valid_cards[0]  # This shouldn't be called for human
        
        # Simple AI strategy
        if not trick_cards:  # Leading the trick
            return self._choose_lead_card(valid_cards, trump_suit)
        else:
            return self._choose_follow_card(valid_cards, led_suit, trump_suit, trick_cards)
    
    def _choose_lead_card(self, valid_cards: List[Card], trump_suit: Suit) -> Card:
        """Choose card when leading a trick"""
        # Try to lead with high non-trump cards first
        non_trump = [c for c in valid_cards if c.suit != trump_suit]
        trump_cards = [c for c in valid_cards if c.suit == trump_suit]
        
        if non_trump:
            # Lead with highest non-trump card
            return max(non_trump, key=lambda c: (c.rank.rank_value, c.points))
        else:
            # Lead with lowest trump if only trump cards
            return min(trump_cards, key=lambda c: (c.rank.rank_value, c.points))
    
    def _choose_follow_card(self, valid_cards: List[Card], led_suit: Optional[Suit], 
                           trump_suit: Suit, trick_cards: List[Card]) -> Card:
        """Choose card when following in a trick"""
        # Simple strategy: try to win if possible, otherwise play lowest card
        same_suit = [c for c in valid_cards if c.suit == led_suit]
        trump_cards = [c for c in valid_cards if c.suit == trump_suit]
        
        if same_suit:
            # Try to win with same suit
            highest_played = max([c.rank.rank_value for c in trick_cards if c.suit == led_suit], default=0)
            winning_cards = [c for c in same_suit if c.rank.rank_value > highest_played]
            
            if winning_cards:
                return min(winning_cards, key=lambda c: c.rank.rank_value)  # Lowest winning card
            else:
                return min(same_suit, key=lambda c: c.points)  # Lowest points
        
        elif trump_cards and led_suit != trump_suit:
            # Can trump
            trump_played = any(c.suit == trump_suit for c in trick_cards)
            if not trump_played:
                return min(trump_cards, key=lambda c: c.points)  # Lowest trump
        
        # Play lowest point card
        return min(valid_cards, key=lambda c: c.points)


class InteractiveGameRound(GameRound):
    """Interactive version of GameRound"""
    
    def __init__(self, round_number: int, players: List[InteractivePlayer], teams: List[Team], 
                 dealer: InteractivePlayer, human_player: InteractivePlayer):
        super().__init__(round_number, players, teams, dealer)
        self.human_player = human_player
        self.current_trick_cards = []
        self.human_card_selection = None
        self.bidding_in_progress = False
        self.trick_in_progress = False
        self.human_bid_selection = None
    
    def conduct_interactive_bidding(self) -> Dict:
        """Start interactive bidding process"""
        dealer_index = self.players.index(self.dealer)
        starting_player = self.players[(dealer_index + 1) % len(self.players)]
        
        # Initialize bidding state
        self._bidding_round = BiddingRound(self.players, self.teams, starting_player)
        self._current_bidder = starting_player
        self._bidding_history = []
        
        # Return first bidder state
        return self._get_current_bidding_state()
    
    def _get_current_bidding_state(self) -> Dict:
        """Get current bidding state"""
        if self._bidding_round.is_complete:
            # Bidding complete
            self._bidding_round.finalize_bidding()
            self.bidding_round = self._bidding_round
            
            return {
                'type': 'bidding_complete',
                'winning_bid': {
                    'player': self._bidding_round.winning_bid.player.name,
                    'amount': self._bidding_round.winning_bid.amount,
                    'team': self._bidding_round.winning_team.name
                } if self._bidding_round.winning_bid else None,
                'current_bid': {
                    'player': self._bidding_round.winning_bid.player.name,
                    'amount': self._bidding_round.winning_bid.amount
                } if self._bidding_round.winning_bid else None
            }
        
        min_bid = self._bidding_round.get_minimum_bid()
        
        if self._current_bidder.player_type == PlayerType.HUMAN:
            return {
                'type': 'human_bid_needed',
                'player': self._current_bidder.name,
                'hand_points': self._current_bidder.get_hand_points(),
                'min_bid': min_bid,
                'max_bid': 56,
                'can_bid': min_bid <= 56,
                'current_bid': {
                    'player': self._bidding_round.winning_bid.player.name,
                    'amount': self._bidding_round.winning_bid.amount
                } if self._bidding_round.winning_bid else None
            }
        else:
            return {
                'type': 'ai_bidding',
                'current_player': self._current_bidder.name,
                'message': f"{self._current_bidder.name} is considering their bid...",
                'current_bid': {
                    'player': self._bidding_round.winning_bid.player.name,
                    'amount': self._bidding_round.winning_bid.amount
                } if self._bidding_round.winning_bid else None
            }
    
    def continue_ai_bidding(self) -> Dict:
        """Continue AI bidding process"""
        if self._bidding_round.is_complete or self._current_bidder.player_type == PlayerType.HUMAN:
            return self._get_current_bidding_state()
        
        min_bid = self._bidding_round.get_minimum_bid()
        
        # Check if the player's team already has the current highest bid
        player_team = None
        for team in self.teams:
            if self._current_bidder in team.players:
                player_team = team
                break
        
        # Check if this team already has the winning bid
        current_team_bidding = False
        if self._bidding_round.winning_bid and player_team:
            current_team_bidding = self._bidding_round.winning_bid.player in player_team.players
        
        should_bid, bid_amount = self._current_bidder.should_bid(
            self._current_bidder.get_hand_points(), 
            min_bid, 
            current_team_bidding
        )
        
        if should_bid and self._bidding_round.can_player_bid(self._current_bidder, bid_amount):
            self._bidding_round.make_bid(self._current_bidder, BidAction.BID, bid_amount)
            self._bidding_history.append({
                'player': self._current_bidder.name,
                'action': 'bid',
                'amount': bid_amount
            })
        else:
            self._bidding_round.make_bid(self._current_bidder, BidAction.PASS)
            self._bidding_history.append({
                'player': self._current_bidder.name,
                'action': 'pass'
            })
        
        # Move to next player
        if not self._bidding_round.is_complete:
            self._current_bidder = self._bidding_round.get_next_player(self._current_bidder)
        
        return self._get_current_bidding_state()
    
    def process_human_bid(self, action: str, amount: int = 0) -> Dict:
        """Process human bid and move to next player"""
        if self._current_bidder.player_type != PlayerType.HUMAN:
            return {'error': 'Not human player turn'}
        
        # Process human bid
        if action == 'bid':
            self._bidding_round.make_bid(self.human_player, BidAction.BID, amount)
            self._bidding_history.append({
                'player': self.human_player.name,
                'action': 'bid',
                'amount': amount
            })
        else:
            self._bidding_round.make_bid(self.human_player, BidAction.PASS)
            self._bidding_history.append({
                'player': self.human_player.name,
                'action': 'pass'
            })
        
        # Move to next player
        if not self._bidding_round.is_complete:
            self._current_bidder = self._bidding_round.get_next_player(self._current_bidder)
        
        return self._get_current_bidding_state()
    
    def start_interactive_tricks(self) -> Dict:
        """Start the trick-taking phase"""
        if not self.trump_suit:
            raise ValueError("Trump suit must be set")
        
        self.trick_manager = TrickManager(self.players, self.teams, self.trump_suit)
        
        # First trick led by player to dealer's left
        dealer_index = self.players.index(self.dealer)
        leading_player = self.players[(dealer_index + 1) % len(self.players)]
        
        return self.play_next_trick(leading_player)
    
    def play_next_trick(self, leading_player: InteractivePlayer) -> Dict:
        """Play the next trick"""
        trick = self.trick_manager.start_new_trick(leading_player)
        current_player = self.trick_manager.get_current_player()
        
        self.current_trick_cards = []
        
        return self.get_next_card_play(current_player, trick)
    
    def get_next_card_play(self, current_player: InteractivePlayer, trick: Trick) -> Dict:
        """Get the next card play (human or AI)"""
        if current_player.player_type == PlayerType.HUMAN:
            # Human player's turn
            led_suit = trick.led_suit if trick.cards_played else None
            valid_cards = current_player.get_valid_cards(led_suit, self.trump_suit)
            
            return {
                'type': 'human_card_needed',
                'player': current_player.name,
                'hand': [{'card': f"{c.rank.display_name} of {c.suit.value}", 
                         'points': c.points, 'suit': c.suit.value, 
                         'rank': c.rank.display_name, 'is_trump': c.suit == self.trump_suit} 
                        for c in current_player.hand],
                'valid_cards': [{'card': f"{c.rank.display_name} of {c.suit.value}", 
                               'points': c.points, 'suit': c.suit.value, 
                               'rank': c.rank.display_name, 'is_trump': c.suit == self.trump_suit} 
                              for c in valid_cards],
                'trick_so_far': self.current_trick_cards,
                'led_suit': led_suit.value if led_suit else None,
                'trump_suit': self.trump_suit.value
            }
        else:
            # AI player's turn
            led_suit = trick.led_suit if trick.cards_played else None
            valid_cards = current_player.get_valid_cards(led_suit, self.trump_suit)
            
            # Get cards already played in this trick
            trick_cards = [tc.card for tc in trick.cards_played]
            
            # AI chooses card
            chosen_card = current_player.choose_card_to_play(valid_cards, led_suit, self.trump_suit, trick_cards)
            
            # Play the card
            self.trick_manager.play_card(chosen_card, current_player)
            
            # Add to current trick display
            self.current_trick_cards.append({
                'player': current_player.name,
                'card': f"{chosen_card.rank.display_name} of {chosen_card.suit.value}",
                'points': chosen_card.points,
                'is_trump': chosen_card.suit == self.trump_suit
            })
            
            # Check if trick is complete
            if trick.is_complete():
                return self.complete_trick(trick)
            else:
                # Next player's turn
                next_player = self.trick_manager.get_current_player()
                return self.get_next_card_play(next_player, trick)
    
    def process_human_card(self, card_info: Dict) -> Dict:
        """Process human card selection"""
        # Find the card in human's hand
        chosen_card = None
        for card in self.human_player.hand:
            if (card.rank.display_name == card_info['rank'] and 
                card.suit.value == card_info['suit']):
                chosen_card = card
                break
        
        if not chosen_card:
            return {'type': 'error', 'message': 'Invalid card selection'}
        
        # Play the card
        current_trick = self.trick_manager.current_trick
        self.trick_manager.play_card(chosen_card, self.human_player)
        
        # Add to current trick display
        self.current_trick_cards.append({
            'player': self.human_player.name,
            'card': f"{chosen_card.rank.display_name} of {chosen_card.suit.value}",
            'points': chosen_card.points,
            'is_trump': chosen_card.suit == self.trump_suit
        })
        
        # Check if trick is complete
        if current_trick.is_complete():
            return self.complete_trick(current_trick)
        else:
            # Continue with next player
            next_player = self.trick_manager.get_current_player()
            return self.get_next_card_play(next_player, current_trick)
    
    def complete_trick(self, trick: Trick) -> Dict:
        """Complete a trick and prepare for next"""
        trick_result = {
            'type': 'trick_complete',
            'trick_number': trick.trick_number,
            'cards': self.current_trick_cards,
            'winner': trick.winner.name,
            'points': trick.get_points(),
            'team_points': {team.name: team.get_total_points() for team in self.teams}
        }
        
        # Check if round is complete
        if self.trick_manager.is_round_complete():
            self.round_complete = True
            scores = self.calculate_scores()
            trick_result.update({
                'round_complete': True,
                'round_scores': {team.name: score for team, score in scores.items()},
                'winning_team': self.winning_team.name if self.winning_team else None
            })
        else:
            # Prepare next trick
            trick_result['next_leader'] = trick.winner.name
        
        return trick_result
    
    def calculate_scores(self) -> Dict[Team, int]:
        """Calculate final scores for the round based on 56 card game rules"""
        if not self.bidding_round or not self.bidding_round.winning_bid:
            return {team: 0 for team in self.teams}
        
        # Get team points from tricks
        team_points = self.trick_manager.get_team_points()
        
        # Identify bidding and defending teams
        bidding_team = self.bidding_round.winning_team
        defending_team = None
        for team in self.teams:
            if team != bidding_team:
                defending_team = team
                break
        
        if not defending_team:
            raise ValueError("Could not identify defending team")
        
        bidding_points = team_points[bidding_team]
        bid_amount = self.bidding_round.winning_bid.amount
        
        scores = {}
        if bidding_points >= bid_amount:
            # Bidding team made their bid
            scores[bidding_team] = bid_amount
            scores[defending_team] = 56 - bid_amount
            self.winning_team = bidding_team
        else:
            # Bidding team failed
            scores[bidding_team] = 0
            scores[defending_team] = 56
            self.winning_team = defending_team
        
        return scores


class InteractiveGame56(Game56):
    """Interactive version of the 56 card game"""
    
    def __init__(self, human_player_name: str = "You", target_score: int = 500):
        # Create interactive players
        self.human_player = InteractivePlayer(human_player_name, Position.SOUTH, PlayerType.HUMAN)
        ai_players = [
            InteractivePlayer("AI North", Position.NORTH, PlayerType.AI),
            InteractivePlayer("AI East", Position.EAST, PlayerType.AI),
            InteractivePlayer("AI West", Position.WEST, PlayerType.AI)
        ]
        
        players = [ai_players[0], ai_players[1], self.human_player, ai_players[2]]  # N, E, S, W
        
        # Create teams: North-South (AI North + Human) vs East-West (AI East + AI West)
        team1 = Team("North-South", players[0], players[2])  # AI North & Human South
        team2 = Team("East-West", players[1], players[3])   # AI East & AI West
        
        self.players = players
        self.teams = [team1, team2]
        self.target_score = target_score
        self.rounds: List[InteractiveGameRound] = []
        self.game_scores: Dict[Team, int] = {team: 0 for team in self.teams}
        self.current_dealer_index = 0
        self.game_complete = False
        self.winning_team: Optional[Team] = None
        self.phase = GamePhase.SETUP
        self.current_round: Optional[InteractiveGameRound] = None
    
    def start_new_round(self) -> Dict:
        """Start a new round"""
        round_number = len(self.rounds) + 1
        dealer = self.get_current_dealer()
        
        self.current_round = InteractiveGameRound(
            round_number, self.players, self.teams, dealer, self.human_player
        )
        
        # Deal cards
        self.current_round.deal_cards()
        
        # Move dealer to next player
        self.current_dealer_index = (self.current_dealer_index + 1) % len(self.players)
        
        return {
            'type': 'round_started',
            'round_number': round_number,
            'dealer': dealer.name,
            'human_hand': [{'card': f"{c.rank.display_name} of {c.suit.value}", 
                           'points': c.points, 'suit': c.suit.value, 
                           'rank': c.rank.display_name} for c in self.human_player.hand],
            'hand_points': self.human_player.get_hand_points()
        }


# Test function
if __name__ == "__main__":
    game = InteractiveGame56("Player")
    result = game.start_new_round()
    print("Round started:")
    print(f"Dealer: {result['dealer']}")
    print(f"Human hand points: {result['hand_points']}")
    print("Human cards:", [card['card'] for card in result['human_hand']])
