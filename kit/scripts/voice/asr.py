"""한국어 받아쓰기(sherpa-onnx zipformer). 모델은 setup.sh 가 DORI_CACHE 에 받아 둔다."""
import os
from pathlib import Path
import numpy as np, sherpa_onnx
from scipy.io import wavfile
from scipy.signal import resample_poly

A = Path(os.environ.get("DORI_ASR") or Path(os.environ.get("DORI_CACHE", Path.home() / ".cache/dori-shorts")) / "sherpa-onnx-zipformer-korean-2024-06-24")
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=str(A / "encoder-epoch-99-avg-1.int8.onnx"), decoder=str(A / "decoder-epoch-99-avg-1.onnx"),
    joiner=str(A / "joiner-epoch-99-avg-1.int8.onnx"), tokens=str(A / "tokens.txt"), num_threads=2, decoding_method="greedy_search")


def transcribe(path):
    sr, x = wavfile.read(path)
    x = x.astype(np.float32) / 32768
    if x.ndim > 1: x = x.mean(1)
    if sr != 16000: x = resample_poly(x, 16000, sr).astype(np.float32)
    s = rec.create_stream(); s.accept_waveform(16000, x); rec.decode_stream(s)
    return s.result.text
