"""Interface do simulador usando Tkinter."""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ahmes import CPU, assemble, load_memory


class Simulador:
    def __init__(self, root):
        self.root = root
        self.cpu = CPU()
        self.initial = [0] * 256
        self.running = False
        root.title('Simulador Ahmes')
        root.geometry('1050x750')
        bar = ttk.Frame(root, padding=8)
        bar.pack(fill='x')
        for title, action in [('Abrir Assembly', self.open_source), ('Salvar Assembly', self.save_source),
                              ('Importar memória', self.import_memory), ('Exportar memória', self.export_memory),
                              ('Montar', self.build), ('Passo', self.step), ('Executar', self.run),
                              ('Pausar', self.pause), ('Reiniciar', self.reset)]:
            ttk.Button(bar, text=title, command=action).pack(side='left', padx=2)
        self.state = tk.StringVar()
        ttk.Label(root, textvariable=self.state, font=('Monospace', 12), padding=10).pack(fill='x')
        panes = ttk.Panedwindow(root, orient='horizontal')
        panes.pack(fill='both', expand=True, padx=10)
        left, right = ttk.Frame(panes), ttk.Frame(panes)
        panes.add(left, weight=1)
        panes.add(right, weight=1)
        ttk.Label(left, text='Programa Assembly').pack(anchor='w')
        self.editor = tk.Text(left, width=45, height=22, undo=True, font=('Monospace', 11))
        self.editor.pack(fill='both', expand=True)
        self.editor.insert('1.0', (Path(__file__).parent / 'exemplos/soma.asm').read_text())
        ttk.Label(right, text='Memória decimal. Selecione uma posição para editar.').pack(anchor='w')
        columns = ('end', 'dec', 'hex', 'bin')
        self.table = ttk.Treeview(right, columns=columns, show='headings', height=20)
        for col, title in zip(columns, ('Endereço', 'Decimal', 'Hexadecimal', 'Binário')):
            self.table.heading(col, text=title)
            self.table.column(col, width=90, anchor='center')
        scroll = ttk.Scrollbar(right, command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side='right', fill='y')
        self.table.pack(fill='both', expand=True)
        self.table.tag_configure('pc', background='#c4e4ff')
        for address in range(256):
            self.table.insert('', 'end', iid=str(address), values=(address, 0, '00', '00000000'))
        edit = ttk.Frame(right)
        edit.pack(fill='x')
        self.value = ttk.Entry(edit, width=10)
        self.value.pack(side='left')
        ttk.Button(edit, text='Alterar byte', command=self.edit_byte).pack(side='left')
        ttk.Label(root, text='Histórico de execução').pack(anchor='w', padx=10)
        self.log = tk.Text(root, height=8, state='disabled', font=('Monospace', 10))
        self.log.pack(fill='x', padx=10, pady=5)
        self.message = tk.StringVar(value='Clique em Montar para carregar o programa.')
        ttk.Label(root, textvariable=self.message, padding=8).pack(fill='x')
        self.refresh()

    def pause(self):
        self.running = False

    def error(self, exc):
        self.pause()
        self.message.set(str(exc))
        messagebox.showerror('Erro', str(exc))

    def refresh(self):
        cpu = self.cpu
        try:
            next_instruction = cpu.instruction() if not cpu.halted else 'HLT executado'
        except ValueError:
            next_instruction = 'Opcode inválido'
        self.state.set(f'PC={cpu.pc:03d}  AC={cpu.ac:03d} [{cpu.ac:08b}]  {cpu.flags()}\n'
                       f'Instruções: {cpu.steps}   Próxima: {next_instruction}')
        for address, value in enumerate(cpu.memory):
            self.table.item(str(address), values=(address, value, f'{value:02X}', f'{value:08b}'),
                            tags=('pc',) if address == cpu.pc else ())
        self.table.see(str(cpu.pc))

    def reset(self):
        self.pause()
        self.cpu = CPU(self.initial)
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        self.log.configure(state='disabled')
        self.message.set('Memória inicial restaurada. PC e AC zerados.')
        self.refresh()

    def build(self):
        self.pause()
        try:
            memory = assemble(self.editor.get('1.0', 'end'))
            self.initial = memory
            self.reset()
            self.message.set('Programa montado. Use Passo ou Executar.')
        except ValueError as exc:
            self.error(exc)

    def step(self):
        try:
            if self.cpu.halted:
                self.pause()
                self.message.set('Execução encerrada por HLT.')
                return
            text = self.cpu.step()
            self.log.configure(state='normal')
            self.log.insert('end', text + '\n')
            self.log.see('end')
            self.log.configure(state='disabled')
            self.refresh()
            if self.cpu.halted:
                self.pause()
                self.message.set('Execução encerrada por HLT.')
        except ValueError as exc:
            self.error(exc)

    def run(self):
        if self.running or self.cpu.halted:
            return
        self.running = True
        self.remaining = 10000
        self.tick()

    def tick(self):
        if not self.running:
            return
        self.step()
        self.remaining -= 1
        if self.running and self.remaining == 0:
            self.pause()
            self.message.set('Pausa após 10000 instruções. Confira possíveis laços infinitos.')
        if self.running:
            self.root.after(60, self.tick)

    def open_source(self):
        path = filedialog.askopenfilename(filetypes=[('Assembly', '*.asm'), ('Todos', '*')])
        if path:
            self.pause()
            try:
                source = Path(path).read_text(encoding='utf-8-sig')
                self.editor.delete('1.0', 'end')
                self.editor.insert('1.0', source)
                self.message.set('Arquivo aberto. Clique em Montar.')
            except (OSError, UnicodeError) as exc:
                self.error(exc)

    def save_source(self):
        path = filedialog.asksaveasfilename(defaultextension='.asm')
        if path:
            try:
                Path(path).write_text(self.editor.get('1.0', 'end-1c'), encoding='utf-8')
            except OSError as exc:
                self.error(exc)

    def import_memory(self):
        path = filedialog.askopenfilename()
        if path:
            self.pause()
            try:
                self.initial = load_memory(Path(path).read_text(encoding='utf-8-sig'))
                self.reset()
            except (OSError, ValueError) as exc:
                self.error(exc)

    def export_memory(self):
        self.pause()
        path = filedialog.asksaveasfilename(defaultextension='.txt')
        if path:
            try:
                Path(path).write_text(''.join(f'{x}\n' for x in self.cpu.memory), encoding='utf-8')
            except OSError as exc:
                self.error(exc)

    def edit_byte(self):
        self.pause()
        try:
            selection = self.table.selection()
            if not selection:
                raise ValueError('Selecione um endereço na tabela.')
            value = int(self.value.get())
            if not 0 <= value <= 255:
                raise ValueError('Digite um valor decimal de 0 a 255.')
            self.cpu.memory[int(selection[0])] = value
            self.refresh()
            self.message.set('Byte alterado. Reiniciar restaura a memória carregada.')
        except ValueError as exc:
            self.error(exc)


def launch():
    root = tk.Tk()
    Simulador(root)
    root.mainloop()
