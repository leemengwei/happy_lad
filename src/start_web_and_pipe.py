import os
from flask import Flask, request, render_template_string, flash, send_from_directory
import json
import time
import json
import glob
from IPython import embed
import main_pipe
import threading
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Default configuration
config = json.load(open('../config.json'))

# HTML template for the configuration form
html_template = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>肥猪观察</title>
</head>
<body>
  <h2>肥猪观察Configuration</h2>
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
    <label for="time_span">记录时长(Years，推荐10年以上才能有效观察肥肥变大):</label>
    <input type="number" id="time_span" name="time_span" value="{{ config.time_span }}"><br><br>
    
    <label for="cold_down_hours">固定记录间隔(Hours):</label>
    <input type="number" id="cold_down_hours" name="cold_down_hours" value="{{ config.cold_down_hours }}"><br><br>
    
    <label for="name">房间名称</label>
    <input type="text" id="name" name="name" value="{{ config.name }}"><br><br>
    
    <input type="submit" value="更新">
  </form>
    <h2>查看安装位置</h2>
  <img id="cameraImage" src="{{ url_for('get_image') }}" alt="Camera Image">
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    global config
    if request.method == 'POST':
        # Update configuration with form data
        config['time_span'] = float(request.form['time_span'])
        config['cold_down_hours'] = float(request.form['cold_down_hours'])
        config['name'] = request.form['name']
        
        # Save the updated configuration to config.json
        with open('../config.json', 'w') as config_file:
            json.dump(config, config_file)
        
        # Flash a success message
        # time.sleep(5)
        # os.system("reboot")
        pipe_class.load_config()
        flash("加载成功")
    
    # Render the form with the current configuration
    return render_template_string(html_template, config=config)

@app.route('/latest.jpg')
def get_image():
    pipe_class.force_sample_this_time = True
    time.sleep(1)
    images = glob.glob("../images/*.jpg")
    images.sort()
    print("Recent samples", images[-10:], dir(pipe_class), pipe_class, pipe_class.sample_chance)
    # rename this last image to latest.jpg.jpg
    os.system("cp -f %s /tmp/latest.jpg" % images[-1])
    return send_from_directory('/tmp', 'latest.jpg')


if __name__ == '__main__':
    pipe_class = main_pipe.ALL()
    pipe_class.load_config()
    print("Starting in 3 sec!!!!!!!!!!!!!!")
    time.sleep(2)
    loop_thread = threading.Thread(target=pipe_class.run_pipe)
    loop_thread.daemon = True  # 设置为守护线程，这样主程序退出时它也会退出
    loop_thread.start()
    app.run(debug=False, host='0.0.0.0')
    