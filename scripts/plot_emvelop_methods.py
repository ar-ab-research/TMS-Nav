"""Reproducible standalone method diagrams (no external rendering service)."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
out=Path('analysis/emvelop'); out.mkdir(exist_ok=True,parents=True)
fig,ax=plt.subplots(figsize=(13,4)); ax.axis('off')
labels=['Geometry + tissue\nassumptions','Unit-source complex\nMaxwell responses G','Optimize complex\nantenna weights w','Envelope + carrier\nheating q','Solve steady bioheat\nand scale currents']
for i,label in enumerate(labels):
 x=.09+i*.205
 ax.text(x,.65,label,ha='center',va='center',transform=ax.transAxes,bbox=dict(boxstyle='round,pad=.7',fc='#e6effa',ec='#365a7c'),fontsize=10)
 if i<4: ax.add_patch(FancyArrowPatch((x+.082,.65),(x+.12,.65),transform=ax.transAxes,arrowstyle='->',mutation_scale=15))
ax.text(.5,.18,'Field scales with current; power and temperature rise scale with current squared.\nChanging scale does not change relative half-target focality.',ha='center',transform=ax.transAxes,fontsize=12)
fig.savefig(out/'methods_workflow.svg',bbox_inches='tight'); plt.close(fig)
equations=[('Linear field map',r'\mathbf{E}_i(\mathbf{r})=\mathbf{G}_i(\mathbf{r})\mathbf{w}_i'),('Envelope objective',r'\min_{\mathbf{w}_1,\mathbf{w}_2}\ \sum_{n\ne T}\min(\|\mathbf{G}_{1n}\mathbf{w}_1\|^2,\|\mathbf{G}_{2n}\mathbf{w}_2\|^2)'),('Carrier heating',r'q=\frac{\sigma}{2}(\|\mathbf{E}_1\|^2+\|\mathbf{E}_2\|^2)'),('Steady temperature rise',r'(-\kappa\nabla^2+b)\Delta T=q'),('Thermal scaling',r'\alpha=\sqrt{\Delta T_{\mathrm{limit}}/\max(\Delta T)}'),('Three-dimensional focality',r'L_{50}=\left(\sum_n v_n\,\mathbf{1}_{M_n\geq M_T/2}\right)^{1/3}')]
fig,ax=plt.subplots(figsize=(13,7)); ax.axis('off')
for i,(label,equation) in enumerate(equations):
 y=.94-i*.16
 ax.text(0,y,label,fontsize=11,transform=ax.transAxes,color='#365a7c')
 ax.text(.32,y,'$'+equation+'$',fontsize=17,transform=ax.transAxes)
fig.savefig(out/'methods_equations.svg',bbox_inches='tight'); plt.close(fig)
