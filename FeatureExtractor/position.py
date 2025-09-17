import chess

# ==============================================================  
# Chess Feature Extractor (Class Version)
# --------------------------------------------------------------  
# This class extracts multiple abstract chess features from a  
# given FEN (Forsyth-Edwards Notation).  
#  
# Usage:
#   extractor = ChessFeatureExtractor(fen)
#   features = extractor.extract_all_features()
# ==============================================================  

# ==============================================================  
# Chess Feature Extractor (with support for comparing prev vs curr FENs)
# ==============================================================  

class ChessFeatureExtractor:
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0
    }

    def __init__(self):
        pass  # we won’t bind a board, everything works off FENs

    # -------------------------------
    # MATERIAL COUNT
    # -------------------------------
    def get_material(self, board):
        white_material = black_material = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                val = self.piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    white_material += val
                else:
                    black_material += val
        return white_material, black_material

    def get_mobility(self, board):
        return len(list(board.legal_moves))

    def get_king_safety(self, board, color):
        king_sq = board.king(color)
        castled = board.has_castling_rights(color) is False
        unsafe = 0
        for sq in chess.SquareSet(chess.BB_KING_ATTACKS[king_sq]):
            if board.is_attacked_by(not color, sq):
                unsafe += 1
        return "Safe" if unsafe <= 2 and castled else "Exposed"

    def get_pawn_structure(self, board, color):
        pawns = board.pieces(chess.PAWN, color)
        files = [chess.square_file(sq) for sq in pawns]

        doubled = sum(files.count(f) > 1 for f in set(files))
        isolated = sum(
            all(abs(f - other) > 1 for other in set(files) if other != f)
            for f in set(files)
        )

        passed = 0
        for sq in pawns:
            rank = chess.square_rank(sq)
            file = chess.square_file(sq)
            blocked = False
            for ahead in range(rank + 1, 8):
                front = chess.square(file, ahead)
                if board.piece_at(front) and board.piece_at(front).color != color:
                    blocked = True
            if not blocked:
                passed += 1

        return {"doubled": doubled, "isolated": isolated, "passed": passed}

    def get_center_control(self, board, color):
        center = [chess.D4, chess.D5, chess.E4, chess.E5]
        return sum(board.is_attacked_by(color, sq) for sq in center)

    def get_development(self, board, color):
        developed = 0
        minors = board.pieces(chess.KNIGHT, color) | board.pieces(chess.BISHOP, color)
        for sq in minors:
            rank = chess.square_rank(sq)
            if (color == chess.WHITE and rank > 0) or (color == chess.BLACK and rank < 7):
                developed += 1
        return developed

    def get_rook_activity(self, board, color):
        rooks = board.pieces(chess.ROOK, color)
        active = 0
        for r in rooks:
            file = chess.square_file(r)
            has_pawn = any(board.piece_at(chess.square(file, rank)) and
                           board.piece_at(chess.square(file, rank)).piece_type == chess.PAWN
                           for rank in range(8))
            if not has_pawn:
                active += 1
        return active

    def get_hanging_pieces(self, board, color):
        hanging = 0
        for sq, piece in board.piece_map().items():
            if piece.color == color:
                if not board.is_attacked_by(color, sq) and board.is_attacked_by(not color, sq):
                    hanging += 1
        return hanging

    def get_piece_activity(self, board, color):
        return sum(1 for move in board.legal_moves if board.color_at(move.from_square) == color)

    def get_piece_coordination(self, board, color):
        defended = 0
        for sq, piece in board.piece_map().items():
            if piece.color == color and board.is_attacked_by(color, sq):
                defended += 1
        return defended

    def get_bishop_pair_bonus(self, board, color):
        return 1 if len(board.pieces(chess.BISHOP, color)) >= 2 else 0

    def get_open_file_control(self, board, color):
        controlled = 0
        for piece_type in [chess.ROOK, chess.QUEEN]:
            for sq in board.pieces(piece_type, color):
                file = chess.square_file(sq)
                pawns_in_file = any(
                    board.piece_at(chess.square(file, rank)) and
                    board.piece_at(chess.square(file, rank)).piece_type == chess.PAWN
                    for rank in range(8)
                )
                if not pawns_in_file:
                    controlled += 1
        return controlled

    def get_space_advantage(self, board, color):
        half_ranks = range(4, 8) if color == chess.WHITE else range(0, 4)
        control = 0
        for rank in half_ranks:
            for file in range(8):
                sq = chess.square(file, rank)
                if board.is_attacked_by(color, sq):
                    control += 1
        return control

    def get_weak_squares(self, board, color):
        weak = 0
        center = [chess.D4, chess.D5, chess.E4, chess.E5]
        for sq in center:
            if not board.is_attacked_by(color, sq) and not board.piece_at(sq):
                weak += 1
        return weak

    def get_outposts(self, board, color):
        outposts = 0
        knights = board.pieces(chess.KNIGHT, color)
        for n in knights:
            for sq in chess.SquareSet(chess.BB_KNIGHT_ATTACKS[n]):
                if not board.is_attacked_by(not color, sq):
                    outposts += 1
        return outposts

    def get_pinned_pieces(self, board, color):
        return sum(1 for sq in board.pieces(chess.PAWN, color) |
                   board.pieces(chess.KNIGHT, color) |
                   board.pieces(chess.BISHOP, color) |
                   board.pieces(chess.ROOK, color) |
                   board.pieces(chess.QUEEN, color)
                   if board.is_pinned(color, sq))

    def get_attacked_vs_defended_balance(self, board, color):
        attacked = defended = 0
        for sq, piece in board.piece_map().items():
            if board.is_attacked_by(not color, sq):
                attacked += 1
            if board.is_attacked_by(color, sq):
                defended += 1
        return {"attacked": attacked, "defended": defended}

    def get_castling_status(self, board, color):
        return board.has_castling_rights(color)

    def get_king_zone_control(self, board, color):
        king_sq = board.king(color)
        zone = chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
        control = sum(board.is_attacked_by(color, sq) for sq in zone)
        return control

    def get_rook_on_7th_rank(self, board, color):
        rank = 6 if color == chess.WHITE else 1
        return sum(1 for sq in board.pieces(chess.ROOK, color) if chess.square_rank(sq) == rank)

    def get_connected_rooks(self, board, color):
        rooks = list(board.pieces(chess.ROOK, color))
        return 1 if len(rooks) == 2 and board.is_attacked_by(color, rooks[0]) and board.is_attacked_by(color, rooks[1]) else 0

    def get_passed_pawn_advancement(self, board, color):
        pawns = board.pieces(chess.PAWN, color)
        advancement = 0
        for sq in pawns:
            if not any(board.piece_at(chess.square(chess.square_file(sq), r)) and
                       board.piece_at(chess.square(chess.square_file(sq), r)).color != color
                       for r in range(chess.square_rank(sq) + 1, 8)):
                advancement += chess.square_rank(sq)
        return advancement

    def get_pawn_shield(self, board, color):
        king_sq = board.king(color)
        rank = chess.square_rank(king_sq)
        file = chess.square_file(king_sq)
        front_rank = rank + 1 if color == chess.WHITE else rank - 1
        files = [file - 1, file, file + 1]
        shield = 0
        for f in files:
            if 0 <= f < 8 and 0 <= front_rank < 8:
                sq = chess.square(f, front_rank)
                piece = board.piece_at(sq)
                if piece and piece.color == color and piece.piece_type == chess.PAWN:
                    shield += 1
        return shield

    def get_backward_pawns(self, board, color):
        pawns = board.pieces(chess.PAWN, color)
        backward = 0
        for p in pawns:
            file = chess.square_file(p)
            rank = chess.square_rank(p)
            supporters = [chess.square(file - 1, rank - 1), chess.square(file + 1, rank - 1)]
            if color == chess.BLACK:
                supporters = [chess.square(file - 1, rank + 1), chess.square(file + 1, rank + 1)]
            if all((s < 0 or s >= 64 or not board.piece_at(s) or board.piece_at(s).piece_type != chess.PAWN) for s in supporters):
                backward += 1
        return backward

    def get_isolated_weakness_clusters(self, board, color):
        pawns = list(board.pieces(chess.PAWN, color))
        files = [chess.square_file(p) for p in pawns]
        clusters = 0
        for f in set(files):
            if all(abs(f - other) > 1 for other in set(files) if other != f):
                clusters += 1
        return clusters

    # -------------------------------
    # COLLECT ALL FEATURES
    # -------------------------------
    def _extract_all_features(self, board):
        white_material, black_material = self.get_material(board)
        return {
            "material": {"white": white_material, "black": black_material},
            "mobility": self.get_mobility(board),
            "king_safety": {"white": self.get_king_safety(board, chess.WHITE), "black": self.get_king_safety(board, chess.BLACK)},
            "pawn_structure": {"white": self.get_pawn_structure(board, chess.WHITE), "black": self.get_pawn_structure(board, chess.BLACK)},
            "center_control": {"white": self.get_center_control(board, chess.WHITE), "black": self.get_center_control(board, chess.BLACK)},
            "development": {"white": self.get_development(board, chess.WHITE), "black": self.get_development(board, chess.BLACK)},
            "rook_activity": {"white": self.get_rook_activity(board, chess.WHITE), "black": self.get_rook_activity(board, chess.BLACK)},
            "threats": {"white": self.get_hanging_pieces(board, chess.WHITE), "black": self.get_hanging_pieces(board, chess.BLACK)},
            "piece_activity": {"white": self.get_piece_activity(board, chess.WHITE), "black": self.get_piece_activity(board, chess.BLACK)},
            "piece_coordination": {"white": self.get_piece_coordination(board, chess.WHITE), "black": self.get_piece_coordination(board, chess.BLACK)},
            "bishop_pair_bonus": {"white": self.get_bishop_pair_bonus(board, chess.WHITE), "black": self.get_bishop_pair_bonus(board, chess.BLACK)},
            "open_file_control": {"white": self.get_open_file_control(board, chess.WHITE), "black": self.get_open_file_control(board, chess.BLACK)},
            "space_advantage": {"white": self.get_space_advantage(board, chess.WHITE), "black": self.get_space_advantage(board, chess.BLACK)},
            "weak_squares": {"white": self.get_weak_squares(board, chess.WHITE), "black": self.get_weak_squares(board, chess.BLACK)},
            "outposts": {"white": self.get_outposts(board, chess.WHITE), "black": self.get_outposts(board, chess.BLACK)},
            "pinned_pieces": {"white": self.get_pinned_pieces(board, chess.WHITE), "black": self.get_pinned_pieces(board, chess.BLACK)},
            "attacked_vs_defended": {"white": self.get_attacked_vs_defended_balance(board, chess.WHITE), "black": self.get_attacked_vs_defended_balance(board, chess.BLACK)},
            "castling_status": {"white": self.get_castling_status(board, chess.WHITE), "black": self.get_castling_status(board, chess.BLACK)},
            "king_zone_control": {"white": self.get_king_zone_control(board, chess.WHITE), "black": self.get_king_zone_control(board, chess.BLACK)},
            "rook_on_7th_rank": {"white": self.get_rook_on_7th_rank(board, chess.WHITE), "black": self.get_rook_on_7th_rank(board, chess.BLACK)},
            "connected_rooks": {"white": self.get_connected_rooks(board, chess.WHITE), "black": self.get_connected_rooks(board, chess.BLACK)},
            "passed_pawn_advancement": {"white": self.get_passed_pawn_advancement(board, chess.WHITE), "black": self.get_passed_pawn_advancement(board, chess.BLACK)},
            "pawn_shield": {"white": self.get_pawn_shield(board, chess.WHITE), "black": self.get_pawn_shield(board, chess.BLACK)},
            "backward_pawns": {"white": self.get_backward_pawns(board, chess.WHITE), "black": self.get_backward_pawns(board, chess.BLACK)},
            "isolated_weakness_clusters": {"white": self.get_isolated_weakness_clusters(board, chess.WHITE), "black": self.get_isolated_weakness_clusters(board, chess.BLACK)}
        }

    def compare_features(self, f1, f2):
        diff = {}
        for key in f2:
            if key not in f1:
                diff[key] = f2[key]
                continue
            val1 = f1[key]
            val2 = f2[key]
            if isinstance(val2, dict):
                sub_diff = self.compare_features(val1, val2)
                if sub_diff:
                    diff[key] = sub_diff
            else:
                if val1 != val2:
                    diff[key] = val2
        return diff

    def extract_features(self, curr, prev=None):
        board2 = chess.Board(curr)
        features2 = self._extract_all_features(board2)

        if prev:
            board1 = chess.Board(prev)
            features1 = self._extract_all_features(board1)
            differences = self.compare_features(features1, features2)
            return differences
        else:
            return features2


# ==============================================================  
# Example Usage  
# ==============================================================  
if __name__ == "__main__":
    # prev_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
    prev_fen = None
    curr_fen = "rnbqkbnr/pppppppp/8/8/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 1"

    extractor = ChessFeatureExtractor()

    f2 = extractor.extract_features(curr=curr_fen, prev=prev_fen)
    for k, v in f2.items():
        print(f"- {k}: {v}")














# There are many functions, each extracting a specific chess feature, such as:

# Material: Counts the total value of pieces for each side.
# Mobility: Number of legal moves.
# King Safety: Evaluates if the king is safe or exposed.
# Pawn Structure: Finds doubled, isolated, and passed pawns.
# Center Control: How many central squares are controlled.
# Development: Number of developed minor pieces.
# Rook Activity: Rooks on open files.
# Threats: Hanging (undefended and attacked) pieces.
# Piece Activity: Number of legal moves for each color.
# Piece Coordination: Number of defended pieces.
# Bishop Pair Bonus: Checks if both bishops are present.
# Open File Control: Rooks/queens on open files.
# Space Advantage: Controlled squares in opponent's half.
# Weak Squares: Central squares not controlled.
# Outposts: Safe squares for knights in enemy territory.
# Pinned Pieces: Number of pinned pieces.
# Attacked vs Defended: Balance of attacked and defended squares.
# Castling Status: Whether castling rights are available.
# King Zone Control: Controlled squares around the king.
# Rook on 7th Rank: Rooks on the 7th rank.
# Connected Rooks: If rooks support each other.
# Passed Pawn Advancement: How far passed pawns have advanced.
# Pawn Shield: Pawns protecting the king.
# Backward Pawns: Pawns with no support from behind.
# Isolated Weakness Clusters: Groups of isolated pawns.