from dataclasses import dataclass, field
from enum import Enum
from random import sample, random, uniform, choice
from time import sleep, time
from typing import List, Dict, Optional
import json
import math


class LightState(Enum):
    """Enumeration for the light states in the game."""
    GREEN = "Green"
    RED = "Red"


@dataclass
class Player:
    """
    Represents a player in the game with realistic movement characteristics.

    Attributes:
        id (str): Unique identifier for the player.
        position (float): Current position of the player (can be fractional).
        eliminated (bool): Whether the player is eliminated. Defaults to False.
        elimination_round (Optional[int]): Round when player was eliminated. None if still active.
        total_moves (int): Total number of moves made by the player.
        successful_moves (int): Number of successful moves (not during red light).
        speed (float): Movement speed of the player (units per round).
        field_length (float): Total length of the field this player needs to traverse.
        reached_finish (bool): Whether the player has reached the finish line.
        finish_round (Optional[int]): Round when player reached finish. None if not finished.
    """

    id: str
    position: float = 0.0
    eliminated: bool = False
    elimination_round: Optional[int] = None
    total_moves: int = 0
    successful_moves: int = 0
    speed: float = 0.0
    field_length: float = 0.0
    reached_finish: bool = False
    finish_round: Optional[int] = None

    def move(self, current_light: LightState, round_number: int) -> bool:
        """
        Moves the player based on their speed and current light state.
        Returns True if move was successful, False if eliminated.

        Args:
            current_light (LightState): Current light state
            round_number (int): Current round number

        Returns:
            bool: True if move was successful, False if eliminated
        """
        if self.eliminated or self.reached_finish:
            return False

        # Calculate movement distance based on speed
        movement_distance = self.speed
        self.position += movement_distance
        self.total_moves += 1

        # Check if player reached the finish line
        if self.position >= self.field_length:
            self.position = self.field_length
            self.reached_finish = True
            self.finish_round = round_number
            self.successful_moves += 1
            return True

        if current_light == LightState.RED:
            self.eliminate(round_number)
            return False
        else:
            self.successful_moves += 1
            return True

    def eliminate(self, round_number: int):
        """
        Marks the player as eliminated when they move during a "Red" light.

        Args:
            round_number (int): The round when the player was eliminated
        """
        self.eliminated = True
        self.elimination_round = round_number

    def reset(self):
        """Resets the player to initial state."""
        self.position = 0.0
        self.eliminated = False
        self.elimination_round = None
        self.total_moves = 0
        self.successful_moves = 0
        self.reached_finish = False
        self.finish_round = None
        # Generate new random speed and field length
        self.speed = uniform(0.5, 2.0)  # Random speed between 0.5 and 2.0 units per round
        self.field_length = uniform(8.0, 15.0)  # Random field length between 8 and 15 units


@dataclass
class GameStats:
    """Statistics tracking for the game."""
    total_rounds: int = 0
    total_eliminations: int = 0
    total_finishers: int = 0
    green_light_moves: int = 0
    red_light_moves: int = 0
    red_light_eliminations: int = 0
    game_duration: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    average_speed: float = 0.0
    average_field_length: float = 0.0

    def start_timer(self):
        """Start the game timer."""
        self.start_time = time()

    def end_timer(self):
        """End the game timer and calculate duration."""
        self.end_time = time()
        self.game_duration = self.end_time - self.start_time

    def to_dict(self) -> Dict:
        """Convert stats to dictionary for serialization."""
        return {
            'total_rounds': self.total_rounds,
            'total_eliminations': self.total_eliminations,
            'total_finishers': self.total_finishers,
            'green_light_moves': self.green_light_moves,
            'red_light_moves': self.red_light_moves,
            'red_light_eliminations': self.red_light_eliminations,
            'game_duration': self.game_duration,
            'average_speed': self.average_speed,
            'average_field_length': self.average_field_length
        }


class SquidGame:
    """
    Simulates the 'Red Light, Green Light' game from Squid Game with realistic movement.

    Attributes:
        total_players (int): Total number of players in the game.
        players (list[Player]): List of players participating in the game.
        stats (GameStats): Game statistics tracker.
        verbose (bool): Whether to print detailed game output.
        light_duration (float): Fixed duration for each light state (in seconds).
    """

    def __init__(self, total_players: int = 20, verbose: bool = True, light_duration: float = 2.0) -> None:
        if total_players <= 0:
            raise ValueError("The number of players must be greater than 0.")
        if light_duration <= 0:
            raise ValueError("Light duration must be greater than 0.")

        self.total_players = total_players
        self.light_duration = light_duration
        self.players = self._create_players(total_players)
        self.stats = GameStats()
        self.verbose = verbose

    def _create_players(self, total_players: int) -> List[Player]:
        """
        Creates a list of Player objects with unique IDs and random characteristics.

        Args:
            total_players (int): The total number of players to be created.

        Returns:
            List[Player]: A list of Player objects representing the players in the game.
        """
        players = []
        for id in range(1, total_players + 1):
            player = Player(f"{id:03}")
            # Generate random speed and field length for each player
            player.speed = uniform(0.5, 2.0)  # Random speed between 0.5 and 2.0 units per round
            player.field_length = uniform(8.0, 15.0)  # Random field length between 8 and 15 units
            players.append(player)
        return players

    def start(self, game_duration: int = 60, green_move_chance: float = 0.8, red_move_chance: float = 0.05) -> List[Player]:
        """
        Runs the game for a specified duration or until all players are eliminated/finished.

        Args:
            game_duration (int): Total game duration (in seconds). Defaults to 60.
            green_move_chance (float): Probability of moving during green light (0.0-1.0). Defaults to 0.8.
            red_move_chance (float): Probability of moving during red light (0.0-1.0). Defaults to 0.05.

        Returns:
            List[Player]: A list of remaining players after the game ends.
        """
        if not (0.0 <= green_move_chance <= 1.0 and 0.0 <= red_move_chance <= 1.0):
            raise ValueError("Move chances must be between 0.0 and 1.0")

        self.stats.start_timer()
        rounds = 0
        start_time: float = time()
        current_light = LightState.GREEN

        # Calculate average speed and field length for stats
        speeds = [p.speed for p in self.players]
        field_lengths = [p.field_length for p in self.players]
        self.stats.average_speed = sum(speeds) / len(speeds)
        self.stats.average_field_length = sum(field_lengths) / len(field_lengths)

        if self.verbose:
            print(f"🎮 Squid Game Starting!")
            print(f"👥 Total Players: {self.total_players}")
            print(f"⏱️  Game Duration: {game_duration} seconds")
            print(f"🔄 Light Duration: {self.light_duration} seconds")
            print(f"📊 Green Move Chance: {green_move_chance:.1%}")
            print(f"📊 Red Move Chance: {red_move_chance:.1%}")
            print(f"🏃 Average Speed: {self.stats.average_speed:.2f} units/round")
            print(f"📏 Average Field Length: {self.stats.average_field_length:.2f} units")
            print("=" * 60)

        while (elapsed_time := time() - start_time) < game_duration:
            rounds += 1
            self.stats.total_rounds = rounds

            # Determine moving players based on the current light
            move_chance = green_move_chance if current_light == LightState.GREEN else red_move_chance
            moving_players = self.get_moving_players(move_chance)
            stationary_players = self.get_stationary_players(moving_players)

            # Track statistics
            if current_light == LightState.GREEN:
                self.stats.green_light_moves += len(moving_players)
            else:
                self.stats.red_light_moves += len(moving_players)

            # Move players and eliminate those moving on Red Light
            eliminated_this_round = 0
            finished_this_round = 0
            for player in moving_players:
                success = player.move(current_light, rounds)
                if not success:
                    if player.eliminated:
                        eliminated_this_round += 1
                        self.stats.total_eliminations += 1
                        if current_light == LightState.RED:
                            self.stats.red_light_eliminations += 1
                else:
                    if player.reached_finish:
                        finished_this_round += 1
                        self.stats.total_finishers += 1

            # Output for current round
            if self.verbose:
                self._print_round_summary(rounds, current_light, moving_players, 
                                       stationary_players, eliminated_this_round, finished_this_round)

            # End game if all players are eliminated or finished
            remaining_count = len(self.get_remaining_players())
            finished_count = len(self.get_finished_players())
            if remaining_count == 0:
                if self.verbose:
                    print("💀 All players eliminated!")
                break
            elif finished_count == self.total_players:
                if self.verbose:
                    print("🏁 All players finished!")
                break

            # Wait for the fixed light duration
            sleep_time = min(self.light_duration, game_duration - elapsed_time)
            if self.verbose and sleep_time > 0:
                print(f"⏳ Waiting {sleep_time:.1f} seconds...")
            sleep(sleep_time)
            
            # Switch light
            current_light = LightState.RED if current_light == LightState.GREEN else LightState.GREEN

        self.stats.end_timer()
        
        if self.verbose:
            self._print_final_summary()

        return self.get_remaining_players()

    def reset(self):
        """
        Resets the game by recreating all players and clearing statistics.

        This method reinitializes the list of players to their original state, 
        with all players starting at position 0 and marked as not eliminated. 
        It can be used to restart the game without creating a new instance of the class.
        """
        self.players = self._create_players(self.total_players)
        self.stats = GameStats()

    def _print_round_summary(self, round_num: int, current_light: LightState, 
                           moving_players: List[Player], stationary_players: List[Player], 
                           eliminated_count: int, finished_count: int):
        """Print detailed round summary."""
        light_emoji = "🟢" if current_light == LightState.GREEN else "🔴"
        print(f"\n{light_emoji} Round {round_num}: {current_light.value} Light")
        
        # Show moving players with their positions
        if moving_players:
            moved_info = []
            for p in moving_players[:8]:  # Show first 8
                pos_str = f"{p.id}({p.position:.1f})"
                if p.reached_finish:
                    pos_str += "🏁"
                moved_info.append(pos_str)
            print(f"🏃 Moved ({len(moving_players)}): {', '.join(moved_info)}{'...' if len(moving_players) > 8 else ''}")
        else:
            print(f"🏃 Moved (0): None")
        
        # Show stationary players
        if stationary_players:
            static_info = []
            for p in stationary_players[:8]:  # Show first 8
                pos_str = f"{p.id}({p.position:.1f})"
                static_info.append(pos_str)
            print(f"🛑 Static ({len(stationary_players)}): {', '.join(static_info)}{'...' if len(stationary_players) > 8 else ''}")
        else:
            print(f"🛑 Static (0): None")
        
        # Show eliminations and finishes
        if eliminated_count > 0:
            eliminated_players = [p for p in moving_players if p.eliminated]
            elim_info = [f"{p.id}({p.position:.1f})" for p in eliminated_players[:5]]
            print(f"💀 Eliminated ({eliminated_count}): {', '.join(elim_info)}{'...' if len(eliminated_players) > 5 else ''}")
        else:
            print("✅ Eliminated: None")
            
        if finished_count > 0:
            finished_players = [p for p in moving_players if p.reached_finish]
            finish_info = [f"{p.id}({p.field_length:.1f})" for p in finished_players[:5]]
            print(f"🏁 Finished ({finished_count}): {', '.join(finish_info)}{'...' if len(finished_players) > 5 else ''}")
        
        remaining = len(self.get_remaining_players())
        finished = len(self.get_finished_players())
        print(f"👥 Remaining: {remaining} players | 🏁 Finished: {finished} players")

    def _print_final_summary(self):
        """ game summary."""
        print("\n" + "=" * 60)
        print("🏁 GAME SUMMARY")
        print("=" * 60)
        
        remaining_players = self.get_remaining_players()
        eliminated_players = self.get_eliminated_players()
        finished_players = self.get_finished_players()
        
        print(f" Total Rounds: {self.stats.total_rounds}")
        print(f"  Game Duration: {self.stats.game_duration:.1f} seconds")
        print(f" Starting Players: {self.total_players}")
        print(f" Surviving Players: {len(remaining_players)}")
        print(f" Finished Players: {len(finished_players)}")
        print(f"💀 Eliminated Players: {len(eliminated_players)}")
        print(f" Survival Rate: {len(remaining_players)/self.total_players:.1%}")
        print(f" Finish Rate: {len(finished_players)/self.total_players:.1%}")
        
        if finished_players:
            print(f"\n🏆 WINNERS (Finished Players):")
            # Sort by finish round (earliest first), then by ID
            winners = sorted(finished_players, key=lambda p: (p.finish_round, p.id))
            for i, player in enumerate(winners[:10], 1):
                print(f"  {i}. Player {player.id} - Finished Round {player.finish_round} (Speed: {player.speed:.2f}, Field: {player.field_length:.1f})")
            if len(winners) > 10:
                print(f"  ... and {len(winners) - 10} more")
        
        if remaining_players:
            print(f"\n🏃 LEADERS (Still Playing):")
            # Sort by position (highest first), then by ID
            leaders = sorted(remaining_players, key=lambda p: (p.position, p.id), reverse=True)
            for i, player in enumerate(leaders[:10], 1):
                progress = (player.position / player.field_length) * 100
                print(f"  {i}. Player {player.id} - Position {player.position:.1f}/{player.field_length:.1f} ({progress:.1f}%) (Speed: {player.speed:.2f})")
            if len(leaders) > 10:
                print(f"  ... and {len(leaders) - 10} more")
        
        print(f"\n📈 MOVEMENT STATISTICS:")
        print(f"  🟢 Green Light Moves: {self.stats.green_light_moves}")
        print(f"  🔴 Red Light Moves: {self.stats.red_light_moves}")
        print(f"  💀 Red Light Eliminations: {self.stats.red_light_eliminations}")
        print(f"  🏁 Total Finishers: {self.stats.total_finishers}")
        print(f"  🏃 Average Speed: {self.stats.average_speed:.2f} units/round")
        print(f"  📏 Average Field Length: {self.stats.average_field_length:.2f} units")
        
        if self.stats.red_light_moves > 0:
            elimination_rate = self.stats.red_light_eliminations / self.stats.red_light_moves
            print(f"  ⚠️  Red Light Elimination Rate: {elimination_rate:.1%}")

    def get_remaining_players(self) -> List[Player]:
        """
        Retrieves the list of players who are still active in the game.

        Returns:
            List[Player]: A list of players who have not been eliminated and haven't finished.
        """
        return [p for p in self.players if not p.eliminated and not p.reached_finish]

    def get_finished_players(self) -> List[Player]:
        """
        Retrieves the list of players who have reached the finish line.

        Returns:
            List[Player]: A list of players who have finished the game.
        """
        return [p for p in self.players if p.reached_finish]

    def get_moving_players(self, move_chance: float) -> List[Player]:
        """
        Selects a subset of remaining players who will attempt to move.

        Args:
            move_chance (float): The probability (0.0-1.0) that each remaining player will attempt to move.

        Returns:
            List[Player]: A random sample of players who will move, based on the specified chance.
        """
        remaining_players: List[Player] = self.get_remaining_players()
        moving_players = []
        
        for player in remaining_players:
            if random() < move_chance:
                moving_players.append(player)
        
        return moving_players

    def get_stationary_players(self, moving_players: List[Player]) -> List[Player]:
        """
        Identifies players who chose to stay still in the current round.

        Args:
            moving_players (List[Player]): The list of players who attempted to move.

        Returns:
            List[Player]: A list of players who did not attempt to move during the current round.
        """
        return [p for p in self.get_remaining_players() if p not in moving_players]

    def get_eliminated_players(self) -> List[Player]:
        """
        Retrieves the list of players who have been eliminated.

        Returns:
            List[Player]: A list of players who are no longer in the game.
        """
        return [p for p in self.players if p.eliminated]

    def export_stats(self, filename: str = "squid_game_stats.json"):
        """
        Export game statistics to a JSON file.

        Args:
            filename (str): The filename to save the statistics to.
        """
        stats_data = {
            'game_config': {
                'total_players': self.total_players,
                'light_duration': self.light_duration,
                'game_duration': 60  # Default, could be made configurable
            },
            'statistics': self.stats.to_dict(),
            'players': {
                'remaining': [{'id': p.id, 'position': p.position, 'field_length': p.field_length,
                              'speed': p.speed, 'total_moves': p.total_moves, 
                              'successful_moves': p.successful_moves} for p in self.get_remaining_players()],
                'finished': [{'id': p.id, 'position': p.position, 'field_length': p.field_length,
                             'speed': p.speed, 'finish_round': p.finish_round,
                             'total_moves': p.total_moves, 'successful_moves': p.successful_moves} 
                            for p in self.get_finished_players()],
                'eliminated': [{'id': p.id, 'position': p.position, 'field_length': p.field_length,
                               'speed': p.speed, 'elimination_round': p.elimination_round,
                               'total_moves': p.total_moves, 'successful_moves': p.successful_moves} 
                              for p in self.get_eliminated_players()]
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(stats_data, f, indent=2)
        
        print(f"📊 Statistics exported to {filename}")


if __name__ == "__main__":
    # Create and run the game with realistic parameters
    game = SquidGame(total_players=20, verbose=True, light_duration=2.0)
    
    try:
        remaining_players: List[Player] = game.start(
            game_duration=60,  # 1 minute game
            green_move_chance=0.8,
            red_move_chance=0.1
        )
        
        # Export statistics
        game.export_stats()
        
    except KeyboardInterrupt:
        print("\n⏹️  Game interrupted by user")
    except Exception as e:
        print(f"❌ Error during game: {e}")