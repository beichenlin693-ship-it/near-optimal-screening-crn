"""Inputs: committed release files, SHA-256 manifest and source/trace records.
Outputs: build/verification.json and a concise PASS/FAIL message.
Runtime: seconds. Read-only verification of stored results; no experiments or simulator calls.
"""
from pathlib import Path
import csv,json,hashlib,importlib,sys,re,ast
import yaml
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(part in ['.git','build','__pycache__','.venv','venv'] for part in p.relative_to(ROOT).parts))
def main():
    checks=[]
    def check(name,passed,detail=''):
        checks.append(dict(check=name,passed=bool(passed),detail=detail))
    manifest=ROOT/'reproducibility/SHA256_MANIFEST.csv'
    if not manifest.exists():raise RuntimeError('Release manifest missing; obtain a complete release.')
    with manifest.open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
    paths=[r['path'] for r in rows]
    check('Manifest has unique safe relative paths',len(paths)==len(set(paths)) and all(not Path(x).is_absolute() and '..' not in Path(x).parts for x in paths))
    mismatches=[]
    for r in rows:
        p=ROOT/r['path']
        if not p.is_file() or p.stat().st_size!=int(r['bytes']) or sha(p)!=r['sha256']:mismatches.append(r['path'])
    check('SHA-256 and sizes match',not mismatches,mismatches)
    payload=[p for p in files() if p!=manifest]
    check('Manifest covers complete payload',set(paths)=={p.relative_to(ROOT).as_posix() for p in payload})
    if not all(c['passed'] for c in checks):
        for c in checks:
            if not c['passed']:print('FAIL:',c['check'],c['detail'])
        raise SystemExit('Manifest verification failed; no library code was imported.')
    with (ROOT/'reproducibility/source_artifacts.csv').open(encoding='utf-8',newline='') as f:sources=list(csv.DictReader(f))
    bad=[r['repository_path'] for r in sources if sha(ROOT/r['repository_path'])!=r['repository_sha256'] or (r['transformation']=='byte-identical' and r['source_artifact_sha256']!=r['repository_sha256'])]
    check('Copied source-artifact checks',not bad,bad)
    check('No large payload files',all(p.stat().st_size<10_000_000 for p in payload),'Conservative 10 MB release cap; large banks are documented separately.')
    forbidden=[p.relative_to(ROOT).as_posix() for p in payload if p.suffix in ['.zip','.parquet','.gz','.pkl','.pickle','.docx'] or p.name.startswith('MANUSCRIPT')]
    check('No raw archives, banks or manuscript PDFs',not forbidden,forbidden)
    textfiles=[p for p in payload if p.suffix in ['.py','.md','.json','.csv','.txt','.cff','.yaml']]
    leaks=[]
    for p in textfiles:
        t=p.read_text(encoding='utf-8-sig')
        if re.search(r'[A-Z]:[\\/]+Users[\\/]+[A-Za-z0-9_.-]+|/(?:Users|home)/[A-Za-z0-9_.-]+/|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{30,}',t):leaks.append(p.relative_to(ROOT).as_posix())
    check('No local user paths or credential patterns',not leaks,leaks)
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    check('Publication-facing README',not re.search(r'\bV[12](?:\.1)?\b|\bM[0-7](?:[–-]M?[0-7])?\b|reconstruction|handoff|audit phase',readme,re.I))
    sections=['Overview','Repository structure','Main methods','Experimental settings','WNBA simulation benchmark','Reproducing tables','Reproducing figures','External comparator analysis','Data provenance','Computational environment','Reproducibility notes','Citation','License','Contact']
    check('README required sections',all('## '+s in readme for s in sections))
    cff=yaml.safe_load((ROOT/'CITATION.cff').read_text(encoding='utf-8'))
    check('Citation identities and license',cff['cff-version']=='1.2.0' and cff['license']=='MIT' and len(cff['authors'])==2 and cff['authors'][0]['orcid']=='https://orcid.org/0009-0003-2486-0718' and 'doi' not in cff)
    check('MIT selection completed',(ROOT/'LICENSE').read_text().startswith('MIT License') and not (ROOT/'LICENSE_PENDING.md').exists())
    with (ROOT/'reproducibility/traceability.csv').open(encoding='utf-8',newline='') as f:trace=list(csv.DictReader(f))
    unresolved=[]
    for row in trace:
        for col in ['machine_readable_inputs','generating_script','configuration','seed_or_reference_source']:
            unresolved += [x for x in row[col].split(';') if not (ROOT/x).exists()]
    check('All 12 display chains resolve',len(trace)==12 and not unresolved,unresolved)
    broken=[]
    for p in [ROOT/'README.md',ROOT/'data/README.md',ROOT/'supplement/README.md']:
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if '://' not in target and not (p.parent/target.split('#')[0]).exists():broken.append(target)
    check('Local documentation links resolve',not broken,broken)
    imported=[]
    for p in sorted((ROOT/'src').rglob('*.py')):
        ast.parse(p.read_text(encoding='utf-8'))
        name='.'.join(p.relative_to(ROOT).with_suffix('').parts);importlib.import_module(name);imported.append(name)
    check('All library modules import',True,len(imported))
    eq=json.loads((ROOT/'reproducibility/code_equivalence.json').read_text(encoding='utf-8'))
    check('Recorded scientific AST comparisons',all(r['normalized_scientific_ast_equal'] for r in eq),len(eq))
    # Confirm strict epsilon and key adverse outcomes directly in stored summaries.
    import pandas as pd
    d=pd.read_csv(ROOT/'results/machine_readable/external/summary_table.csv',float_precision='round_trip')
    a=d[(d.environment=='Synthetic G2')&(~d.crn)&(d.procedure=='DSTTB-setwise-2023')].iloc[0]
    b=d[(d.environment=='Synthetic G2')&(~d.crn)&(d.procedure=='epsilon-CPC-SH')].iloc[0]
    check('Adverse DSTTB comparison retained',abs(a.active_set_size_mean-18.786)<1e-12 and abs(b.active_set_size_mean-21.669)<1e-12)
    v=pd.read_csv(ROOT/'results/machine_readable/formal/variance_diagnostics.csv',float_precision='round_trip')
    check('Near-tie VRR retained',round(float(v.iloc[0].VRR),2)==291.81)
    output=ROOT/'build';output.mkdir(exist_ok=True)
    receipt={'status':'PASS' if all(c['passed'] for c in checks) else 'FAIL','checks':checks,'scientific_result_modifications':0,'new_experiments':0,'new_simulator_calls':0,'scope':'Hash/source/traceability/import verification only. Run the two display-reproduction commands to verify regenerated displays.'}
    (output/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(receipt['status']+f': {sum(c["passed"] for c in checks)}/{len(checks)} checks; {len(rows)} manifest entries; 0 simulator calls.')
    for c in checks:
        if not c['passed']:print('FAIL:',c['check'],c['detail'])
    if receipt['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
