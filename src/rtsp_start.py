import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# 初始化 GStreamer
Gst.init(None)

# 创建 GStreamer 管道
pipeline_str = '''
v4l2src device=/dev/video0 ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=ultrafast ! rtph264pay config-interval=1 pt=96 ! udpsink host=127.0.0.1 port=5000
'''

pipeline = Gst.parse_launch(pipeline_str)

# 设置 GStreamer 管道为播放状态
pipeline.set_state(Gst.State.PLAYING)

# 创建一个主循环
loop = GLib.MainLoop()

try:
    loop.run()
except KeyboardInterrupt:
    pass
finally:
    # 清理并释放资源
    pipeline.set_state(Gst.State.NULL)
