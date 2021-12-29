# Imports
from flask_sqlalchemy import SQLAlchemy
from flask import Flask,jsonify,request
from sqlalchemy.sql import expression
from flask_cors import CORS

# App Initialize
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# SQLite
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slots.sqlite3'
app.config['SECRET_KEY'] = "ultimatesupersecretstring"
db = SQLAlchemy(app)

# Database Model
class Slots(db.Model):
    __tablename__ = 'slots'
    id = db.Column(db.Integer, primary_key = True)
    slotname = db.Column(db.String(10), unique=True)
    reserved = db.Column(db.Boolean, server_default=expression.true(), nullable=False)
    carnumber = db.Column(db.String(100)) 
    owner = db.Column(db.String(100))

    def __init__(self, slotname, reserved, carnumber,owner):
        self.slotname = slotname
        self.reserved = reserved
        self.carnumber = carnumber
        self.owner = owner

# Utilities
def slotReserved(slot):
    slot = Slots.query.filter_by(slotname=slot).first()
    return slot.reserved == True

def fillSlots():
    for i in range(1,101):
        slot = Slots( slotname = f'D{i}',  reserved = False, carnumber = 'None', owner = 'None')
        db.session.add(slot)
        db.session.commit()

def getSlot(slot):
    slot = Slots.query.filter_by(slotname=slot).first()
    return {'slotname':slot.slotname, 'reserved':slot.reserved, 'carnumber':slot.carnumber, 'owner':slot.owner}

def getAllSlots():
    slots = Slots.query.all()
    allSlots = {}
    for slot in slots:
        allSlots[slot.slotname] =  {
                'reserved':slot.reserved,
                'owner':slot.owner,
                'carnumber':slot.carnumber
        }
    return allSlots


def slotExist(slot):
    return Slots.query.filter_by(slotname=slot).first() is not None

def slotState(slot):
    if(slotExist(slot)):
        if(slotReserved(slot)):
            return "Slot is Reserved"
        else:
            return "Slot is Not Reserved"
    else:
        return "Slot doesn't Exist"

def reserveSlot(slotname,carnumber,owner):
    if(slotExist(slotname) and  not slotReserved(slotname)):
        value = Slots.query.filter(Slots.slotname == slotname).first()
        value.reserved = True
        value.carnumber = carnumber
        value.owner = owner
        db.session.flush()
        db.session.commit()


def clearSlot(slotname):
    if(slotExist(slotname)):
        value = Slots.query.filter(Slots.slotname == slotname).first()
        value.reserved = False
        value.carnumber = "None"
        value.owner = "None"
        db.session.flush()
        db.session.commit()

# Routes

# Default Route
@app.route("/")
def hello():
    return "Nothing"

# Get State of a Slot
@app.route('/slot/<slotname>', methods=['GET'])
def get_slot(slotname):
    slot = getSlot(slotname)
    return jsonify(slot)

# Clear a Slot
@app.route('/slot/<slotname>', methods=['DELETE'])
def clear_slot(slotname):
    clearSlot(slotname)
    return jsonify("Success",200)

# Get State of all Slots
@app.route('/slots', methods=['GET'])
def get_all_slots():
    slots = getAllSlots()
    return jsonify(slots)

# Reserve a Slot
@app.route('/reserve/<slotname>/<carnumber>/<owner>', methods=["GET"])
def reserve_slot(slotname,carnumber,owner):
    reserveSlot(slotname,carnumber,owner)
    return jsonify("Success")


if __name__ == '__main__':
    app.run(debug = True)