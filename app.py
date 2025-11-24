from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from yandex_storage import upload_to_yandex_cloud, delete_from_yandex_cloud

from config import config

load_dotenv()

app = Flask(__name__)
app.config.from_object(config)

db = SQLAlchemy(app)

class Item(db.Model):
    __tablename__ = 'items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(255))  

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'image_url': f"{config.YC_ENDPOINT_URL}/{config.YC_BUCKET_NAME}/{self.image_filename}" if self.image_filename else None
        }


# CREATE - Создание элемента
@app.route('/items', methods=['POST'])
def create_item():
    try:
        data = request.form
        name = data.get('name')
        description = data.get('description')
        
        new_item = Item(name=name, description=description) # type: ignore
        
        # Обработка загрузки файла
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = f"item_{new_item.id}_{file.filename}"
                upload_to_yandex_cloud(file, filename)
                new_item.image_filename = filename
        
        db.session.add(new_item)
        db.session.commit()
        
        return jsonify({'message': 'Item created', 'item': new_item.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# READ - Получение всех элементов
@app.route('/items', methods=['GET'])
def get_all_items():
    try:
        items = Item.query.all()
        return jsonify([item.to_dict() for item in items]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# READ - Получение одного элемента
@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        return jsonify(item.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# UPDATE - Обновление элемента
@app.route('/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        data = request.form
        
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
        
        # Обновление файла
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Удаление старого файла
                if item.image_filename:
                    delete_from_yandex_cloud(item.image_filename)
                
                # Загрузка нового
                filename = f"item_{item_id}_{file.filename}"
                upload_to_yandex_cloud(file, filename)
                item.image_filename = filename
        
        db.session.commit()
        return jsonify({'message': 'Item updated', 'item': item.to_dict()}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# DELETE - Удаление элемента
@app.route('/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        
        # Удаление файла из Object Storage
        if item.image_filename:
            delete_from_yandex_cloud(item.image_filename)
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'Item deleted'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            print("Таблицы базы данных успешно созданы")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
    
    app.run(host='0.0.0.0', port=5000, debug=True)