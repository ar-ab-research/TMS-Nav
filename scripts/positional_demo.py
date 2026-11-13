"""Synthetic numerical demo. Never represents individualized target validation."""
from pathlib import Path
import pyvista as pv
from src.positional import compare, write_results

mesh=pv.Cube(bounds=(-10,10,-10,10,-10,10)).triangulate()
imported=dict(provenance=dict(mode='synthetic'),targets=[dict(name='synthetic planned',position=[3,4,0])])
mappings={s:dict(marker='synthetic cap',brainsight='synthetic planned') for s in ['SMA','right_DLPFC']}
sem={'synthetic planned':dict(outside=[3,4,20],inside=[3,4,0],verified=True,evidence='constructed cube')}
rows=compare('synthetic',mesh,{'synthetic cap':[0,0,12]},imported,mappings,sem)
write_results(rows,Path('saves/positional-demo/results'))
print('Synthetic results: saves/positional-demo/results.json and .csv; each distance is 5 mm')
