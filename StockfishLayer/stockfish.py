import chess
import chess.engine
import os
from dotenv import load_dotenv

load_dotenv()

class Stockfish:
    def __init__(self, threads=1, hash_size=16, skill_level=20, uci_elo=2600):
        self.engine = chess.engine.SimpleEngine.popen_uci(os.getenv("STOCKFISH_PATH"))
        self.engine.configure({
            "Threads": threads,
            "Hash": hash_size,
            "Skill Level": skill_level,
            "UCI_Elo": uci_elo
        })
        self.analysis = []

    def _moves_to_san(self, board, moves):
        san_moves = []
        temp_board = board.copy()
        for move in moves:
            try:
                san_moves.append(temp_board.san(move))
                temp_board.push(move)
            except Exception as e:
                san_moves.append(str(move))
                break
        return san_moves

    def _format_score(self, score_obj):
        if score_obj.is_mate():
            mate = score_obj.mate()
            return f"# {mate}" if mate > 0 else f"# -{abs(mate)}"
        else:
            return score_obj.score()

    # def _format_score(self, score_obj):
    #     if score_obj.is_mate():
    #         mate = score_obj.mate()
    #         return 100000 if mate > 0 else -100000
    #     else:
    #         return score_obj.score()


    def analyze(self, fen, time_limit=0.1, multipv=1):
        board = chess.Board(fen)
        info = self.engine.analyse(board, chess.engine.Limit(time=time_limit), multipv=multipv)
        analysis = []
    
        for entry in info:
            score_obj_white = entry["score"].white()
            score_obj_black = entry["score"].black()
        
            score_white = self._format_score(score_obj_white)
            score_black = self._format_score(score_obj_black)

            pv = entry.get("pv", [])

            pv_board = board.copy()
            for move in pv:
                pv_board.push(move)
            final_fen = pv_board.fen()

            analysis.append({
                "score": {
                    "white": score_white,
                    "black": score_black
                },
                "pv_san": self._moves_to_san(board, pv),
                "final_fen": final_fen
            })

        self.analysis = analysis
        return analysis

    def get_analysis(self):
        return self.analysis


    def quit(self):
        self.engine.quit()


if __name__ == "__main__":
    stockfish = Stockfish(threads=2, hash_size=16, skill_level=15, uci_elo=1320)

    fen = "r2q1rk1/pp2ppbp/1np2np1/2Q3B1/3PP1b1/2N2N2/PP3PPP/3RKB1R b K - 6 11"
    out = stockfish.analyze(fen, time_limit=0.1, multipv=1)
    print(out)
    stockfish.quit()