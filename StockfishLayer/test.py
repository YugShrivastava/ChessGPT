import chess
import chess.engine

stockfish_path = "/home/yug/Downloads/stockfish-ubuntu-x86-64-avx2/stockfish/stockfish-ubuntu-x86-64-avx2"

engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
engine.configure({"Threads": 1, "Hash": 16, "Skill Level": 20, "UCI_Elo": 2600})

fen="rn1qkbnr/pp3ppp/2p1p3/3p4/3P4/2N1PN2/PPP2PPP/R1BQKB1R w KQkq - 0 1"



board = chess.Board(fen)

info = engine.analyse(board, chess.engine.Limit(time=0.1), multipv=3)


print(info)


engine.quit()