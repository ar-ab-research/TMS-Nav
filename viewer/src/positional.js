import * as THREE from 'three';
import {CSS2DObject} from 'three/examples/jsm/renderers/CSS2DRenderer.js';
import {PLYLoader} from 'three/examples/jsm/loaders/PLYLoader.js';
// Numerical coordinates are native MRI RAS mm; camera/display transforms never enter distances.
export function positionalViewer(root, getMarkers, hooks={}) {
  const make=(tag,text,className)=>{const el=document.createElement(tag);if(text)el.textContent=text;if(className)el.className=className;return el;};
  const panel=make('section',null,'positional-panel');panel.id='positional-panel';
  panel.append(make('h2','Aim 1 positional scalp comparison'));
  const intro=make('p','SMA projection endpoint and separate trajectory endpoint. All distances use MRI-world millimeters.','hint');panel.append(intro);
  const toolbar=make('div',null,'positional-actions');
  const reload=make('button','Reload analysis');reload.type='button';toolbar.append(reload);panel.append(toolbar);
  const status=make('p',null,'hint');status.setAttribute('role','status');panel.append(status);
  const results=make('div');panel.append(results);
  const sourceHead=new THREE.Group();root.add(sourceHead);
  const sourceRaw=new THREE.Group();root.add(sourceRaw);
  const commonHead=new THREE.Group();root.add(commonHead);
  const variantGroups=new Map();
  const groups={};
  const controls=[];
  let saved={};try{saved=JSON.parse(localStorage.getItem('positional-layers-v2')||'{}');}catch{}
  for(const [name,id,group] of [
    ['Projected cap points','toggle-scalp-projections',new THREE.Group()],
    ['Raw Brainsight / trajectories','toggle-brainsight-targets',sourceRaw],
    ['Brainsight scalp points','toggle-scalp-entries',new THREE.Group()],
    ['Comparison lines','toggle-comparison-lines',new THREE.Group()],
    ['Registered Brainsight surface','toggle-brainsight-surface',sourceHead],
    ['Common skin','toggle-common-skin',commonHead],
    ['Projection lines','toggle-projection-lines',new THREE.Group()]]){
    groups[name]=group;if(group!==sourceRaw&&group!==sourceHead&&group!==commonHead)root.add(group);
    const box=document.getElementById(id);box.checked=saved[id]??(id!=='toggle-projection-lines');
    const apply=()=>{group.visible=box.checked;box.dataset.renderVisible=String(group.visible);applyVisibility();};
    box.addEventListener('change',()=>{saved[id]=box.checked;localStorage.setItem('positional-layers-v2',JSON.stringify(saved));apply();});
    apply();controls.push(box);
  }
  const parentBox=document.getElementById('toggle-brainsight-parent');parentBox.checked=saved[parentBox.id]??true;
  parentBox.addEventListener('click',e=>e.stopPropagation());
  parentBox.addEventListener('change',()=>{saved[parentBox.id]=parentBox.checked;localStorage.setItem('positional-layers-v2',JSON.stringify(saved));applyVisibility();});
  function applyVisibility(){
    const parent=document.getElementById('toggle-brainsight-parent')?.checked??true;
    sourceRaw.visible=parent&&document.getElementById('toggle-brainsight-targets').checked;
    sourceHead.visible=parent&&document.getElementById('toggle-brainsight-surface').checked;
    if(groups['Comparison lines'])groups['Comparison lines'].visible=parent&&document.getElementById('toggle-comparison-lines').checked;
    document.getElementById('toggle-brainsight-targets').dataset.renderVisible=String(sourceRaw.visible);
    document.getElementById('toggle-brainsight-surface').dataset.renderVisible=String(sourceHead.visible);
    for(const [name,v] of variantGroups){v.raw.visible=v.enabled.checked&&v.rawBox.checked;v.projected.visible=parent&&v.enabled.checked&&v.projectedBox.checked;v.lines.visible=parent&&v.enabled.checked&&v.projectedBox.checked;}
  }
  function variant(name){
    const detail=make('details');detail.open=true;const summary=make('summary');
    const slug=name.toLowerCase().replaceAll(' ','-');
    function box(suffix,label,parent){const input=make('input');input.type='checkbox';input.id='bs-'+slug+'-'+suffix;input.checked=saved[input.id]??true;input.setAttribute('aria-label',name+' '+label);input.addEventListener('click',e=>e.stopPropagation());input.onchange=()=>{saved[input.id]=input.checked;localStorage.setItem('positional-layers-v2',JSON.stringify(saved));applyVisibility();};const text=make('label');text.append(input,document.createTextNode(label));parent.append(text);return input;}
    const enabled=box('enabled',name,summary);detail.append(summary);
    const rawBox=box('raw','raw point',detail),projectedBox=box('projected','projected point',detail);
    document.getElementById('brainsight-target-layers').append(detail);
    const raw=new THREE.Group(),projected=new THREE.Group(),lines=new THREE.Group();
    sourceRaw.add(raw);groups['Projected cap points'].add(projected);groups['Projection lines'].add(lines);
    const value={raw,projected,lines,enabled,rawBox,projectedBox};variantGroups.set(name,value);return value;
  }
  const imported=make('details');imported.append(make('summary','Import results JSON'));
  const input=make('input');input.type='file';input.accept='.json';input.setAttribute('aria-label','Import positional results JSON');imported.append(input);panel.append(imported);
  let payload=null,revision=0;
  function dot(group,p,color,opacity=1){if(!p)return;const mesh=new THREE.Mesh(new THREE.SphereGeometry(1.8),new THREE.MeshBasicMaterial({color,transparent:opacity<1,opacity,depthTest:false,depthWrite:false}));mesh.position.fromArray(p);mesh.renderOrder=12;group.add(mesh);}
  function targetShape(position,name,group=sourceRaw){const mesh=new THREE.Mesh(new THREE.ConeGeometry(3.8,7,4),new THREE.MeshBasicMaterial({color:0x43d17a,depthTest:false,depthWrite:false,transparent:true,opacity:1}));mesh.rotation.x=Math.PI/2;mesh.position.fromArray(position);mesh.renderOrder=10;mesh.name='Brainsight: '+name;group.add(mesh);}
  function line(group,a,b,color,label){if(!a||!b)return;group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a),new THREE.Vector3(...b)]),new THREE.LineBasicMaterial({color,depthTest:false})));if(label){const el=make('span',label,'projection-line-label');const obj=new CSS2DObject(el);obj.position.fromArray(a.map((v,i)=>(v+b[i])/2));group.add(obj);}}
  function dispose(group){for(const c of [...group.children]){c.traverse(n=>{n.geometry?.dispose();n.material?.dispose();n.element?.remove();});group.remove(c);}}
  function clear(){payload=null;variantGroups.clear();document.getElementById('brainsight-target-layers').replaceChildren();results.replaceChildren();panel.removeAttribute('data-brainsight-rendered');panel.removeAttribute('data-overlay-frame');for(const group of Object.values(groups))dispose(group);for(const box of controls)box.disabled=true;}
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
    for(const p of data.cap_points||[]){dot(groups['Projected cap points'],p.scalp,0xef5350,.45);line(groups['Projection lines'],p.raw,p.scalp,0xef5350,p.name+' → skin');}
    const metric=data.sma_projection;
    if(metric?.eeg_raw)checkMarker(metric.marker_name,metric.eeg_raw,markers);
    if(metric?.distance_mm!==undefined){
      if(metric.surface.surface_sha256!==data.common_skin?.surface_sha256)throw Error('Stale common-surface metric');
      const result=make('section',null,'sma-projection-result');result.append(make('h3',metric.measurement));result.append(make('strong',metric.distance_mm.toFixed(3)+' mm · '+metric.qc.toUpperCase()));result.append(make('p',metric.reason||'Confirmed mapping and reviewed common surface','hint'));
      result.append(table(['Coordinate (MRI world mm)','x, y, z'],[['EEG raw · cap',metric.eeg_raw],['SMA raw · source',metric.brainsight_raw_source],['SMA raw · cap',metric.brainsight_raw_cap],['EEG projected · cap',metric.eeg_projected],['SMA projected · cap',metric.brainsight_projected]].map(([name,p])=>[name,p.map(v=>v.toFixed(3)).join(', ')])));
      result.append(make('p',`Projection offsets: EEG ${metric.eeg_projection_offset_mm.toFixed(3)} mm; SMA ${metric.brainsight_projection_offset_mm.toFixed(3)} mm. Single-subject result; not cortical targeting error.`,'hint'));results.prepend(result);
      line(groups['Comparison lines'],metric.eeg_projected,metric.brainsight_projected,0xffffff,'SMA projected difference · '+metric.qc);
    }
    const valid=rows.filter(r=>r.qc==='valid').length;
    status.textContent=`${markers.subject} · ${valid}/${rows.length} trajectory comparisons available`+(metric?.distance_mm!==undefined?` · SMA projected ${metric.distance_mm.toFixed(3)} mm (${metric.qc.toUpperCase()})`:'');
    results.append(make('h3','Separate trajectory-based endpoint'));
    results.append(table(['Target / cap','Scalp-entry localization difference (mm)'],rows.map(r=>[`${r.target==='right_DLPFC'?'Right DLPFC':r.target} / ${r.cap_label}`,r.qc==='valid'?r.distance_mm.toFixed(3)+' mm':'Unavailable: '+(r.qc_issues?.join('; ')||r.reason)])));
    if(data.project_inventory?.planned_names?.length)results.append(make('p','Project targets: '+data.project_inventory.planned_names.join(', '),'hint'));
    const blockers=data.blockers||[...new Set(rows.filter(r=>r.qc!=='valid').map(r=>r.reason))];
    if(blockers.length){const detail=make('details');detail.open=true;detail.append(make('summary','Required inputs'));const list=make('ul');for(const reason of blockers)list.append(make('li',reason));detail.append(list);results.append(detail);}
    results.append(make('p','Scalp projection layer: red fiducials and green Brainsight points. SMA closest-triangle projections define the separately labeled projection endpoint; SMA Skin remains a diagnostic variant. Trajectory-based entries retain their own gates.','hint'));
    if(data.cap_points?.length){const detail=make('details');detail.open=true;detail.append(make('summary','Cap projections · mm'));detail.append(table(['Marker','Offset to scalp'],data.cap_points.map(p=>[p.label,p.projection_distance_mm.toFixed(3)])));results.append(detail);}
    for(const r of rows.filter(r=>r.qc==='valid'))results.append(make('p',`${r.cap_label}: ${r.method}`,'hint'));
    if(valid&&new Set(rows.map(r=>r.subject)).size>1){const summary=make('details');summary.append(make('summary','Across-subject summary · mm'));const fmt=v=>Number.isFinite(v)?v.toFixed(3):'—';summary.append(table(['Target','n','Mean','SD','Median','IQR'],Object.entries(data.summary||{}).map(([k,v])=>[k,v.n,fmt(v.mean),fmt(v.SD),fmt(v.median),fmt(v.IQR)])));results.append(summary);}
    if(data.brainsight){
      const bs=data.brainsight;
      if(bs.frame!=='cap_MRI_RAS_mm'||bs.marker_mri_sha256!==markers.source_sha256||bs.registration?.numerical_qc!=='passed')throw Error('Registered cap MRI frame unresolved');
      const detail=make('details');detail.open=true;detail.append(make('summary','Imported Brainsight targets'));
      detail.append(table(['Export name','Role','Projected SMA difference (mm)'],bs.targets.map(t=>{const r=rows.find(r=>r.brainsight_name===t.name&&r.qc==='valid');return [t.name,t.name==='SMA Skin'?'Diagnostic variant':t.internal_target||'Unassigned',t.name==='SMA'&&metric?.distance_mm!==undefined?metric.distance_mm.toFixed(3)+' · '+metric.qc:t.name==='SMA Skin'?'Diagnostic only':'Unavailable'];})));
      detail.append(make('p','Raw target offset to common scalp (QC only): '+bs.targets.map(t=>`${t.name}: ${t.raw_offset_to_common_scalp_mm.toFixed(2)} mm`).join('; '),'hint'));
      detail.append(make('p','Registered overlay in cap MRI RAS mm. Raw target positions are preserved; a raw-point offset is not the scalp-entry localization difference.','hint'));
      const qc=make('details');qc.append(make('summary','Registration QC · '+bs.registration.anatomical_qc.replaceAll('_',' ')));const qcImage=make('img');qcImage.src=`/api/subjects/${encodeURIComponent(markers.subject)}/registration-qc.png`;qcImage.alt='Source-to-cap MRI registration: before and after orthogonal overlays';qcImage.style.width='100%';const qcLink=make('a','Open full QC views');qcLink.href=qcImage.src;qcLink.target='_blank';qcLink.rel='noopener';qc.append(qcLink,qcImage);detail.append(qc);
      results.prepend(detail);
      for(const t of bs.targets){
        assertPoint(t.position);
        const v=variant(t.name);targetShape(t.position,t.name,v.raw);
        if(t.exploratory_scalp_projection){assertPoint(t.exploratory_scalp_projection.position);dot(v.projected,t.exploratory_scalp_projection.position,0x43d17a,.45);line(v.lines,t.position,t.exploratory_scalp_projection.position,0x43d17a,t.name+' → skin');}
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
    if(data.common_skin){
      const skin=data.common_skin;const detail=make('details');detail.open=true;detail.append(make('summary','Common skin QC · '+skin.status));
      const link=make('a','Open anatomical boundary QC');link.href=`/api/subjects/${encodeURIComponent(markers.subject)}/skin-qc.png`;link.target='_blank';detail.append(link);
      const audit=skin.selected_audit,old=skin.old_surface_audit;
      if(Number.isFinite(audit.raw_source_separation_mm))detail.append(table(['SMA vs SMA Skin','Separation mm'],[['Raw source',audit.raw_source_separation_mm],['Raw registered',audit.raw_cap_separation_mm],['Old mesh projected',old.projected_separation_mm],['Selected mesh projected',audit.projected_separation_mm]].map(([k,v])=>[k,v.toFixed(6)])));
      detail.append(make('p','Provisional cap-free intensity boundary, without erosion or cosmetic smoothing. Review skin/hair ambiguity, FOV edges, registration and competing surface regions.','hint'));results.append(detail);
      const ticket=revision;new PLYLoader().load(`/api/subjects/${encodeURIComponent(markers.subject)}/common-skin.ply`,geometry=>{if(ticket!==revision){geometry.dispose();return;}geometry.computeVertexNormals();commonHead.add(new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({color:0xc5cbd0,side:THREE.DoubleSide,transparent:true,opacity:.75})));hooks.onCommonSkin?.();if(!saved['common-skin-first-view']){saved['common-skin-first-view']=true;const box=document.getElementById('toggle-brainsight-surface');box.checked=false;box.dispatchEvent(new Event('change'));}panel.dataset.commonSkin=skin.status;});
    }
    applyVisibility();
    for(const box of controls)box.disabled=false;
    for(const id of ['toggle-scalp-entries','toggle-comparison-lines']){const box=document.getElementById(id);box.disabled=valid===0&&!(id==='toggle-comparison-lines'&&metric?.distance_mm!==undefined);box.title=box.disabled?'No verified trajectory comparison points are available':'';}
    payload=data;
  }
  async function load(){const ticket=++revision;clear();const markers=getMarkers();if(!markers?.source_sha256){status.textContent='Select an individual subject to load positional analysis.';return;}status.textContent='Loading saved analysis…';try{const response=await fetch(`/api/subjects/${encodeURIComponent(markers.subject)}/positional`);if(ticket!==revision)return;if(!response.ok)throw Error('Could not load analysis');const data=await response.json();if(ticket!==revision)return;render(data);}catch(e){if(ticket!==revision)return;clear();status.textContent=`${e.message}. Run python compare_positions.py --subject ${markers.subject}, then python run_viewer.py.`;}}
  reload.onclick=load;
  input.onchange=async()=>{const ticket=++revision;try{const data=JSON.parse(await input.files[0].text());if(ticket===revision)render(data);}catch(e){if(ticket===revision){clear();status.textContent=e.message;}}};
  for(const format of ['json','csv']){const b=make('button',`Export ${format.toUpperCase()}`);b.type='button';b.onclick=()=>{if(!payload)return;const exportRows=[...payload.rows,...(payload.sma_projection?[payload.sma_projection]:[])];const fields=[...new Set(exportRows.flatMap(r=>Object.keys(r)))];const quote=v=>'"'+String(typeof v==='object'?JSON.stringify(v):v??'').replaceAll('"','""')+'"';const content=format==='json'?JSON.stringify(payload,null,2):[fields.map(quote).join(','),...exportRows.map(r=>fields.map(k=>quote(r[k])).join(','))].join('\n');const a=make('a');a.href=URL.createObjectURL(new Blob([content],{type:'text/plain'}));a.download='positional.'+format;a.click();URL.revokeObjectURL(a.href);};toolbar.append(b);}
  document.getElementById('aim1-metrics').append(panel);
  return ()=>{input.value='';load();};
}
