from FeatureExtractor.position import ChessFeatureExtractor
from TacticalLayer.tactic import TacticalAnalyzer

def get_analysis(fen_before: str, fen_after):
    tactical_analyzer = TacticalAnalyzer()
    analysis = tactical_analyzer.analysis(fen_before, fen_after, 1.0, 1)
    if not analysis.get("tactic"):
        extractor = ChessFeatureExtractor()
        analysis = extractor.extract_features(fen_after)

    return analysis