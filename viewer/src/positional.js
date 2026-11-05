import * as THREE from 'three';
import {PLYLoader} from 'three/examples/jsm/loaders/PLYLoader.js';
import {CSS2DObject} from 'three/examples/jsm/renderers/CSS2DRenderer.js';
// Numerical coordinates are native MRI RAS mm; camera/display transforms never enter distances.
export function positionalViewer(root, getMarkers) {
  const make=(tag,text,className)=>{const el=document.createElement(tag);if(text)el.textContent=text;if(className)el.className=className;return el;};
  const panel=make('section',null,'positional-panel');panel.id='positional-panel';
  panel.append(make('h2','Aim 1 positional scalp comparison'));
  const intro=make('p','Cap triangle projections and planned Brainsight scalp points. Distances use MRI-world millimeters.','hint');panel.append(intro);
  const toolbar=make('div',null,'positional-actions');
  const reload=make('button','Reload analysis');reload.type='button';toolbar.append(reload);panel.append(toolbar);
  const status=make('p',null,'hint');status.setAttribute('role','status');panel.append(status);
  const results=make('div');panel.append(results);
  const layers=make('details');layers.open=true;layers.append(make('summary','Comparison layers'));panel.append(layers);
  const sourceHead=new THREE.Group();root.add(sourceHead);
  const sourceRaw=new THREE.Group();root.add(sourceRaw);
  const groups={};
  for(const [name,color] of [['Original cap markers','#ffaa00'],['Projected cap points','#00ffff'],['Raw Brainsight / trajectories','#ff00ff'],['Brainsight scalp points','#00ff00'],['Comparison lines','#ffffff'],['Registered Brainsight surface','#91a4bc']]) {
    const group=new THREE.Group();groups[name]=group;root.add(group);
    const label=make('label',null,'positional-layer'),box=make('input');box.type='checkbox';box.checked=true;
    box.onchange=()=>{group.visible=box.checked;if(name==='Raw Brainsight / trajectories')sourceRaw.visible=box.checked;if(name==='Registered Brainsight surface')sourceHead.visible=box.checked;};
    const swatch=make('span',null,'positional-swatch');swatch.style.background=color;
    label.append(box,swatch,document.createTextNode(name));layers.append(label);
  }
  const imported=make('details');imported.append(make('summary','Import results JSON'));
  const input=make('input');input.type='file';input.accept='.json';input.setAttribute('aria-label','Import positional results JSON');imported.append(input);panel.append(imported);
  let payload=null,revision=0;
  function dot(group,p,color){if(!p)return;const mesh=new THREE.Mesh(new THREE.SphereGeometry(2),new THREE.MeshBasicMaterial({color}));mesh.position.fromArray(p);group.add(mesh);}
  function line(group,a,b,color){if(!a||!b)return;group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a),new THREE.Vector3(...b)]),new THREE.LineBasicMaterial({color})));}
  function dispose(group){for(const c of [...group.children]){c.traverse(n=>{n.geometry?.dispose();n.material?.dispose();n.element?.remove();});group.remove(c);}}
  function clear(){payload=null;results.replaceChildren();dispose(sourceRaw);for(const c of [...sourceHead.children]){c.geometry?.dispose();c.material?.dispose();sourceHead.remove(c);}panel.removeAttribute('data-brainsight-rendered');for(const g of Object.values(groups)){for(const c of [...g.children]){c.geometry?.dispose();c.material?.dispose();g.remove(c);}}}
  function table(headers,rows){const t=make('table',null,'agree positional-table');const head=make('thead'),tr=make('tr');for(const h of headers)tr.append(make('th',h));head.append(tr);t.append(head);const body=make('tbody');for(const row of rows){const tr=make('tr');for(const value of row)tr.append(make('td',String(value)));body.append(tr);}t.append(body);return t;}
  function assertPoint(p){if(!Array.isArray(p)||p.length!==3||p.some(v=>typeof v!=='number'||!Number.isFinite(v)))throw Error('Invalid result coordinates');}
  function checkMarker(name,p,markers){assertPoint(p);const marker=markers.fiducials?.find(m=>m.name===name);if(!marker||marker.position.some((v,i)=>Math.abs(v-p[i])>1e-6))throw Error('Cap markers changed; rerun analysis before rendering.');}
  function render(data){
    clear();const markers=getMarkers();
    if(data.status==='not_run'){status.textContent=`Run: python compare_positions.py --subject ${markers.subject}`;return;}
    if(data.frame!=='native_RAS_mm'||!Array.isArray(data.rows))throw Error('Expected native RAS mm results');
    const rows=data.rows.filter(r=>r.subject===markers.subject);
    if(!rows.length)throw Error('No results for current subject');
    for(const r of rows){
      if(!markers.source_sha256||r.provenance?.context?.marker_mri_sha256!==markers.source_sha256)throw Error('MRI identity mismatch');
      if(r.eeg_raw)checkMarker(r.marker_name,r.eeg_raw,markers);
      for(const k of ['eeg_scalp','brainsight_raw','brainsight_scalp'])if(r[k])assertPoint(r[k]);
      if(r.qc==='valid'&&(!Number.isFinite(r.distance_mm)||!r.eeg_scalp||!r.brainsight_scalp))throw Error('Invalid comparison');
    }
    for(const p of data.cap_points||[]){checkMarker(p.name,p.raw,markers);assertPoint(p.scalp);}
    for(const r of rows){
      dot(groups['Original cap markers'],r.eeg_raw,0xffaa00);dot(groups['Projected cap points'],r.eeg_scalp,0x00ffff);
      dot(groups['Raw Brainsight / trajectories'],r.brainsight_raw,0xff00ff);
      line(groups['Raw Brainsight / trajectories'],r.trajectory?.outside,r.trajectory?.inside,0xff00ff);
      if(r.qc==='valid'){dot(groups['Brainsight scalp points'],r.brainsight_scalp,0x00ff00);line(groups['Comparison lines'],r.eeg_scalp,r.brainsight_scalp,0xffffff);}
    }
    for(const p of data.cap_points||[]){dot(groups['Original cap markers'],p.raw,0xffaa00);dot(groups['Projected cap points'],p.scalp,0x00ffff);}
    const valid=rows.filter(r=>r.qc==='valid').length;
    status.textContent=`${markers.subject} · ${valid}/${rows.length} comparisons available`;
    results.append(table(['Target / cap','Scalp-entry localization difference (mm)'],rows.map(r=>[`${r.target==='right_DLPFC'?'Right DLPFC':r.target} / ${r.cap_label}`,r.qc==='valid'?r.distance_mm.toFixed(3)+' mm':'Unavailable'])));
    if(data.project_inventory?.planned_names?.length)results.append(make('p','Project targets: '+data.project_inventory.planned_names.join(', '),'hint'));
    const blockers=data.blockers||[...new Set(rows.filter(r=>r.qc!=='valid').map(r=>r.reason))];
    if(blockers.length){const detail=make('details');detail.open=true;detail.append(make('summary','Required inputs'));const list=make('ul');for(const reason of blockers)list.append(make('li',reason));detail.append(list);results.append(detail);}
    if(data.cap_points?.length){const detail=make('details');detail.open=true;detail.append(make('summary','Cap projections · mm'));detail.append(table(['Marker','Offset to scalp'],data.cap_points.map(p=>[p.label,p.projection_distance_mm.toFixed(3)])));results.append(detail);}
    for(const r of rows.filter(r=>r.qc==='valid'))results.append(make('p',`${r.cap_label}: ${r.method}`,'hint'));
    if(valid){const summary=make('details');summary.append(make('summary','Across-subject summary · mm'));const fmt=v=>Number.isFinite(v)?v.toFixed(3):'—';summary.append(table(['Target','n','Mean','SD','Median','IQR'],Object.entries(data.summary||{}).map(([k,v])=>[k,v.n,fmt(v.mean),fmt(v.SD),fmt(v.median),fmt(v.IQR)])));results.append(summary);}
    if(data.brainsight){
      const bs=data.brainsight;
      if(bs.frame!=='cap_MRI_RAS_mm'||bs.marker_mri_sha256!==markers.source_sha256||bs.registration?.numerical_qc!=='passed')throw Error('Registered cap MRI frame unresolved');
      const detail=make('details');detail.open=true;detail.append(make('summary','Imported Brainsight targets'));
      detail.append(table(['Export name','Internal site','Scalp-entry localization difference (mm)'],bs.targets.map(t=>{const r=rows.find(r=>r.brainsight_name===t.name&&r.qc==='valid');return [t.name,t.internal_target||'Unassigned',r?r.distance_mm.toFixed(3):'Unavailable'];})));
      detail.append(make('p','Raw target offset to common scalp (QC only): '+bs.targets.map(t=>`${t.name}: ${t.raw_offset_to_common_scalp_mm.toFixed(2)} mm`).join('; '),'hint'));
      detail.append(make('p','Registered overlay in cap MRI RAS mm. Raw target positions are preserved; a raw-point offset is not the scalp-entry localization difference.','hint'));
      const qc=make('details');qc.append(make('summary','Registration QC · '+bs.registration.anatomical_qc.replaceAll('_',' ')));const qcImage=make('img');qcImage.src=`/api/subjects/${encodeURIComponent(markers.subject)}/registration-qc.png`;qcImage.alt='Source-to-cap MRI registration: before and after orthogonal overlays';qcImage.style.width='100%';const qcLink=make('a','Open full QC views');qcLink.href=qcImage.src;qcLink.target='_blank';qcLink.rel='noopener';qc.append(qcLink,qcImage);detail.append(qc);
      results.prepend(detail);
      for(const t of bs.targets){assertPoint(t.position);dot(sourceRaw,t.position,0xff00ff);const point=sourceRaw.children.at(-1);point.material.depthTest=false;point.renderOrder=10;const label=make('span',t.name+' · raw','brainsight-point-label');label.dataset.bsTarget=t.name;const object=new CSS2DObject(label);object.position.fromArray(t.position);object.position.z+=t.name.toLowerCase().includes('skin')?-9:9;sourceRaw.add(object);}
      const ticket=revision;
      new PLYLoader().load(`/api/subjects/${encodeURIComponent(markers.subject)}/brainsight-overlay.ply`,geometry=>{
        if(ticket!==revision){geometry.dispose();return;}geometry.computeVertexNormals();
        const overlay=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0x91a4bc,transparent:true,opacity:.16,side:THREE.FrontSide,roughness:.85,depthWrite:false,depthTest:false}));overlay.renderOrder=1;sourceHead.add(overlay);
        panel.dataset.brainsightRendered=String(bs.targets.length);
        status.textContent+=` · ${bs.targets.length} Brainsight targets rendered`;
        panel.dataset.overlayFrame='cap_MRI_RAS_mm';
      },undefined,()=>{if(ticket===revision)status.textContent+=' · Brainsight scalp load failed';});
    }
    payload=data;
  }
  async function load(){const ticket=++revision;clear();const markers=getMarkers();if(!markers?.source_sha256){status.textContent='Select an individual subject to load positional analysis.';return;}status.textContent='Loading saved analysis…';try{const response=await fetch(`/api/subjects/${encodeURIComponent(markers.subject)}/positional`);if(ticket!==revision)return;if(!response.ok)throw Error('Could not load analysis');const data=await response.json();if(ticket!==revision)return;render(data);}catch(e){if(ticket!==revision)return;clear();status.textContent=`${e.message}. Run python compare_positions.py --subject ${markers.subject}, then python run_viewer.py.`;}}
  reload.onclick=load;
  input.onchange=async()=>{const ticket=++revision;try{const data=JSON.parse(await input.files[0].text());if(ticket===revision)render(data);}catch(e){if(ticket===revision){clear();status.textContent=e.message;}}};
  for(const format of ['json','csv']){const b=make('button',`Export ${format.toUpperCase()}`);b.type='button';b.onclick=()=>{if(!payload)return;const fields=[...new Set(payload.rows.flatMap(r=>Object.keys(r)))];const quote=v=>'"'+String(typeof v==='object'?JSON.stringify(v):v??'').replaceAll('"','""')+'"';const content=format==='json'?JSON.stringify(payload,null,2):[fields.map(quote).join(','),...payload.rows.map(r=>fields.map(k=>quote(r[k])).join(','))].join('\n');const a=make('a');a.href=URL.createObjectURL(new Blob([content],{type:'text/plain'}));a.download='positional.'+format;a.click();URL.revokeObjectURL(a.href);};toolbar.append(b);}
  document.getElementById('aim1-metrics').append(panel);
  return ()=>{input.value='';load();};
}
