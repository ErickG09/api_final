from flask import Flask, jsonify, abort, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    # Definimos las columnas de la tabla de la BD
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(120), nullable=False)  
    category = db.Column(db.String(120), nullable=False)  
    status = db.Column(db.Boolean, default=False)  
    created = db.Column(db.DateTime, default=datetime.utcnow)  
    update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 

    def tasks_bd(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'status': self.status,
            'created': self.created.isoformat(),
            'update': self.update.isoformat()
        }

BASE_URL = '/api/'

@app.route('/')
def home():
    return 'Welcome to my To-Do List!'

# CREAR UNA NUEVA TAREA CON LA SOLICITUD POST
@app.route(BASE_URL + 'tasks', methods=['POST'])
def create_task():
    if not request.json:
        abort(400, "Missing JSON body in request")
    
    if 'name' not in request.json:
        abort(400, "Error, missing 'name' in JSON data.")
    
    if 'category' not in request.json:
        abort(400, "Error, missing 'category' in JSON data.")
    task = Task(name=request.json['name'], category=request.json['category'])
    db.session.add(task)  # Agrega la tarea a la BD
    db.session.commit()  # Guarda los cambios en la BD
    return jsonify({'task': task.tasks_bd()}), 201 

# LEER TODAS LAS TAREAS REGISTRADAS CON LA SOLICITUD GET
@app.route(BASE_URL + 'tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.all()  # Recupera todas las tareas de la BD
    return jsonify({'tasks': [task.tasks_bd() for task in tasks]}) 

# LEER UNA TAREA ESPECÍFICA MEDIANTE EL ID CON LA SOLICITUD GET
@app.route(BASE_URL + 'tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id) # Obtenemos el registro 
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({'task': task.tasks_bd()})

# ACTUALIZAR EL ESTADO DE UNA TAREA CON LA SOLICITUD PUT
@app.route(BASE_URL + 'tasks/<int:id>', methods=['PUT'])
def update_task(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    if not request.json:
        abort(400, "Missing JSON body in request")
    task.status = not task.status 
    db.session.commit()  
    return jsonify({'task': task.tasks_bd()})  

# ELIMINAR UNA TAREA POR SU ID CON LA SOLICITUD DELETE
@app.route(BASE_URL + 'tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    task = Task.query.get(id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    db.session.delete(task)  
    db.session.commit()  
    return jsonify({'result': True})  

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True) 

