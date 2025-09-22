import sys
import os

# Go one directory up from TacticalLayer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from StockfishLayer.stockfish import Stockfish
from FeatureExtractor.position import ChessFeatureExtractor

class TacticalAnalyzer():
    def __init__(self):
        self.stockfish = Stockfish(threads=1, hash_size=16, skill_level=20, uci_elo=2600)
        self.analysis_before = []
        self.analysis_after = []
        self.analysis_after_n_moves = []
        self.positional_analysis_after_n_moves = []
        self.feature_extractor = ChessFeatureExtractor()
        self.analysis = []
    
    def analyze(self, fen_before, fen_after, time_limit=0.1, multipv=1):
        self.analysis_before = self.stockfish.analyze(fen_before, time_limit=time_limit, multipv=multipv)
        self.analysis_after = self.stockfish.analyze(fen_after, time_limit=time_limit, multipv=multipv)

        if(self.analysis_after[0]["score"]["white"] - self.analysis_before[0]["score"]["white"] >= 10):
            self.analysis_after_n_moves = self.stockfish.analyze(self.analysis_after[0]["final_fen"], time_limit=time_limit, multipv=multipv)
            self.positional_analysis_after_n_moves = [self.feature_extractor.extract_features(curr=fen_after, prev=x['final_fen']) for x in self.analysis_after]

            for analysis in self.analysis_after_n_moves:
                analysis["tactic"] = {}
                analysis["tactic"]["positional_features"] = self.feature_extractor.extract_features(curr=fen_after, prev=analysis['final_fen'])
                analysis["tactic"]["is_tactic"] = True
            
            self.analysis = self.analysis_after_n_moves

        else:
            self.analysis = self.analysis_after
            self.analysis["tactic"] = {}

    def get_analysis(self):
        return self.analysis

    def quit(self):
        self.stockfish.quit()   


if __name__ == "__main__":
    tactical_analyzer = TacticalAnalyzer()
    tactical_analyzer.analyze("r1b1k2r/ppp2ppp/2nqpn2/3pN3/3P1P2/3B4/PPPN1PPP/R2QK2R w KQkq - 0 1", "r1b1k2r/ppp2ppp/2n1pn2/3pq3/3P1P2/3B4/PPPN1PPP/R2QK2R w KQkq - 0 1", 1.0, 1)
    print(tactical_analyzer.get_analysis())

    tactical_analyzer.quit()