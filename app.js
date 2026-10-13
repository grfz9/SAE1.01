const BASE = 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/';
const SEED = [
  { user: 'nature_lover', avatar: '🌸', desc: 'Les fleurs qui s\'ouvrent 🌼 #nature #fyp', music: 'Son original - nature_lover', src: 'ForBiggerBlazes.mp4' },
  { user: 'roadtrip', avatar: '🚗', desc: 'Petite virée en voiture 😎 #vibes', music: 'Chill beats - lofi', src: 'ForBiggerJoyrides.mp4' },
  { user: 'funny.daily', avatar: '😂', desc: 'Quand le prof dit "interro surprise" #humour', music: 'Oh no - Kreepa', src: 'ForBiggerFun.mp4' },
  { user: 'escape', avatar: '🏝️', desc: 'Vacances quand ? ☀️ #travel', music: 'Summer - Calvin Harris', src: 'ForBiggerEscapes.mp4' },
  { user: 'meltdown', avatar: '🔥', desc: 'Moment intense 😳 #wow', music: 'Son original - meltdown', src: 'ForBiggerMeltdowns.mp4' },
];

const load = (k, d) => { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch { return d; } };
const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };

const state = load('minitok', {});
const videos = SEED.map((v, i) => ({
  id: 'v' + i, ...v, src: BASE + v.src,
  likes: 1000 + i * 3721, shares: 120 + i * 37,
  liked: false, followed: false, comments: [{ user: 'fan_' + i, text: 'Trop bien 😍' }],
  ...state['v' + i],
}));
const myUploads = [];
const persist = () => save('minitok', Object.fromEntries(videos.filter(v => !v.local).map(v =>
  [v.id, { likes: v.likes, liked: v.liked, followed: v.followed, comments: v.comments }])));

const $ = s => document.querySelector(s);
const feed = $('#feed');
const fmt = n => n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e3 ? (n / 1e3).toFixed(1) + 'K' : n;
const toast = msg => { const t = $('#toast'); t.textContent = msg; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 1200); };

function slideHTML(v) {
  return `<div class="slide" data-id="${v.id}">
    <video src="${v.src}" loop playsinline muted preload="metadata"></video>
    <div class="progress"></div>
    <div class="info"><h3>@${v.user}</h3><p>${v.desc}</p><div class="music">🎵 ${v.music}</div></div>
    <div class="actions">
      <button data-act="follow"><div class="avatar">${v.avatar}${v.followed ? '' : '<div class="follow">+</div>'}</div></button>
      <button data-act="like" class="${v.liked ? 'liked' : ''}">❤<span>${fmt(v.likes)}</span></button>
      <button data-act="comment">💬<span>${v.comments.length}</span></button>
      <button data-act="share">↗<span>${fmt(v.shares)}</span></button>
    </div></div>`;
}

let currentFeed = 'foryou';
function render() {
  const list = currentFeed === 'following' ? videos.filter(v => v.followed) : videos;
  feed.innerHTML = list.length ? list.map(slideHTML).join('') :
    '<div class="slide"><p style="padding:30px;text-align:center">Abonne-toi à des créateurs pour voir leurs vidéos ici ✨</p></div>';
  feed.scrollTop = 0;
  feed.querySelectorAll('.slide video').forEach(vid => {
    observer.observe(vid);
    vid.addEventListener('timeupdate', () => {
      vid.parentElement.querySelector('.progress').style.width = (vid.currentTime / vid.duration * 100 || 0) + '%';
    });
  });
}

let soundOn = false;
const observer = new IntersectionObserver(entries => entries.forEach(e => {
  const vid = e.target;
  if (e.isIntersecting) { vid.muted = !soundOn; vid.play().catch(() => {}); vid.parentElement.classList.remove('paused'); }
  else { vid.pause(); vid.currentTime = 0; }
}), { threshold: 0.6 });

const byId = id => videos.find(v => v.id === id);

function toggleLike(slide, force) {
  const v = byId(slide.dataset.id);
  if (force && v.liked) return;
  v.liked = !v.liked; v.likes += v.liked ? 1 : -1;
  const btn = slide.querySelector('[data-act=like]');
  btn.classList.toggle('liked', v.liked); btn.querySelector('span').textContent = fmt(v.likes);
  btn.classList.remove('pop'); void btn.offsetWidth; btn.classList.add('pop');
  persist(); updateProfile();
}

let lastTap = 0;
feed.addEventListener('click', e => {
  const slide = e.target.closest('.slide[data-id]');
  if (!slide) return;
  const btn = e.target.closest('[data-act]');
  const v = byId(slide.dataset.id);
  if (btn) {
    const act = btn.dataset.act;
    if (act === 'like') toggleLike(slide);
    if (act === 'comment') openComments(v);
    if (act === 'share') { v.shares++; btn.querySelector('span').textContent = fmt(v.shares);
      navigator.clipboard?.writeText(location.href + '#' + v.id).catch(() => {}); toast('Lien copié !'); }
    if (act === 'follow') { v.followed = !v.followed; btn.querySelector('.avatar').innerHTML = v.avatar + (v.followed ? '' : '<div class="follow">+</div>');
      toast(v.followed ? 'Abonné à @' + v.user : 'Désabonné'); persist(); }
    return;
  }
  const vid = slide.querySelector('video');
  const now = Date.now();
  if (now - lastTap < 300) { // double tap = like
    toggleLike(slide, true);
    const h = document.createElement('div'); h.className = 'heart'; h.textContent = '❤';
    const r = slide.getBoundingClientRect();
    h.style.left = e.clientX - r.left - 45 + 'px'; h.style.top = e.clientY - r.top - 60 + 'px';
    slide.appendChild(h); setTimeout(() => h.remove(), 800);
    clearTimeout(feed._t);
  } else {
    feed._t = setTimeout(() => {
      if (!soundOn) { soundOn = true; vid.muted = false; toast('🔊 Son activé'); return; }
      vid.paused ? vid.play() : vid.pause(); slide.classList.toggle('paused', vid.paused);
    }, 300);
  }
  lastTap = now;
});

let openVid = null;
function openComments(v) {
  openVid = v;
  $('#cList').innerHTML = v.comments.map(c => `<li><b>@${c.user}</b>${c.text.replace(/</g, '&lt;')}</li>`).join('');
  $('#cCount').textContent = v.comments.length + ' commentaires';
  $('#comments').hidden = false;
}
$('#closeComments').onclick = () => $('#comments').hidden = true;
$('#cForm').onsubmit = e => {
  e.preventDefault();
  const text = $('#cInput').value.trim(); if (!text) return;
  openVid.comments.push({ user: 'moi', text }); $('#cInput').value = '';
  openComments(openVid); persist();
  const s = feed.querySelector(`[data-id="${openVid.id}"] [data-act=comment] span`); if (s) s.textContent = openVid.comments.length;
};

document.querySelectorAll('.tab').forEach(t => t.onclick = () => {
  document.querySelectorAll('.tab').forEach(x => x.classList.toggle('active', x === t));
  currentFeed = t.dataset.feed; render();
});

$('#uploadBtn').onclick = () => $('#fileInput').click();
$('#fileInput').onchange = e => {
  const f = e.target.files[0]; if (!f) return;
  const desc = prompt('Description de ta vidéo :', '#fyp') ?? '';
  const v = { id: 'u' + Date.now(), user: 'moi', avatar: '🙂', desc, music: 'Son original - moi',
    src: URL.createObjectURL(f), likes: 0, shares: 0, liked: false, followed: true, comments: [], local: true };
  videos.unshift(v); myUploads.push(v);
  showPage('home'); currentFeed = 'foryou'; render(); updateProfile(); toast('Vidéo publiée ! 🎉');
  e.target.value = '';
};

function updateProfile() {
  $('#pLikes').textContent = videos.filter(v => v.liked).length;
  $('#pPosts').textContent = myUploads.length;
  $('#pGrid').innerHTML = myUploads.map(v => `<video src="${v.src}" muted></video>`).join('');
}
function showPage(name) {
  document.querySelectorAll('[data-nav]').forEach(b => b.classList.toggle('active', b.dataset.nav === name));
  $('#profile').hidden = name !== 'profile';
  if (name !== 'home' && name !== 'profile') toast('Bientôt disponible 🚧');
  if (name === 'profile') feed.querySelectorAll('video').forEach(v => v.pause());
}
document.querySelectorAll('[data-nav]').forEach(b => b.onclick = () => showPage(b.dataset.nav));

document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT') return;
  if (e.key === 'ArrowDown') feed.scrollBy({ top: feed.clientHeight, behavior: 'smooth' });
  if (e.key === 'ArrowUp') feed.scrollBy({ top: -feed.clientHeight, behavior: 'smooth' });
});

render(); updateProfile();
