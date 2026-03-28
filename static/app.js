// app.js: fetch /api/tournament?url=... or /api/mock and update DOM
(function(){
  const POLL_INTERVAL = 15000; // ms

  function qs(name){
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  }

  const urlParam = qs('url');
  const useMock = !urlParam;
  const apiBase = useMock ? '/api/mock' : '/api/tournament?url=' + encodeURIComponent(urlParam);

  const nameEl = document.getElementById('tournament-name');
  const currentEl = document.getElementById('current');
  const upcomingList = document.getElementById('upcoming-list');

  function render(data){
    nameEl.textContent = data.name || 'Challonge';

    // current
    currentEl.innerHTML = '';
    if(data.current_matches && data.current_matches.length){
      data.current_matches.forEach(m => {
        const row = document.createElement('div');
        row.className = 'match-row';
        const left = document.createElement('div');
        left.innerHTML = `<div class="player">${m.player1 || ''}</div><div class="player muted">${m.player2 || ''}</div>`;
        const right = document.createElement('div');
        if(typeof m.score1 !== 'undefined'){
          right.innerHTML = `<div class="score">${m.score1} - ${m.score2}</div>`;
        }
        row.appendChild(left);
        row.appendChild(right);
        currentEl.appendChild(row);
      });
    } else {
      currentEl.textContent = '無正在進行的比賽';
    }

    // upcoming
    upcomingList.innerHTML = '';
    if(data.upcoming_matches && data.upcoming_matches.length){
      data.upcoming_matches.slice(0,6).forEach(m => {
        const li = document.createElement('li');
        li.innerHTML = `<span>${m.player1 || ''} vs ${m.player2 || ''}</span><span class="muted">` + (m.round || '') + `</span>`;
        upcomingList.appendChild(li);
      });
    } else {
      const li = document.createElement('li'); li.textContent = '無'; upcomingList.appendChild(li);
    }
  }

  async function fetchAndRender(){
    try{
      const res = await fetch(apiBase);
      if(!res.ok) throw new Error('network');
      const data = await res.json();
      render(data);
    }catch(e){
      console.warn('fetch error', e);
      nameEl.textContent = '載入失敗';
    }
  }

  fetchAndRender();
  setInterval(fetchAndRender, POLL_INTERVAL);
})();
