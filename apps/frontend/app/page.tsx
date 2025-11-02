"use client";

import { useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const HEADER_HEIGHT_PX = 64;

interface GameState {
  grid_width: number;
  grid_height: number;
  snake: [number, number][];
  food: [number, number];
  score: number;
  running?: boolean;
}

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<Socket>();
  const [game, setGame] = useState<GameState | null>(null);
  const [gameOver, setGameOver] = useState(false);

  // === Connect to backend & listen for updates ===
  useEffect(() => {
    if (!socketRef.current) {
      socketRef.current = io("http://localhost:8765");

      const socket = socketRef.current;

      const onConnect = () => {
        console.log("[CONNECT] Connected to backend");
        socket.emit("start_game", {
          grid_width: 29,
          grid_height: 19,
          game_tick: 0.05,
        });
      };

      const onGameStarted = (data: GameState) => {
        console.log("[GAME_STARTED]", data);
        setGame(data);
        setGameOver(false);
      };

      const onGameUpdate = (data: GameState) => {
        setGame(data);
      };

      const onGameOver = (data: { score: number }) => {
        console.log("[GAME_OVER]", data);
        setGameOver(true);
      };

      socket.on("connect", onConnect);
      socket.on("game_started", onGameStarted);
      socket.on("game_update", onGameUpdate);
      socket.on("game_over", onGameOver);

      return () => {
        socket.off("connect", onConnect);
        socket.off("game_started", onGameStarted);
        socket.off("game_update", onGameUpdate);
        socket.off("game_over", onGameOver);
      };
    }
  }, []);

  // === Drawing logic ===
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");

    if (!ctx || !game) return;

    // Resize canvas to fill available space under header
    const containerWidth = window.innerWidth;
    const containerHeight = window.innerHeight - HEADER_HEIGHT_PX;
    const cellSize = Math.floor(
      Math.min(containerWidth / game.grid_width, containerHeight / game.grid_height)
    );

    canvas.width = game.grid_width * cellSize;
    canvas.height = game.grid_height * cellSize;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw grid background
    ctx.fillStyle = "#0a0a0a";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Draw snake
    if (Array.isArray(game.snake)) {
      ctx.fillStyle = "#22c55e"; // green
      for (const [x, y] of game.snake) {
        ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      }
    }

    // Draw food
    if (Array.isArray(game.food)) {
      const [fx, fy] = game.food;
      ctx.fillStyle = "#ef4444"; // red
      ctx.beginPath();
      ctx.arc(
        fx * cellSize + cellSize / 2,
        fy * cellSize + cellSize / 2,
        cellSize / 3,
        0,
        2 * Math.PI
      );
      ctx.fill();
    }

    // Draw score overlay (top left)
    ctx.fillStyle = "white";
    ctx.font = `${Math.max(16, cellSize)}px monospace`;
    ctx.textAlign = "left";
    ctx.textBaseline = "top";
    ctx.fillText(`Score: ${game.score}`, 8, 8);
  }, [game]);

  // === Handle window resizing ===
  useEffect(() => {
    const handleResize = () => {
      if (game) {
        const canvas = canvasRef.current;
        if (canvas) {
          const ctx = canvas.getContext("2d");
          if (ctx) {
            const cellSize = Math.floor(
              Math.min(
                window.innerWidth / game.grid_width,
                (window.innerHeight - HEADER_HEIGHT_PX) / game.grid_height
              )
            );
            canvas.width = game.grid_width * cellSize;
            canvas.height = game.grid_height * cellSize;
          }
        }
      }
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [game]);

  const handleRestart = () => {
    socketRef.current?.emit("start_game", {
      grid_width: 29,
      grid_height: 19,
      game_tick: 0.05,
    });
    setGameOver(false);
  };

  return (
    <div className="absolute top-16 left-0 right-0 bottom-0 flex flex-col items-center justify-center">
      <canvas
        ref={canvasRef}
        style={{
          border: "2px solid #333",
          backgroundColor: "#000",
          maxWidth: "100%",
          maxHeight: "100%",
        }}
      />

      {/* Overlay for Game Over + Score */}
      {gameOver && (
        <div className="absolute flex flex-col items-center justify-center backdrop-blur-md bg-black/70 rounded-2xl p-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Game Over</h2>
          <p className="text-lg text-gray-300 mb-6">
            Final Score: {game?.score ?? 0}
          </p>
          <button
            onClick={handleRestart}
            className="px-6 py-3 rounded-lg bg-green-500 text-white font-semibold hover:bg-green-600 transition"
          >
            Restart
          </button>
        </div>
      )}
    </div>
  );
}
