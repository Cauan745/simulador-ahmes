# Simulador Ahmes

Trabalho de Arquitetura de Computadores. O programa simula o processador Ahmes, uma extensão do Neander fornecido como exemplo.

## Execução

É necessário Python 3.10 ou superior. Não usa pacotes do pip.

Para abrir a interface, execute no terminal:

    python3 ahmes.py

No Windows, use python no lugar de python3. A interface usa Tkinter. Em distribuições Linux que não incluem esse módulo, instale o pacote python3-tk.

Na interface, clique em Montar e depois em Passo ou Executar. A tabela mostra os 256 bytes da memória e destaca a posição do PC. O botão Pausar interrompe a execução. Reiniciar restaura a memória carregada e zera os registradores. Alterações no editor passam a valer depois de clicar em Montar.

Também é possível executar pelo terminal:

    python3 ahmes.py exemplos/soma.asm --trace
    python3 ahmes.py exemplos/multiplicacao.asm
    python3 ahmes.py neander/trab_arq/mem.txt --mem
    python3 ahmes.py exemplos/soma.asm --export resultado.txt

O formato de memória é o mesmo usado no mem.txt do exemplo: um byte decimal por linha. A importação aceita até 256 valores e completa o restante com zeros. Não importa diretamente o executável WAhmes, arquivos binários dele ou a listagem soma11.TXT.

## Organização

- ahmes.py contém o processador, o montador e a execução pelo terminal.
- interface.py contém a interface gráfica.
- exemplos contém programas Assembly para demonstração.
- test_ahmes.py verifica as instruções e o montador.
- neander contém o material original do professor, preservado.

## Funcionamento

A memória tem 256 posições de 8 bits e armazena instruções e dados. O AC guarda o resultado das operações. O PC indica o endereço da próxima instrução e volta a zero depois de 255.

Cada passo busca uma instrução na memória, lê seu operando quando necessário e executa a operação. Isso permite executar programas diferentes sem recompilar o simulador.

Os valores na memória ficam entre 0 e 255. Com sinal, os mesmos bits representam valores de -128 a 127 em complemento de dois. Resultados são limitados a 8 bits.

As flags são N para negativo, Z para zero, V para overflow com sinal, C para carry da soma e B para borrow da subtração. ADD altera N, Z, V e C. SUB altera N, Z, V e B. LDA e as operações lógicas alteram N e Z. Deslocamentos e rotações alteram N, Z e C. As demais instruções preservam as flags.

ROR e ROL usam o valor anterior de C como bit de entrada e guardam o bit que saiu em C. JP desvia quando N é zero, inclusive quando o resultado é zero. HLT para o processador até reiniciar.

## Instruções

| Instrução | Código decimal | Ação |
| --- | --- | --- |
| NOP | 0 | Não altera o estado além do PC |
| STA end | 16 | Guarda AC na memória |
| LDA end | 32 | Carrega AC da memória |
| ADD end | 48 | Soma ao AC |
| OR end | 64 | OU bit a bit |
| AND end | 80 | E bit a bit |
| NOT | 96 | Inverte os bits do AC |
| SUB end | 112 | Subtrai do AC |
| JMP end | 128 | Desvia sempre |
| JN end | 144 | Desvia se N = 1 |
| JP end | 148 | Desvia se N = 0 |
| JV end | 152 | Desvia se V = 1 |
| JNV end | 156 | Desvia se V = 0 |
| JZ end | 160 | Desvia se Z = 1 |
| JNZ end | 164 | Desvia se Z = 0 |
| JC end | 176 | Desvia se C = 1 |
| JNC end | 180 | Desvia se C = 0 |
| JB end | 184 | Desvia se B = 1 |
| JNB end | 188 | Desvia se B = 0 |
| SHR | 224 | Desloca para a direita |
| SHL | 225 | Desloca para a esquerda |
| ROR | 226 | Rotaciona para a direita usando C |
| ROL | 227 | Rotaciona para a esquerda usando C |
| HLT | 240 | Encerra a execução |

Instruções com endereço ocupam dois bytes. As demais ocupam um byte. Os bits indicados como indiferentes na codificação Ahmes são ignorados. Códigos reservados provocam uma mensagem de erro.

## Montador e exemplos

O montador aceita rótulos seguidos de dois-pontos, comentários iniciados por ponto e vírgula, ORG para definir o endereço de montagem e DB para inserir dados. Os números podem ser decimais, hexadecimais com prefixo 0x ou binários com prefixo 0b. DB também aceita negativos de -128 a -1. A execução começa no endereço zero, mesmo quando o programa usa ORG.

O exemplo soma.asm calcula 7 + 4 e guarda 11 no endereço 131. multiplicacao.asm calcula 6 vezes 4 por somas sucessivas e guarda 24 no endereço 132. flags.asm demonstra overflow e borrow, guardando 128 no endereço 131 e 255 no endereço 132.

## Verificação

Para executar os testes:

    python3 -m unittest -v

Os testes verificam todas as combinações de operandos de ADD e SUB, deslocamentos e rotações com os dois valores de carry, desvios condicionais, operações lógicas, exemplos, memória do Neander e erros de montagem. A execução tem um limite de instruções para permitir interromper programas sem HLT.

## Referências

O enunciado e os fontes Neander fornecidos pelo professor são a base do trabalho. A referência indicada no enunciado é a [página do Ahmes da UFRGS](https://www.inf.ufrgs.br/arq/wiki/doku.php?id=ahmes), que não respondeu durante a consulta. A codificação e as regras das flags foram conferidas na [documentação do projeto ArchSims](https://github.com/fdcastel/ArchSims/blob/master/doc/Ahmes.md). O simulador foi implementado em Python neste projeto.
