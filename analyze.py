from FeatureExtractor.position import ChessFeatureExtractor
from TacticalLayer.tactic import TacticalAnalyzer
from dotenv import load_dotenv

load_dotenv()


def get_analysis(fen_before: str, fen_after):
    tactical_analyzer = TacticalAnalyzer()
    analysis=tactical_analyzer.analyze(fen_before, fen_after, time_limit=1.0, multipv=1)
    # analysis = tactical_analyzer.get_analysis()[0]

    extractor = ChessFeatureExtractor()
    analysis["postional_features"] = {}
    analysis["positional_features"] = extractor.extract_features(fen_after)

    tactical_analyzer.quit()

    return analysis

if __name__ == "__main__":
    print(get_analysis("r5k1/1p3pp1/2pBpb1p/2P4P/1q1P4/2nQ4/P2R1PP1/R5K1 b - - 11 33","r5k1/1p3pp1/2pBpb1p/2P4P/1q1Pn3/3Q4/P2R1PP1/R5K1 w - - 12 34"))