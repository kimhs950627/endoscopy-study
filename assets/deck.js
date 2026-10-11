(function(){
  const slides=[...document.querySelectorAll('.slide')];
  let i=0;
  const pg=document.getElementById('pg'), bar=document.getElementById('bar');
  function render(){
    slides.forEach((s,n)=>s.classList.toggle('active',n===i));
    if(pg) pg.innerHTML='<b>'+(i+1)+'</b> / '+slides.length;
    if(bar) bar.style.width=((i+1)/slides.length*100)+'%';
  }
  function go(d){ i=Math.min(slides.length-1,Math.max(0,i+d)); render(); }
  window.go=go;
  document.addEventListener('keydown',e=>{
    if(['ArrowRight','ArrowDown',' ','PageDown','Enter'].includes(e.key)){e.preventDefault();go(1);}
    if(['ArrowLeft','ArrowUp','PageUp'].includes(e.key)){e.preventDefault();go(-1);}
    if(e.key==='Home'){i=0;render();}
    if(e.key==='End'){i=slides.length-1;render();}
  });
  render();
})();
