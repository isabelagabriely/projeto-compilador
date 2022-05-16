import Lexer
import Parser

def main():
    lexicalAnalyzer = Lexer.Lexer()
    symbols_table = lexicalAnalyzer.tokenize()
    parser = Parser.Parser(symbols_table)
    parser.simpleProgram()



if __name__ == '__main__':
    main()