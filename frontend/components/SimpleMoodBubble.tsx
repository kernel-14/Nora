import React, { useEffect, useRef } from 'react';
import Matter from 'matter-js';

export interface MoodData {
  id: string;
  type: string;
  intensity: number;
  timestamp: string;
  keywords: string[];
}

interface SimpleMoodBubbleProps {
  moods: MoodData[];
  onMoodClick: (mood: MoodData) => void;
}

const COLORS: Record<string, string> = {
  '喜悦': '#FED7AA',
  '开心': '#FECACA',
  '兴奋': '#FEF08A',
  '平静': '#BFDBFE',
  '放松': '#D9F99D',
  '焦虑': '#DDD6FE',
  '紧张': '#E9D5FF',
  '悲伤': '#CBD5E1',
  '疲惫': '#E0E7FF',
  '困倦': '#F3E8FF',
};

export const SimpleMoodBubble: React.FC<SimpleMoodBubbleProps> = ({ moods, onMoodClick }) => {
  const sceneRef = useRef<HTMLDivElement>(null);
  const engineRef = useRef<Matter.Engine | null>(null);

  useEffect(() => {
    if (!sceneRef.current || moods.length === 0) return;

    const width = sceneRef.current.clientWidth;
    const height = sceneRef.current.clientHeight;

    console.log('🎨 初始化气泡池:', { width, height, count: moods.length });

    // 创建引擎
    const engine = Matter.Engine.create({ gravity: { x: 0, y: 0.05, scale: 0.001 } });
    engineRef.current = engine;

    // 创建渲染器
    const render = Matter.Render.create({
      element: sceneRef.current,
      engine: engine,
      options: {
        width,
        height,
        wireframes: false,
        background: 'transparent',
      },
    });

    // 创建边界
    const walls = [
      Matter.Bodies.rectangle(width / 2, -25, width, 50, { isStatic: true, render: { visible: false } }),
      Matter.Bodies.rectangle(width / 2, height + 25, width, 50, { isStatic: true, render: { visible: false } }),
      Matter.Bodies.rectangle(-25, height / 2, 50, height, { isStatic: true, render: { visible: false } }),
      Matter.Bodies.rectangle(width + 25, height / 2, 50, height, { isStatic: true, render: { visible: false } }),
    ];
    Matter.World.add(engine.world, walls);

    // 创建气泡
    const bubbles = moods.map((mood, i) => {
      const radius = 25 + (mood.intensity / 10) * 35;
      const angle = (i / moods.length) * Math.PI * 2;
      const distance = Math.min(width, height) * 0.2;
      const x = width / 2 + Math.cos(angle) * distance;
      const y = height / 2 + Math.sin(angle) * distance;
      const color = COLORS[mood.type] || '#E2E8F0';

      const bubble = Matter.Bodies.circle(x, y, radius, {
        restitution: 0.6,
        friction: 0.01,
        frictionAir: 0.02,
        render: { fillStyle: color, strokeStyle: '#fff', lineWidth: 2 },
        label: mood.id,
      });

      Matter.Body.setVelocity(bubble, {
        x: (Math.random() - 0.5) * 2,
        y: (Math.random() - 0.5) * 2,
      });

      return { body: bubble, mood };
    });

    Matter.World.add(engine.world, bubbles.map(b => b.body));

    // 鼠标交互
    const mouse = Matter.Mouse.create(render.canvas);
    const mouseConstraint = Matter.MouseConstraint.create(engine, {
      mouse,
      constraint: { stiffness: 0.2, render: { visible: false } },
    });
    Matter.World.add(engine.world, mouseConstraint);

    // 点击事件
    Matter.Events.on(mouseConstraint, 'mousedown', (event) => {
      const clicked = Matter.Query.point(bubbles.map(b => b.body), event.mouse.position)[0];
      if (clicked) {
        const bubble = bubbles.find(b => b.body === clicked);
        if (bubble) onMoodClick(bubble.mood);
      }
    });

    // 自定义渲染文字
    Matter.Events.on(render, 'afterRender', () => {
      const ctx = render.context;
      bubbles.forEach(({ body, mood }) => {
        ctx.save();
        ctx.fillStyle = '#334155';
        ctx.font = `${Math.max(12, (body.circleRadius || 30) * 0.35)}px sans-serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(mood.type, body.position.x, body.position.y);
        ctx.restore();
      });
    });

    // 启动
    const runner = Matter.Runner.create();
    Matter.Runner.run(runner, engine);
    Matter.Render.run(render);

    console.log('✅ 气泡池启动成功');

    // 清理
    return () => {
      Matter.Render.stop(render);
      Matter.Runner.stop(runner);
      Matter.World.clear(engine.world, false);
      Matter.Engine.clear(engine);
      render.canvas.remove();
      render.textures = {};
    };
  }, []); // 空依赖，只运行一次

  return <div ref={sceneRef} style={{ width: '100%', height: '100%' }} />;
};
