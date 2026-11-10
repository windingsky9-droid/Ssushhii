/**
 * Sushir Tactical Decision Engine — portable, dependency-free training logic.
 * Modeled situations only. This does not read or control Rainbow Six Siege.
 * Every output is deterministic for the same inputs.
 */
export const SCENARIOS = Object.freeze({
  entry: ['DRONE', 'PRE-AIM', 'CONTACT', 'TRADE', 'RESET'],
  defense: ['SETUP', 'LISTEN', 'CONTACT', 'FALLBACK', 'HOLD'],
  clutch: ['LISTEN', 'ISOLATE', 'CONTACT', 'SHIFT', 'FINISH'],
  late: ['TIME', 'LOCATE', 'PICK', 'COMMIT', 'CLOSE'],
});

const result = (decision, reason, next) => ({ decision, reason, next });

export function decideEngagement({scenario='entry', phase=0, intel=false, allyReady=false}={}) {
  if (!Object.hasOwn(SCENARIOS, scenario)) throw new RangeError('Unknown scenario');
  const step = Number(phase);
  if (!Number.isInteger(step) || step < 0 || step > 4) throw new RangeError('Phase must be 0–4');
  const known = intel === true, trade = allyReady === true && scenario !== 'clutch';
  let advice;
  if (scenario === 'defense') {
    advice = step >= 3
      ? result('RESET', 'Preserve the clock and change positions.', 'Fall back to a second defensible angle.')
      : known && trade && step >= 2
        ? result('TRADE', 'Confirmed contact and a separate teammate angle.', 'Ping and hold the crossfire.')
        : result('HOLD', 'The attacker must spend time to move you.', 'Listen and keep a fallback route.');
  } else if (scenario === 'clutch') {
    advice = step === 0 && !known
      ? result('LISTEN', 'Do not expose yourself to multiple unconfirmed angles.', 'Isolate audio from cover.')
      : step >= 3
        ? result('REPOSITION', 'Repeating a known peek favors the defender.', 'Change angle before the next challenge.')
        : result(known ? 'ISOLATE' : 'HOLD', 'Create a single isolated engagement.', 'Pre-aim one lane with an exit.');
  } else if (scenario === 'late') {
    advice = step >= 2
      ? result('COMMIT', 'The remaining clock limits further information gathering.', 'Execute the feasible objective route.')
      : result(known ? 'SETUP' : 'LOCATE', 'Establish one feasible path before committing.', 'Check clock and objective access.');
  } else {
    advice = step >= 4
      ? result('RESET', 'Avoid an identical second peek.', 'Break line of sight and re-drone.')
      : step >= 2 && known && trade
        ? result('COMMIT', 'Enemy is located and the trade is ready.', 'Swing with your crosshair prepared.')
        : step >= 2 && known
          ? result('ISOLATE', 'Enemy is known but a trade is not ready.', 'Take a narrow angle and save your exit.')
          : result('HOLD', 'An unconfirmed entry gives away initiative.', 'Drone or listen, then pre-aim.');
  }
  return Object.freeze({scenario, phase:step, beat:SCENARIOS[scenario][step], ...advice, modeled:true});
}
