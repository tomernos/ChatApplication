from flask import Flask, render_template
import os

app = Flask(__name__)

clock_app_url = os.getenv('CLOCK_APP_URL', "http://clock_upp")

@app.route('/')
def home():
    return render_template('update_index.html')

@app.route('/update', methods=['POST'])
def update_clock_app():
    updated_time = request.form.get('updated_time')
    os.system(f'curl -X POST {clock_app_url}/update_time -H "Content-Type: application/json" -d \'{{"time": "{updated_time}" }}\'')
    return 'Time updated successfully!', 200


if __name__ == '__main__':
    app.run(debug=True, port=80, host="0.0.0.0")
