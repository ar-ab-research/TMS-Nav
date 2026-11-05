import * as THREE from 'three';
// Payload coordinates are native RAS mm, identical to scalp geometry. No scaling.
export function positionalViewer(root, getMarkers) {
  const panel=document.createElement('details');
  const title=document.createElement('summary'); title.textContent='Aim 1 positional scalp comparison';panel.append(title);
  const input=document.createElement('input'); input.type='file';input.accept='.json';panel.append(input);
  const status=document.createElement('pre');panel.append(status);
  const groups={};
  for(const name of ['Original cap markers','Projected cap points','Raw Brainsight / trajectories','Brainsight scalp points','Comparison lines']) {
    const group=new THREE.Group();groups[name]=group;root.add(group);
    const label=document.createElement('label'),box=document.createElement('input');box.type='checkbox';box.checked=true;
    box.onchange=()=>{group.visible=box.checked;};label.append(box,document.createTextNode(name));panel.append(label,document.createElement('br'));
  }
  let payload;
  function dot(group,p,color){if(!p)return;const mesh=new THREE.Mesh(new THREE.SphereGeometry(2),new THREE.MeshBasicMaterial({color}));mesh.position.fromArray(p);group.add(mesh);}
  function line(group,a,b,color){if(!a||!b)return;group.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...a),new THREE.Vector3(...b)]),new THREE.LineBasicMaterial({color})));}
  function clear(){for(const g of Object.values(groups)){for(const c of [...g.children]){c.geometry?.dispose();c.material?.dispose();g.remove(c);}}}
  input.onchange=async()=>{clear();try{
    payload=JSON.parse(await input.files[0].text());
    const markers=getMarkers();
    if(payload.frame!=='native_RAS_mm'||!Array.isArray(payload.rows))throw Error('Expected native RAS mm results');
    const rows=payload.rows.filter(r=>r.subject===markers.subject);
    if(!rows.length)throw Error('No results for current subject');
    for(const r of rows){
      const marker=markers.fiducials?.find(m=>m.name===r.marker_name);
      if(r.eeg_raw && (!marker || marker.position.some((v,i)=>Math.abs(v-r.eeg_raw[i])>1e-6)))throw Error('Marker coordinates changed; recompute results');
      if(!markers.source_sha256 || r.provenance.context.marker_mri_sha256!==markers.source_sha256)throw Error('MRI identity mismatch');
    }
    for(const r of rows){
      dot(groups['Original cap markers'],r.eeg_raw,0xffaa00);dot(groups['Projected cap points'],r.eeg_scalp,0x00ffff);
      dot(groups['Raw Brainsight / trajectories'],r.brainsight_raw,0xff00ff);
      line(groups['Raw Brainsight / trajectories'],r.trajectory?.outside,r.trajectory?.inside,0xff00ff);
      if(r.qc==='valid'){dot(groups['Brainsight scalp points'],r.brainsight_scalp,0x00ff00);line(groups['Comparison lines'],r.eeg_scalp,r.brainsight_scalp,0xffffff);}
    }
    status.textContent=rows.map(r=>`${r.subject} ${r.target} / ${r.cap_label}: ${r.qc==='valid'?r.distance_mm.toFixed(3)+' mm':r.reason}\n${r.method}`).join('\n')+'\n'+JSON.stringify(payload.summary,null,2);
  }catch(e){clear();payload=null;status.textContent=e.message;}};
  for(const format of ['json','csv']){const b=document.createElement('button');b.textContent=`Export ${format.toUpperCase()}`;b.onclick=()=>{if(!payload)return;const fields=[...new Set(payload.rows.flatMap(r=>Object.keys(r)))];const quote=v=>'"'+String(typeof v==='object'?JSON.stringify(v):v??'').replaceAll('"','""')+'"';const content=format==='json'?JSON.stringify(payload,null,2):[fields.map(quote).join(','),...payload.rows.map(r=>fields.map(k=>quote(r[k])).join(','))].join('\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([content],{type:'text/plain'}));a.download='positional.'+format;a.click();URL.revokeObjectURL(a.href);};panel.append(b);}
  document.body.append(panel);panel.style.cssText='position:fixed;bottom:12px;left:12px;z-index:20;background:#17202a;color:white;padding:10px;max-height:60vh;overflow:auto;max-width:500px';
  return ()=>{clear();payload=null;status.textContent='Load reviewed comparison JSON for this subject';input.value='';};
}
