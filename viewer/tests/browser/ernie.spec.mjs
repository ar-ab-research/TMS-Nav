import {test,expect} from '@playwright/test';
import {existsSync} from 'node:fs';

test('Ernie landmark edits persist and checked electrodes and arcs remain rendered',async({page})=>{
  test.skip(!existsSync('src/data/Ernie/markers.json'),'Restore the public Ernie demo first');
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/');
  await page.locator('#subject-select').selectOption('Ernie');
  await expect(page.locator('#stage')).toHaveAttribute('data-subject','Ernie');
  for(const id of ['toggle-eeg','toggle-arcs','toggle-targets','toggle-coil'])await page.locator('#'+id).check();
  const names=await page.locator('#landmark-select option').evaluateAll(options=>options.map(o=>o.value));
  expect(names).toHaveLength(4);
  for(const name of names){
    await page.locator('#landmark-select').selectOption(name);
    const x=Number(await page.locator('#landmark-x').inputValue());
    await page.locator('#landmark-x').fill(String(x+.2));
    await page.getByRole('button',{name:'Apply coordinates',exact:true}).click();
  }
  const saved=await page.evaluate(()=>localStorage.getItem('tms-nav-landmarks-v1:Ernie'));
  const checkRendering=async()=>{
    for(const id of ['toggle-eeg','toggle-arcs']){
      await expect(page.locator('#'+id)).toBeChecked();
      const rendered=await page.locator('#c').screenshot();
      await page.locator('#'+id).uncheck();
      const hidden=await page.locator('#c').screenshot();
      expect(rendered.equals(hidden)).toBe(false);
      await page.locator('#'+id).check();
    }
  };
  await expect(page.locator('#eeg-status')).toContainText('Showing original demo electrodes');
  await checkRendering();
  await page.reload();
  await expect(page.locator('#stage')).toHaveAttribute('data-subject','Ernie');
  await expect(page.locator('#landmark-status')).toContainText('Restored browser edits');
  expect(await page.evaluate(()=>localStorage.getItem('tms-nav-landmarks-v1:Ernie'))).toBe(saved);
  await expect(page.locator('#eeg-status')).toContainText('Showing original demo electrodes');
  await checkRendering();
  expect(errors).toEqual([]);
});

test('public Ernie Aim 2 fields load and switch sites and placements',async({page})=>{
  test.skip(!existsSync('src/data/Ernie/efield/manifest.json'),'Restore the public Ernie demo first');
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('/#aim2');
  await page.locator('#subject-select').selectOption('Ernie');
  await expect(page.locator('#stage')).toHaveAttribute('data-subject','Ernie');
  await expect(page.locator('#a2-body')).toBeVisible();
  for(const site of ['F4','SMA']){
    await page.locator('#a2-sites').getByRole('button',{name:site,exact:true}).click();
    for(const name of ['MRI-guided','Cap from MRI']){
      await page.locator('#a2-methods').getByRole('button',{name,exact:true}).click();
      await expect(page.locator('#a2-roi')).toContainText('V/m');
    }
  }
  await page.locator('#a2-diff').check();
  await expect(page.locator('#a2-roi')).toContainText('V/m');
  await page.locator('#subject-select').selectOption('MNI152');
  await expect(page.locator('#a2-empty')).toBeVisible();
  expect(errors).toEqual([]);
});
