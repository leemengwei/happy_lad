from flask import Flask, request, render_template_string, flash, send_from_directory
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Default configuration
config = {
    "time_span": 10,  # Default value for aaa
    "cold_down_hours": 24,  # Default value for bbb
    "name": "Kitchen"  # Default value for ccc
}

# HTML template for the configuration form
html_template = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>与爱相伴</title>
</head>
<body>
  <h2>与爱相伴Configuration</h2>
  {% with messages = get_flashed_messages() %}
    {% if messages %}
      <ul>
      {% for message in messages %}
        <li>{{ message }}</li>
      {% endfor %}
      </ul>
    {% endif %}
  {% endwith %}
  <form method="POST">
    <label for="time_span">Time Span 想要记录的时光长度(Years):</label>
    <input type="number" id="time_span" name="time_span" value="{{ config.time_span }}"><br><br>
    
    <label for="cold_down_hours">Cold Down Time (Hours):</label>
    <input type="number" id="cold_down_hours" name="cold_down_hours" value="{{ config.cold_down_hours }}"><br><br>
    
    <label for="name">Name (Just A Name ^_^):</label>
    <input type="text" id="name" name="name" value="{{ config.name }}"><br><br>
    
    <input type="submit" value="Submit">
  </form>
    <h2>TestCamera</h2>
  <button onclick="refreshImage()">Refresh Image</button>
  <br><br>
  <img id="cameraImage" src="{{ url_for('get_image') }}" alt="Camera Image">
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    global config
    if request.method == 'POST':
        # Update configuration with form data
        config['time_span'] = int(request.form['time_span'])
        config['cold_down_hours'] = int(request.form['cold_down_hours'])
        config['name'] = request.form['name']
        
        # Save the updated configuration to config.json
        with open('../config.json', 'w') as config_file:
            json.dump(config, config_file)
        
        # Flash a success message
        flash('重启机器以生效')
    
    # Render the form with the current configuration
    return render_template_string(html_template, config=config)

@app.route('/cam.jpg')
def get_image():
    return send_from_directory('..', 'cam.jpg')


if __name__ == '__main__':
    app.run(debug=True)

