import {test,expect} from '@playwright/test';
import {existsSync,readFileSync} from 'node:fs';

// Optional local acceptance test: never checks in subject fixtures or screenshots.
const reportPath='../saves/derivatives/subjects/r-02/positional.json';
test('local r-02 CLI report loads automatically in existing right sidebar',async({page})=>{
  test.skip(!existsSync(reportPath),'Run python compare_positions.py --subject r-02 with local data first');
  const report=JSON.parse(readFileSync(reportPath,'utf8'));
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  await expect(page.locator('#stage')).toHaveAttribute('data-subject','MNI152');
  await page.locator('#subject-select').selectOption('r-02');
  await expect(page.locator('#stage')).toHaveAttribute('data-subject','r-02');
  const panel=page.locator('#dist #aim1-metrics #positional-panel');
  await expect(panel).toHaveCount(1);
  await expect(page.locator('#metrics-panel')).toHaveCount(0);
  await expect(page.getByText('No Brainsight data yet.',{exact:false})).toHaveCount(0);
  await expect(panel.getByRole('status')).toContainText('comparisons available',{timeout:30000});
  if(report.common_skin){
    await expect(panel).toHaveAttribute('data-common-skin',report.common_skin.status);
    await expect(panel.locator('.sma-projection-result')).toContainText('SMA scalp-projected localization difference (mm)');
    await expect(panel.locator('.sma-projection-result')).toContainText(report.sma_projection.qc.toUpperCase());
    const parent=page.locator('#toggle-brainsight-parent');await parent.uncheck();
    await expect(page.locator('#toggle-brainsight-targets')).toHaveAttribute('data-render-visible','false');await parent.check();
    for(const name of ['SMA','SMA Skin']){
      const raw=page.getByRole('checkbox',{name:name+' raw point',exact:true});
      const projected=page.getByRole('checkbox',{name:name+' projected point',exact:true});
      await raw.uncheck();await projected.uncheck();await raw.check();await projected.check();
    }
    await page.locator('#toggle-projection-lines').check();await page.locator('#toggle-projection-lines').uncheck();
  }
  await expect(panel.locator('.positional-layer input')).toHaveCount(0);
  for(const id of ['toggle-brainsight-surface','toggle-brainsight-targets','toggle-scalp-projections']){
    const box=page.locator('#ui #'+id);await expect(box).toBeVisible();await expect(box).toBeEnabled();
    await box.uncheck();await expect(box).toHaveAttribute('data-render-visible','false');
    await box.check();await expect(box).toHaveAttribute('data-render-visible','true');
  }
  if(report.brainsight){
    await expect(panel).toHaveAttribute('data-brainsight-rendered',String(report.brainsight.targets.length));
    await expect(page.locator('[data-bs-target]')).toHaveCount(0);
    await expect(panel).toHaveAttribute('data-brainsight-shape','sphere');
    await expect(panel).toHaveAttribute('data-scalp-projections',String(report.cap_points.length+report.brainsight.targets.length));
    await expect(panel).toContainText('Imported Brainsight targets');
    await expect(panel).toContainText('Registered overlay in cap MRI RAS mm');
    await expect(panel).toHaveAttribute('data-overlay-frame','cap_MRI_RAS_mm');
    await expect(panel).toContainText('Scalp-entry localization difference (mm)');
    await panel.getByText('Registration QC', {exact:false}).click();
    await expect.poll(()=>panel.locator('img').evaluate(img=>img.naturalWidth)).toBeGreaterThan(0);
    const surface=page.locator('#toggle-brainsight-surface');
    await surface.uncheck();await expect(surface).not.toBeChecked();await surface.check();
  }
  await expect(panel.getByRole('button',{name:'Reload analysis'})).toHaveCSS('background-color','rgb(42, 48, 60)');
  await expect(panel).toContainText('Cap projections');
  for(const point of report.cap_points||[])await expect(panel).toContainText(point.label);
  await page.locator('#toggle-scalp-projections').uncheck();
  await expect(page.locator('#toggle-scalp-projections')).toHaveAttribute('data-render-visible','false');
  if(report.common_skin)await page.getByRole('checkbox',{name:'SMA Skin raw point',exact:true}).uncheck();
  await panel.getByRole('button',{name:'Reload analysis'}).click();
  await expect(panel.getByRole('status')).toContainText('comparisons available');
  await expect(page.locator('#toggle-scalp-projections')).not.toBeChecked();await page.locator('#toggle-scalp-projections').check();
  if(report.common_skin){await expect(page.getByRole('checkbox',{name:'SMA Skin raw point',exact:true})).not.toBeChecked();await page.getByRole('checkbox',{name:'SMA Skin raw point',exact:true}).check();}
  const download=page.waitForEvent('download');await panel.getByRole('button',{name:'Export JSON'}).click();
  expect((await download).suggestedFilename()).toBe('positional.json');
  if(report.brainsight)await expect(panel).toHaveAttribute('data-brainsight-rendered',String(report.brainsight.targets.length));
  await panel.scrollIntoViewIfNeeded();
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const beforeTargets=await page.locator('#c').screenshot();
  await page.locator('#toggle-brainsight-targets').uncheck();
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  const withoutTargets=await page.locator('#c').screenshot();
  expect(beforeTargets.equals(withoutTargets)).toBe(false);
  await page.locator('#toggle-brainsight-targets').check();
  await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.screenshot({path:'test-results/positional-layers.png'});
  expect(errors).toEqual([]);
});
