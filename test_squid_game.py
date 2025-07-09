import unittest
from unittest.mock import patch
import json
import tempfile
import os

from squid_game import Player, SquidGame, LightState, GameStats


class TestPlayer(unittest.TestCase):
    """
    Test cases for the Player class.
    """

    def test_player_initialization(self):
        """
        Test the initialization of a Player object.
        Ensures the player has the correct ID, starting position, and elimination status.
        """
        player = Player(id="001")
        self.assertEqual(player.id, "001")
        self.assertEqual(player.position, 0.0)
        self.assertFalse(player.eliminated)
        self.assertIsNone(player.elimination_round)
        self.assertEqual(player.total_moves, 0)
        self.assertEqual(player.successful_moves, 0)
        self.assertEqual(player.speed, 0.0)
        self.assertEqual(player.field_length, 0.0)
        self.assertFalse(player.reached_finish)
        self.assertIsNone(player.finish_round)

    def test_player_move_green_light(self):
        """
        Test the movement functionality of a Player during green light.
        Ensures the player's position updates correctly and move is successful.
        """
        player = Player(id="001")
        player.speed = 1.5
        player.field_length = 10.0
        
        success = player.move(LightState.GREEN, 1)
        
        self.assertTrue(success)
        self.assertEqual(player.position, 1.5)
        self.assertEqual(player.total_moves, 1)
        self.assertEqual(player.successful_moves, 1)
        self.assertFalse(player.eliminated)
        self.assertFalse(player.reached_finish)

    def test_player_move_red_light(self):
        """
        Test the movement functionality of a Player during red light.
        Ensures the player gets eliminated when moving during red light.
        """
        player = Player(id="001")
        player.speed = 1.0
        player.field_length = 10.0
        
        success = player.move(LightState.RED, 1)
        
        self.assertFalse(success)
        self.assertEqual(player.position, 1.0)
        self.assertEqual(player.total_moves, 1)
        self.assertEqual(player.successful_moves, 0)
        self.assertTrue(player.eliminated)
        self.assertEqual(player.elimination_round, 1)

    def test_player_move_when_eliminated(self):
        """
        Test that eliminated players cannot move.
        """
        player = Player(id="001")
        player.eliminate(1)
        
        success = player.move(LightState.GREEN, 2)
        self.assertFalse(success)
        self.assertEqual(player.position, 0.0)  # Should not have moved

    def test_player_move_when_finished(self):
        """
        Test that finished players cannot move.
        """
        player = Player(id="001")
        player.reached_finish = True
        player.finish_round = 1
        
        success = player.move(LightState.GREEN, 2)
        self.assertFalse(success)

    def test_player_reach_finish(self):
        """
        Test that players can reach the finish line.
        """
        player = Player(id="001")
        player.speed = 5.0
        player.field_length = 10.0
        
        # First move - should not finish yet
        success = player.move(LightState.GREEN, 1)
        self.assertTrue(success)
        self.assertEqual(player.position, 5.0)
        self.assertFalse(player.reached_finish)
        
        # Second move - should finish
        success = player.move(LightState.GREEN, 2)
        self.assertTrue(success)
        self.assertEqual(player.position, 10.0)
        self.assertTrue(player.reached_finish)
        self.assertEqual(player.finish_round, 2)

    def test_player_eliminate(self):
        """
        Test the elimination functionality of a Player.
        Ensures the player's elimination status changes correctly.
        """
        player = Player(id="001")
        self.assertFalse(player.eliminated)
        self.assertIsNone(player.elimination_round)

        player.eliminate(5)
        self.assertTrue(player.eliminated)
        self.assertEqual(player.elimination_round, 5)

    def test_player_reset(self):
        """
        Test the reset functionality of a Player.
        """
        player = Player(id="001")
        player.move(LightState.GREEN, 1)
        player.eliminate(2)
        
        player.reset()
        
        self.assertEqual(player.position, 0.0)
        self.assertFalse(player.eliminated)
        self.assertIsNone(player.elimination_round)
        self.assertEqual(player.total_moves, 0)
        self.assertEqual(player.successful_moves, 0)
        self.assertFalse(player.reached_finish)
        self.assertIsNone(player.finish_round)
        # Speed and field_length should be regenerated
        self.assertGreater(player.speed, 0)
        self.assertGreater(player.field_length, 0)


class TestGameStats(unittest.TestCase):
    """
    Test cases for the GameStats class.
    """

    def test_stats_initialization(self):
        """
        Test the initialization of GameStats.
        """
        stats = GameStats()
        self.assertEqual(stats.total_rounds, 0)
        self.assertEqual(stats.total_eliminations, 0)
        self.assertEqual(stats.total_finishers, 0)
        self.assertEqual(stats.green_light_moves, 0)
        self.assertEqual(stats.red_light_moves, 0)
        self.assertEqual(stats.red_light_eliminations, 0)
        self.assertEqual(stats.game_duration, 0.0)
        self.assertEqual(stats.average_speed, 0.0)
        self.assertEqual(stats.average_field_length, 0.0)

    def test_stats_timer(self):
        """
        Test the timer functionality of GameStats.
        """
        stats = GameStats()
        stats.start_timer()
        self.assertGreater(stats.start_time, 0)
        
        stats.end_timer()
        self.assertGreater(stats.end_time, stats.start_time)
        self.assertGreater(stats.game_duration, 0)

    def test_stats_to_dict(self):
        """
        Test the to_dict method of GameStats.
        """
        stats = GameStats()
        stats.total_rounds = 5
        stats.total_eliminations = 10
        stats.total_finishers = 3
        stats.green_light_moves = 20
        stats.red_light_moves = 5
        stats.red_light_eliminations = 5
        stats.game_duration = 30.5
        stats.average_speed = 1.5
        stats.average_field_length = 12.0
        
        stats_dict = stats.to_dict()
        
        self.assertEqual(stats_dict['total_rounds'], 5)
        self.assertEqual(stats_dict['total_eliminations'], 10)
        self.assertEqual(stats_dict['total_finishers'], 3)
        self.assertEqual(stats_dict['green_light_moves'], 20)
        self.assertEqual(stats_dict['red_light_moves'], 5)
        self.assertEqual(stats_dict['red_light_eliminations'], 5)
        self.assertEqual(stats_dict['game_duration'], 30.5)
        self.assertEqual(stats_dict['average_speed'], 1.5)
        self.assertEqual(stats_dict['average_field_length'], 12.0)


class TestSquidGame(unittest.TestCase):
    """
    Test cases for the SquidGame class.
    """

    def setUp(self):
        """
        Set up the SquidGame instance with a total of 10 players before each test.
        """
        self.game = SquidGame(total_players=10, verbose=False, light_duration=2.0)

    def test_game_initialization(self):
        """
        Test the initialization of the SquidGame.
        Ensures the game starts with the correct number of players,
        all players in the correct initial state (position 0, not eliminated).
        """
        self.assertEqual(len(self.game.players), 10)
        self.assertEqual(self.game.total_players, 10)
        self.assertEqual(self.game.light_duration, 2.0)
        self.assertFalse(self.game.verbose)
        self.assertIsInstance(self.game.stats, GameStats)

        for player in self.game.players:
            self.assertIsInstance(player, Player)
            self.assertEqual(player.position, 0.0)
            self.assertFalse(player.eliminated)
            self.assertFalse(player.reached_finish)
            self.assertGreater(player.speed, 0)
            self.assertGreater(player.field_length, 0)

    def test_game_initialization_invalid_players(self):
        """
        Test that initialization with invalid number of players raises ValueError.
        """
        with self.assertRaises(ValueError):
            SquidGame(total_players=0)
        
        with self.assertRaises(ValueError):
            SquidGame(total_players=-5)

    def test_game_initialization_invalid_light_duration(self):
        """
        Test that initialization with invalid light duration raises ValueError.
        """
        with self.assertRaises(ValueError):
            SquidGame(light_duration=0)
        
        with self.assertRaises(ValueError):
            SquidGame(light_duration=-2.0)

    def test_get_remaining_players(self):
        """
        Test the get_remaining_players method.
        Ensures that the method returns the correct number of remaining players,
        and that eliminating a player reduces the number of remaining players.
        """
        self.assertEqual(len(self.game.get_remaining_players()), 10)

        self.game.players[0].eliminate(1)
        self.assertEqual(len(self.game.get_remaining_players()), 9)

        self.game.players[1].reached_finish = True
        self.assertEqual(len(self.game.get_remaining_players()), 8)

    def test_get_finished_players(self):
        """
        Test the get_finished_players method.
        """
        self.assertEqual(len(self.game.get_finished_players()), 0)

        self.game.players[0].reached_finish = True
        self.game.players[1].reached_finish = True
        self.assertEqual(len(self.game.get_finished_players()), 2)

    def test_get_eliminated_players(self):
        """
        Test the get_eliminated_players method.
        Ensures that eliminated players are correctly tracked.
        """
        self.assertEqual(len(self.game.get_eliminated_players()), 0)

        self.game.players[0].eliminate(1)
        self.game.players[1].eliminate(2)
        self.assertEqual(len(self.game.get_eliminated_players()), 2)

    def test_get_moving_players(self):
        """
        Test the get_moving_players method.
        Ensures that the correct number of players move, based on the specified chance.
        """
        # Test with 50% chance
        moving_players = self.game.get_moving_players(move_chance=0.5)
        self.assertGreaterEqual(len(moving_players), 0)
        self.assertLessEqual(len(moving_players), 10)

        # Test with 0% chance
        moving_players = self.game.get_moving_players(move_chance=0.0)
        self.assertEqual(len(moving_players), 0)

        # Test with 100% chance
        moving_players = self.game.get_moving_players(move_chance=1.0)
        self.assertEqual(len(moving_players), 10)

    def test_get_stationary_players(self):
        """
        Test the get_stationary_players method.
        Ensures that the sum of moving and stationary players equals the total number of remaining players.
        """
        moving_players = self.game.get_moving_players(move_chance=0.5)
        stationary_players = self.game.get_stationary_players(moving_players)
        self.assertEqual(
            len(moving_players) + len(stationary_players),
            len(self.game.get_remaining_players()),
        )

    def test_reset(self):
        """
        Test the reset functionality of the SquidGame.
        Ensures that after resetting, all players return to their initial state.
        """
        self.game.players[0].eliminate(1)
        self.assertEqual(len(self.game.get_remaining_players()), 9)

        self.game.reset()
        self.assertEqual(len(self.game.get_remaining_players()), 10)

        for player in self.game.players:
            self.assertEqual(player.position, 0.0)
            self.assertFalse(player.eliminated)
            self.assertFalse(player.reached_finish)

    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_start_game_invalid_chances(self, mock_sleep):
        """
        Test that start method raises ValueError for invalid move chances.
        """
        with self.assertRaises(ValueError):
            self.game.start(green_move_chance=1.5, red_move_chance=0.1)
        
        with self.assertRaises(ValueError):
            self.game.start(green_move_chance=0.5, red_move_chance=-0.1)

    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_start_game_basic(self, mock_sleep):
        """
        Test the start method of SquidGame with basic parameters.
        """
        remaining_players = self.game.start(
            game_duration=2,
            green_move_chance=0.5,
            red_move_chance=0.1
        )
        
        self.assertTrue(len(remaining_players) <= 10)
        # All remaining players should not be eliminated or finished
        for player in remaining_players:
            self.assertFalse(player.eliminated)
            self.assertFalse(player.reached_finish)

    def test_export_stats(self):
        """
        Test the export_stats method.
        """
        # Eliminate a few players and finish a few others
        self.game.players[0].eliminate(1)
        self.game.players[1].eliminate(2)
        self.game.players[2].reached_finish = True
        self.game.players[2].finish_round = 3
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            self.game.export_stats(tmp_filename)
            
            # Verify the file was created and contains valid JSON
            self.assertTrue(os.path.exists(tmp_filename))
            
            with open(tmp_filename, 'r') as f:
                stats_data = json.load(f)
            
            # Check structure
            self.assertIn('game_config', stats_data)
            self.assertIn('statistics', stats_data)
            self.assertIn('players', stats_data)
            self.assertIn('remaining', stats_data['players'])
            self.assertIn('finished', stats_data['players'])
            self.assertIn('eliminated', stats_data['players'])
            
            # Check specific values
            self.assertEqual(stats_data['game_config']['total_players'], 10)
            self.assertEqual(stats_data['game_config']['light_duration'], 2.0)
            self.assertEqual(len(stats_data['players']['eliminated']), 2)
            self.assertEqual(len(stats_data['players']['finished']), 1)
            self.assertEqual(len(stats_data['players']['remaining']), 7)
            
        finally:
            # Clean up
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)


if __name__ == "__main__":
    unittest.main()