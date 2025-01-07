#!/usr/bin/env python3
import sys
sys.path.append('../')
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst
from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call

import pyds

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3

# Function to handle the buffer probe for RTSP sink
def rtsp_sink_pad_buffer_probe(pad, info, u_data):
    # In this case, we're not processing the buffer, just pushing it through.
    # This probe is mainly to ensure the pipeline runs and we can inspect the elements if needed.
    return Gst.PadProbeReturn.PASS

def main(args):
    # Check for correct GPU
    if not is_aarch64():
        print("This script is designed to run on an NVIDIA GPU with AARCH64 architecture.")
        print("Exiting.")
        return

    # Standard GStreamer initialization
    Gst.init(None)

    # Create GStreamer elements
    pipeline = Gst.parse_launch("""
        filesrc location=camera_input_jpeg_stream ! jpegdec ! 
        nvvideoconvert ! 
        video/x-raw(memory:NVMM), format=NV12, width=1920, height=1080, framerate=30/1 ! 
        nvstreammux name=nvmux width=1920 height=1080 ! 
        nvinfer config-file-path=config_infer_primary.txt ! 
        nvtracker ! 
        nvvideoconvert ! 
        x264enc tune=zerolatency byte-stream=true ! 
        h264parse ! 
        rtph264pay name=pay0 pt=96 ! 
        udpsink host=127.0.0.1 port=5004 sync=false
    """)

    # Ensure all elements are created
    if not pipeline:
        print("Pipeline could not be created.")
        return -1

    # Get handles for elements
    infer_element = pipeline.get_by_name('nvinfer')
    nvstreammux = pipeline.get_by_name('nvmux')

    # Set property to load the engine first
    infer_element.set_property('engine-file', 'path_to_your_engine')

    # Link sources to mux
    for i in range(1):  # Assuming only one source for simplicity
        src_pad = pipeline.get_by_name(f'source{i}').get_static_pad('src')
        sink_pad = nvstreammux.get_request_pad('sink_{}'.format(i))
        src_pad.link(sink_pad)

    # Start playing the pipeline
    pipeline.set_state(Gst.State.PLAYING)

    try:
        # Wait until error or EOS
        bus = pipeline.get_bus()
        bus.poll(Gst.MessageType.EOS | Gst.MessageType.ERROR, Gst.CLOCK_TIME_NONE)
    except:
        pass

    # Stop playing the pipeline
    pipeline.set_state(Gst.State.NULL)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
