async function runCheck(caseId){
  const box=document.getElementById('pythonStatus');
  box.textContent='Running deterministic rule check…';
  const r=await fetch('/api/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({case_id:caseId})});
  const d=await r.json();
  box.textContent = d.status + ' — ' + d.finding;
}
async function copyPrompt(caseId){
  const box=document.getElementById('promptStatus');
  const r=await fetch('/api/prompt',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({case_id:caseId})});
  const d=await r.json();
  await navigator.clipboard.writeText(d.prompt);
  box.textContent='AI prompt copied to clipboard.';
}
let decision='';
function setDecision(btn,value){
  document.querySelectorAll('.review-btn').forEach(b=>b.classList.remove('selected'));
  btn.classList.add('selected'); decision=value;
}
function saveReview(caseId){
  const note=document.getElementById('reviewNote').value.trim();
  const box=document.getElementById('reviewSaved');
  if(!decision){box.textContent='Select Accept, Edit, or Reject first.'; return;}
  if(!note){box.textContent='Add a short reviewer note before saving.'; return;}
  const key='netsage-review-'+caseId;
  localStorage.setItem(key,JSON.stringify({decision,note,at:new Date().toISOString()}));
  box.textContent=`Saved locally: ${decision}.`;
}
const search=document.getElementById('caseSearch');
if(search){
  search.addEventListener('input',()=>{
    const q=search.value.toLowerCase();
    document.querySelectorAll('.case-card').forEach(card=>card.style.display=card.dataset.search.includes(q)?'block':'none');
  });
}
