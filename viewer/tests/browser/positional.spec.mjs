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
  await expect(panel.getByRole('status')).toContainText('comparisons available',{timeout:30000});
  await expect(panel.locator('.positional-layer input')).toHaveCount(6);
  if(report.brainsight){
    await expect(panel).toHaveAttribute('data-brainsight-rendered',String(report.brainsight.targets.length));
    for(const t of report.brainsight.targets){
      await expect(page.locator('[data-bs-target]').filter({hasText:t.name+' · raw'})).toBeVisible();
    }
    await expect(panel).toContainText('Imported Brainsight targets');
    await expect(panel).toContainText('Registered overlay in cap MRI RAS mm');
    await expect(panel).toHaveAttribute('data-overlay-frame','cap_MRI_RAS_mm');
    await expect(panel).toContainText('Scalp-entry localization difference (mm)');
    await panel.getByText('Registration QC', {exact:false}).click();
    await expect.poll(()=>panel.locator('img').evaluate(img=>img.naturalWidth)).toBeGreaterThan(0);
    const surface=panel.locator('label').filter({hasText:'Registered Brainsight surface'}).locator('input');
    await surface.uncheck();await expect(surface).not.toBeChecked();await surface.check();
  }
  await expect(panel.getByRole('button',{name:'Reload analysis'})).toHaveCSS('background-color','rgb(42, 48, 60)');
  await expect(panel).toContainText('Cap projections');
  for(const point of report.cap_points||[])await expect(panel).toContainText(point.label);
  await panel.locator('.positional-layer input').first().uncheck();
  await expect(panel.locator('.positional-layer input').first()).not.toBeChecked();
  await panel.getByRole('button',{name:'Reload analysis'}).click();
  await expect(panel.getByRole('status')).toContainText('comparisons available');
  const download=page.waitForEvent('download');await panel.getByRole('button',{name:'Export JSON'}).click();
  expect((await download).suggestedFilename()).toBe('positional.json');
  if(report.brainsight)await expect(panel).toHaveAttribute('data-brainsight-rendered',String(report.brainsight.targets.length));
  await panel.scrollIntoViewIfNeeded();
  await page.screenshot({path:'test-results/positional-local.png'});
  expect(errors).toEqual([]);
});
