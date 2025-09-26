import sys
import os

# Go one directory up from TacticalLayer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from StockfishLayer.stockfish import Stockfish
from FeatureExtractor.position import ChessFeatureExtractor

class TacticalAnalyzer():
    def __init__(self):
        self.stockfish = Stockfish(threads=1, hash_size=16, skill_level=20, uci_elo=2600)
        self.feature_extractor = ChessFeatureExtractor()
        self.analysis = []

    def analyze(self, fen, time_limit=0.1, multipv=1, depth=12):
        analysis = self.stockfish.analyze(fen, time_limit=time_limit, multipv=multipv, depth=depth)

        for pv in analysis:
            positional_analysis_after_n_moves = self.feature_extractor.extract_features(pv["final_fen"], fen)
            self.analysis.append(analysis)
            self.analysis.append(positional_analysis_after_n_moves)

    def get_analysis(self):
        return self.analysis

    def quit(self):
        self.stockfish.quit()   


if __name__ == "__main__":
    tactical_analyzer = TacticalAnalyzer()
    out = tactical_analyzer.analyze("r2q1rk1/pp2ppbp/1np2np1/2Q5/3PPBb1/2N2N2/PP3PPP/3RKB1R w K - 5 11", 0.1, 1)
    print(tactical_analyzer.get_analysis())
    tactical_analyzer.quit()