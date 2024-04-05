import os
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

db = SQLAlchemy(app)
BASE_URL = '/api/v2/'

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    developer = db.Column(db.String(60), nullable=False)
    release_year = db.Column(db.String(4), nullable=False)
    platform = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.String(1), nullable=False)
    picture = db.Column(db.String(2048), nullable=False)
    
    def show(self):
        return {
            'id': self.id,
            'title': self.title,
            'developer': self.developer,
            'release': self.release_year,
            'platform': self.platform,
            'rating': self.rating,
            'picture': self.picture
        }

@app.route('/')
def home():
    return 'Welcome to my game api'

@app.route(BASE_URL + 'add_game', methods=['POST'])
def addGame():
    if not request.json:
        abort(400, description='Missing body in request')

    required_fields = ['title', 'developer', 'release_year', 'platform', 'rating', 'picture']
    for field in required_fields:
        if field not in request.json:
            abort(400, description=f'Missing {field} in request')

    game = Game(title=request.json['title'],
                developer=request.json['developer'],
                release_year=request.json['release_year'],
                platform=request.json['platform'],
                rating=request.json['rating'],
                picture=request.json['picture'])

    db.session.add(game)
    db.session.commit()

    return jsonify({'message': 'Game added successfully', 'game': game.show()}), 201

@app.route(BASE_URL + 'change_game/<int:id>', methods=['PATCH'])
def updateGame(id):
    game = Game.query.get(id)
    if game is None:
        abort(404, description="game not found!")
        
    if request.json == {}:
        abort(400, description='Missing required fields')
        
    required_fields = ['title', 'developer', 'release_year', 'platform', 'rating', 'picture']
    changed = False    
        
    for field in required_fields:
        if field in request.json:
            game.__dict__[field] = request.json[field]
            changed = True
    
    db.session.commit()
    if changed == True:
        return jsonify('game has been changed has been succesfully changed'), 200
    elif changed == False:
        return jsonify('There were no valid values to be changed', 400)
        
    
@app.route(BASE_URL + 'show_games', methods=['GET'])
def getgames():
    allgames = Game.query.all()
    return jsonify({'These are all your games': [game.show() for game in allgames]}), 200

@app.route(BASE_URL + 'show_game/<int:id>', methods=['GET'])
def getGame(id):
    game = Game.query.get(id)
    if game is None:
        abort(404, error="game not found!")
    return jsonify({'This is the game you asked for': game.show()}), 200

@app.route(BASE_URL + 'delete_game/<int:id>', methods=['DELETE'])
def deleteGame(id):
    game = Game.query.get(id)
    if game is None:
        abort(404, error="game not found!")
    db.session.delete(game)
    db.session.commit()
    
    return jsonify('game has been deleted'), 200
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)