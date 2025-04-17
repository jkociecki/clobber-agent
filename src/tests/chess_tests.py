import copy
import pytest
from chess.chess_state import Chess


def get_number_of_possible_positions(fen_start: str, depth: int) -> int:
    chess = Chess(fen_start)

    def inner(state, depth):
        if depth == 0:
            return 1

        num_pos = 0
        moves = state.get_legal_moves()

        for move in moves:
            new_state = copy.deepcopy(state)
            new_state.make_move(move)
            num_pos += inner(new_state, depth - 1)

        return num_pos

    return inner(chess, depth)


@pytest.mark.parametrize('depth, expected', [
    (1, 20),
    (2, 400),
    (3, 8902),
    (4, 197281)
])
def test_start_position(depth, expected):
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    assert get_number_of_possible_positions(fen, depth) == expected


@pytest.mark.parametrize("depth, expected", [
    (1, 48),
    (2, 2039),
    (3, 97862),
    (4, 4085603)
])
def test_kiwipete_positions(depth, expected):
    fen = 'r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -'
    assert get_number_of_possible_positions(fen, depth) == expected


@pytest.mark.parametrize("depth, expected", [
    (1, 14),
    (2, 191),
    (3, 2812),
    (4, 43238),
    (5, 674624)
])
def test_pos3_positions(depth, expected):
    fen = '8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1'
    assert get_number_of_possible_positions(fen, depth) == expected


@pytest.mark.parametrize("depth, expected", [
    (1, 6),
    (2, 264),
    (3, 9467),
    (4, 422333)
])
def test_pos4_positions(depth, expected):
    fen = 'r2q1rk1/pP1p2pp/Q4n2/bbp1p3/Np6/1B3NBn/pPPP1PPP/R3K2R b KQ - 0 1'
    assert get_number_of_possible_positions(fen, depth) == expected


@pytest.mark.parametrize("depth, expected", [
    (1, 44),
    (2, 1486),
    (3, 62379),
    (4, 2103487)
])
def test_talkchess_positions(depth, expected):
    fen = 'rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8'
    assert get_number_of_possible_positions(fen, depth) == expected


@pytest.mark.parametrize("depth, expected", [
    (1, 46),
    (2, 2079),
    (3, 89890),
    (4, 3894594)
])
def test_steven_edwards_positions(depth, expected):
    fen = 'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10'
    assert get_number_of_possible_positions(fen, depth) == expected