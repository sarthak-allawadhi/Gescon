let ambientAnimationId = null;
let currentStream = null;

function startAmbientAnimation() {
  const canvas = document.getElementById('ambientCanvas');
  if(!canvas) return;
  if(ambientAnimationId) return; // Already running

  const ctx = canvas.getContext('2d');
  function resize(){
    canvas.width = canvas.clientWidth * devicePixelRatio;
    canvas.height = canvas.clientHeight * devicePixelRatio;
  }
  resize();
  window.addEventListener('resize', resize);

  const connections = [
    [0,1],[1,2],[2,3],[3,4],
    [0,5],[5,6],[6,7],[7,8],
    [0,9],[9,10],[10,11],[11,12],
    [0,13],[13,14],[14,15],[15,16],
    [0,17],[17,18],[18,19],[19,20],
    [5,9],[9,13],[13,17]
  ];
  const base = [
    [0.5,0.85],[0.42,0.72],[0.36,0.58],[0.33,0.46],[0.30,0.36],
    [0.44,0.5],[0.42,0.32],[0.41,0.19],[0.40,0.08],
    [0.5,0.5],[0.5,0.3],[0.5,0.16],[0.5,0.05],
    [0.56,0.52],[0.58,0.33],[0.59,0.19],[0.60,0.09],
    [0.62,0.56],[0.66,0.42],[0.69,0.32],[0.71,0.24]
  ];

  let t = 0;
  function draw(){
    const w = canvas.width, h = canvas.height;
    ctx.clearRect(0,0,w,h);
    t += 0.02;
    const curl = (Math.sin(t)+1)/2;

    const pts = base.map((p,i)=>{
      const foldFactor = i>4 ? curl*0.18 : 0;
      const x = p[0]*w;
      const y = (p[1] + foldFactor*(1-p[1])*0.3)*h + Math.sin(t+i)*2;
      return [x,y];
    });

    ctx.lineWidth = 1.6;
    ctx.strokeStyle = 'rgba(79,216,196,0.55)';
    connections.forEach(([a,b])=>{
      ctx.beginPath();
      ctx.moveTo(pts[a][0], pts[a][1]);
      ctx.lineTo(pts[b][0], pts[b][1]);
      ctx.stroke();
    });

    pts.forEach((p,i)=>{
      ctx.beginPath();
      ctx.arc(p[0], p[1], i===0?5:3.4, 0, Math.PI*2);
      ctx.fillStyle = i===4 || i===8 ? '#FF8A5C' : '#4FD8C4';
      ctx.fill();
    });

    ambientAnimationId = requestAnimationFrame(draw);
  }
  draw();
}

function stopAmbientAnimation() {
  if (ambientAnimationId) {
    cancelAnimationFrame(ambientAnimationId);
    ambientAnimationId = null;
  }
}

// MediaPipe variables
let handsModel = null;
let cameraUtil = null;
let cameraRunning = false;

async function loadScript(src){
  return new Promise((resolve,reject)=>{
    const s = document.createElement('script');
    s.src = src;
    s.onload = resolve;
    s.onerror = () => reject(new Error('Failed to load script: ' + src));
    document.head.appendChild(s);
  });
}

function stopCamera() {
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop());
    currentStream = null;
  }
  if (cameraUtil) {
    cameraUtil.stop();
    cameraUtil = null;
  }
  cameraRunning = false;
  // Reset buttons
  const startBtn = document.getElementById('startBtn');
  if (startBtn) {
    startBtn.textContent = 'Enable camera';
    startBtn.disabled = false;
  }
  const statusPill = document.getElementById('statusPill');
  const statusText = document.getElementById('statusText');
  if (statusPill && statusText) {
    statusPill.classList.remove('live');
    statusText.textContent = 'Camera off';
  }
}

function initDemo() {
  const startBtn = document.getElementById('startBtn');
  if (!startBtn) return;
  
  // Make sure we don't attach multiple listeners
  if (startBtn.getAttribute('data-listener-attached')) return;
  startBtn.setAttribute('data-listener-attached', 'true');

  startBtn.addEventListener('click', async ()=>{
    const btn = document.getElementById('startBtn');
    const statusPill = document.getElementById('statusPill');
    const statusText = document.getElementById('statusText');
    if(cameraRunning) return;
    btn.textContent = 'Loading model…';
    btn.disabled = true;

    try{
      if(!window.Hands){
        await loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js');
      }

      const videoEl = document.getElementById('video');
      const overlay = document.getElementById('overlay');
      const placeholder = document.getElementById('placeholder');
      const octx = overlay.getContext('2d');
      const cursorDot = document.getElementById('cursorDot');
      const pad = document.getElementById('pad');
      const pinchVal = document.getElementById('pinchVal');
      const stateVal = document.getElementById('stateVal');

      const stream = await navigator.mediaDevices.getUserMedia({ video:{ width:640, height:480 } });
      videoEl.srcObject = stream;
      currentStream = stream;
      placeholder.style.display = 'none';

      handsModel = new window.Hands({ locateFile:(f)=>`https://cdn.jsdelivr.net/npm/@mediapipe/hands/${f}` });
      handsModel.setOptions({ maxNumHands:1, modelComplexity:1, minDetectionConfidence:0.6, minTrackingConfidence:0.6 });

      function dist(a,b){ return Math.hypot(a.x-b.x, a.y-b.y); }

      handsModel.onResults((results)=>{
        // Check if elements are still in DOM
        const curVideo = document.getElementById('video');
        const curOverlay = document.getElementById('overlay');
        if (!curVideo || !curOverlay) return;

        curOverlay.width = curVideo.videoWidth || 640;
        curOverlay.height = curVideo.videoHeight || 480;
        octx.clearRect(0,0,curOverlay.width, curOverlay.height);

        if(results.multiHandLandmarks && results.multiHandLandmarks.length){
          const lm = results.multiHandLandmarks[0];

          const HAND_CONNECTIONS = [[0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],[0,9],[9,10],[10,11],[11,12],[0,13],[13,14],[14,15],[15,16],[0,17],[17,18],[18,19],[19,20],[5,9],[9,13],[13,17]];
          octx.strokeStyle = 'rgba(79,216,196,0.8)';
          octx.lineWidth = 2;
          HAND_CONNECTIONS.forEach(([a,b])=>{
            octx.beginPath();
            octx.moveTo(lm[a].x*curOverlay.width, lm[a].y*curOverlay.height);
            octx.lineTo(lm[b].x*curOverlay.width, lm[b].y*curOverlay.height);
            octx.stroke();
          });
          lm.forEach((p,i)=>{
            octx.beginPath();
            octx.arc(p.x*curOverlay.width, p.y*curOverlay.height, i===4||i===8?5:3, 0, Math.PI*2);
            octx.fillStyle = (i===4||i===8) ? '#FF8A5C' : '#4FD8C4';
            octx.fill();
          });

          const pinchDist = dist(lm[4], lm[8]);
          if(pinchVal) pinchVal.textContent = pinchDist.toFixed(3);
          const isPinching = pinchDist < 0.055;
          if(stateVal) stateVal.textContent = isPinching ? 'CLICK' : 'MOVE';
          if(cursorDot) {
            cursorDot.classList.toggle('clicking', isPinching);
            const nx = 1 - lm[8].x;
            const ny = lm[8].y;
            cursorDot.style.left = (nx*100)+'%';
            cursorDot.style.top = (ny*100)+'%';
          }
        } else {
          if(pinchVal) pinchVal.textContent = '—';
          if(stateVal) stateVal.textContent = 'NO HAND';
        }
      });

      if(!window.Camera){
        await loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js');
      }
      cameraUtil = new window.Camera(videoEl, {
        onFrame: async ()=>{ 
          const activeVideo = document.getElementById('video');
          if (activeVideo && handsModel) {
            await handsModel.send({ image: activeVideo }); 
          }
        },
        width: 640, height: 480
      });
      cameraUtil.start();

      cameraRunning = true;
      statusPill.classList.add('live');
      statusText.textContent = 'Tracking live';
      btn.textContent = 'Camera active';
    }catch(err){
      console.error(err);
      statusText.textContent = 'Error: ' + err.message + ' (' + err.name + ')';
      btn.textContent = 'Enable camera';
      btn.disabled = false;
      alert('Camera Error: ' + err.toString());
    }
  });
}

// Router checker to re-init components on page changes
function checkPageElements() {
  const canvas = document.getElementById('ambientCanvas');
  if (canvas) {
    startAmbientAnimation();
  } else {
    stopAmbientAnimation();
  }

  const startBtn = document.getElementById('startBtn');
  if (startBtn) {
    initDemo();
  } else {
    if (cameraRunning) {
      stopCamera();
    }
  }
}

// Observe page DOM mutations (routing)
const observer = new MutationObserver(checkPageElements);
observer.observe(document.body, { childList: true, subtree: true });

// Run initial check
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', checkPageElements);
} else {
  checkPageElements();
}
