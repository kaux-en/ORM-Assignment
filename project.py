from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from marshmallow import ValidationError
from password import password

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://root:{password}@localhost/FitnessCenter_db'
db = SQLAlchemy(app)
ma = Marshmallow(app)


class MemberSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    age = fields.String(required=True)

class Meta:
    fields = ('id', 'name', 'age')


member_schema = MemberSchema()
members_schema = MemberSchema(many=True)


class Member(db.Model):
    __tablename__= 'Members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer)
    


@app.route('/members', methods=['GET'])
def get_members():
    members = Member.query.all() 
    return members_schema.jsonify(members)


@app.route('/members', methods=['POST'])
def add_member():
    try:
        #validate and deserialize input
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_member = Member(id=member_data['id'], name=member_data['name'], age=member_data['age'])
    db.session.add(new_member) 
    db.session.commit() 
    return jsonify({"message": "New member added successfully"}), 201

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    member = Member.query.get_or_404(id) 
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    member.id = member_data['id']
    member.name = member_data['name']
    member.age = member_data['age']
    db.session.commit()
    return jsonify({"message": "Member details updated successfully"}), 200

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    member = Member.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": "Member removed successfully"}), 200

# -------------------------------------------

class WorkoutSession(db.Model):
    __tablename__= 'WorkoutSessions'
    session_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.String(255), db.ForeignKey('Members.id'), nullable=False)
    session_date = db.Column(db.String(100))
    session_time = db.Column(db.String(100))
    activity = db.Column(db.String(255))


class SessionSchema(ma.Schema):
    session_id = fields.Int(required=True) 
    member_id = fields.Int(required=True)
    session_date = fields.String(required=True)
    session_time = fields.String(required=True)
    activity = fields.String(required=True)

    class Meta: 
        fields = ("session_id", "member_id", "session_date", "session_time", "activity") 

session_schema = SessionSchema() 
sessions_schema = SessionSchema(many=True) 


@app.route('/workoutsessions', methods=['GET'])
def view_sessions():
    sessions = WorkoutSession.query.all() 
    return sessions_schema.jsonify(sessions)


@app.route('/workoutsessions', methods=['POST'])
def schedule_session():
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_session = WorkoutSession(session_id=session_data['session_id'], member_id=session_data['member_id'], session_date=session_data['session_date'], session_time=session_data['session_time'], activity=session_data['activity'])
    db.session.add(new_session) 
    db.session.commit() 
    return jsonify({"message": "New workout session added successfully"}), 201


@app.route('/workoutsessions/<int:id>', methods=['PUT'])
def update_session(id):
    session = WorkoutSession.query.get_or_404(id) 
    try:
        session_data = session_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    session.session_id = session_data['session_id']
    session.member_id = session_data['member_id']
    session.session_date = session_data['session_date']
    session.session_time = session_data['session_time']
    session.activity = session_data['activity']
    db.session.commit()
    return jsonify({"message": "Workout session details updated successfully"}), 200


@app.route('/workoutsessions/member/<int:id>', methods=['GET'])
def member_workout_sessions(id): #sessions for a specific member
    session = WorkoutSession.query.get_or_404(id)  
    return sessions_schema.jsonify(session)
   



with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)