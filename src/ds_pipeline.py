#!/usr/bin/env python3

import sys
sys.path.append('../')
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst
from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call

import pyds
import time
import random
import os
from PIL import Image
import numpy as np
import cv2
import json
from IPython import embed
project_dir = "/home/feifeichouchou/happy_lad/"
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3

WIDTH = 1920
HEIGHT = 1080
class ALL():
    def __init__(self):

        # Check input arguments

        # Standard GStreamer initialization
        Gst.init(None)

        # Create gstreamer elements
        print("Creating Pipeline \n")
        self.pipeline = Gst.Pipeline()

        if not self.pipeline:
            sys.stderr.write(" Unable to create Pipeline \n")

        # Source element for reading the image files
        print("Creating Source \n")
        self.source = Gst.ElementFactory.make("v4l2src", "usb-cam-source")
        if not self.source:
            sys.stderr.write(" Unable to create Source \n")

        # Set resolution using capsfilter
        caps = Gst.Caps.from_string("image/jpeg, width=%s, height=%s, framerate=30/1"%(WIDTH, HEIGHT)) 
        caps_filter = Gst.ElementFactory.make("capsfilter", "caps-filter")
        if not caps_filter:
            sys.stderr.write(" Unable to create capsfilter \n")

        caps_filter.set_property("caps", caps)

        # Set resolution using capsfilter
        caps2 = Gst.Caps.from_string("video/x-raw(memory:NVMM),format=RGBA") 
        caps_filter2 = Gst.ElementFactory.make("capsfilter", "caps-filter2")
        if not caps_filter2:
            sys.stderr.write(" Unable to create capsfilter2 \n")

        caps_filter2.set_property("caps", caps2)

        # Decode JPEG image
        jpegdec = Gst.ElementFactory.make("jpegdec", "jpeg-decoder")
        if not jpegdec:
            sys.stderr.write(" Unable to create jpegdec \n")

        # Video conversion to NV12 format for processing by nvinfer
        vidconv = Gst.ElementFactory.make("videoconvert", "video-converter")
        if not vidconv:
            sys.stderr.write(" Unable to create videoconvert \n")

        nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "nv-video-converter")
        if not nvvidconv:
            sys.stderr.write(" Unable to create nvvideoconvert \n")

        # Create nvstreammux instance to form batches from one or more sources.
        streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
        if not streammux:
            sys.stderr.write(" Unable to create NvStreamMux \n")

        # Use nvinfer to run inferencing on image frames.
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        if not pgie:
            sys.stderr.write(" Unable to create pgie \n")

        # Convert from NV12 to RGBA as required by nvosd
        nvvidconv_osd = Gst.ElementFactory.make("nvvideoconvert", "convertor-osd")
        if not nvvidconv_osd:
            sys.stderr.write(" Unable to create nvvideoconvert for OSD \n")

        # Create OSD to draw on the processed image
        nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
        if not nvosd:
            sys.stderr.write(" Unable to create nvosd \n")

        # Create UDPSink to send data to a remote host
        udpsink = Gst.ElementFactory.make("udpsink", "udpsink")
        if not udpsink:
            sys.stderr.write(" Unable to create udpsink \n")

        # Set the UDP destination address and port
        udpsink.set_property('host', '127.0.0.1')  # Replace with target IP
        udpsink.set_property('port', 8554)

        # Set the properties for streammux
        streammux.set_property('width', WIDTH)
        streammux.set_property('height', HEIGHT)
        streammux.set_property('batch-size', 1)
        streammux.set_property('batched-push-timeout', 4000000)
        pgie.set_property('config-file-path', "dstest1_pgie_config.txt")

        # Add elements to self.pipeline
        self.pipeline.add(self.source)
        self.pipeline.add(caps_filter)
        self.pipeline.add(jpegdec)
        self.pipeline.add(vidconv)
        self.pipeline.add(nvvidconv)
        self.pipeline.add(streammux)
        self.pipeline.add(pgie)
        self.pipeline.add(nvvidconv_osd)
        self.pipeline.add(caps_filter2)
        self.pipeline.add(nvosd)
        self.pipeline.add(udpsink)

        # Link elements in the self.pipeline
        self.source.link(caps_filter)
        caps_filter.link(jpegdec)
        jpegdec.link(vidconv)
        vidconv.link(nvvidconv)

        # Muxing video stream and inference
        sinkpad = streammux.get_request_pad("sink_0")
        srcpad = nvvidconv.get_static_pad("src")
        srcpad.link(sinkpad)

        streammux.link(pgie)
        pgie.link(nvvidconv_osd)
        nvvidconv_osd.link(caps_filter2)
        caps_filter2.link(nvosd)
        nvosd.link(udpsink)


        # Add probe to retrieve metadata
        osdsinkpad = nvosd.get_static_pad("sink")
        osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, self.osd_sink_pad_buffer_probe, self)


    def load_config(self, device_location, config_file):
        self.configs = json.load(open(project_dir+config_file))
        self.sample_chance = (200*1024*2)/(self.configs['time_span']*365*24*3600*30)
        self.room_name= self.configs['room_name']
        self.cold_down_seconds = self.configs['cold_down_hours'] * 3600
        self.now_lottery_chance = random.random()
        self.last_sample_time = 0
        self.source.set_property('device', device_location)

    def osd_sink_pad_buffer_probe(self, pad, info, u_data):
        def do_sample():
            frame = pyds.get_nvds_buf_surface(hash(gst_buffer), 0)
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)
            cv2.imwrite(project_dir+"/images/"+img_name, frame)
            resized_frame = cv2.resize(frame, (int(WIDTH/2), int(HEIGHT/2)), interpolation=cv2.INTER_AREA)
            cv2.imwrite(project_dir+"/images/latest.jpg", resized_frame)
            return
        frame_number = 0
        # Initializing object counter with 0.
        obj_counter = {
            PGIE_CLASS_ID_VEHICLE: 0,
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_BICYCLE: 0,
            PGIE_CLASS_ID_ROADSIGN: 0
        }
        num_rects = 0

        gst_buffer = info.get_buffer()
        if not gst_buffer:
            print("Unable to get GstBuffer ")
            return

        # Retrieve batch metadata from the gst_buffer
        batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
        l_frame = batch_meta.frame_meta_list
        while l_frame is not None:
            try:
                frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
            except StopIteration:
                break

            frame_number = frame_meta.frame_num
            num_rects = frame_meta.num_obj_meta
            l_obj = frame_meta.obj_meta_list
            while l_obj is not None:
                try:
                    obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
                except StopIteration:
                    break
                obj_counter[obj_meta.class_id] += 1
                try:
                    l_obj = l_obj.next
                except StopIteration:
                    break

            # Get current timestamp
            timestamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
            # 我的存图逻辑
            img_name = "{}_{}.jpg".format(self.room_name, timestamp.replace("/", "-").replace(" ", "_").replace(":","-"))
            self.not_sample_chance = 1 - (self.sample_chance * obj_counter[PGIE_CLASS_ID_PERSON])
            self.up_to_now_time = time.time() - self.last_sample_time
            if self.up_to_now_time >= self.cold_down_seconds:
                self.now_lottery_chance = 1   
                self.last_sample_time = time.time()
            if self.now_lottery_chance >= self.not_sample_chance:
                do_sample()
                print(f"Sampled @{self.now_lottery_chance} with not chance {self.not_sample_chance*100}%%: {img_name}"*100)
            # 下次抽奖几率
            self.now_lottery_chance = random.random()

            display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
            display_meta.num_labels = 1
            py_nvosd_text_params = display_meta.text_params[0]

            py_nvosd_text_params.display_text = "not_sample_chance={}  Time={} Frame Number={} Sample_Chance={} lottery_get={} Up_to_now_Sec={} Number of Objects={} Vehicle_count={} Person_count={} Configs={} ".format(
                self.not_sample_chance, timestamp, frame_number, self.sample_chance, self.now_lottery_chance, self.up_to_now_time, num_rects, obj_counter[PGIE_CLASS_ID_VEHICLE], obj_counter[PGIE_CLASS_ID_PERSON], self.configs)

            py_nvosd_text_params.x_offset = 10
            py_nvosd_text_params.y_offset = 12
            py_nvosd_text_params.font_params.font_name = "Serif"
            py_nvosd_text_params.font_params.font_size = 10
            py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
            py_nvosd_text_params.set_bg_clr = 1
            py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
            
            print(pyds.get_string(py_nvosd_text_params.display_text))
            pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
            
            try:
                l_frame = l_frame.next
            except StopIteration:
                break

        return Gst.PadProbeReturn.OK

    def run_pipe(self):
        # Create event loop and watch for messages from the bus
        loop = GLib.MainLoop()
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", bus_call, loop)
        # Start playback and listen to events
        print("Starting self.pipeline \n")
        self.pipeline.set_state(Gst.State.PLAYING)
        try:
            loop.run()
        except:
            pass
        # Clean up
        self.pipeline.set_state(Gst.State.NULL)


# # Just for Test, run in web.py
if __name__ == '__main__':
    all = ALL()
    all.load_config("/dev/video0", "config.json")
    print("Starting in 3 sec!!!!!!!!!!!!!!")
    time.sleep(3)
    all.run_pipe()
