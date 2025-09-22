from FeatureExtractor.position import ChessFeatureExtractor
from TacticalLayer.tactic import TacticalAnalyzer
from dotenv import load_dotenv

load_dotenv()


def get_analysis(fen_before: str, fen_after):
    tactical_analyzer = TacticalAnalyzer()
    tactical_analyzer.analyze(fen_before, fen_after, time_limit=1.0, multipv=1)
    analysis = tactical_analyzer.get_analysis()[0]

    if analysis["tactic"]:
        extractor = ChessFeatureExtractor()
        analysis["postional_features"] = {}
        analysis["positional_features"] = extractor.extract_features(fen_after)

    tactical_analyzer.quit()

    return analysis

if __name__ == "__main__":
    print(get_analysis("r2qk2r/1p2bppp/p1n1p1n1/2PpP3/BP6/5N1P/P1P2PP1/R1BQK2R w KQkq - 1 12", "r2qk2r/4bppp/ppn1p1n1/2PpP3/BP6/P4N1P/2P2PP1/R1BQK2R w KQkq - 0 13"))