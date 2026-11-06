#!/usr/bin/env python3
"""Reproduce the declared goals of the two manuscript models and normal executions."""
import argparse, hashlib, json, os, pathlib, platform, re, shutil, subprocess, sys, time
ROOT = pathlib.Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def split_args(text):
    out, start, depth = [], 0, 0
    for i, char in enumerate(text):
        if char in "({[": depth += 1
        elif char in ")}]": depth -= 1
        elif char == "," and depth == 0: out.append(text[start:i].strip()); start = i + 1
    out.append(text[start:].strip())
    return out
def state_terms(text):
    result = []
    for m in re.finditer(r"\b(state_[A-Za-z0-9_]+)\(", text):
        start = pos = m.end(); depth = 1
        while depth:
            if pos >= len(text): raise ValueError("Unbalanced state fact")
            depth += (text[pos] == "(") - (text[pos] == ")"); pos += 1
        result.append((m.group(1), split_args(text[start:pos-1])))
    return result
def layout(raw):
    text = raw.read_text()
    state_slots = {}
    for name, signature in re.findall(r"(?m)^(state_\w+):\s*(.*?)\s*->\s*fact", text):
        state_slots[name] = [x.strip() for x in signature.split("*")].index("nat")
    key_slots = {}
    for name, args in state_terms(text):
        for key in ("SK_local", "SK_new", "SK_cv"):
            if key in args:
                key_slots.setdefault(name, {}).setdefault(key, set()).add(args.index(key))
    keys = {}
    for name, slots in key_slots.items():
        keys[name] = {}
        for key, indices in slots.items():
            if len(indices) != 1: raise ValueError("Ambiguous key slot")
            keys[name][key] = next(iter(indices))
    return state_slots, keys
def checked_trace_constraint(text, raw):
    """Evaluate only booleans and inequalities of distinct generated fresh atoms.

    Unsupported residual constraints fail closed. Printed N(step) names must
    correspond to existential fresh declarations in the actual translator IF.
    This checks a selected execution, never changes a backend search verdict.
    """
    clauses = re.findall(r"(?m)^\s*where (.+)$", text)
    if len(clauses) != 1: return None
    expression = clauses[0].strip()
    fresh = set()
    for declaration in re.findall(r"=\[exists ([^]]+)\]=>", raw.read_text()):
        fresh.update(x.strip() for x in declaration.split(","))
    evaluated = []
    def inequality(match):
        left, li, right, ri = match.groups()
        if left not in fresh or right not in fresh: return "UNSUPPORTED"
        value = (left, li) != (right, ri)
        evaluated.append(dict(left=f"{left}({li})", right=f"{right}({ri})", value=value))
        return str(value)
    reduced = re.sub(r"([A-Z]\w*)\((\d+)\)\s*/=\s*([A-Z]\w*)\((\d+)\)", inequality, expression)
    tokens = re.findall(r"True|False|and|or|[()]", reduced)
    if "".join(tokens) != re.sub(r"\s+", "", reduced): return None
    pos = 0
    def atom():
        nonlocal pos
        token = tokens[pos]; pos += 1
        if token in ("True", "False"): return token == "True"
        if token != "(": raise ValueError("Unsupported constraint")
        value = disjunction()
        if tokens[pos] != ")": raise ValueError("Unbalanced constraint")
        pos += 1
        return value
    def conjunction():
        nonlocal pos
        value = atom()
        while pos < len(tokens) and tokens[pos] == "and":
            pos += 1; right = atom(); value = value and right
        return value
    def disjunction():
        nonlocal pos
        value = conjunction()
        while pos < len(tokens) and tokens[pos] == "or":
            pos += 1; right = conjunction(); value = value or right
        return value
    try: value = disjunction()
    except (IndexError, ValueError): return None
    if pos != len(tokens) or not value: return None
    return dict(expression=expression, fresh_inequalities=evaluated, satisfied=True)

def inspect_trace(text, raw, kind):
    state_slots, key_slots = layout(raw)
    # Only the reached state, before postponed alternatives or intruder state.
    state_text = text.split("postponed:", 1)[0].split("ik state:", 1)[0]
    terms = dict(state_terms(state_text))
    targets = ({"state_local_v":"4", "state_local_ataj":"3"} if kind == "local" else
        {"state_cross_cv":"2", "state_cross_atai":"3", "state_cross_ta":"2", "state_cross_ataj":"1"})
    reached = {name: terms[name][state_slots[name]] for name in targets if name in terms}
    if reached != targets: return None
    peers = ("state_local_v","state_local_ataj") if kind == "local" else ("state_cross_cv","state_cross_atai")
    keys = ("SK_local","SK_new") if kind == "local" else ("SK_cv",)
    equal = {}
    for key in keys:
        values = [terms[p][key_slots[p][key]] for p in peers]
        if values[0] != values[1] or "dummy_" in values[0]: return None
        equal[key] = values[0]
    witnesses = {tuple(split_args(line[len("witness("):-1])) for line in state_text.splitlines() if line.startswith("witness(") and line.endswith(")")}
    requests = [split_args(line[len("request("):-1]) for line in state_text.splitlines() if line.startswith("request(") and line.endswith(")")]
    matched = all(tuple([r[1],r[0],*r[2:-1]]) in witnesses for r in requests)
    expected = 4 if kind == "local" else 2
    if len(requests) != expected or not matched: return None
    constraint = checked_trace_constraint(text, raw)
    if constraint is None: return None
    return dict(terminal_states=reached, equal_keys=equal, matched_requests=len(requests),
        constraint_check=constraint,
        scope="One completed symbolic execution; not an attack-search result")
def goal_block(path):
    s=re.sub(r"%[^\n]*","",path.read_text())
    return s.split("\ngoal\n",1)[1].split("\nend goal",1)[0].strip()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=pathlib.Path,default=ROOT/"validation-output")
    args=ap.parse_args(); out=args.output.resolve()
    if out==ROOT: raise SystemExit("Use a separate output directory")
    for name in ("models","if","ofmc_if","results","execution"):
        (out/name).mkdir(parents=True,exist_ok=True)
    report=dict(source_commit=os.getenv("GITHUB_SHA") or subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        run_id=os.getenv("GITHUB_RUN_ID"), platform=platform.platform(), tools={}, models={},
        interpretation="SAFE applies to the declared security goals of these two models in the stated bounded-session setting.")
    def save(): (out/"verification_manifest.json").write_text(json.dumps(report,indent=2)+"\n")
    def run(command, log, timeout=90):
        start=time.monotonic()
        try:
            proc=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
            data,code,timed=proc.stdout,proc.returncode,False
        except subprocess.TimeoutExpired as e: data,code,timed=e.stdout or b"",None,True
        log.write_bytes(data)
        text=data.decode(errors="replace")
        match=re.search(r"SUMMARY:?\s+([A-Z_]+)",text)
        item=dict(command=command,exit_code=code,timeout=timed,seconds=round(time.monotonic()-start,3),
            log=str(log.relative_to(out)),sha256=sha(log),summary=match.group(1) if match else None)
        print(json.dumps({k:item[k] for k in ("log","exit_code","summary","timeout")}),flush=True)
        return item
    bins={}
    for name in ("hlpsl2if","ofmc","cl-atse"):
        path=shutil.which(name)
        if not path: raise SystemExit("Missing "+name)
        bins[name]=path
    bins["ofmc2024"]=os.environ.get("OFMC2024","")
    if not pathlib.Path(bins["ofmc2024"]).is_file(): raise SystemExit("Set OFMC2024 to the pinned executable")
    for name,path in bins.items():
        report["tools"][name]=dict(path=path,sha256=sha(pathlib.Path(path)),
            version=run([path,"--version"],out/"results"/(name+"_version.txt"),15))
    failures=[]
    declared = json.loads((ROOT/"docs/declared_goals.json").read_text())
    source_files = [*sorted((ROOT/"models").glob("*.hlpsl")), *sorted((ROOT/"scripts").glob("*")), ROOT/"docs/declared_goals.json"]
    report["verification_source_sha256"] = {str(p.relative_to(ROOT)):sha(p) for p in source_files if p.is_file()}
    cases=[("models/spaka_local_auth_key_update.hlpsl","local","SAFE"),
           ("models/spaka_cross_region.hlpsl","cross","SAFE")]
    for source,kind,expected in cases:
        src=ROOT/source; stem=src.stem; model=out/source
        shutil.copyfile(src,model)
        item=dict(source=source,source_sha256=sha(src),expected_audit_result=expected,checks={})
        report["models"][stem]=item
        actual_goals = [line.strip() for line in goal_block(src).splitlines() if line.strip()]
        if actual_goals != declared[source]: raise SystemExit("Declared goals changed: "+source)
        item["declared_goals_preserved"] = True
        item["declared_goals"] = actual_goals
        item["translation"]=run([bins["hlpsl2if"],str(model)],out/"results"/(stem+"_hlpsl2if.txt"))
        generated=model.with_suffix(".if")
        if item["translation"]["exit_code"]!=0 or not generated.is_file():
            failures.append(stem+": translation");save();continue
        raw=out/"if"/(stem+".if");shutil.move(generated,raw)
        item["if_sha256"]=sha(raw)
        raw_text = raw.read_text()
        if kind == "local":
            checks = {"ata_cache_guard_translated": "not(equal(Ci_next,Ci))" in raw_text}
        else:
            checks = {
                "protected_confirmation_receive": "iknows(scrypt(SK_cv,apply(H,pair(P2,T8))))" in raw_text,
                "derived_symmetric_key_send": "iknows(scrypt(apply(H," in raw_text,
            }
        item["model_correction_checks"] = checks
        if not all(checks.values()): failures.append(stem+": model correction translation")
        adapted=out/"ofmc_if"/(stem+".if")
        item["adapter"]=run([sys.executable,str(ROOT/"scripts/adapt_ofmc_if.py"),str(raw),str(adapted)],out/"results"/(stem+"_adapter.txt"))
        if item["adapter"]["exit_code"]!=0: failures.append(stem+": adapter");save();continue
        item["ofmc_if_sha256"]=sha(adapted)
        checks=[("ofmc",[bins["ofmc"],"--classic",str(adapted)]),
                ("ofmc2024",[bins["ofmc2024"],"--classic",str(adapted)]),
                ("clatse",[bins["cl-atse"],str(raw)]),
                ("clatse_noopt",[bins["cl-atse"],"-noopt",str(raw)])]
        for name,command in checks:
            result=run(command,out/"results"/(stem+"_"+name+".txt"))
            item["checks"][name]=result
            wanted="NO_ATTACK_FOUND" if name=="ofmc2024" else "SAFE"
            if result["exit_code"]!=0 or result["summary"]!=wanted: failures.append(stem+": "+name)
        if kind:
            # Start with a known transition schedule, then explore actual successors if needed.
            preferred=[0,0,0,1,0,0,0] if kind=="local" else [0]*8
            pending=[preferred,[0]];seen=set();found=None;attempts=[]
            while pending and len(seen)<60:
                path=pending.pop(0);key=tuple(path)
                if key in seen:continue
                seen.add(key)
                log=out/"execution"/(stem+"_trace_"+"_".join(map(str,path))+".txt")
                result=run([bins["ofmc2024"],"--classic","--trace",*map(str,path),str(adapted)],log,15)
                attempts.append(dict(path=path,**result))
                text=log.read_text(errors="replace")
                if result["exit_code"]==0:
                    found=inspect_trace(text,raw,kind)
                    if found:
                        found.update(path=path,log=str(log.relative_to(out)),log_sha256=sha(log));break
                    if len(path)<9:
                        pending.extend(path+[int(n)] for n in re.findall(r"(?m)^\((\d+)\)\s*$",text))
            item["execution"]=dict(attempts=attempts,completed=found)
            if found is None:failures.append(stem+": completed execution")
        save()
    report["validation_failures"]=failures
    report["capture_complete"]=not failures
    save()
    if failures:raise SystemExit("Verification workflow failures: "+", ".join(failures))
    print("Both manuscript models passed their declared bounded-session goals and completed-execution checks.")
if __name__=="__main__":main()
