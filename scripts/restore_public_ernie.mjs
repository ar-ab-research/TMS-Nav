// Restore the published, public Ernie demo without downloading a FEM head model.
// Read only the pinned gh-pages snapshot already held in the local Git objects.
import {execFileSync} from 'node:child_process';
import {mkdirSync, writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {join} from 'node:path';
import vm from 'node:vm';

const root=fileURLToPath(new URL('../',import.meta.url));
const ref='04263d28d0cd3e4e549e5bd9bb57a7fee0e3a5c8';
const blob=name=>execFileSync('git',['show',`${ref}:${name}`],{cwd:root,maxBuffer:64*1024*1024});
const html=blob('index.html').toString();
const imports=JSON.parse(html.match(/<script type=importmap>(.*?)<\/script>/s)[1]).imports;
const bundle=blob('viewer.59849639.js').toString();
function jsonModule(variable){
  const expression=bundle.match(new RegExp(`${variable}=JSON\\.parse\\(('(?:\\\\.|[^'\\\\])*')\\)`))[1];
  return JSON.parse(vm.runInNewContext(expression,Object.create(null),{timeout:1000}));
}
function asset(variable){
  const key=bundle.match(new RegExp(`${variable}=import\\.meta\\.resolve\\("([^"]+)"\\)`))[1];
  return blob(imports[key].replace(/^\.\//,''));
}
const out=join(root,'viewer/src/data/Ernie');mkdirSync(join(out,'efield'),{recursive:true});
writeFileSync(join(out,'markers.json'),JSON.stringify(jsonModule('sD'),null,2));
writeFileSync(join(out,'efield/manifest.json'),JSON.stringify(jsonModule('sR'),null,2));
writeFileSync(join(out,'scalp.ply'),asset('sW'));
writeFileSync(join(out,'coil.ply'),asset('sY'));
writeFileSync(join(out,'montecarlo.json'),asset('sI'));
const entry=bundle.match(/Ernie:\{label:"Ernie".*?files:\{(.*?)\}\}\}/s)[1];
for(const match of entry.matchAll(/"([^"]+)":new URL\(([^)]+)\)/g)){
  writeFileSync(join(out,'efield',match[1]),asset(match[2].replace('$','\\$')));
}
console.log(`Restored public Ernie Aim 1 and Aim 2 assets from ${ref}. Run scripts/refresh_viewer_registry.py next.`);
