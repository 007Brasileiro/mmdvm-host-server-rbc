from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do banco de dados
class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    tg_id = db.Column(db.String(20), nullable=False)
    slot = db.Column(db.Integer, nullable=False)
    color_code = db.Column(db.Integer, nullable=False)

# Criação do banco de dados
with app.app_context():
    db.create_all()

# Template HTML
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciador de Canais DMR</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/css/bootstrap.min.css">
</head>
<body class="container">
    <h1 class="mt-5">Gerenciador de Canais DMR</h1>

    <form class="mt-4" id="channelForm">
        <div class="mb-3">
            <label for="name" class="form-label">Nome do Canal</label>
            <input type="text" class="form-control" id="name" name="name" required>
        </div>
        <div class="mb-3">
            <label for="tg_id" class="form-label">ID do Talk Group</label>
            <input type="number" class="form-control" id="tg_id" name="tg_id" required>
        </div>
        <div class="mb-3">
            <label for="slot" class="form-label">Slot (1 ou 2)</label>
            <input type="number" class="form-control" id="slot" name="slot" min="1" max="2" required>
        </div>
        <div class="mb-3">
            <label for="color_code" class="form-label">Código de Cor</label>
            <input type="number" class="form-control" id="color_code" name="color_code" min="0" max="15" required>
        </div>
        <button type="submit" class="btn btn-primary">Criar Canal</button>
    </form>

    <h2 class="mt-5">Canais Criados</h2>
    <ul id="channelList" class="list-group mt-3"></ul>

    <script>
        const form = document.getElementById('channelForm');
        const channelList = document.getElementById('channelList');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);

            const response = await fetch('/add_channel', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const channel = await response.json();
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = `Nome: ${channel.name}, TG: ${channel.tg_id}, Slot: ${channel.slot}, Código de Cor: ${channel.color_code}`;
                channelList.appendChild(li);
            } else {
                alert('Erro ao criar o canal. Verifique os campos!');
            }
        });

        async function fetchChannels() {
            const response = await fetch('/channels');
            const channels = await response.json();

            channels.forEach(channel => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = `Nome: ${channel.name}, TG: ${channel.tg_id}, Slot: ${channel.slot}, Código de Cor: ${channel.color_code}`;
                channelList.appendChild(li);
            });
        }

        fetchChannels();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)

@app.route('/add_channel', methods=['POST'])
def add_channel():
    name = request.form.get('name')
    tg_id = request.form.get('tg_id')
    slot = request.form.get('slot')
    color_code = request.form.get('color_code')

    if not name or not tg_id or not slot or not color_code:
        return "Todos os campos são obrigatórios!", 400

    channel = Channel(name=name, tg_id=tg_id, slot=slot, color_code=color_code)
    db.session.add(channel)
    db.session.commit()
    return jsonify({"name": name, "tg_id": tg_id, "slot": slot, "color_code": color_code})

@app.route('/channels', methods=['GET'])
def get_channels():
    channels = Channel.query.all()
    return jsonify([{
        "id": channel.id,
        "name": channel.name,
        "tg_id": channel.tg_id,
        "slot": channel.slot,
        "color_code": channel.color_code
    } for channel in channels])

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
