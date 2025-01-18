<script lang="ts">
  let isInView = $state(false);
  let canvas: HTMLCanvasElement;
  let animationFrameId: number;
  let memoizedColor: string;

  let {
    squareSize = 4,
    gridGap = 6,
    flickerChance = 0.3,
    color = 'rgb(0, 0, 0)',
    width,
    height,
    maxOpacity = 0.3,
    class: className = '',
  } = $props<{
    squareSize?: number;
    gridGap?: number;
    flickerChance?: number;
    color?: string;
    width?: number;
    height?: number;
    maxOpacity?: number;
    class?: string;
  }>();

  $derived: {
    memoizedColor = toRGBA(color);
  }

  function toRGBA(color: string) {
    if (typeof window === 'undefined') {
      return `rgba(0, 0, 0,`;
    }
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1;
    const ctx = canvas.getContext('2d');
    if (!ctx) return 'rgba(255, 0, 0,';
    ctx.fillStyle = color;
    ctx.fillRect(0, 0, 1, 1);
    const [r, g, b] = ctx.getImageData(0, 0, 1, 1).data;
    return `rgba(${r}, ${g}, ${b},`;
  }

  function setupCanvas() {
    const dpr = typeof window !== 'undefined' ? window.devicePixelRatio : 1;
    const canvasWidth = width || canvas.offsetWidth;
    const canvasHeight = height || canvas.offsetHeight;

    canvas.width = canvasWidth * dpr;
    canvas.height = canvasHeight * dpr;
    canvas.style.width = `${canvasWidth}px`;
    canvas.style.height = `${canvasHeight}px`;

    const cols = Math.floor(canvasWidth / (squareSize + gridGap));
    const rows = Math.floor(canvasHeight / (squareSize + gridGap));

    const squares = Array.from({ length: cols * rows }, () => ({
      opacity: Math.random() * maxOpacity,
      targetOpacity: Math.random() * maxOpacity,
      transitionSpeed: 2 + Math.random() * 3,
    }));

    return { canvasWidth, canvasHeight, cols, rows, squares, dpr };
  }

  function updateSquares(
    squares: Array<{ opacity: number; targetOpacity: number; transitionSpeed: number }>,
    deltaTime: number
  ) {
    squares.forEach((square) => {
      if (Math.random() < flickerChance * deltaTime) {
        square.targetOpacity = Math.random() * maxOpacity;
      }

      const diff = square.targetOpacity - square.opacity;
      square.opacity += diff * square.transitionSpeed * deltaTime;
    });
  }

  function drawGrid(
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    cols: number,
    rows: number,
    squares: Array<{ opacity: number }>,
    dpr: number
  ) {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < cols; i++) {
      for (let j = 0; j < rows; j++) {
        const square = squares[i + j * cols];
        if (!square) continue;

        const x = i * (squareSize + gridGap) * dpr;
        const y = j * (squareSize + gridGap) * dpr;
        const size = squareSize * dpr;

        ctx.fillStyle = `${memoizedColor}${square.opacity})`;
        ctx.fillRect(x, y, size, size);
      }
    }
  }

  $effect(() => {
    if (!canvas) return;

    // Reset isInView when component mounts
    isInView = false;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let { canvasWidth, canvasHeight, cols, rows, squares, dpr } = setupCanvas();
    let lastTime = 0;

    const animate = (time: number) => {
      if (!isInView) return;
      const deltaTime = (time - lastTime) / 1000;
      lastTime = time;

      updateSquares(squares, deltaTime);
      drawGrid(ctx, canvasWidth * dpr, canvasHeight * dpr, cols, rows, squares, dpr);
      animationFrameId = requestAnimationFrame(animate);
    };

    const handleResize = () => {
      ({ canvasWidth, canvasHeight, cols, rows, squares, dpr } = setupCanvas());
    };

    const observer = new IntersectionObserver(
      ([entry]) => {
        isInView = entry.isIntersecting;
        if (isInView) {
          // Cancel any existing animation frame before starting a new one
          if (animationFrameId) {
            cancelAnimationFrame(animationFrameId);
          }
          animationFrameId = requestAnimationFrame(animate);
        }
      },
      { threshold: 0 }
    );

    observer.observe(canvas);
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
      }
      observer.disconnect();
    };
  });
</script>

<canvas bind:this={canvas} class={className} />
