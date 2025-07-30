"""
game.py - Main game logic for the 56 Card Game
"""

from typing import List, Optional, Dict
from enum import Enum
from card import Deck, Suit, calculate_hand_points
from player import Player, Team, GameSetup
from bidding import BiddingManager, BiddingRound
from trick import TrickManager


class GamePhase(Enum):
    """Different phases of the game"""
    SETUP = "setup"
    DEALING = "dealing"
    BIDDING = "bidding"
    TRUMP_SELECTION = "trump_selection"
    TRICK_TAKING = "trick_taking"
    SCORING = "scoring"
    GAME_OVER = "game_over"


class GameRound:
    """Represents a single round of the 56 card game"""
    
    def __init__(self, round_number: int, players: List[Player], teams: List[Team], dealer: Player):
        self.round_number = round_number
        self.players = players
        self.teams = teams
        self.dealer = dealer
        self.deck = Deck()
        self.bidding_round: Optional[BiddingRound] = None
        self.trump_suit: Optional[Suit] = None
        self.trick_manager: Optional[TrickManager] = None
        self.winning_team: Optional[Team] = None
        self.round_complete = False
    
    def deal_cards(self):
        """Deal 12 cards to each player"""
        self.deck.shuffle()
        for player in self.players:
            player.reset_for_new_round()
            hand = self.deck.deal_hand(12)
            player.receive_cards(hand)
    
    def conduct_bidding(self) -> bool:
        """Conduct the bidding phase"""
        # Bidding starts with player to dealer's left
        dealer_index = self.players.index(self.dealer)
        starting_player = self.players[(dealer_index + 1) % len(self.players)]
        
        # Show hands to players (for demo - in real game this would be hidden)
        print("\nPlayer hands after dealing:")
        for player in self.players:
            print(f"{player.name}: {player.get_hand_points()} points")
        
        bidding_manager = BiddingManager(self.players, self.teams)
        self.bidding_round = bidding_manager.conduct_bidding(starting_player)
        
        return self.bidding_round.winning_bid is not None
    
    def set_trump_suit(self, trump_suit: Suit):
        """Set the trump suit (chosen by winning bidder)"""
        self.trump_suit = trump_suit
    
    def play_tricks(self):
        """Play all 12 tricks"""
        if not self.trump_suit:
            raise ValueError("Trump suit must be set before playing tricks")
        
        self.trick_manager = TrickManager(self.players, self.teams, self.trump_suit)
        
        # First trick is led by player to dealer's left
        dealer_index = self.players.index(self.dealer)
        leading_player = self.players[(dealer_index + 1) % len(self.players)]
        
        # Play all 12 tricks
        for trick_num in range(12):
            print(f"\n--- Trick {trick_num + 1} ---")
            trick = self.trick_manager.start_new_trick(leading_player)
            print(f"{leading_player.name} leads this trick")
            
            # Each player plays a card
            for card_num in range(4):
                current_player = self.trick_manager.get_current_player()
                led_suit = trick.led_suit if trick.cards_played else None
                valid_cards = current_player.get_valid_cards(led_suit, self.trump_suit)
                
                if valid_cards:
                    # For demo: randomly select from valid cards (more realistic)
                    import random
                    card_to_play = random.choice(valid_cards)
                    self.trick_manager.play_card(card_to_play, current_player)
                    
                    # Show what was played
                    trump_indicator = " (TRUMP)" if card_to_play.suit == self.trump_suit else ""
                    print(f"  {current_player.name} plays {card_to_play}{trump_indicator}")
            
            # Show trick winner and points
            print(f"  → {trick.winner.name} wins the trick ({trick.get_points()} points)")
            
            # Winner of current trick leads next trick
            leading_player = trick.winner
        
        self.round_complete = True
        
        # Show final trick totals
        print(f"\nTrick-taking complete!")
        team_points = self.trick_manager.get_team_points()
        print(f"Points from tricks:")
        for team, points in team_points.items():
            print(f"  {team.name}: {points} points")
    
    def calculate_scores(self) -> Dict[Team, int]:
        """Calculate and return scores for this round"""
        if not self.round_complete:
            raise ValueError("Round not complete")
        
        team_points = self.trick_manager.get_team_points()
        scores = {}
        
        # Find the bidding team
        bidding_team = None
        defending_team = None
        
        for team in self.teams:
            if team.is_bidding_team:
                bidding_team = team
            else:
                defending_team = team
        
        if not bidding_team or not defending_team:
            raise ValueError("Could not identify bidding and defending teams")
        
        bidding_points = team_points[bidding_team]
        bid_amount = bidding_team.bid
        
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
    
    def get_round_summary(self) -> str:
        """Get a summary of the round"""
        summary = f"=== Round {self.round_number} Summary ===\n"
        summary += f"Dealer: {self.dealer.name}\n"
        
        if self.bidding_round:
            summary += f"\nBidding:\n{self.bidding_round.get_bidding_summary()}\n"
        
        if self.trump_suit:
            summary += f"\nTrump suit: {self.trump_suit.value}\n"
        
        if self.round_complete and self.trick_manager:
            team_points = self.trick_manager.get_team_points()
            summary += f"\nPoints from tricks:\n"
            for team, points in team_points.items():
                summary += f"  {team.name}: {points} points\n"
            
            scores = self.calculate_scores()
            summary += f"\nRound scores:\n"
            for team, score in scores.items():
                summary += f"  {team.name}: {score} points\n"
            
            if self.winning_team:
                summary += f"\nRound winner: {self.winning_team.name}\n"
        
        return summary


class Game56:
    """Main game class for the 56 card game"""
    
    def __init__(self, player_names: List[str] = None, target_score: int = 500):
        if player_names is None:
            player_names = ["North", "East", "South", "West"]
        
        self.players, self.teams = GameSetup.create_standard_game(player_names)
        self.target_score = target_score
        self.rounds: List[GameRound] = []
        self.game_scores: Dict[Team, int] = {team: 0 for team in self.teams}
        self.current_dealer_index = 0
        self.game_complete = False
        self.winning_team: Optional[Team] = None
        self.phase = GamePhase.SETUP
    
    def get_current_dealer(self) -> Player:
        """Get the current dealer"""
        return self.players[self.current_dealer_index]
    
    def play_round(self) -> GameRound:
        """Play a complete round"""
        round_number = len(self.rounds) + 1
        dealer = self.get_current_dealer()
        
        print(f"\n{'='*60}")
        print(f"ROUND {round_number} - Dealer: {dealer.name}")
        print(f"{'='*60}")
        
        # Create and play the round
        game_round = GameRound(round_number, self.players, self.teams, dealer)
        
        # Phase 1: Deal cards
        self.phase = GamePhase.DEALING
        game_round.deal_cards()
        print("Cards dealt to all players.")
        
        # Phase 2: Bidding
        self.phase = GamePhase.BIDDING
        print(f"\nStarting bidding...")
        if not game_round.conduct_bidding():
            print("No valid bids - redeal required")
            return self.play_round()  # In real game, might handle differently
        
        # Phase 3: Trump selection (by winning bidder)
        self.phase = GamePhase.TRUMP_SELECTION
        if game_round.bidding_round and game_round.bidding_round.winning_bid:
            winning_bidder = game_round.bidding_round.winning_bid.player
            # For demo: choose trump suit based on strongest suit in hand
            trump_suit = self._choose_best_trump_suit(winning_bidder)
            game_round.set_trump_suit(trump_suit)
            print(f"{winning_bidder.name} (winning bidder) chooses {trump_suit.value} as trump")
        else:
            # Fallback
            trump_suit = Suit.HEARTS
            game_round.set_trump_suit(trump_suit)
            print(f"Trump suit: {trump_suit.value}")
        
        # Phase 4: Play tricks
        self.phase = GamePhase.TRICK_TAKING
        print(f"\nPlaying 12 tricks...")
        game_round.play_tricks()
        
        # Phase 5: Scoring
        self.phase = GamePhase.SCORING
        round_scores = game_round.calculate_scores()
        
        # Update game scores
        for team, score in round_scores.items():
            self.game_scores[team] += score
        
        self.rounds.append(game_round)
        
        # Move dealer to next player
        self.current_dealer_index = (self.current_dealer_index + 1) % len(self.players)
        
        # Check for game end
        for team, total_score in self.game_scores.items():
            if total_score >= self.target_score:
                self.game_complete = True
                self.winning_team = team
                self.phase = GamePhase.GAME_OVER
                break
        
        print(game_round.get_round_summary())
        print(f"\nCurrent game scores:")
        for team, score in self.game_scores.items():
            print(f"  {team.name}: {score} points")
        
        return game_round
    
    def _choose_best_trump_suit(self, player: Player) -> Suit:
        """Choose the best trump suit for a player based on their hand"""
        from card import calculate_suit_points
        
        suit_scores = {}
        for suit in Suit:
            # Count both points and number of cards in each suit
            suit_cards = [card for card in player.hand if card.suit == suit]
            points = calculate_suit_points(player.hand, suit)
            card_count = len(suit_cards)
            
            # Score = points + bonus for having many cards of the suit
            suit_scores[suit] = points + (card_count * 0.5)
        
        # Return the suit with highest score
        best_suit = max(suit_scores.keys(), key=lambda s: suit_scores[s])
        return best_suit
    
    def play_game(self):
        """Play a complete game"""
        print(f"Starting new game of 56!")
        print(f"Players: {', '.join(p.name for p in self.players)}")
        print(f"Teams: {self.teams[0].name} vs {self.teams[1].name}")
        print(f"Target score: {self.target_score}")
        
        while not self.game_complete:
            self.play_round()
        
        print(f"\n{'='*60}")
        print(f"GAME OVER!")
        print(f"{'='*60}")
        print(f"Winner: {self.winning_team.name}")
        print(f"Final scores:")
        for team, score in self.game_scores.items():
            print(f"  {team.name}: {score} points")
        print(f"Rounds played: {len(self.rounds)}")


# Test the complete game if run directly
if __name__ == "__main__":
    # Create a game with custom player names
    game = Game56(["Alice", "Bob", "Carol", "Dave"], target_score=100)  # Lower target for demo
    
    # Play just one round for demonstration
    game.play_round()
    
    print(f"\nGame demonstration complete!")
    print(f"To play a full game, call game.play_game()")
