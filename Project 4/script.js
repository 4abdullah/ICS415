class BezierEditor {
  constructor(opts) {
    this.canvas    = document.querySelector(opts.canvas);
    this.ctx       = this.canvas.getContext('2d');
    this.coordsEl  = document.querySelector(opts.coordsEl);
    this.resetBtn  = document.querySelector(opts.resetBtn);
    this.addBtn    = document.querySelector(opts.addBtn);
    this.removeBtn = document.querySelector(opts.removeBtn);

    this.points    = [];
    this.dragIdx   = null;
    this.isDragging= false;

    // Bind events
    window.addEventListener('resize',    ()=>this.onResize());
    this.canvas.addEventListener('mousedown',  e=>this.onMouseDown(e));
    this.canvas.addEventListener('mousemove',  e=>this.onMouseMove(e));
    this.canvas.addEventListener('mouseup',    ()=>this.onMouseUp());
    this.canvas.addEventListener('contextmenu',e=>this.onContextMenu(e));
    this.resetBtn.addEventListener('click',    ()=>this.reset());
    this.addBtn.addEventListener('click',      ()=>this.addRandom());
    this.removeBtn.addEventListener('click',   ()=>this.removeLast());

    this.onResize();
    this.reset();
    requestAnimationFrame(()=>this.draw());
  }

  onResize() {
    this.canvas.width  = this.canvas.clientWidth;
    this.canvas.height = this.canvas.clientHeight;
  }

  reset() {
    this.points = [];
    this.updateCoords();
  }

  addRandom() {
    this.points.push([
      Math.random() * this.canvas.width,
      Math.random() * this.canvas.height
    ]);
    this.updateCoords();
  }

  removeLast() {
    this.points.pop();
    this.updateCoords();
  }

  onMouseDown(e) {
    const [mx,my] = this.getMousePos(e);
    this.dragIdx = this.points.findIndex(p=>{
      const dx=p[0]-mx, dy=p[1]-my;
      return dx*dx+dy*dy < 36;
    });
    if (this.dragIdx >= 0) {
      this.isDragging = true;
    } else if (e.button === 0) {
      this.points.push([mx,my]);
      this.updateCoords();
    }
  }

  onMouseMove(e) {
    if (!this.isDragging) return;
    const [mx,my] = this.getMousePos(e);
    this.points[this.dragIdx] = [mx,my];
    this.updateCoords();
  }

  onMouseUp() {
    this.isDragging = false;
    this.dragIdx    = null;
  }

  onContextMenu(e) {
    e.preventDefault();
    const [mx,my] = this.getMousePos(e);
    const idx = this.points.findIndex(p=>{
      const dx=p[0]-mx, dy=p[1]-my;
      return dx*dx+dy*dy < 36;
    });
    if (idx >= 0) {
      this.points.splice(idx,1);
      this.updateCoords();
    }
  }

  getMousePos(e) {
    const r = this.canvas.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  }

  updateCoords() {
    this.coordsEl.textContent = JSON.stringify(
      this.points.map(p=>[p[0].toFixed(1), p[1].toFixed(1)]),
      null, 2
    );
  }

  deCasteljau(pts, t) {
    if (pts.length === 1) return pts[0];
    const next = [];
    for (let i = 0; i < pts.length - 1; i++) {
      const [x1,y1] = pts[i], [x2,y2] = pts[i+1];
      next.push([ (1-t)*x1 + t*x2, (1-t)*y1 + t*y2 ]);
    }
    return this.deCasteljau(next, t);
  }

  draw() {
    const ctx = this.ctx, pts = this.points;
    ctx.clearRect(0,0,this.canvas.width,this.canvas.height);

    // Draw control polygon
    if (pts.length > 1) {
      ctx.beginPath();
      ctx.moveTo(...pts[0]);
      for (let p of pts.slice(1)) ctx.lineTo(...p);
      ctx.setLineDash([5,5]);
      ctx.strokeStyle = '#6c757d';
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // Draw Bézier curve
    if (pts.length > 1) {
      ctx.beginPath();
      for (let i = 0; i <= 200; i++) {
        const t = i / 200, [x,y] = this.deCasteljau(pts, t);
        i === 0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
      }
      ctx.strokeStyle = '#0d6efd';
      ctx.lineWidth   = 2;
      ctx.stroke();
      ctx.lineWidth   = 1;
    }

    // Draw control points
    pts.forEach(([x,y], i) => {
      ctx.beginPath();
      ctx.arc(x,y,6,0,2*Math.PI);
      ctx.fillStyle = (i===0||i===pts.length-1) ? '#198754' : '#fd7e14';
      ctx.fill();
      ctx.strokeStyle = '#00000033';
      ctx.stroke();
    });

    requestAnimationFrame(()=>this.draw());
  }
}

// Instantiate the Poly Bézier editor
document.addEventListener('DOMContentLoaded', () => {
  new BezierEditor({
    canvas:    '#canvasPoly',
    coordsEl:  '#polyCoords',
    resetBtn:  '#polyReset',
    addBtn:    '#polyAddRandom',
    removeBtn: '#polyRemoveLast'
  });
});
