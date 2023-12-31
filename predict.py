﻿import numpy as np
import soundfile as sf
import yaml
import tensorflow as tf
from tensorflow_tts.inference import TFAutoModel
from tensorflow_tts.inference import AutoProcessor
import python_supporter
import random
from pydub import AudioSegment
from langdetect import detect

import nltk
nltk.download('punkt')

#'''
# initialize fastspeech2 model.
fastspeech2_en = TFAutoModel.from_pretrained("tensorspeech/tts-fastspeech2-ljspeech-en")
# initialize mb_melgan model
mb_melgan_en = TFAutoModel.from_pretrained("tensorspeech/tts-mb_melgan-ljspeech-en")
# inference
processor_en = AutoProcessor.from_pretrained("tensorspeech/tts-fastspeech2-ljspeech-en")
#'''
#'''
# initialize fastspeech2 model.
fastspeech2_ko = TFAutoModel.from_pretrained("tensorspeech/tts-fastspeech2-kss-ko")
# initialize mb_melgan model
mb_melgan_ko = TFAutoModel.from_pretrained("tensorspeech/tts-mb_melgan-kss-ko")
# inference
processor_ko = AutoProcessor.from_pretrained("tensorspeech/tts-fastspeech2-kss-ko")
#'''

def text_to_speech(text, save_file):
    detected = detect(text)
    if detected == "ko":
        fastspeech2 = fastspeech2_ko
        mb_melgan = mb_melgan_ko
        processor = processor_ko
    else:
        fastspeech2 = fastspeech2_en
        mb_melgan = mb_melgan_en
        processor = processor_en
        
    input_ids = processor.text_to_sequence(text)

    # fastspeech inference
    mel_before, mel_after, duration_outputs, _, _ = fastspeech2.inference(
        input_ids=tf.expand_dims(tf.convert_to_tensor(input_ids, dtype=tf.int32), 0),
        speaker_ids=tf.convert_to_tensor([0], dtype=tf.int32),
        speed_ratios=tf.convert_to_tensor([1.0], dtype=tf.float32),
        f0_ratios =tf.convert_to_tensor([1.0], dtype=tf.float32),
        energy_ratios =tf.convert_to_tensor([1.0], dtype=tf.float32),
    )
    # melgan inference
    audio_before = mb_melgan.inference(mel_before)[0, :, 0]
    audio_after = mb_melgan.inference(mel_after)[0, :, 0]
    
    # save to file
    #sf.write('./audio_before.wav', audio_before, 22050, "PCM_16")
    #sf.write('./audio_after.wav', audio_after, 22050, "PCM_16")
    sf.write(save_file, audio_after, 22050, "PCM_16")

#https://stackoverflow.com/questions/59819936/adding-a-pause-in-google-text-to-speech
#pydub-concatenate-mp3-in-a-directory
#https://stackoverflow.com/questions/26363558/pydub-concatenate-mp3-in-a-directory
def test_to_speech_break(text, save_file):
    #text = "Hello with <break><break> 1 seconds pause"
    #print(text)
    parts = text.split("<break>") # I have chosen this symbol for the pause.
    #print(parts)
    temp = []
    for i, part in enumerate(parts): 
        part = part.strip()
        if part:
            temp.append(part)
        if i != len(parts) - 1:
            temp.append("<break>")
    parts = temp
    #print(parts)
    pause1s = AudioSegment.from_mp3("predict_inputs/pause_05second.mp3") 
    cnt = 0
    combined = AudioSegment.empty()
    for part in parts:
        # The pause will happen for the empty element of the list
        if not part:
            #print("1:", part)
            pass
        if part == "<break>":
            #print("2:", part)
            combined += pause1s
        else:
            #print("3:", part)
            tmpFileName = "predict_inputs/tmp"+str(cnt)+".wav"
            text_to_speech(part, tmpFileName)
            combined+=AudioSegment.from_mp3(tmpFileName) 
        cnt+=1     
    combined.export(save_file, format="mp3") 
    
if __name__ == "__main__":
    #text = "Hello with <break><break> 2 seconds pause"
    #text = "안녕하세요 <break><break> 반갑습니다"
    text = python_supporter.file.read_file("predict_inputs/inputs.txt")
    #python에서 \ufeff가 읽힐 때 해결방법
    #https://frhyme.github.io/python-basic/py_eff_byte_order_mark/
    text = text.replace("\ufeff", "")
    test_to_speech_break(text, "predict_outputs/outputs.mp3")