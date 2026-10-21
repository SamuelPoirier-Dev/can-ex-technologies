from app.game.board import DEFAULT_BOARD


def test_first_square_is_start_and_not_a_property() -> None:
    assert DEFAULT_BOARD[0].name == "Départ"
    assert not DEFAULT_BOARD[0].is_property


def test_properties_have_positive_price_and_rent() -> None:
    properties = [s for s in DEFAULT_BOARD.squares if s.is_property]

    assert properties
    for square in properties:
        assert square.price is not None and square.price > 0
        assert square.rent is not None and square.rent > 0


def test_board_mixes_properties_and_empty_squares() -> None:
    assert any(not s.is_property for s in DEFAULT_BOARD.squares[1:])
