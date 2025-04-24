from flask import Flask, request, jsonify
from utils.predict import predict_landmark

app = Flask(__name__)

@app.route('/')
def home():
    return "Campus Navigation API Running!"

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    img = request.files['image']
    prediction, distance = predict_landmark(img)

    return jsonify({
        'landmark': prediction,
        'estimated_distance': distance
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
