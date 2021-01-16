import random

from events.event_handler import EventHandler
from game_types.round import Round
from game_types.player import Player
from game_types.score_board import ScoreBoard
from utils.point_service import PointService

from mock_data import mock_instructions


class DQGame(EventHandler):
    """
    Main class for a game instance
    """

    def __init__(self):
        self.instructions = mock_instructions  # TODO: Get instructions from API ?
        self.question_pools = []  # TODO: Change to a map
        self.rounds = []
        self.players = []
        self.round_number = 0

        print("Creating a new game")

    def initialize_players(self, players):
        for player in players:
            self.players.append(player)

    def set_game_question_pools(self, question_pools):
        self.question_pools = question_pools

    def get_available_theme_names(self):
        return list(
            map(lambda question_pool: question_pool.theme.name, self.question_pools)
        )

    def set_round_number(self, number):
        self.round_number = number

    def set_rounds(self, themes):
        all_questions = [[], [], []]  # 12 x 3 questions
        for theme in themes:
            for question_pool in self.question_pools:
                if question_pool.theme.name == theme:
                    all_questions[0] += question_pool.questions[0:4]
                    all_questions[1] += question_pool.questions[4:8]
                    all_questions[2] += question_pool.questions[8:12]
        for i in range(3):
            round = Round(i + 1)
            random.shuffle(all_questions[i])
            round.set_questions(all_questions[i])
            self.rounds.append(round)

    def receive_answers(self, player_answers, question, jokers):
        point_service = PointService(self.round_number)

        for player in self.players:
            has_answer, is_correct_answer, answer_order = self.check_answer(
                player, player_answers, question
            )

            points = point_service.calculate_points(
                has_answer, is_correct_answer, answer_order
            )

            player.add_points(points)

            is_double = False

            try:
                is_double = jokers[player.name]["value"] == "DOUBLE"
            except KeyError:
                pass

            if is_double:
                player.double_differential()

    def check_answer(self, player, player_answers, question):

        has_answer = False
        is_correct_answer = False
        answer_order = None
        player_answer = None

        for index, player_answer in enumerate(player_answers):
            if player.name == player_answer.player_name:
                has_answer = True
                is_correct_answer = (
                    player_answer.answer == question.answers[question.correct_answer]
                )
                answer_order = index

        return has_answer, is_correct_answer, answer_order

    def undo_wrong_answer_blocks(self):
        for player in self.players:
            player.blocked_for_wrong_answer = False

    def unblock_players(self):
        for player in self.players:
            player.blocked_by = None

    def consume_jokers(self, played_jokers):
        for player in self.players:
            played_joker_type = None
            try:
                played_joker_type = played_jokers[player.name]["value"]
            except KeyError:
                pass
            player.consume_joker(played_joker_type)

    def get_score_board(self):
        score_board = ScoreBoard()
        for player in self.players:
            score_board.add_score(
                player.name, player.differential, player.points - player.differential
            )
        score_board.sort_board()
        print(score_board.__repr__())
        return score_board

    def get_player_names(self):
        return [player.name for player in self.players]

    def find_player_by_name(self, name):
        for player in self.players:
            if player.name == name:
                return player
        raise RuntimeError("No player with this name")
