#!/usr/bin/env python3
"""Adapt AVISPA HLPSL2IF state-fact layout to OFMC 2012c/2024 input layout.
Only move final state session-ID field to position 2 in state facts and signatures.
No network messages, initial sessions, role transitions, or attack goals are changed.
"""
import argparse, re, json, hashlib
from pathlib import Path

def split_args(s):
    depth=0; start=0; result=[]
    for i,c in enumerate(s):
        if c=='(': depth+=1
        elif c==')': depth-=1
        elif c==',' and depth==0:
            result.append(s[start:i]); start=i+1
    result.append(s[start:]); return result

def adapt(s, reverse=False):
    def move(a):
        if len(a)<3: raise ValueError('Invalid state argument list')
        return ([a[0]]+a[2:]+[a[1]]) if reverse else ([a[0],a[-1]]+a[1:-1])
    def sig(m):
        return m.group(1)+" * ".join(move([a.strip() for a in m.group(2).split('*')]))+m.group(3)
    s=re.sub(r'^(state_[A-Za-z0-9_]+:\s*)(.+?)(\s*->\s*fact\s*)$',sig,s,flags=re.M)
    out=[]; cur=0
    for m in re.finditer(r'\bstate_[A-Za-z0-9_]+\(',s):
        if m.start()<cur: continue
        start=m.end(); pos=start; depth=1
        while depth:
            if pos>=len(s): raise ValueError('Unbalanced state fact')
            if s[pos]=='(': depth+=1
            elif s[pos]==')': depth-=1
            pos+=1
        out.append(s[cur:start]);out.append(','.join(move(split_args(s[start:pos-1]))));out.append(')');cur=pos
    out.append(s[cur:]);return ''.join(out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('output',type=Path);args=p.parse_args()
    if args.input.resolve()==args.output.resolve(): raise ValueError('Keep the raw IF unchanged; choose a separate output')
    source=args.input.read_text()
    if args.input.resolve()==args.output.resolve(): raise ValueError('Keep the original IF')
    signatures=re.findall(r'^(state_[A-Za-z0-9_]+):\s*(.*?)\s*->\s*fact',source,re.M)
    if not signatures: raise ValueError('No state signatures')
    for name,signature in signatures:
        types=[x.strip() for x in signature.split('*')]
        if types[0]!='agent' or types[-1]!='nat' or types[1]=='nat':
            raise ValueError('Expected unadapted SPAKA state layout: actor, parameters, session ID')
    target=adapt(source)
    if source.split('section attack_states:',1)[1]!=target.split('section attack_states:',1)[1]:
        raise ValueError('Attack goals changed')
    # Check structural reversibility modulo signature whitespace.
    normalize=lambda t: re.sub(r'\s+',' ',t).strip()
    if normalize(adapt(target,True))!=normalize(source): raise ValueError('Round-trip failed')
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(target)
    digest=lambda text: hashlib.sha256(text.encode()).hexdigest()
    manifest=dict(input=str(args.input), output=str(args.output), input_sha256=digest(source),
        output_sha256=digest(target), operation="Move last state field (SID) to second position, including signatures",
        reversible=True, attack_states_byte_identical=True, state_signatures=[n for n,_ in signatures])
    args.output.with_suffix('.adapter.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest))
