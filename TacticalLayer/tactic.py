# tactical_analyzer_fixed.py
import logging
from typing import List, Dict, Any, Optional

import chess
import chess.engine
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from StockfishLayer.stockfish import Stockfish
from FeatureExtractor.position import ChessFeatureExtractor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def cp_from_score(score_obj, perspective="white"):
    """
    Convert Stockfish score object into a centipawn (cp) integer.
    
    Handles:
      - {"cp": value}
      - {"mate": N}
      - {"white": cp, "black": cp}
      - direct int/float
    perspective: "white" or "black" → ensures scores are always from that side’s POV
    """
    if isinstance(score_obj, dict):
        # Case 1: Stockfish style { "cp": value }
        if "cp" in score_obj:
            return int(score_obj["cp"])

        # Case 2: Mate scores { "mate": N }
        if "mate" in score_obj:
            return 100000 if score_obj["mate"] > 0 else -100000

        # Case 3: Custom wrapper { "white": cp, "black": cp }
        if "white" in score_obj and "black" in score_obj:
            return int(score_obj[perspective])

    # Case 4: Already a number
    if isinstance(score_obj, (int, float)):
        return int(score_obj)

    raise ValueError(f"Unsupported score_obj format: {score_obj}")



class TacticalAnalyzer:
    def __init__(self, engine_path: Optional[str] = None, threads=1, hash_size=16, skill_level=20):
        self.stockfish = Stockfish(threads=threads, hash_size=hash_size, skill_level=skill_level)
        self.feature_extractor = ChessFeatureExtractor()
        # tune these thresholds per your design
        self.T_INACCURACY = 50
        self.T_MISTAKE = 100
        self.T_BLUNDER = 200
        self.T_MISS = 150

    def _safe_analyze(self, fen: str, time_limit: float = 0.1, multipv: int = 1) -> List[Dict[str, Any]]:
        """
        Call engine analyze; return list of analysis entries (normalized).
        Each entry is a dict with keys: 'score' (raw), 'pv' (uci list).
        We normalize to always return a list.
        """
        try:
            raw = self.stockfish.analyze(fen, time_limit=time_limit, multipv=multipv)
            if isinstance(raw, list):
                return raw
            return [raw]
        except Exception:
            logger.exception("Engine analysis failed for FEN: %s", fen)
            return []

    def detect_basic_motifs(self, board: chess.Board, move: chess.Move) -> List[str]:
        """
        Very small motif detectors that rely on python-chess board after move.
        Returns list of motif tags such as 'hanging_piece', 'fork', 'pin', 'discovered_attack', 'back_rank'.
        """
        motifs = []
        # apply move
        board.push(move)

        # hanging_piece: any moved side piece that is attacked more than defended
        to_sq = move.to_square
        mover = not board.turn  # because we pushed
        attackers = board.attackers(not mover, to_sq)
        defenders = board.attackers(mover, to_sq)
        if attackers and len(attackers) > len(defenders):
            motifs.append("hanging_piece")

        # fork: moved piece attacks >=2 valuable targets
        attacked_targets = 0
        for sq in chess.SQUARES:
            p = board.piece_at(sq)
            if p and p.color != mover and p.piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT):
                if board.is_attacked_by(mover, sq):
                    attacked_targets += 1
        if attacked_targets >= 2:
            motifs.append("fork")

        # pin: check if any opponent piece is pinned to their king
        # python-chess provides board.is_pinned(color, square)
        for sq in chess.SQUARES:
            p = board.piece_at(sq)
            if p and p.color == mover and board.is_pinned(mover, sq):
                motifs.append("pin")
                break

        # discovered attack / check: compare attack maps naive approach
        # (more robust logic can be added later)
        # back-rank: check opponent king escape squares and heavy piece on back rank
        # We'll do a simple heuristic:
        king_sq = board.king(not mover)
        # if king on back rank and its flight squares are blocked -> potential back rank issue
        if king_sq is not None:
            rank = chess.square_rank(king_sq)
            if rank in (0, 7):
                # check flight squares around king
                flights = 0
                for d in board.attacks(king_sq):
                    p = board.piece_at(d)
                    if p is None:
                        flights += 1
                if flights == 0:
                    motifs.append("back_rank")

        board.pop()
        return list(dict.fromkeys(motifs))  # unique preserve order

    def classify_delta(self, delta_cp: int, eval_best_gap: Optional[int] = None, eval_after_vs_before: Optional[int] = None) -> str:
        """
        Classify the move using deltas in centipawns.
        delta_cp = eval_after_cp - eval_before_cp from mover perspective (negative means worse).
        eval_best_gap = eval_best_cp - eval_after_cp (positive means engine best is better than played).
        """
        # Miss detection (opportunity missed)
        if eval_best_gap is not None and eval_best_gap >= self.T_MISS and (eval_after_vs_before is None or eval_after_vs_before >= -self.T_INACCURACY):
            return "miss"
        if delta_cp <= -self.T_BLUNDER:
            return "blunder"
        if delta_cp <= -self.T_MISTAKE:
            return "mistake"
        if delta_cp <= -self.T_INACCURACY:
            return "inaccuracy"
        if delta_cp >= -10 and delta_cp <= 10:
            return "good"
        return "good"

    def analyze(self, fen_before: str, fen_after: str, time_limit: float = 0.1, multipv: int = 1) -> Dict[str, Any]:
        """
        Main entry: analyze a user move from fen_before -> fen_after.
        Returns structured tactical-layer output (see spec).
        """
        board_before = chess.Board(fen_before)
        mover = "white" if board_before.turn else "black"

        # 1) get engine results (normalized lists)
        before_list = self._safe_analyze(fen_before, time_limit=time_limit, multipv=1)
        after_list = self._safe_analyze(fen_after, time_limit=time_limit, multipv=multipv)

        if not before_list or not after_list:
            return {
                "fen_before": fen_before,
                "fen_after": fen_after,
                "error": "engine analysis failed or returned empty",
                "confidence": 0.0
            }

        # For primary score use the first entry
        score_before_cp = cp_from_score(before_list[0].get("score", 0))
        score_after_cp = cp_from_score(after_list[0].get("score", 0))

        # get engine best after-play score (if provided in after_list)
        score_best_cp = score_after_cp
        if len(after_list) > 0 and "pv" in after_list[0]:
            # assume first multipv is top move
            # score_after already corresponds to top move; keep that
            pass

        # compute delta from mover perspective
        # eval values are always "white perspective": positive means white better
        if mover == "white":
            delta_mover = score_after_cp - score_before_cp
        else:
            delta_mover = (score_before_cp - score_after_cp)  # improvement for black is negative in white-perspective

        # if candidate_pvs available compute eval_best_gap convenience
        eval_best_gap = None
        if "pv" in after_list[0] and len(after_list) >= 1:
            # if `after_list` multipv>1, then after_list[0] is best, after_list[1] second etc.
            if len(after_list) > 1:
                # assume after_list[0] best, after_list[1] second
                best_cp = cp_from_score(after_list[0].get("score", 0))
                played_cp = cp_from_score(after_list[0].get("score", 0))  # in this call played is the same; but in general wrap later
                eval_best_gap = best_cp - played_cp  # for post-game when we compare actual played vs best, you should fill properly
            else:
                eval_best_gap = 0

        # To detect motifs we need the actual move object: infer by comparing fen_before -> fen_after
        move_uci = None
        try:
            b = chess.Board(fen_before)
            # get the move that transitions to fen_after by iterating legal moves
            found_move = None
            for mv in b.legal_moves:
                b.push(mv)
                if b.fen().split(" ")[0] == fen_after.split(" ")[0]:
                    found_move = mv
                    b.pop()
                    break
                b.pop()
            if found_move is None:
                logger.warning("Could not infer move from fen_before -> fen_after; please pass user_move_uci explicitly")
                # fallback: leave motifs empty
            else:
                move_uci = found_move.uci()
        except Exception:
            logger.exception("Failed to infer move from FENs")
            found_move = None

        motifs = []
        if found_move:
            board = chess.Board(fen_before)
            motifs = self.detect_basic_motifs(board, found_move)

        classification = self.classify_delta(delta_mover, eval_best_gap=eval_best_gap, eval_after_vs_before=(score_after_cp - score_before_cp))

        out = {
            "move_uci": found_move.uci() if found_move else None,
            "move_san": board.san(found_move) if found_move else None,
            "fen_before": fen_before,
            "fen_after": fen_after,
            "player_color": mover,
            "eval_before_cp": score_before_cp,
            "eval_after_cp": score_after_cp,
            "eval_delta_cp": int(delta_mover),
            "classification": classification,
            "motifs": motifs,
            "evidence": f"eval_before={score_before_cp}, eval_after={score_after_cp}",
            "confidence": 0.9
        }
        return out
    
    def quit(self):
        try:
            self.stockfish.quit()
        except Exception:
            pass


if __name__ == "__main__":
    ta = TacticalAnalyzer()
    res = ta.analyze(
        fen_before="2k3rr/pbp2p2/1p1qpp2/1N1p4/7p/PP2PB2/2PPQ1PP/R4RK1 b - - 3 18",
        fen_after="2k3rr/pbp2p2/1pq1pp2/1N1p4/7p/PP2PB2/2PPQ1PP/R4RK1 w - - 4 19",
        time_limit=0.5,
        multipv=2
    )
    print(res)
    ta.quit()
