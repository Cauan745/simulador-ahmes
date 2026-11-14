"""Processador Ahmes, montador e execução pelo terminal. Python 3.10+."""
from dataclasses import dataclass, field
from pathlib import Path
import argparse
import re


OPCODES = dict(NOP=0, STA=16, LDA=32, ADD=48, OR=64, AND=80,
               NOT=96, SUB=112, JMP=128, JN=144, JP=148, JV=152,
               JNV=156, JZ=160, JNZ=164, JC=176, JNC=180, JB=184,
               JNB=188, SHR=224, SHL=225, ROR=226, ROL=227, HLT=240)
OPERANDOS = set('STA LDA ADD OR AND SUB JMP JN JP JV JNV JZ JNZ JC JNC JB JNB'.split())


def decode(byte):
    """Os bits marcados como x na codificação não participam da decodificação."""
    family = byte >> 4
    code = byte & (0xFC if family in (9, 10, 11) else 0xF3 if family == 14 else 0xF0)
    for name, value in OPCODES.items():
        if code == value:
            return name
    raise ValueError(f'Opcode inválido: {byte:02X}')


@dataclass
class CPU:
    memory: list = field(default_factory=lambda: [0] * 256)
    pc: int = 0
    ac: int = 0
    n: bool = False
    z: bool = True
    v: bool = False
    c: bool = False
    b: bool = False
    halted: bool = False
    steps: int = 0

    def __post_init__(self):
        if len(self.memory) != 256 or any(type(x) is not int or not 0 <= x <= 255 for x in self.memory):
            raise ValueError('A memória deve conter exatamente 256 bytes.')
        self.memory = self.memory.copy()

    def instruction(self):
        name = decode(self.memory[self.pc])
        return name + (f' {self.memory[(self.pc + 1) & 255]}' if name in OPERANDOS else '')

    def step(self):
        if self.halted:
            return 'Processador parado em HLT'
        start = self.pc
        text = self.instruction()
        name = text.split()[0]
        self.pc = (self.pc + 1) & 255
        address = None
        if name in OPERANDOS:
            address = self.memory[self.pc]
            self.pc = (self.pc + 1) & 255
        old = self.ac
        if name == 'STA':
            self.memory[address] = self.ac
        elif name == 'LDA':
            self.ac = self.memory[address]
        elif name in ('ADD', 'SUB'):
            value = self.memory[address]
            total = old + value if name == 'ADD' else old - value
            self.ac = total & 255
            if name == 'ADD':
                self.c = total > 255
                self.v = bool((~(old ^ value) & (old ^ self.ac)) & 128)
            else:
                self.b = total < 0
                self.v = bool(((old ^ value) & (old ^ self.ac)) & 128)
        elif name == 'OR':
            self.ac |= self.memory[address]
        elif name == 'AND':
            self.ac &= self.memory[address]
        elif name == 'NOT':
            self.ac ^= 255
        elif name in ('SHR', 'SHL', 'ROR', 'ROL'):
            carry = int(self.c)
            if name in ('SHR', 'ROR'):
                self.c = bool(old & 1)
                self.ac = (old >> 1) | ((carry << 7) if name == 'ROR' else 0)
            else:
                self.c = bool(old & 128)
                self.ac = ((old << 1) & 255) | (carry if name == 'ROL' else 0)
        elif name.startswith('J'):
            conditions = dict(JMP=True, JN=self.n, JP=not self.n,
                              JV=self.v, JNV=not self.v, JZ=self.z,
                              JNZ=not self.z, JC=self.c, JNC=not self.c,
                              JB=self.b, JNB=not self.b)
            if conditions[name]:
                self.pc = address
        elif name == 'HLT':
            self.halted = True
        if name in ('LDA', 'ADD', 'SUB', 'OR', 'AND', 'NOT', 'SHR', 'SHL', 'ROR', 'ROL'):
            self.n, self.z = bool(self.ac & 128), self.ac == 0
        self.steps += 1
        return f'{start:03d}: {text:<9} AC={self.ac:03d} PC={self.pc:03d} ' + self.flags()

    def flags(self):
        return ' '.join(f'{flag.upper()}={int(getattr(self, flag))}' for flag in 'nzvcb')

    def run(self, limit=10000):
        for _ in range(limit):
            if self.halted:
                return
            self.step()
        if not self.halted:
            raise ValueError(f'Limite de {limit} instruções atingido. Possível laço infinito.')


def number(token, symbols):
    token = token.upper()
    if token in symbols:
        return symbols[token]
    try:
        return int(token, 0) if token.startswith(('0X', '0B', '-0X', '-0B')) else int(token)
    except ValueError:
        raise ValueError(f'Número ou rótulo desconhecido: {token}') from None


def assemble(source):
    """Duas passagens: resolve rótulos e depois emite instruções/dados."""
    symbols, records, memory, occupied = {}, [], [0] * 256, set()
    address = 0
    for lineno, raw in enumerate(source.splitlines(), 1):
        line = raw.split(';')[0].strip().upper()
        if not line:
            continue
        try:
            if ':' in line:
                label, line = line.split(':', 1)
                label, line = label.strip(), line.strip()
                if not re.fullmatch(r'[A-Z_][A-Z_0-9]*', label) or label in symbols:
                    raise ValueError('Rótulo inválido ou repetido.')
                symbols[label] = address
            if not line:
                continue
            tokens = line.replace(',', ' ').split()
            op, args = tokens[0].lstrip('.'), tokens[1:]
            if op == 'ORG':
                if len(args) != 1:
                    raise ValueError('ORG exige um endereço.')
                address = number(args[0], symbols)
                if not 0 <= address <= 255:
                    raise ValueError('Endereço fora de 0 a 255.')
                continue
            if op not in OPCODES and op not in ('DB', 'BYTE'):
                raise ValueError(f'Instrução desconhecida: {op}')
            if op in ('DB', 'BYTE'):
                if not args:
                    raise ValueError('DB exige ao menos um valor.')
                size = len(args)
            else:
                if len(args) != int(op in OPERANDOS):
                    raise ValueError(f'Quantidade de operandos incorreta para {op}.')
                size = 1 + int(op in OPERANDOS)
            if address + size > 256:
                raise ValueError('Programa ultrapassa a memória.')
            records.append((lineno, address, op, args))
            address += size
        except ValueError as exc:
            raise ValueError(f'Linha {lineno}: {exc}') from None
    for lineno, address, op, args in records:
        try:
            if op in ('DB', 'BYTE'):
                values = [number(arg, symbols) for arg in args]
                if any(not -128 <= value <= 255 for value in values):
                    raise ValueError('Dado fora de -128 a 255.')
                values = [value & 255 for value in values]
            else:
                values = [OPCODES[op]]
                if args:
                    value = number(args[0], symbols)
                    if not 0 <= value <= 255:
                        raise ValueError('Endereço fora de 0 a 255.')
                    values.append(value)
            for value in values:
                if address in occupied:
                    raise ValueError(f'Sobreposição no endereço {address}.')
                memory[address] = value
                occupied.add(address)
                address += 1
        except ValueError as exc:
            raise ValueError(f'Linha {lineno}: {exc}') from None
    return memory


def load_memory(source):
    values = [int(token) for token in source.split()]
    if not 1 <= len(values) <= 256 or any(not 0 <= value <= 255 for value in values):
        raise ValueError('Arquivo de memória exige de 1 a 256 bytes decimais.')
    return values + [0] * (256 - len(values))


def main():
    parser = argparse.ArgumentParser(description='Simulador Ahmes de 8 bits')
    parser.add_argument('arquivo', nargs='?', help='Programa Assembly ou memória decimal')
    parser.add_argument('--mem', action='store_true', help='Ler memória decimal, como mem.txt do Neander')
    parser.add_argument('--trace', action='store_true', help='Exibir cada instrução')
    parser.add_argument('--limit', type=int, default=10000)
    parser.add_argument('--export', help='Salvar memória final em formato decimal')
    args = parser.parse_args()
    if not args.arquivo:
        from interface import launch
        launch()
        return
    try:
        source = Path(args.arquivo).read_text(encoding='utf-8-sig')
        cpu = CPU(load_memory(source) if args.mem else assemble(source))
        if args.trace:
            for _ in range(args.limit):
                if cpu.halted:
                    break
                print(cpu.step())
            if not cpu.halted:
                raise ValueError('Limite atingido sem HLT.')
        else:
            cpu.run(args.limit)
        print(f'PC={cpu.pc} AC={cpu.ac} AC com sinal={cpu.ac if cpu.ac < 128 else cpu.ac - 256}')
        print(f'{cpu.flags()} Instruções={cpu.steps}')
        for base in range(0, 256, 16):
            print(f'{base:03d}: ' + ' '.join(f'{value:03d}' for value in cpu.memory[base:base + 16]))
        if args.export:
            Path(args.export).write_text(''.join(f'{value}\n' for value in cpu.memory), encoding='utf-8')
    except (OSError, ValueError) as exc:
        parser.exit(1, f'Erro: {exc}\n')


if __name__ == '__main__':
    main()
