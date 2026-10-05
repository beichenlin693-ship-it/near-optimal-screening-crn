"""Inputs: unchanged stored result CSVs and retained plotting specifications.
Outputs: seven PNG, PDF and SVG figures in build/main_figures (or --output-dir).
Runtime: usually under one minute. Redraws existing figures, never resamples or simulates.
"""
from pathlib import Path
import argparse,os,subprocess,sys,json
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=ROOT/'build/main_figures');args=p.parse_args()
    out=args.output_dir.resolve()
    if out.is_relative_to((ROOT/'results').resolve()):raise ValueError('Use a build directory; approved results are read-only.')
    out.mkdir(parents=True,exist_ok=True);env=dict(os.environ,REPRO_FIGURE_OUTPUT=str(out),PYTHONUTF8='1',MPLBACKEND='Agg')
    for script in ['_figures_overview.py','_figures_comparisons.py']:
        subprocess.run([sys.executable,str(ROOT/'scripts'/script)],cwd=ROOT,env=env,check=True)
    checks=[]
    for original in sorted((ROOT/'results/main_figures').glob('*.png')):
        with Image.open(original) as a,Image.open(out/original.name) as b:
            equal=a.size==b.size and ImageChops.difference(a.convert('RGB'),b.convert('RGB')).getbbox() is None
        checks.append(dict(figure=original.stem,png_pixels_equal=equal))
    if len(checks)!=7:raise ValueError('Expected seven complete figure renders')
    (out/'reproduction_receipt.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    if not all(c['png_pixels_equal'] for c in checks):
        raise RuntimeError('Render differs from approved PNG pixels; inspect receipt. Font/library differences may affect rendering. Do not overwrite approved figures.')
    print('PASS: 7 figures redrawn with identical PNG pixels; 0 simulation calls. PDF/SVG metadata may differ.')
if __name__=='__main__':main()
