# app.py
# Instalasi yang dibutuhkan:
# pip install Flask Flask-SQLAlchemy Flask-Bcrypt Flask-Cors

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os
import json
from datetime import datetime

# --- Konfigurasi Aplikasi ---
app = Flask(__name__)
CORS(app) 

# Konfigurasi database SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'meowly.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super-secret-key-for-development'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# --- Model Database (SQLAlchemy) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    histories = db.relationship('DiagnosisHistory', backref='user', lazy=True)
    
    def __repr__(self):
        return f"User('{self.email}')"

class DiagnosisHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    diagnosis_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    top_disease = db.Column(db.String(100), nullable=False)
    top_percentage = db.Column(db.Float, nullable=False)
    full_result = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"History('{self.top_disease}' on '{self.diagnosis_date}')"


# --- Logika Sistem Pakar ---
class ExpertSystem:
    def __init__(self):
        self.symptoms = {
            "G1": "Ruam merah pada kepala/punggung/ekor", "G2": "Ruam merah pada telinga", "G3": "Ruam bentuk abstrak",
            "G4": "Ruam bentuk bulat", "G5": "Bulu rontok pada seluruh tubuh", "G6": "Bulu rontok pada bagian terjangkit",
            "G7": "Gatal (menggaruk seluruh tubuh)", "G8": "Gatal (menggaruk punggung tengah)", "G9": "Gatal (menggaruk punggung ekor)",
            "G10": "Gatal (menggaruk telinga)", "G11": "Gatal (menggaruk kepala/kaki/ekor)", "G12": "Diare",
            "G13": "Diare disertai darah", "G14": "Diare berlendir", "G15": "Diare disertai cacing",
            "G16": "Pup normal disertai cacing", "G17": "Demam", "G18": "Demam tinggi",
            "G19": "Tidak mau makan/nafsu makan turun", "G20": "Berat badan turun", "G21": "Lemas",
            "G22": "Muntah", "G23": "Dehidrasi/gusi putih", "G24": "Pucat", "G25": "Nyeri di bagian perut",
            "G26": "Sesak napas", "G27": "Ikterus", "G28": "Radang mata", "G29": "Bulu kusam",
            "G30": "Selaput putih pada mata", "G31": "Telinga radang", "G32": "Sariawan", "G33": "Ngiler/ngeces",
            "G34": "Anemia", "G35": "Keropeng pada bagian tubuh", "G36": "Keropeng pada telinga",
            "G37": "Terdapat bintik merah", "G38": "Infeksi pada luka", "G39": "Terdapat banyak kutu",
            "G40": "Sering mengigit/menjilat tubuh", "G41": "Sering menggoyangkan kepala", "G42": "Kotoran telinga berwarna coklat kehitaman",
            "G43": "Terdapat luka lembab/basah", "G44": "Terdapat luka mengandung nanah"
        }
        self.diseases_rules = {
            "P1": {"name": "Ringworm / kurap / dermathopysis", "symptoms": ["G1", "G4", "G6", "G11"], "solution": "a. Diberi obat jamur, bisa dalam bentuk salep atau minum (oral)\nb. Grooming (dimandikan) secara rutin menggunakan sampo anti jamur\nc. Hindari menempatkan kucing pada tempat yang lembab\nd. Dipisah dari kucing yang lain agar tidak menular\ne. Diberi pakan kucing khusus untuk kesehatan kulit\nf. Apabila sudah parah lebih baik dibawa ke pengobatan dokter hewan"},
            "P2": {"name": "Salmonellosis / Tifus Kucing", "symptoms": ["G12", "G17", "G19", "G21", "G22", "G23", "G24", "G25"], "solution": "a. Diberi antibiotik dan penanganan sesuai gejala yang muncul\nb. Diberikan makan berupa pakan kucing khusus untuk saluran pencernaan, bisa dibeli di petshop\nc. Apabila sudah parah lebih baik dibawa ke pengobatan dokter hewan"},
            "P3": {"name": "Toxoplasmosis", "symptoms": ["G12", "G17", "G18", "G19", "G21", "G22", "G23", "G26", "G27", "G28", "G29"], "solution": "a. Dapat dilakukan terapi cairan (infus) jika kucing mengalami dehidrasi\nb. Pemberian antibiotic/anti radang\nc. Diberikan pakan kucing khusus recovery, bisa dibeli di petshop\nd. Apabila sudah parah lebih baik dibawa ke pengobatan dokter hewan"},
            "P4": {"name": "Toxocara", "symptoms": ["G5", "G12", "G13", "G14", "G15", "G16", "G17", "G19", "G22", "G23", "G29", "G30"], "solution": "a. Diberikan obat cacing sesuai dengan dosis\nb. Apabila sudah parah lebih baik dibawa ke pengobatan dokter hewan"},
            "P5": {"name": "FPV (Feline Panleukopenia Virus)", "symptoms": ["G12", "G13", "G17", "G19", "G21", "G22", "G24", "G27", "G31", "G32", "G33"], "solution": "a. Diberi infus, antibiotik, obat sesuai gejalanya, seperti obat anti muntah, anti diare\nb. Diberi vaksin, vitamin tambahan\nc. Dibawa ke dokter hewan"},
            "P6": {"name": "Kutuan / Infeksi Kutu", "symptoms": ["G5", "G11", "G19", "G21", "G24", "G29", "G34", "G37", "G39", "G40"], "solution": "a. Digrooming (dimandikan) dengan sampo kutu\nb. Diberi obat anti parasite bisa dalam bentuk suntik atau tetes tengkuk (spot on)\nc. Kucing disisir menggunakan sisir anti kutu\nd. Apabila sudah parah lebih baik dibawa ke pengobatan dokter hewan"},
            "P7": {"name": "Scabies", "symptoms": ["G1", "G5", "G11", "G35", "G36", "G37"], "solution": "a. Diberikan anti parasite dalam bentuk suntik atau spot on\nb. Kalau sudah parah, kucing jangan dimandikan, karena dapat membuatnya lebih parah\nc. Dapat diberi vitamin / nutrisi kulit / bulu untuk kucing\nd. Diberi makan pakan terapi khusus\ne. Apabila sudah parah lebih baik dibawa ke pengobatan dokter hewan"},
            "P8": {"name": "Scabies Akut", "symptoms": ["G1", "G5", "G11", "G35", "G36", "G37", "G38"], "solution": "a. Diberi antibiotic\nb. Dibawa kedokter"},
            "P9": {"name": "Feline Demodecosis", "symptoms": ["G5", "G8", "G37", "G38", "G39", "G40"], "solution": "a. Mandi ddengan obat antiekstoparasit"},
            "P10": {"name": "Feline Demodecosis Akut", "symptoms": ["G5", "G8", "G19", "G20", "G37", "G38", "G39", "G40"], "solution": "a. Dibawa kedokter hewan"},
            "P11": {"name": "Alopecia", "symptoms": ["G5"], "solution": "a. Diberi penyubur rambut"},
            "P12": {"name": "Flea Allergy Derma", "symptoms": ["G5", "G9", "G38"], "solution": "a. Dimandikan\nb. Luka dibersihkan"},
            "P13": {"name": "Pruritus", "symptoms": ["G7"], "solution": "a. Pemberian obat anti radang"},
            "P14": {"name": "Ear Mite", "symptoms": ["G2", "G10", "G38", "G41", "G42"], "solution": "a. Pemberian obat antiekstoparasit"},
            "P15": {"name": "Pyoderma", "symptoms": ["G3", "G6", "G38", "G43", "G44"], "solution": "a. Luka dibershkan\nb. Nanah dibersihkan"},
            "P16": {"name": "Hotspot", "symptoms": ["G4", "G5", "G40", "G43"], "solution": "a. Diberikan salep"}
        }

    def diagnose(self, user_symptoms):
        possible_diseases = []
        for code, disease in self.diseases_rules.items():
            matched_symptoms = [symptom for symptom in disease["symptoms"] if symptom in user_symptoms]
            if not matched_symptoms:
                continue
            total_symptoms_for_disease = len(disease["symptoms"])
            match_percentage = (len(matched_symptoms) / total_symptoms_for_disease) * 100
            if match_percentage > 0:
                possible_diseases.append({
                    "name": disease["name"],
                    "match_percentage": round(match_percentage, 2),
                    "matched_symptoms_count": len(matched_symptoms),
                    "total_symptoms": total_symptoms_for_disease,
                    "solution": disease["solution"]
                })
        possible_diseases.sort(key=lambda x: x["match_percentage"], reverse=True)
        if not possible_diseases:
            return {"message": "Tidak ada penyakit yang cocok dengan gejala yang diberikan.", "results": []}
        return {"message": "Hasil diagnosis ditemukan.", "results": possible_diseases}

# --- API Endpoints ---

@app.route("/")
def index():
    return "<h1>Meowly Backend is running!</h1>"

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email dan password dibutuhkan'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'Email sudah terdaftar'}), 409
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'User berhasil terdaftar'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password, password):
        return jsonify({
            'status': 'success', 
            'message': 'Login berhasil',
            'user': {'id': user.id, 'email': user.email}
        }), 200
    return jsonify({'status': 'error', 'message': 'Email atau password salah'}), 401

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    system = ExpertSystem()
    symptoms_list = [{"code": code, "text": text} for code, text in system.symptoms.items()]
    return jsonify(symptoms_list)

# === [BARU] Endpoint untuk Daftar Penyakit ===
@app.route('/api/diseases', methods=['GET'])
def get_diseases():
    system = ExpertSystem()
    disease_list = []
    # Mengubah data dari dictionary ke list
    for code, details in system.diseases_rules.items():
        # Mengganti kode gejala dengan teksnya untuk ditampilkan di frontend
        symptom_texts = [system.symptoms[s_code] for s_code in details['symptoms']]
        
        disease_list.append({
            "name": details['name'],
            "symptoms": symptom_texts,
            "solution": details['solution']
        })
    # Mengurutkan daftar berdasarkan nama penyakit
    disease_list.sort(key=lambda x: x['name'])
    return jsonify(disease_list)

@app.route('/api/diagnose', methods=['POST'])
def diagnose_endpoint():
    data = request.get_json()
    user_symptoms = data.get('symptoms')
    user_id = data.get('user_id')

    if not all([user_symptoms, isinstance(user_symptoms, list), user_id]):
        return jsonify({'status': 'error', 'message': 'Format gejala atau user_id tidak valid'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User tidak ditemukan'}), 404

    system = ExpertSystem()
    result = system.diagnose(user_symptoms)
    
    if result.get("results"):
        top_result = result["results"][0]
        history_entry = DiagnosisHistory(
            user_id=user_id,
            top_disease=top_result["name"],
            top_percentage=top_result["match_percentage"],
            full_result=json.dumps(result["results"])
        )
        db.session.add(history_entry)
        db.session.commit()

    return jsonify(result), 200

@app.route('/api/history/<int:user_id>', methods=['GET'])
def get_history(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User tidak ditemukan'}), 404
        
    histories = DiagnosisHistory.query.filter_by(user_id=user_id).order_by(DiagnosisHistory.diagnosis_date.desc()).all()
    
    history_list = []
    for h in histories:
        history_list.append({
            'id': h.id,
            'date': h.diagnosis_date.strftime("%d %B %Y, %H:%M"),
            'top_disease': h.top_disease,
            'top_percentage': h.top_percentage,
            'full_result': json.loads(h.full_result)
        })
        
    return jsonify(history_list), 200


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5500)