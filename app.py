from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def conectar():
    conn = sqlite3.connect('tarefas.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = conectar()
    # Ordena as tarefas pelo campo 'ordem'
    tarefas = conn.execute('SELECT * FROM Tarefas ORDER BY ordem').fetchall()
    # Faz o somatório dos custos para o rodapé
    total = sum(t['custo'] for t in tarefas)
    conn.close()
    return render_template('index.html', tarefas=tarefas, total=total)

@app.route('/incluir', methods=['GET', 'POST'])
def incluir():
    if request.method == 'POST':
        nome, custo, data = request.form['nome'], float(request.form['custo']), request.form['data']
        conn = conectar()
        try:
            ultima = conn.execute('SELECT MAX(ordem) FROM Tarefas').fetchone()[0] or 0
            conn.execute('INSERT INTO Tarefas (nome, custo, data_limite, ordem) VALUES (?, ?, ?, ?)',
                         (nome, custo, data, ultima + 1))
            conn.commit()
            return redirect('/')
        except sqlite3.IntegrityError:
            return "<h1>Erro: Nome já existe!</h1><a href='/incluir'>Voltar</a>"
        finally:
            conn.close()
    return render_template('incluir.html')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = conectar()
    tarefa = conn.execute('SELECT * FROM Tarefas WHERE id = ?', (id,)).fetchone()
    if request.method == 'POST':
        nome, custo, data = request.form['nome'], float(request.form['custo']), request.form['data']
        try:
            conn.execute('UPDATE Tarefas SET nome=?, custo=?, data_limite=? WHERE id=?', (nome, custo, data, id))
            conn.commit()
            return redirect('/')
        except sqlite3.IntegrityError:
            return "<h1>Erro: Nome já existe!</h1><a href='/'>Voltar</a>"
        finally:
            conn.close()
    return render_template('editar.html', tarefa=tarefa)

@app.route('/excluir/<int:id>')
def excluir(id):
    conn = conectar()
    conn.execute('DELETE FROM Tarefas WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)