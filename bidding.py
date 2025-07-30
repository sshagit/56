"""
bidding.py - Bidding system for the 56 Card Game
"""

from typing import List, Optional, Dict
from enum import Enum
from player import Player, Team


class BidAction(Enum):
    """Possible bidding actions"""
    BID = "bid"
    PASS = "pass"


class Bid:
    """Represents a bid made by a player"""
    
    def __init__(self, player: Player, action: BidAction, amount: int = 0):
        self.player = player
        self.action = action
        self.amount = amount
    
    def __str__(self) -> str:
        if self.action == BidAction.BID:
            return f"{self.player.name} bids {self.amount}"
        else:
            return f"{self.player.name} passes"
    
    def __repr__(self) -> str:
        return f"Bid({self.player}, {self.action}, {self.amount})"


class BiddingRound:
    """Manages a round of bidding"""
    
    def __init__(self, players: List[Player], teams: List[Team], starting_player: Player):
        self.players = players
        self.teams = teams
        self.starting_player = starting_player
        self.bids: List[Bid] = []
        self.current_bid = 27  # Minimum bid is 28, so current starts at 27
        self.winning_bid: Optional[Bid] = None
        self.winning_team: Optional[Team] = None
        self.is_complete = False
        self.consecutive_passes = 0
    
    def get_minimum_bid(self) -> int:
        """Get the minimum valid bid amount"""
        return max(28, self.current_bid + 1)
    
    def get_maximum_bid(self) -> int:
        """Get the maximum possible bid"""
        return 56
    
    def is_valid_bid(self, amount: int) -> bool:
        """Check if a bid amount is valid"""
        return self.get_minimum_bid() <= amount <= self.get_maximum_bid()
    
    def get_player_team(self, player: Player) -> Team:
        """Get the team that a player belongs to"""
        for team in self.teams:
            if player in team.players:
                return team
        raise ValueError(f"Player {player} not found in any team")
    
    def can_player_bid(self, player: Player, amount: int) -> bool:
        """Check if a player can make a specific bid"""
        if self.is_complete:
            return False
        
        if not self.is_valid_bid(amount):
            return False
        
        # Player cannot outbid their own team's current bid
        player_team = self.get_player_team(player)
        if self.winning_team == player_team:
            return False
        
        return True
    
    def make_bid(self, player: Player, action: BidAction, amount: int = 0) -> bool:
        """Make a bid or pass"""
        if self.is_complete:
            return False
        
        if action == BidAction.BID:
            if not self.can_player_bid(player, amount):
                return False
            
            bid = Bid(player, action, amount)
            self.bids.append(bid)
            self.current_bid = amount
            self.winning_bid = bid
            self.winning_team = self.get_player_team(player)
            self.consecutive_passes = 0
            
        else:  # PASS
            bid = Bid(player, action)
            self.bids.append(bid)
            self.consecutive_passes += 1
            
            # If 3 consecutive passes after a bid, bidding is complete
            if self.consecutive_passes >= 3 and self.winning_bid is not None:
                self.is_complete = True
        
        return True
    
    def get_next_player(self, current_player: Player) -> Player:
        """Get the next player in bidding order"""
        current_index = self.players.index(current_player)
        next_index = (current_index + 1) % len(self.players)
        return self.players[next_index]
    
    def get_bidding_summary(self) -> str:
        """Get a summary of the bidding round"""
        if not self.bids:
            return "No bids made yet"
        
        summary = "Bidding history:\n"
        for bid in self.bids:
            summary += f"  {bid}\n"
        
        if self.is_complete and self.winning_bid:
            summary += f"\nWinning bid: {self.winning_bid.amount} by {self.winning_team.name}"
        elif self.is_complete:
            summary += "\nAll players passed - no valid bid"
        
        return summary.strip()
    
    def finalize_bidding(self):
        """Finalize the bidding and set the winning team's bid"""
        if self.winning_bid and self.winning_team:
            self.winning_team.set_bid(self.winning_bid.amount)
            # Clear the other team's bid
            for team in self.teams:
                if team != self.winning_team:
                    team.clear_bid()


class BiddingManager:
    """High-level manager for the bidding process"""
    
    def __init__(self, players: List[Player], teams: List[Team]):
        self.players = players
        self.teams = teams
    
    def conduct_bidding(self, starting_player: Player) -> Optional[BiddingRound]:
        """Conduct a complete bidding round (for demo/testing)"""
        bidding_round = BiddingRound(self.players, self.teams, starting_player)
        
        print(f"Bidding starts with {starting_player.name}")
        print(f"Minimum bid: {bidding_round.get_minimum_bid()}")
        
        current_player = starting_player
        
        # More realistic bidding logic based on hand strength
        while not bidding_round.is_complete:
            hand_points = current_player.get_hand_points()
            min_bid = bidding_round.get_minimum_bid()
            
            # Enhanced bidding strategy
            should_bid = False
            bid_amount = min_bid
            
            # Strong hand (18+ points) - likely to bid
            if hand_points >= 18 and min_bid <= 40:
                should_bid = True
                bid_amount = min(min_bid + 2, 56)  # Aggressive bidding
            # Good hand (15-17 points) - moderate bidding
            elif hand_points >= 15 and min_bid <= 35:
                should_bid = True
                bid_amount = min_bid
            # Decent hand (12-14 points) - conservative bidding
            elif hand_points >= 12 and min_bid <= 30:
                import random
                should_bid = random.random() < 0.3  # 30% chance
                bid_amount = min_bid
            
            # Check if player can actually bid
            if should_bid and bidding_round.can_player_bid(current_player, bid_amount):
                bidding_round.make_bid(current_player, BidAction.BID, bid_amount)
                print(f"{current_player.name} bids {bid_amount} (hand: {hand_points} pts)")
            else:
                bidding_round.make_bid(current_player, BidAction.PASS)
                print(f"{current_player.name} passes (hand: {hand_points} pts)")
            
            if not bidding_round.is_complete:
                current_player = bidding_round.get_next_player(current_player)
        
        bidding_round.finalize_bidding()
        return bidding_round


# Test the bidding system if run directly
if __name__ == "__main__":
    from card import Deck
    from player import GameSetup
    
    # Create a standard game
    players, teams = GameSetup.create_standard_game(["Alice", "Bob", "Carol", "Dave"])
    
    # Deal cards
    deck = Deck()
    deck.shuffle()
    for player in players:
        hand = deck.deal_hand(12)
        player.receive_cards(hand)
    
    print("Starting hand points:")
    for player in players:
        print(f"  {player.name}: {player.get_hand_points()} points")
    
    print("\n" + "="*50)
    
    # Conduct bidding
    bidding_manager = BiddingManager(players, teams)
    bidding_round = bidding_manager.conduct_bidding(players[0])  # Start with Alice
    
    print("\n" + "="*50)
    print(bidding_round.get_bidding_summary())
    
    print(f"\nFinal team bids:")
    for team in teams:
        if team.is_bidding_team:
            print(f"  {team.name}: {team.bid} (bidding team)")
        else:
            print(f"  {team.name}: defending")
