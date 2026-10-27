"""이번 push 로 새로 올라온 jobs/*.json 을 읽어 작업 매트릭스(JSON)를 출력한다."""
import json, subprocess, sys
from pathlib import Path


def changed():
    try:
        out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", "HEAD~1", "HEAD", "--", "jobs/"],
                             capture_output=True, text=True, check=True).stdout.split()
    except subprocess.CalledProcessError:          # 첫 커밋
        out = subprocess.run(["git", "ls-files", "jobs/"], capture_output=True, text=True).stdout.split()
    return [f for f in out if f.endswith(".json")]


files = [f for f in sys.argv[1:] if f] or changed()
inc = []
for f in files:
    j = json.loads(Path(f).read_text(encoding="utf-8"))
    if (Path("out") / j["id"] / "done.json").exists():
        continue                                    # 이미 만든 작업은 건너뛴다
    for t in j["tasks"]:
        inc.append({"job": f, "jid": j["id"], "task": t["id"]})
print(json.dumps({"include": inc}, ensure_ascii=False))
