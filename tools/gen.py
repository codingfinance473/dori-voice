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
    # CPU 확인: bf16 을 빠르게 계산하는 CPU(AVX512-BF16·AMX)면 bf16, 아니면 작은 모델(0.6B)은 fp32 가 훨씬 빠르다
    info = Path("/proc/cpuinfo").read_text() if Path("/proc/cpuinfo").exists() else ""
    cpu = next((l.split(":", 1)[1].strip() for l in info.splitlines() if l.startswith("model name")), "?")
    fast_bf16 = ("avx512_bf16" in info) or ("amx_bf16" in info)
    want = task.get("dtype", "auto")
    if want == "auto":
        want = "bf16" if (fast_bf16 or "1.7B" in task["model"]) else "fp32"
    dtype = {"bf16": torch.bfloat16, "fp32": torch.float32}[want]
    m = Qwen3TTSModel.from_pretrained(task["model"], device_map="cpu", dtype=dtype)
    meta = {"task": task, "load_s": round(time.time() - t0, 1), "cpu": os.cpu_count(), "cpu_model": cpu, "fast_bf16": fast_bf16,
            "dtype": want, "outputs": []}
    print(f"[{task_id}] CPU {cpu} · bf16 가속 {fast_bf16} · {want}", flush=True)
    print(f"[{task_id}] 모델 준비 {meta['load_s']}s", flush=True)
    lang = task.get("language", "Korean")
    prompt = None
    if task["mode"] == "clone":
        ref = Path(task["voice"])
        wav, sr = sf.read(ref / "ref.wav", dtype="float32")
        prompt = m.create_voice_clone_prompt(ref_audio=(wav, sr), ref_text=(ref / "ref.txt").read_text(encoding="utf-8").strip())
    for ti, text in enumerate(task["texts"]):
        for k in range(int(task.get("takes", 1))):
            torch.manual_seed(int(task.get("seed", 0)) * 1000 + ti * 10 + k)
            # 멈추지 않고 계속 말하는 실패를 막는다: 12.5프레임/초, 한국어 초당 6~7자 → 글자당 3프레임이면 넉넉하다
            gen = {**task.get("gen", {})}
            gen.setdefault("max_new_tokens", 60 + 3 * len(text))
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
            (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[{task_id}] {rec}", flush=True)
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
