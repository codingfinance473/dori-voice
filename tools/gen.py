"""작업 하나(task)를 실행해 out/<jid>/<task>/ 에 wav 와 meta.json 을 쓴다.

  python tools/gen.py jobs/<작업>.json <task id>
"""
import json, os, sys, time
from pathlib import Path

import numpy as np
import soundfile as sf
import torch


def main(job_path, task_id):
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    task = next(t for t in job["tasks"] if t["id"] == task_id)
    out = Path("out") / job["id"] / task["id"]
    out.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(os.cpu_count() or 2)
    from qwen_tts import Qwen3TTSModel
    t0 = time.time()
    dtype = {"bf16": torch.bfloat16, "fp32": torch.float32}[task.get("dtype", "bf16")]
    m = Qwen3TTSModel.from_pretrained(task["model"], device_map="cpu", dtype=dtype)
    meta = {"task": task, "load_s": round(time.time() - t0, 1), "cpu": os.cpu_count(), "outputs": []}
    print(f"[{task_id}] 모델 준비 {meta['load_s']}s", flush=True)
    lang = task.get("language", "Korean")
    gen = task.get("gen", {})
    prompt = None
    if task["mode"] == "clone":
        ref = Path(task["voice"])
        wav, sr = sf.read(ref / "ref.wav", dtype="float32")
        prompt = m.create_voice_clone_prompt(ref_audio=(wav, sr), ref_text=(ref / "ref.txt").read_text(encoding="utf-8").strip())
    for ti, text in enumerate(task["texts"]):
        for k in range(int(task.get("takes", 1))):
            torch.manual_seed(int(task.get("seed", 0)) * 1000 + ti * 10 + k)
            s = time.time()
            if task["mode"] == "design":
                wavs, sr = m.generate_voice_design(text=text, language=lang, instruct=task["instruct"], **gen)
            elif task["mode"] == "custom":
                wavs, sr = m.generate_custom_voice(text=text, language=lang, speaker=task["speaker"], instruct=task.get("instruct", ""), **gen)
            elif task["mode"] == "clone":
                wavs, sr = m.generate_voice_clone(text=text, language=lang, voice_clone_prompt=prompt, **gen)
            else:
                raise SystemExit(f"모르는 mode: {task['mode']}")
            w = np.asarray(wavs[0], dtype=np.float32)
            f = out / f"{ti:02d}_{k}.wav"
            sf.write(f, w, sr)
            rec = {"file": f.name, "text_index": ti, "take": k, "sec": round(len(w) / sr, 2), "gen_s": round(time.time() - s, 1), "sr": sr}
            meta["outputs"].append(rec)
            print(f"[{task_id}] {rec}", flush=True)
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
