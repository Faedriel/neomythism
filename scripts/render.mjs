import fs from 'node:fs';
const {marked} = await import(process.env.MARKED_MODULE || 'marked');
const items = JSON.parse(fs.readFileSync(0, 'utf8'));
process.stdout.write(JSON.stringify(items.map(text => marked.parse(text, {gfm:true, breaks:false}))));
