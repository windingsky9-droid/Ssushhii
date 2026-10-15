import test from 'node:test';
import assert from 'node:assert/strict';
import {SCENARIOS,decideEngagement} from '../modules/tactical-decision-engine.mjs';

test('exposes four stable scenario timelines',()=>{
  assert.deepEqual(Object.keys(SCENARIOS),['entry','defense','clutch','late']);
  assert.ok(Object.values(SCENARIOS).every(v=>v.length===5));
});
test('entry rewards verified intel and trade, not imagined confidence',()=>{
  assert.equal(decideEngagement({scenario:'entry',phase:2}).decision,'HOLD');
  assert.equal(decideEngagement({scenario:'entry',phase:2,intel:true}).decision,'ISOLATE');
  assert.equal(decideEngagement({scenario:'entry',phase:2,intel:true,allyReady:true}).decision,'COMMIT');
});
test('defense uses clock and teammate geometry',()=>{
  assert.equal(decideEngagement({scenario:'defense',phase:2,intel:true,allyReady:true}).decision,'TRADE');
  assert.equal(decideEngagement({scenario:'defense',phase:3,intel:true,allyReady:true}).decision,'RESET');
});
test('clutch never treats allyReady as a real teammate',()=>{
  assert.equal(decideEngagement({scenario:'clutch',phase:0,allyReady:true}).decision,'LISTEN');
  assert.equal(decideEngagement({scenario:'clutch',phase:3,intel:true}).decision,'REPOSITION');
});
test('late round prioritizes objective after the setup phases',()=>{
  assert.equal(decideEngagement({scenario:'late',phase:3}).decision,'COMMIT');
});
test('rejects unknown scenarios and invalid timeline positions',()=>{
  assert.throws(()=>decideEngagement({scenario:'fake'}),RangeError);
  assert.throws(()=>decideEngagement({phase:-1}),RangeError);
  assert.throws(()=>decideEngagement({phase:2.5}),RangeError);
});
