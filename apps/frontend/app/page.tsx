"use client";

import { io, Socket } from "socket.io-client";
import { useEffect, useRef, useState } from "react";

export default function HomePage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [score, setScore] = useState(0);
  const [gameRunning, setGameRunning] = useState(false);
  const [snake, setSnake] = useState([{ x: 5, y: 5 }]);
  const [food, setFood] = useState({ x: 8, y: 8 });
  const [direction, setDirection] = useState("right");
  const [gameOver, setGameOver] = useState(false);

  const gridSize = 20; // pixels per cell
  const gridCount = 25; // 25x25 grid → 500x500px canvas
  const width = gridSize * gridCount;
  const height = gridSize * gridCount;

  // handle keypresses
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (!gameRunning) return;
      if (e.key === "ArrowUp" && direction !== "down") setDirection("up");
      if (e.key === "ArrowDown" && direction !== "up") setDirection("down");
      if (e.key === "ArrowLeft" && direction !== "right") setDirection("left");
      if (e.key === "ArrowRight" && direction !== "left") setDirection("right");
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [direction, gameRunning]);

  // draw everything
  useEffect(() => {
    const ctx = canvasRef.current?.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, width, height);

    // draw grid
    ctx.strokeStyle = "#333";
    for (let i = 0; i < gridCount; i++) {
      for (let j = 0; j < gridCount; j++) {
        ctx.strokeRect(i * gridSize, j * gridSize, gridSize, gridSize);
      }
    }

    // draw snake
    ctx.fillStyle = "#00FFFF";
    snake.forEach((segment) => {
      ctx.fillRect(segment.x * gridSize, segment.y * gridSize, gridSize, gridSize);
    });

    // draw food
    ctx.fillStyle = "red";
    ctx.beginPath();
    ctx.arc(
      food.x * gridSize + gridSize / 2,
      food.y * gridSize + gridSize / 2,
      gridSize / 2 - 2,
      0,
      Math.PI * 2
    );
    ctx.fill();
  }, [snake, food]);

  // main game loop
  useEffect(() => {
    if (!gameRunning || gameOver) return;
    const interval = setInterval(() => {
      moveSnake();
    }, 150);
    return () => clearInterval(interval);
  });

  function moveSnake() {
    const newSnake = [...snake];
    const head = { ...newSnake[0] };

    if (direction === "up") head.y -= 1;
    if (direction === "down") head.y += 1;
    if (direction === "left") head.x -= 1;
    if (direction === "right") head.x += 1;

    // check wall collision
    if (
      head.x < 0 ||
      head.y < 0 ||
      head.x >= gridCount ||
      head.y >= gridCount
    ) {
      setGameOver(true);
      setGameRunning(false);
      return;
    }

    // check self collision
    if (newSnake.some((seg) => seg.x === head.x && seg.y === head.y)) {
      setGameOver(true);
      setGameRunning(false);
      return;
    }

    newSnake.unshift(head);

    // check food
    if (head.x === food.x && head.y === food.y) {
      setScore((s) => s + 1);
      setFood({
        x: Math.floor(Math.random() * gridCount),
        y: Math.floor(Math.random() * gridCount),
      });
    } else {
      newSnake.pop();
    }

    setSnake(newSnake);
  }

  function startGame() {
    setSnake([{ x: 5, y: 5 }]);
    setDirection("right");
    setFood({ x: 8, y: 8 });
    setScore(0);
    setGameOver(false);
    setGameRunning(true);
  }

  function handleRestart() {
    startGame();
  }

  return (
    <div className="relative flex flex-col items-center justify-center mt-8">
      {/* Score display (top-left of the grid) */}
      <div className="absolute top-0 left-0 text-red-500 font-bold text-lg z-20">
        Score: {score}
      </div>

      {/* Game canvas */}
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        className="border border-gray-700 rounded-xl bg-black"
      ></canvas>

      {/* Overlay (only shown when not running) */}
      {!gameRunning && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 rounded-2xl z-30">
          <h2 className="text-cyan-400 text-3xl font-bold mb-2">
            CSAI Student
          </h2>
          <p className="text-white mb-4">Score: {score}</p>
          <button
            onClick={handleRestart}
            className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-500"
          >
            {gameOver ? "Restart" : "Start Game"}
          </button>
        </div>
      )}
    </div>
  );
}
