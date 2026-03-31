// main.js — shared helpers
function openModal(id){document.getElementById(id).classList.add('active');}
function closeModal(id){document.getElementById(id).classList.remove('active');}

// Auto-dismiss toasts
document.addEventListener('DOMContentLoaded',()=>{
  setTimeout(()=>{
    document.querySelectorAll('.toast').forEach(t=>{
      t.style.opacity='0';t.style.transition='opacity .5s';
      setTimeout(()=>t.remove(),500);
    });
  },4000);
  // Close modal on backdrop click
  document.querySelectorAll('.modal-overlay').forEach(o=>{
    o.addEventListener('click',e=>{if(e.target===o)o.classList.remove('active');});
  });
});
