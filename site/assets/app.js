
(function(){
  var q=document.getElementById('q'), cards=[].slice.call(document.querySelectorAll('.card')),
      groups=[].slice.call(document.querySelectorAll('.group')), none=document.getElementById('none'),
      btns=[].slice.call(document.querySelectorAll('.filters button')), cur='all';
  function apply(){
    var k=(q.value||'').trim().toLowerCase(), shown=0;
    cards.forEach(function(c){
      var ok=(cur==='all'||c.classList.contains(cur)) && (!k||c.dataset.k.indexOf(k)>=0);
      c.style.display=ok?'':'none'; if(ok)shown++;
    });
    groups.forEach(function(g){ g.style.display=g.querySelector('.card:not([style*="none"])')?'':'none'; });
    none.hidden=shown>0;
  }
  q.addEventListener('input',apply);
  btns.forEach(function(b){b.addEventListener('click',function(){
    btns.forEach(function(x){x.classList.remove('on')}); b.classList.add('on');
    cur=b.dataset.f; apply();
  })});
})();
