import os
import io
import sys
import zipfile
from scipy.io import wavfile

def format_sample(sample):
    start = 0
    stop = len(wavfile.read(sample.filename)[1])
    basename = os.path.basename(sample.filename)
    s = f"""<sample file="{basename}" sample-start="{start}" sample-stop="{stop}" zone-logic="always-play">
    <key root="{sample.note_root}" high="{sample.note_max}" low="{sample.note_min}" track="1.0" tune="0.0"/>
    <velocity/>
    <select/>
    <loop fase="0.0" mode="loop" start="{sample.loop_start}" stop="{sample.loop_stop}"/>
</sample>
"""
    return s

def format_xml(filename, sample):
    generator = "samplegen"
    name = os.path.splitext(os.path.basename(filename))[0].replace("_", " ")
    content = format_sample(sample).rstrip()
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<multisample name="{name}">
    <generator>{generator}</generator>
    <category></category>
    <creator>{generator}</creator>
    <description/>
    <keywords/>
    {content}
</multisample>
"""
    return xml

def write_single(filename, sample):
    mem_zip = io.BytesIO()
    mem_xml = io.StringIO()
    
    xml = format_xml(filename, sample)
    mem_xml.write(xml)
    mem_xml.seek(0)
    
    with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        # Write XML to archive
        zf.writestr("multisample.xml", mem_xml.getvalue())

        # Write audio to archive
        basename = os.path.basename(sample.filename)
        zf.write(sample.filename, basename)
    mem_zip.seek(0)
    
    with open(filename, "wb") as f:
        f.write(mem_zip.getvalue())    

