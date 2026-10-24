const input=document.getElementById('search');
const status=document.getElementById('search-status');
const cards=[...document.querySelectorAll('.work-card')];
const corpus=new Map((window.NEOMYTHISM_SEARCH||[]).map(x=>[x.id,[x.title,x.credit,x.group,x.text].join(' ').normalize('NFKC').toLowerCase()]));
let timer;
function filter(){
  const terms=input.value.normalize('NFKC').toLowerCase().trim().split(/\s+/).filter(Boolean);
  let count=0;
  for(const card of cards){const hit=terms.every(term=>(corpus.get(card.dataset.id)||'').includes(term));card.hidden=!hit;if(hit)count++;}
  for(const group of document.querySelectorAll('.collection-group'))group.hidden=![...group.querySelectorAll('.work-card')].some(c=>!c.hidden);
  status.textContent=terms.length?`${count} matching records`:`${cards.length} records · search across full included text`;
  document.getElementById('no-results').hidden=count>0;
}
input.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(filter,120);});
document.getElementById('clear-search').addEventListener('click',()=>{input.value='';filter();input.focus();});
input.addEventListener('keydown',e=>{if(e.key==='Escape'){input.value='';filter();}});
filter();
