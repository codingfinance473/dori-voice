import sys,json,glob,re; sys.path.insert(0,'voice')
import numpy as np, parselmouth
from scipy.io import wavfile
from scipy.signal import resample_poly
from asr import rec
def tr(x):
    s=rec.create_stream(); s.accept_waveform(16000,x); rec.decode_stream(s); return s.result.text
L={l['id']:l for l in json.load(open('voice/lines.json',encoding='utf-8'))}
job=json.load(open('/home/claude/dori-voice/jobs/ex13-05.json'))
ids=["M01m","M01m","M06m","M06m","M07m","M07m","M03m","M03m","M04m","M04m","M08m","M08m"]
res={}
for ti,t in enumerate(job['tasks'][:12]):
    lid=ids[ti]; keys=L[lid]['keys']; n=len(re.sub(r'[\s,.~?!]','',L[lid]['say']))
    for f in sorted(glob.glob(f"/home/claude/dori-voice/out/ex13-05/{t['id']}/*.wav")):
        sr,x=wavfile.read(f); x=x.astype(np.float32); x=x/32768 if np.abs(x).max()>2 else x
        y=resample_poly(x,16000,sr).astype(np.float32); txt=tr(y)
        ok=all(k.replace(' ','') in txt.replace(' ','') for k in keys)
        snd=parselmouth.Sound(y,16000); p=snd.to_pitch(time_step=.01,pitch_floor=75,pitch_ceiling=500).selected_array['frequency']
        v=p[p>0]; med=float(np.median(v)); st=12*np.log2(v/med); sd=float(np.std(st))
        jumps=int(np.sum(np.abs(np.diff(12*np.log2(np.where(p>0,p,np.nan))))>5))
        a=np.abs(y); env=np.convolve(a,np.ones(320)/320,'same'); th=.04*env.max(); on=env>th
        idx=np.where(on)[0]; dur=(idx[-1]-idx[0])/16000
        # 안쪽 긴 쉼
        gaps=0; run=0
        for b in on[idx[0]:idx[-1]]:
            run=run+1 if not b else 0
            if run==int(.45*16000): gaps+=1
        rate=n/dur
        score=(0 if ok else 100)+abs(sd-2.2)*6+jumps*2+max(0,140-med)/3+max(0,med-185)/3+abs(rate-6.3)*3+gaps*8
        res.setdefault(lid,[]).append((round(score,1),f.split('ex13-05/')[1],t['gen'] and 'b' or 'a',ok,round(med),round(sd,2),jumps,round(rate,1),gaps,round(dur,2),txt))
for lid,r in res.items():
    r.sort(); print(lid,L[lid]['say'])
    for row in r[:6]: print('  ',row)
json.dump({k:v[0][1] for k,v in res.items()},open('ab/mori_pick.json','w'),indent=1)
