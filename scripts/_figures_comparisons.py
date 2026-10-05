"""Inputs: stored aggregate result CSVs. Outputs: Figures 4–6.
Runtime: seconds. Presentation-only redraw; no simulation, inference or resampling.
"""
from pathlib import Path
import json,hashlib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1]
import os
OUT=Path(os.environ['REPRO_FIGURE_OUTPUT']);OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.spines.top':False,'axes.spines.right':False,'legend.frameon':False,'svg.fonttype':'none','pdf.fonttype':42,'axes.labelsize':8,'axes.titlesize':9,'savefig.facecolor':'white'})
sources=[]
def rd(rel):
    p=P/rel;sources.append(dict(file=rel,sha256=hashlib.sha256(p.read_bytes()).hexdigest()));return pd.read_csv(p,float_precision='round_trip')
def save(fig,name):
    for ext in ['pdf','svg','png']:fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight',dpi=350)
    plt.close(fig)
def err(ax,x,df,col,lo,hi,color,marker,label,scale=100,ls='-'):
    y=df[col].to_numpy()*scale
    er=np.maximum(0,np.vstack([y-df[lo].to_numpy()*scale,df[hi].to_numpy()*scale-y]))
    ax.errorbar(x,y,yerr=er,color=color,marker=marker,ms=4,lw=1,ls=ls,capsize=2,label=label)
d=rd('results/machine_readable/external/summary_table.csv')
d['short']=d.procedure.map(lambda x:'CPC' if x=='epsilon-CPC-SH' else 'B1' if x.startswith('B1') else 'B2' if x.startswith('B2') else 'DSTTB' if x.startswith('DSTTB') else 'Uniform')
v=rd('results/machine_readable/formal/variance_diagnostics.csv')
fig,axs=plt.subplots(1,2,figsize=(7.2,3.2),gridspec_kw={'width_ratios':[1,1.25]},layout='constrained')
for k,r in enumerate(v.itertuples()):
    axs[0].errorbar(r.VRR,k,xerr=[[r.VRR-r.VRR_ci_low],[r.VRR_ci_high-r.VRR]],fmt='o',color='#0072B2',capsize=3)
    axs[0].annotate(f'{r.VRR:.2f}',(r.VRR,k),xytext=(0,10),textcoords='offset points',ha='center',fontsize=8)
axs[0].set(xscale='log',yticks=[0,1,2],yticklabels=['Near tie','Medium gap','Large gap'],xlim=(2,600),ylim=(-.6,2.6),xlabel='Variance reduction ratio (OFF / ON)',title='a  Three prespecified WNBA pairs');axs[0].invert_yaxis()
for i,env in enumerate(['Synthetic G2','WNBA']):
    for r in d[(d.environment==env)&d.crn&(d.short!='Uniform')].itertuples():
        off={'B1':-.18,'B2':0,'CPC':.18}[r.short]
        axs[1].errorbar(r.screening_power_mean,i+off,xerr=[[r.screening_power_mean-r.screening_power_mean_ci_low],[r.screening_power_mean_ci_high-r.screening_power_mean]],fmt={'B1':'o','B2':'s','CPC':'^'}[r.short],color={'B1':'#777777','B2':'#009E73','CPC':'#0072B2'}[r.short],capsize=3,label=r.short if i==0 else None)
axs[1].set(yticks=[0,1],yticklabels=['G2','WNBA'],xlim=(.1,1.03),ylim=(-.5,1.5),xlabel='Fraction of inferior alternatives removed',title='b  ON screening beyond CPC');axs[1].legend(fontsize=8,ncol=3,loc='upper left');axs[1].invert_yaxis()
save(fig,'Fig4_crn')
w=rd('results/machine_readable/formal/formal_metrics.csv')
methods=['Uniform','SH','SR','OCBA','CPC-v1','CPC-v2'];colors=['#8a8a8a','#3b7db0','#62a6a0','#c58b42','#aa86ac','#b75050'];markers=['o','s','^','D','v','P']
labels={m:('CPC' if m=='CPC-v2' else 'Bounded CPC' if m=='CPC-v1' else m) for m in methods}
fig,axes=plt.subplots(2,2,figsize=(7.2,4.7),sharex=True)
for j,mode in enumerate([False,True]):
    for k,m in enumerate(methods):
        q=w[(w.method==m)&(w.crn==mode)].sort_values('budget');xs=np.arange(3)+(k-2.5)*.025
        err(axes[0,j],xs,q,'PGS','PGS_ci_low','PGS_ci_high',colors[k],markers[k],labels[m])
        err(axes[1,j],xs,q,'EOC_mean','EOC_ci_low','EOC_ci_high',colors[k],markers[k],labels[m],scale=1e-6)
    axes[0,j].set_title(f'{chr(97+j)}  CRN '+('ON' if mode else 'OFF'));axes[0,j].set_ylim(76,101.5);axes[1,j].set_ylim(-.02,1.0)
    axes[1,j].set_title(f'{chr(99+j)}  CRN '+('ON' if mode else 'OFF'));axes[1,j].set_xlabel('Budget');axes[1,j].set_xticks(range(3),[256,512,1024])
    for ax in axes[:,j]:ax.grid(alpha=.15)
axes[0,0].set_ylabel('Plug-in PGS (%)');axes[1,0].set_ylabel('Plug-in EOC (million proxy units)')
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='lower center',ncol=6,fontsize=7,bbox_to_anchor=(.5,-.01));fig.tight_layout(rect=[0,.06,1,1]);save(fig,'Fig5_recommendation')
e=rd('results/machine_readable/robustness/Table_Sensitivity_2_epsilon_sensitivity_metrics.csv');ec=e[e.method=='CPC-v2']
fig,axes=plt.subplots(1,3,figsize=(7.2,2.7))
for j,mode in enumerate([False,True]):
    for fraction,color,marker in [(.0025,'#b75050','o'),(.005,'#367cac','s'),(.01,'#6a997e','^')]:
        q=ec[(ec.crn==mode)&(ec.epsilon_fraction==fraction)].sort_values('budget');err(axes[j],range(3),q,'PGS','PGS_ci_low','PGS_ci_high',color,marker,f'{100*fraction:.2f}%')
    axes[j].set(xticks=range(3),xticklabels=[256,512,1024],ylim=(40,102),xlabel='Budget',title=f'{chr(97+j)}  CRN '+('ON' if mode else 'OFF'))
axes[0].set_ylabel('Plug-in PGS (%)');axes[0].legend(fontsize=7,title='$\\epsilon/R_{\\mathrm{cal}}$',title_fontsize=7)
for mode,color,marker in [(False,'#bc8543','o'),(True,'#367cac','s')]:
    q=ec[(ec.budget==512)&(ec.crn==mode)].sort_values('epsilon_fraction');axes[2].plot(range(3),q.mean_final_active_set_size,color=color,marker=marker,label='ON' if mode else 'OFF')
axes[2].set(xticks=range(3),xticklabels=['0.25','0.50','1.00'],xlabel='$\\epsilon/R_{\\mathrm{cal}}$ (%)',ylabel='Mean active-set size',ylim=(0,33),title='c  Budget 512');axes[2].legend(fontsize=7);fig.tight_layout();save(fig,'Fig6_epsilon')
