import React, { useEffect, useRef } from 'react';
import Matter from 'matter-js';

export interface PhysicsMoodData {
  id: string;
  type: string;
  intensity: number;
  timestamp: string;
  keywords: string[];
  recordId: string;
}

interface PhysicsMoodBubbleProps {
  moods: PhysicsMoodData[];
  onMoodClick: (mood: PhysicsMoodData) => void;
  containerWidth: number;
  containerHeight: number;
}

// 心情类型到颜色的映射
const getMoodColor = (type: string): { fill: string; stroke: string; glow: string } => {
  const colorMap: Record<string, { fill: string; stroke: string; glow: string }> = {
    '喜悦': { fill: '#FED7AA', stroke: '#FB923C', glow: 'rgba(251, 146, 60, 0.4)' },
    '开心': { fill: '#FECACA', stroke: '#FB7185', glow: 'rgba(251, 113, 133, 0.4)' },
    '兴奋': { fill: '#FEF08A', stroke: '#FACC15', glow: 'rgba(250, 204, 21, 0.4)' },
    '平静': { fill: '#BFDBFE', stroke: '#60A5FA', glow: 'rgba(96, 165, 250, 0.4)' },
    '放松': { fill: '#D9F99D', stroke: '#84CC16', glow: 'rgba(132, 204, 22, 0.4)' },
    '焦虑': { fill: '#DDD6FE', stroke: '#A78BFA', glow: 'rgba(167, 139, 250, 0.4)' },
    '紧张': { fill: '#E9D5FF', stroke: '#C084FC', glow: 'rgba(192, 132, 252, 0.4)' },
    '悲伤': { fill: '#CBD5E1', stroke: '#64748B', glow: 'rgba(100, 116, 139, 0.4)' },
    '疲惫': { fill: '#E0E7FF', stroke: '#818CF8', glow: 'rgba(129, 140, 248, 0.4)' },
    '困倦': { fill: '#F3E8FF', stroke: '#D8B4FE', glow: 'rgba(216, 180, 254, 0.4)' },
  };
  
  return colorMap[type] || { fill: '#E2E8F0', stroke: '#94A3B8', glow: 'rgba(148, 163, 184, 0.4)' };
};

export const PhysicsMoodBubble: React.FC<PhysicsMoodBubbleProps> = ({
  moods,
  onMoodClick,
  containerWidth,
  containerHeight,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<Matter.Engine | null>(null);
  const renderRef = useRef<Matter.Render | null>(null);
  const bodiesRef = useRef<Map<string, { body: Matter.Body; mood: PhysicsMoodData }>>(new Map());
  const mouseConstraintRef = useRef<Matter.MouseConstraint | null>(null);
  const onMoodClickRef = useRef(onMoodClick);

  // 更新回调引用（不触发重新渲染）
  useEffect(() => {
    onMoodClickRef.current = onMoodClick;
  }, [onMoodClick]);

  useEffect(() => {
    if (!canvasRef.current) {
      return;
    }
    
    if (moods.length === 0) {
      return;
    }
    
    if (containerWidth === 0 || containerHeight === 0) {
      return;
    }

    console.log('🎨 创建物理气泡池:', { 气泡数量: moods.length, 容器: `${containerWidth}x${containerHeight}` });

    // 创建物理引擎
    const engine = Matter.Engine.create({
      gravity: { x: 0, y: 0.05, scale: 0.001 }, // 极轻微的重力
    });
    engineRef.current = engine;

    // 创建渲染器
    const render = Matter.Render.create({
      canvas: canvasRef.current,
      engine: engine,
      options: {
        width: containerWidth,
        height: containerHeight,
        wireframes: false,
        background: 'transparent',
        pixelRatio: window.devicePixelRatio || 1,
        showAngleIndicator: false,
        showCollisions: false,
        showVelocity: false,
      },
    });
    renderRef.current = render;

    // 创建边界墙（不可见）
    const wallThickness = 50;
    const walls = [
      // 顶部
      Matter.Bodies.rectangle(containerWidth / 2, -wallThickness / 2, containerWidth, wallThickness, {
        isStatic: true,
        render: { visible: false },
      }),
      // 底部
      Matter.Bodies.rectangle(containerWidth / 2, containerHeight + wallThickness / 2, containerWidth, wallThickness, {
        isStatic: true,
        render: { visible: false },
      }),
      // 左侧
      Matter.Bodies.rectangle(-wallThickness / 2, containerHeight / 2, wallThickness, containerHeight, {
        isStatic: true,
        render: { visible: false },
      }),
      // 右侧
      Matter.Bodies.rectangle(containerWidth + wallThickness / 2, containerHeight / 2, wallThickness, containerHeight, {
        isStatic: true,
        render: { visible: false },
      }),
    ];

    Matter.World.add(engine.world, walls);

    // 创建气泡
    const bodies = moods.map((mood, index) => {
      // 根据强度计算半径 (intensity 1-10 -> radius 25-60)
      const radius = 25 + (mood.intensity / 10) * 35;
      
      // 随机初始位置（避免重叠）
      const angle = (index / moods.length) * Math.PI * 2;
      const distance = Math.min(containerWidth, containerHeight) * 0.2;
      const x = containerWidth / 2 + Math.cos(angle) * distance;
      const y = containerHeight / 2 + Math.sin(angle) * distance;

      const colors = getMoodColor(mood.type);
      
      const body = Matter.Bodies.circle(x, y, radius, {
        restitution: 0.6, // 弹性系数（0-1，越大越弹）
        friction: 0.01, // 摩擦力
        frictionAir: 0.02, // 空气阻力
        density: 0.001, // 密度
        render: {
          fillStyle: colors.fill,
          strokeStyle: colors.stroke,
          lineWidth: 2,
        },
        label: mood.id, // 用于识别
      });

      // 添加初始随机速度
      Matter.Body.setVelocity(body, {
        x: (Math.random() - 0.5) * 2,
        y: (Math.random() - 0.5) * 2,
      });

      bodiesRef.current.set(mood.id, { body, mood });
      return body;
    });

    Matter.World.add(engine.world, bodies);

    // 添加鼠标交互
    const mouse = Matter.Mouse.create(canvasRef.current);
    const mouseConstraint = Matter.MouseConstraint.create(engine, {
      mouse: mouse,
      constraint: {
        stiffness: 0.2,
        render: { visible: false },
      },
    });
    mouseConstraintRef.current = mouseConstraint;

    Matter.World.add(engine.world, mouseConstraint);

    // 点击事件
    Matter.Events.on(mouseConstraint, 'mousedown', (event) => {
      const mousePosition = event.mouse.position;
      const clickedBody = Matter.Query.point(bodies, mousePosition)[0];
      
      if (clickedBody) {
        const moodData = bodiesRef.current.get(clickedBody.label);
        if (moodData) {
          onMoodClickRef.current(moodData.mood);
        }
      }
    });

    // 启动引擎和渲染
    const runner = Matter.Runner.create();
    Matter.Runner.run(runner, engine);
    Matter.Render.run(render);
    
    console.log('✅ 物理气泡池启动成功');

    // 自定义渲染（添加文字和光晕效果）
    Matter.Events.on(render, 'afterRender', () => {
      const context = render.context;
      
      bodiesRef.current.forEach(({ body, mood }) => {
        const { position } = body;
        const radius = body.circleRadius || 30;
        const colors = getMoodColor(mood.type);

        // 绘制光晕
        context.save();
        context.globalAlpha = 0.3;
        const gradient = context.createRadialGradient(
          position.x, position.y, radius * 0.5,
          position.x, position.y, radius * 1.5
        );
        gradient.addColorStop(0, colors.glow);
        gradient.addColorStop(1, 'transparent');
        context.fillStyle = gradient;
        context.beginPath();
        context.arc(position.x, position.y, radius * 1.5, 0, Math.PI * 2);
        context.fill();
        context.restore();

        // 绘制高光（毛玻璃效果）
        context.save();
        context.globalAlpha = 0.5;
        context.fillStyle = 'rgba(255, 255, 255, 0.6)';
        context.beginPath();
        context.arc(
          position.x - radius * 0.3,
          position.y - radius * 0.3,
          radius * 0.25,
          0,
          Math.PI * 2
        );
        context.fill();
        context.restore();

        // 绘制文字
        context.save();
        context.fillStyle = '#334155';
        context.font = `${Math.max(12, radius * 0.35)}px sans-serif`;
        context.textAlign = 'center';
        context.textBaseline = 'middle';
        context.fillText(mood.type, position.x, position.y);
        context.restore();
      });
    });

    // 添加轻微的随机扰动（模拟布朗运动）
    const intervalId = setInterval(() => {
      bodiesRef.current.forEach(({ body }) => {
        Matter.Body.applyForce(body, body.position, {
          x: (Math.random() - 0.5) * 0.0001,
          y: (Math.random() - 0.5) * 0.0001,
        });
      });
    }, 100);

    // 清理函数
    return () => {
      clearInterval(intervalId);
      Matter.Render.stop(render);
      Matter.Runner.stop(runner);
      Matter.World.clear(engine.world, false);
      Matter.Engine.clear(engine);
      if (render.canvas) {
        render.canvas.remove();
      }
      render.textures = {};
    };
  }, [moods, containerWidth, containerHeight]);

  return (
    <div className="absolute inset-0" style={{ zIndex: 1 }}>
      <canvas
        ref={canvasRef}
        className="absolute inset-0"
        style={{ cursor: 'pointer', zIndex: 1 }}
      />
    </div>
  );
};
