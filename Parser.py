class Parser:
    """ Analisador Sintático
    """
    def __init__(self, symbols_table):
        self.SYMBOLS_TABLE = symbols_table
        self.TOKENS = [token for token in symbols_table if token != ("NEWLINE", "\\n")] # CRIAR UMA CÓPIA DA TABELA DE TOKENS
        self.TOKEN = 0

    #VERIFICA SE O TOKEN COMBINA COM O ESPERADO SE NÃO GERA UM ERRO
    def match(self, token):
        if self.lookahead(1) == token:
            self.TOKEN += 1
        else:
            self.syntaticError(token)
    
    
    #RETORNA O TOKEN EM K NA TABELA DE TOKENS
    def lookahead(self, k):
        k = k + self.TOKEN
        if (self.TOKEN == len(self.TOKENS)):
            return None
        
        if ((k-1) >= len(self.TOKENS)):
            return self.TOKENS[len(self.TOKENS)][0]
        
        return self.TOKENS[k - 1][0]
    
    # RETORNA A LINHA DO TOKEN ATUAL
    def getLine(self):
        return (self.SYMBOLS_TABLE[:self.TOKEN].count(('NEWLINE', '\\n')))+1

    def syntaticError(self, expectedTokens):
        msg = f'syntatic error exception, expected one of the following "{", ".join(expectedTokens) if isinstance(expectedTokens, list) else expectedTokens}".\nBut found {self.TOKENS[self.TOKEN][1]} on line {self.getLine()}'
        raise SyntaxError(msg)
    
    
    #DEFINICAO DE UM TIPO PARA FUNCOES
    def type(self):
        if self.lookahead(1) == 'VOID':
            self.match('VOID')
        elif self.lookahead(1) == 'INT':
            self.match('INT')
        elif self.lookahead(1) == 'FLOAT':
            self.match('FLOAT')
        elif self.lookahead(1) == "CHAR":
            self.match('CHAR')
        else:
            self.syntaticError(['void', 'int', 'float', 'char/string'])
    
    #DEFINICAO DE UM TIPO PARA VARIAVEIS COMUNS
    def varType(self):
        if self.lookahead(1) == 'INT':
            self.match('INT')
        elif self.lookahead(1) == 'FLOAT':
            self.match('FLOAT')
        elif self.lookahead(1) == 'CHAR':
            self.match('CHAR')
        else:
            self.syntaticError(['int', 'float', 'char/string'])


    #DEFINICAO PARA UMA LISTA DE ARGUMENTOS
    def listArgs(self):
        self.declaration()

        if self.lookahead(1) == 'RPAREN':
            self.match('RPAREN')
        elif self.lookahead(1) == 'COMMA':
            self.match('COMMA')
            self.listArgs()

            
    #REGRA PARA UMA LISTA DE VARIAVEIS
    def declarationList(self):
        if (self.lookahead(1) == 'ID'):
            self.onlyAttribuition()
        else:
            self.declaration()
        if self.lookahead(1) == 'COMMA':
            self.match('COMMA')
            self.idList()
        
        self.match('SEMCOL')

    #LISTA DE VARIAVEIS EX: x, y, z;   
    def idList(self):
        if self.lookahead(1) == 'MEMADRESS':
            self.match('MEMADRESS')
            self.match('ID')
        else:
            self.match('ID')
            if self.lookahead(1) == 'ATTR':
                self.attribuition()
            
            if self.lookahead(1) == 'LBRACKET':
                self.listDeclaration()
            
        if self.lookahead(1) == 'COMMA':
            self.match('COMMA')
            self.idList()


    #DECLARACAO/ATRIBUICAO DE UMA VARIAVEL: int x; | int x = EXPRESSÃO | int x[];..
    def onlyAttribuition(self):
        self.match('ID')
        if self.lookahead(1) == 'LBRACKET':
            self.match('LBRACKET')
            self.expression()
            self.match('RBRACKET')
        self.attribuition()

    def declaration(self):
        self.varType()
        self.match('ID')

        if self.lookahead(1) == 'ATTR':
            self.attribuition()
        elif self.lookahead(1) == 'LBRACKET':
            self.listDeclaration()

    def listDeclaration(self):
        self.match('LBRACKET')

        if self.lookahead(1) != 'RBRACKET':
            self.expression()

        self.match('RBRACKET')

        if self.lookahead(1) == 'ATTR':
            self.listAttr() 
      
    def listAttr(self):
        self.match('ATTR')
        if self.lookahead(1) == 'CHAR_CONST':
          self.match('CHAR_CONST')
        else:
            self.match('LBRACE')
            self.valuesList()
            self.match('RBRACE')

    def valuesList(self):
        self.expression()
        if self.lookahead(1) == 'COMMA':
            self.match('COMMA')
            self.valuesList()

    #REGRA PARA CASO DE ATRIBUIÇÃO DE UMA VARIAVEL: variavel = EXPRESSÃO(10, 10 + 10, y + 10, y + z, ...)
    def attribuition(self):
        self.match('ATTR')
        if self.lookahead(1) == 'SEMCOL':
            self.syntaticError(['Expression'])
        self.expression()

    #REGRAS PARA EXPRESSÕES
    def expression(self):
        self.artTerm()
        self.nextExpression()
    
    
    def nextExpression(self):
        if self.lookahead(1) == 'PLUS' or self.lookahead(1) == 'MINUS':
            self.nextExpressionRule()
            if self.lookahead(1) == 'SEMCOL':
                return
            self.artTerm()

    
    def nextExpressionRule(self):
        if self.lookahead(1) == 'PLUS':
            self.match('PLUS')
            self.artTerm()
        elif self.lookahead(1) == 'MINUS':
            self.match('MINUS')
            self.artTerm()
        else:
            self.syntaticError(['+', '-'])

    
    def artTerm(self):
        if self.lookahead(1) == 'SEMCOL' or self.lookahead(1) == 'RPAREN' or self.lookahead(1) == 'RBRANCE':
            self.syntaticError(['Integer', 'Variable', 'Float', 'Char/String', 'or ('])
        self.operate()
        self.nextArtTerm()
    
    
    def nextArtTerm(self):
        if self.lookahead(1) == 'MULT' or self.lookahead(1) == 'DEV':
            self.artTermRule()
            self.nextArtTerm()

    
    def artTermRule(self):
        if self.lookahead(1) == 'MULT':
            self.match('MULT')
            self.operate()
        elif self.lookahead(1) == 'DEV':
            self.match('DEV')
            self.operate()
        elif self.lookahead(1) == 'PERCENT':
            self.match('PERCENT')
            self.operate()
        else:
            self.syntaticError(['*', '/', '%'])

    
    def operate(self):
        if self.lookahead(1) == 'INT_CONST':
            self.match('INT_CONST')
        elif self.lookahead(1) == 'CHAR_CONST':
            self.match('CHAR_ CONST')
        elif self.lookahead(1) == 'FLOAT_CONST':
            self.match('FLOAT_CONST')
        elif self.lookahead(1) == 'ID':
            self.match('ID')
        elif self.lookahead(1) == 'MEMADRESS':
            self.match('MEMADRESS')
            self.match('ID')
        elif self.lookahead(1) == 'LPAREN':
            self.match('LPAREN')
            self.expression()
            self.match('RPAREN')
        elif self.lookahead(1) == 'SEMCOL' or self.lookahead(1) == 'RPAREN' or self.lookahead(1) == 'RBRACKET' or self.lookahead(1) == 'RBRACE':
            return
        else:
            self.syntaticError(['Integer', 'Variable', 'Float', 'Char/String', 'or ('])
    
    
    # Regras para expressões relacionais 10 > 5...
    def relExpression(self):
        self.relTerm()
        self.relExp()
    
    
    def relExp(self):
        if self.lookahead(1) == "AND" or self.lookahead(1) == "OR":
            self.booleanOperator()
            self.relTerm()
            self.relExp()

    
    def relTerm(self):
        term = self.lookahead(1)
        if term == 'INT' or term == 'FLOAT' or term == 'STRING' or term == 'ID' or term == 'LPAREN':
            self.expression()
            self.opRel()
            self.expression()
        else:
            self.syntaticError(['int', 'variable', 'float', 'string', '('])
    
    
    def opRel(self):
        op = self.lookahead(1)
        if op == 'EQ':
            self.match('EQ')
        elif op == 'NE':
            self.match('NE')
        elif op == 'LE':
            self.match('LE')
        elif op == 'GE':
            self.match('GE')
        elif op == 'LT':
            self.match('LT')
        elif op == 'GT':
            self.match('GT')
        else:
            self.syntaticError(['==', '!=', '<=', '>=', '<', '>'])
    
    
    def booleanOperator(self):
        if self.lookahead(1) == 'AND':
            self.match('AND')
        elif self.lookahead(1) == 'OR':
            self.match('OR')
        else:
            self.syntaticError(['&&', '||'])
    
    
    #REGRAS PARA INSTRUÇÕES, LIMITADAS A IF,ELSE; printf; scanf;
    def instructions(self):
        self.instruction()
        self.instructionList()
    
    
    def instructionList(self):
        op = self.lookahead(1)
        if op == 'PRINTF' or op == 'SCANF' or op == 'IF':
            self.instructions()
    
    
    def instruction(self):
        op = self.lookahead(1)
        if op == 'PRINTF':
            self.printf()
        elif op == 'SCANF':
            self.scanf()
        elif op == 'IF':
            self.condition()
        else:
            self.syntaticError(['if', 'printf', 'or scanf'])

    
    def printf(self):
        self.match('PRINTF')
        self.match('LPAREN')
        self.printfArgs()
        self.match('RPAREN')
        self.match('SEMCOL')
    
    
    def printfArgs(self):
        if self.lookahead(1) == 'CHAR_CONST':
            self.match('CHAR_CONST')
        elif self.lookahead(1) == 'ID':
            self.match('ID')
        else:
            self.syntaticError(['variable', 'or String'])
        
        if self.lookahead(1) == 'COMMA':
            self.match('COMMA')
            self.idList()

    def scanf(self):
        self.match('SCANF')
        self.match('LPAREN')
        self.scanfArgs()
        self.match('RPAREN')
        self.match('SEMCOL')
    
    def scanfArgs(self):
        if self.lookahead(1) == 'CHAR_CONST':
            self.match('CHAR_CONST')
        elif self.lookahead(1) == 'ID':
            self.match('ID')
        self.match('COMMA')
        self.idList()

    
    def condition(self):
        self.match('IF')
        self.match('LPAREN')
        self.relExpression()
        self.match('RPAREN')
        self.match('LBRACE')
        self.executionBlock()
        self.match('RBRACE')
        self.elseCondition()
    
    def elseCondition(self):
        if self.lookahead(1) == 'ELSE':
            self.match('ELSE')
            self.match('LBRACE')
            self.executionBlock()
            self.match('RBRACE')
        
    def isInstruction(self):
        op = self.lookahead(1)
        if op == 'PRINTF' or op == 'SCANF' or op == 'IF':
            return True
        return False

    def executionBlock(self):
        if self.isInstruction():
            self.instructions()
        else:
            self.declarationList()
        
        if self.lookahead(1) == "RBRACE":
            return
        self.executionBlock()

    #Regra para a estrutura de um programa simples
    def simpleProgram(self):
        self.type()
        self.match('MAIN')
        self.match('LPAREN')
        self.listArgs()
        self.match('LBRACE')
        self.executionBlock()
        self.match('RBRACE')