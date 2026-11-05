import * as THREE from 'three';
import {PLYLoader} from 'three/examples/jsm/loaders/PLYLoader.js';
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
  const sourceHead=new THREE.Group();root.add(sourceHead);
  const sourceRaw=new THREE.Group();root.add(sourceRaw);
  const groups={};
  const controls=[];
  let saved={};try{saved=JSON.parse(localStorage.getItem('positional-layers-v2')||'{}');}catch{}
  for(const [name,id,group] of [
    ['Projected cap points','toggle-scalp-projections',new THREE.Group()],
    ['Raw Brainsight / trajectories','toggle-brainsight-targets',sourceRaw],
    ['Brainsight scalp points','toggle-scalp-entries',new THREE.Group()],
    ['Comparison lines','toggle-comparison-lines',new THREE.Group()],
    ['Registered Brainsight surface','toggle-brainsight-surface',sourceHead]]){
    groups[name]=group;if(group!==sourceRaw&&group!==sourceHead)root.add(group);
    const box=document.getElementById(id);box.checked=saved[id]??true;
    const apply=()=>{group.visible=box.checked;box.dataset.renderVisible=String(group.visible);};
    box.addEventListener('change',()=>{saved[id]=box.checked;localStorage.setItem('positional-layers-v2',JSON.stringify(saved));apply();});
    apply();controls.push(box);
  }
  const imported=make('details');imported.append(make('summary','Import results JSON'));
  const input=make('input');input.type='file';input.accept='.json';input.setAttribute('aria-label','Import positional results JSON');imported.append(input);panel.append(imported);
  let payload=null,revision=0;
  function dot(group,p,color,opacity=1){if(!p)return;const mesh=new THREE.Mesh(new THREE.SphereGeometry(1.8),new THREE.MeshBasicMaterial({color,transparent:opacity<1,opacity,depthTest:false,depthWrite:false}));mesh.position.fromArray(p);mesh.renderOrder=12;group.add(mesh);}
  function targetShape(position,name){const mesh=new THREE.Mesh(new THREE.ConeGeometry(3.8,7,4),new THREE.MeshBasicMaterial({color:0x43d17a,depthTest:false,depthWrite:false,transparent:true,opacity:1}));mesh.rotation.x=Math.PI/2;mesh.position.fromArray(position);mesh.renderOrder=10;mesh.name='Brainsight: '+name;sourceRaw.add(mesh);}
  function line(group,a,b,color){if(!a||!b)return;group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a),new THREE.Vector3(...b)]),new THREE.LineBasicMaterial({color})));}
  function dispose(group){for(const c of [...group.children]){c.traverse(n=>{n.geometry?.dispose();n.material?.dispose();n.element?.remove();});group.remove(c);}}
  function clear(){payload=null;results.replaceChildren();panel.removeAttribute('data-brainsight-rendered');panel.removeAttribute('data-overlay-frame');for(const group of Object.values(groups))dispose(group);for(const box of controls)box.disabled=true;}
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
      if(!(data.cap_points||[]).some(p=>p.name===r.marker_name))dot(groups['Projected cap points'],r.eeg_scalp,0xef5350,.45);
      if(!data.brainsight&&r.brainsight_raw)targetShape(r.brainsight_raw,r.brainsight_name);

      line(groups['Raw Brainsight / trajectories'],r.trajectory?.outside,r.trajectory?.inside,0x43d17a);
      if(r.qc==='valid'){dot(groups['Brainsight scalp points'],r.brainsight_scalp,0x43d17a);line(groups['Comparison lines'],r.eeg_scalp,r.brainsight_scalp,0xffffff);}
    }
    for(const p of data.cap_points||[])dot(groups['Projected cap points'],p.scalp,0xef5350,.45);
    const valid=rows.filter(r=>r.qc==='valid').length;
    status.textContent=`${markers.subject} · ${valid}/${rows.length} comparisons available`;
    results.append(table(['Target / cap','Scalp-entry localization difference (mm)'],rows.map(r=>[`${r.target==='right_DLPFC'?'Right DLPFC':r.target} / ${r.cap_label}`,r.qc==='valid'?r.distance_mm.toFixed(3)+' mm':'Unavailable: '+(r.qc_issues?.join('; ')||r.reason)])));
    if(data.project_inventory?.planned_names?.length)results.append(make('p','Project targets: '+data.project_inventory.planned_names.join(', '),'hint'));
    const blockers=data.blockers||[...new Set(rows.filter(r=>r.qc!=='valid').map(r=>r.reason))];
    if(blockers.length){const detail=make('details');detail.open=true;detail.append(make('summary','Required inputs'));const list=make('ul');for(const reason of blockers)list.append(make('li',reason));detail.append(list);results.append(detail);}
    results.append(make('p','Scalp projection layer: red fiducials and green Brainsight points. Brainsight closest-triangle projections are exploratory and do not enable primary comparisons.','hint'));
    if(data.cap_points?.length){const detail=make('details');detail.open=true;detail.append(make('summary','Cap projections · mm'));detail.append(table(['Marker','Offset to scalp'],data.cap_points.map(p=>[p.label,p.projection_distance_mm.toFixed(3)])));results.append(detail);}
    for(const r of rows.filter(r=>r.qc==='valid'))results.append(make('p',`${r.cap_label}: ${r.method}`,'hint'));
    if(valid){const summary=make('details');summary.append(make('summary','Across-subject summary · mm'));const fmt=v=>Number.isFinite(v)?v.toFixed(3):'—';summary.append(table(['Target','n','Mean','SD','Median','IQR'],Object.entries(data.summary||{}).map(([k,v])=>[k,v.n,fmt(v.mean),fmt(v.SD),fmt(v.median),fmt(v.IQR)])));results.append(summary);}
    if(data.brainsight){
      const bs=data.brainsight;
      if(bs.frame!=='cap_MRI_RAS_mm'||bs.marker_mri_sha256!==markers.source_sha256||bs.registration?.numerical_qc!=='passed')throw Error('Registered cap MRI frame unresolved');
      const detail=make('details');detail.open=true;detail.append(make('summary','Imported Brainsight targets'));
      detail.append(table(['Export name','Internal site','Scalp-entry localization difference (mm)'],bs.targets.map(t=>{const r=rows.find(r=>r.brainsight_name===t.name&&r.qc==='valid');return [t.name,t.internal_target||'Unassigned',r?r.distance_mm.toFixed(3):'Unavailable — see QC reasons below'];})));
      detail.append(make('p','Raw target offset to common scalp (QC only): '+bs.targets.map(t=>`${t.name}: ${t.raw_offset_to_common_scalp_mm.toFixed(2)} mm`).join('; '),'hint'));
      detail.append(make('p','Registered overlay in cap MRI RAS mm. Raw target positions are preserved; a raw-point offset is not the scalp-entry localization difference.','hint'));
      const qc=make('details');qc.append(make('summary','Registration QC · '+bs.registration.anatomical_qc.replaceAll('_',' ')));const qcImage=make('img');qcImage.src=`/api/subjects/${encodeURIComponent(markers.subject)}/registration-qc.png`;qcImage.alt='Source-to-cap MRI registration: before and after orthogonal overlays';qcImage.style.width='100%';const qcLink=make('a','Open full QC views');qcLink.href=qcImage.src;qcLink.target='_blank';qcLink.rel='noopener';qc.append(qcLink,qcImage);detail.append(qc);
      results.prepend(detail);
      for(const t of bs.targets){
        assertPoint(t.position);
        targetShape(t.position,t.name);
        if(t.exploratory_scalp_projection){assertPoint(t.exploratory_scalp_projection.position);dot(groups['Projected cap points'],t.exploratory_scalp_projection.position,0x43d17a,.45);}
      }
      panel.dataset.brainsightShape='pyramid';
      panel.dataset.scalpProjections=String((data.cap_points||[]).length+bs.targets.filter(t=>t.exploratory_scalp_projection).length);
      const ticket=revision;
      new PLYLoader().load(`/api/subjects/${encodeURIComponent(markers.subject)}/brainsight-overlay.ply`,geometry=>{
        if(ticket!==revision){geometry.dispose();return;}geometry.computeVertexNormals();
        const overlay=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0xb49cdb,transparent:true,opacity:.16,side:THREE.FrontSide,roughness:.85,depthWrite:false,depthTest:false}));overlay.renderOrder=1;sourceHead.add(overlay);
        panel.dataset.brainsightRendered=String(bs.targets.length);
        status.textContent+=` · ${bs.targets.length} Brainsight targets rendered`;
        panel.dataset.overlayFrame='cap_MRI_RAS_mm';
      },undefined,()=>{if(ticket===revision)status.textContent+=' · Brainsight scalp load failed';});
    }
    for(const box of controls)box.disabled=false;
    for(const id of ['toggle-scalp-entries','toggle-comparison-lines']){const box=document.getElementById(id);box.disabled=valid===0;box.title=valid?'':'No verified comparison points are available';}
    payload=data;
  }
  async function load(){const ticket=++revision;clear();const markers=getMarkers();if(!markers?.source_sha256){status.textContent='Select an individual subject to load positional analysis.';return;}status.textContent='Loading saved analysis…';try{const response=await fetch(`/api/subjects/${encodeURIComponent(markers.subject)}/positional`);if(ticket!==revision)return;if(!response.ok)throw Error('Could not load analysis');const data=await response.json();if(ticket!==revision)return;render(data);}catch(e){if(ticket!==revision)return;clear();status.textContent=`${e.message}. Run python compare_positions.py --subject ${markers.subject}, then python run_viewer.py.`;}}
  reload.onclick=load;
  input.onchange=async()=>{const ticket=++revision;try{const data=JSON.parse(await input.files[0].text());if(ticket===revision)render(data);}catch(e){if(ticket===revision){clear();status.textContent=e.message;}}};
  for(const format of ['json','csv']){const b=make('button',`Export ${format.toUpperCase()}`);b.type='button';b.onclick=()=>{if(!payload)return;const fields=[...new Set(payload.rows.flatMap(r=>Object.keys(r)))];const quote=v=>'"'+String(typeof v==='object'?JSON.stringify(v):v??'').replaceAll('"','""')+'"';const content=format==='json'?JSON.stringify(payload,null,2):[fields.map(quote).join(','),...payload.rows.map(r=>fields.map(k=>quote(r[k])).join(','))].join('\n');const a=make('a');a.href=URL.createObjectURL(new Blob([content],{type:'text/plain'}));a.download='positional.'+format;a.click();URL.revokeObjectURL(a.href);};toolbar.append(b);}
  document.getElementById('aim1-metrics').append(panel);
  return ()=>{input.value='';load();};
}
