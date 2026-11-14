import {calibrateVolatilityModel} from './modelCalibration.mjs';
let text=''; for await (const chunk of process.stdin) { text+=chunk; if(text.length>2000000)throw Error('Input exceeds budget'); }
try { const input=JSON.parse(text); const result=calibrateVolatilityModel(input.model,input.surface,input.options||{}); process.stdout.write(JSON.stringify(result)); }
catch(error){process.stderr.write(String(error.message||error));process.exitCode=2;}
