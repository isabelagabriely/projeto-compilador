class Lexer:
    """ Analisador Léxico
    """
    def __init__(self):
        with open('input.txt', 'r') as source:
            source_code = source.read()
            self.code = repr(source_code).strip("'")
        
        self.rules = self.__txt_to_dict('patterns/rules.txt')
        self.symbols = open('patterns/symbols.txt', 'r').read().split()

    @staticmethod
    def __txt_to_dict(file: str):
        with open(file, 'r') as f:
            dic = {}
            for line in f.readlines():
                pattern, token = line.split()
                dic[pattern] = token
        return dic

    def __split_into_lexems(self):
        lexems = []
        input_string = self.code
        char = input_string[0]
        lexem = ''
        next_index = 1
        __string = False
        __double_sym = False

        while next_index <= len(input_string):
            if char == '"':
                __string = True
            
            # Concatenar enquanto for uma string ou enquanto char não for ' ' nem um símbolo
            while (
                    next_index <= len(input_string) and 
                    (char != ' ' and char not in self.symbols) or
                    __string
                ):
                lexem += char

                if next_index < len(input_string):
                    char = input_string[next_index]

                if char == '"':
                    __string = False

                next_index += 1
                
            # Caso char concatenado com próximo valor da string seja um símbolo válido de duas posições
            if next_index < len(input_string) and char + input_string[next_index] in self.symbols:
                    __double_sym = True

            elif char in self.symbols:
                # Não entrou no while para atualizar lexem, voltamos para o indice anterior p/ na próxima iteração identificarmos o símbolo como um lexema
                if lexem != '':
                    next_index -= 1
                # Na iteração seguinte conseguimos entrar nesse else e atualizar lexem com o símbolo (não atualizamos de primeira pois perderia o resultado do lexema encontrado anteriormente)
                else:
                    lexem = char

            # Verificação se o lexema é válido pois quando encontramos char ou símbolo único não atualizamos essa variável
            if lexem != '':
                lexems.append(lexem)
                lexem = ''
            
            # char atualizada
            if next_index < len(input_string):
                # Concatena caso seja um símbolo de duas posições 
                if __double_sym:
                    char += input_string[next_index]
                    __double_sym = False
                # Pega o próximo ou caso seja um símbolo único pegará esse mesmo símbolo para virar um lexema
                else:
                    char = input_string[next_index]
            
            next_index += 1
                
        return lexems

    @property
    def lexems(self):
        return self.__split_into_lexems()

    @property
    def tokens(self):
        tokens_found = []

        for lexem in self.lexems:
            if lexem in self.rules.keys():
                tokens_found.append(self.rules[lexem])
            
            elif lexem.isidentifier():
                tokens_found.append('ID')

            elif lexem.isdigit():
                tokens_found.append('INT_CONST')

            elif '"' not in lexem and "." in lexem:
                tokens_found.append('FLOAT_CONST')

            elif lexem[0] == '"' and lexem[-1] == '"':
                tokens_found.append('CHAR_CONST')
            
            else:
                tokens_found.append('NONE')

        return tokens_found

    def tokenize(self):
        symbols_table = list(zip(self.tokens, self.lexems))

        if 'NONE' in self.tokens:
            token_index = self.tokens.index('NONE')
            invalid_lexem = self.lexems[token_index]
            line_num = self.tokens[:token_index].count('NEWLINE')

            print(f'{invalid_lexem} inesperado na linha {line_num+1}')
            exit()
            
        return symbols_table