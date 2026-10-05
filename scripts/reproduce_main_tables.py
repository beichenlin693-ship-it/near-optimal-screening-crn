"""Inputs: approved display-row CSVs, stored numerical summaries, rendering config.
Outputs: five TeX tables in build/main_tables (or --output-dir).
Runtime: seconds. Reproduces existing displays; no simulation or new inference.
"""
from pathlib import Path
import argparse,csv,json,hashlib
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def numeric_rows(stem):
    if stem=='Table3_external':
        d=pd.read_csv(ROOT/'results/machine_readable/external/summary_table.csv',float_precision='round_trip')
        out=[]
        for r in d.itertuples():
            short='CPC' if r.procedure=='epsilon-CPC-SH' else next((n for n in ['DSTTB','B1','B2'] if r.procedure.startswith(n)), 'Uniform')
            if short=='Uniform':continue
            power=f'{r.screening_power_mean:.3f}' if pd.notna(r.screening_power_mean) else f'[{r.screening_power_mean_bound_low:.6f}, {r.screening_power_mean_bound_high:.6f}]'
            out.append([r.environment.replace('Synthetic ','')+(' ON' if r.crn else ' OFF'),short,f'{r.preservation_successes}/{r.M}',f'{r.active_set_size_mean:.3f} [{r.active_set_size_mean_ci_low:.3f}, {r.active_set_size_mean_ci_high:.3f}]',power])
        return out
    if stem=='Table4_recommendation':
        d=pd.read_csv(ROOT/'results/machine_readable/formal/formal_metrics.csv',float_precision='round_trip');out=[]
        for budget in [256,512,1024]:
            for method in ['Uniform','SH','SR','OCBA','CPC-v2']:
                r=d[(d.budget==budget)&(~d.crn)&(d.method==method)].iloc[0]
                out.append([str(budget),'CPC' if method=='CPC-v2' else method,f'{100*r.PGS:.2f} [{100*r.PGS_ci_low:.2f}, {100*r.PGS_ci_high:.2f}]',f'{r.EOC_mean/1e6:.3f} [{r.EOC_ci_low/1e6:.3f}, {r.EOC_ci_high/1e6:.3f}]'])
        return out
    return None

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'build/main_tables')
    args=parser.parse_args();out=args.output_dir.resolve()
    if out.is_relative_to((ROOT/'results').resolve()):raise ValueError('Use a build directory; approved results are read-only.')
    out.mkdir(parents=True,exist_ok=True);receipt=[]
    for cfg in json.loads((ROOT/'configs/table_rendering.json').read_text(encoding='utf-8')):
        with (ROOT/cfg['csv']).open(encoding='utf-8',newline='') as f:rows=list(csv.DictReader(f))
        cells=[[r[h] for h in cfg['headers']] for r in rows]
        computed=numeric_rows(cfg['stem'])
        if computed is not None and computed!=cells:raise ValueError(cfg['stem']+' numerical summary mismatch')
        text=cfg['prefix']+''.join(cfg['row_separator'].join(r)+cfg['row_terminator'] for r in cells)+cfg['suffix']
        path=out/(cfg['stem']+'.tex');path.write_text(text,encoding='utf-8',newline=cfg.get('line_ending','\n'))
        if path.read_bytes()!=(ROOT/'results/main_tables'/path.name).read_bytes():raise ValueError(path.name+' differs from approved source')
        receipt.append(dict(table=cfg['stem'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),byte_identical=True,numerical_summary_checked=computed is not None))
    (out/'reproduction_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('PASS: 5 tables reproduced; stored numerical summaries checked for Tables 3–4; 0 simulation calls.')
if __name__=='__main__':main()
