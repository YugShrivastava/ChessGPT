from FeatureExtractor.position import ChessFeatureExtractor
from TacticalLayer.tactic import TacticalAnalyzer
from dotenv import load_dotenv

load_dotenv()


def get_analysis(fen: str):
    tactical_analyzer = TacticalAnalyzer()
    tactical_analyzer.analyze(fen, time_limit=1.0, multipv=1)
    analysis = tactical_analyzer.get_analysis()[0]

    tactical_analyzer.quit()

    return analysis

if __name__ == "__main__":
    print(get_analysis("r2qk2r/1p2bppp/p1n1p1n1/2PpP3/BP6/5N1P/P1P2PP1/R1BQK2R w KQkq - 1 12"))