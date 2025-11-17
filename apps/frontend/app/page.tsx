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
  agent_stats?: {
    games: number;
    record: number;
    epsilon: number;
  };
}

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<Socket>();
  const [game, setGame] = useState<GameState | null>(null);
  const [connected, setConnected] = useState(false);
  const [isTraining, setIsTraining] = useState(false);

  // === Connect to backend & listen for updates ===
  useEffect(() => {
    if (!socketRef.current) {
      socketRef.current = io("http://localhost:8765");

      const socket = socketRef.current;

      const onConnect = () => {
        console.log("[CONNECT] Connected to backend");
        setConnected(true);
      };

      const onDisconnect = () => {
        console.log("[DISCONNECT] Disconnected from backend");
        setConnected(false);
        setIsTraining(false);
      };

      const onGameStarted = (data: GameState) => {
        console.log("[GAME_STARTED]", data);
        setGame(data);
        setIsTraining(true);
      };

      const onGameUpdate = (data: GameState) => {
        setGame(data);
      };

      const onGameOver = (data: { score: number; games: number; record: number }) => {
        console.log("[GAME_OVER] Game:", data.games, "Score:", data.score, "Record:", data.record);
        // Don't show overlay - AI will auto-restart
      };

      const onError = (data: { message: string }) => {
        console.error("[ERROR]", data.message);
      };

      socket.on("connect", onConnect);
      socket.on("disconnect", onDisconnect);
      socket.on("game_started", onGameStarted);
      socket.on("game_update", onGameUpdate);
      socket.on("game_over", onGameOver);
      socket.on("error", onError);

      return () => {
        socket.off("connect", onConnect);
        socket.off("disconnect", onDisconnect);
        socket.off("game_started", onGameStarted);
        socket.off("game_update", onGameUpdate);
        socket.off("game_over", onGameOver);
        socket.off("error", onError);
        socket.disconnect();
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

    // Draw grid lines
    ctx.strokeStyle = "#1a1a1a";
    ctx.lineWidth = 1;
    for (let x = 0; x <= game.grid_width; x++) {
      ctx.beginPath();
      ctx.moveTo(x * cellSize, 0);
      ctx.lineTo(x * cellSize, canvas.height);
      ctx.stroke();
    }
    for (let y = 0; y <= game.grid_height; y++) {
      ctx.beginPath();
      ctx.moveTo(0, y * cellSize);
      ctx.lineTo(canvas.width, y * cellSize);
      ctx.stroke();
    }

    // Draw snake
    if (Array.isArray(game.snake)) {
      game.snake.forEach((segment, index) => {
        ctx.fillStyle = index === 0 ? "#22c55e" : "#4ade80"; // head is darker green
        ctx.fillRect(
          segment[0] * cellSize + 1,
          segment[1] * cellSize + 1,
          cellSize - 2,
          cellSize - 2
        );
      });
    }

    // Draw food
    if (Array.isArray(game.food)) {
      const [fx, fy] = game.food;
      ctx.fillStyle = "#ef4444"; // red
      ctx.shadowBlur = 10;
      ctx.shadowColor = "#ef4444";
      ctx.beginPath();
      ctx.arc(
        fx * cellSize + cellSize / 2,
        fy * cellSize + cellSize / 2,
        cellSize / 3,
        0,
        2 * Math.PI
      );
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    // Draw stats overlay (top left)
    const fontSize = Math.max(14, Math.floor(cellSize * 0.7));
    ctx.font = `${fontSize}px monospace`;
    ctx.textAlign = "left";
    ctx.textBaseline = "top";

    // Semi-transparent background for text
    ctx.fillStyle = "rgba(0, 0, 0, 0.7)";
    ctx.fillRect(4, 4, 250, game.agent_stats ? 85 : 30);

    // Score
    ctx.fillStyle = "white";
    ctx.fillText(`Score: ${game.score}`, 8, 8);

    // Agent stats if available
    if (game.agent_stats) {
      ctx.fillStyle = "#22c55e";
      ctx.fillText(`Games: ${game.agent_stats.games}`, 8, 8 + fontSize + 4);
      ctx.fillStyle = "#3b82f6";
      ctx.fillText(`Record: ${game.agent_stats.record}`, 8, 8 + (fontSize + 4) * 2);
      ctx.fillStyle = "#eab308";
      ctx.fillText(`Explore: ${game.agent_stats.epsilon.toFixed(1)}`, 8, 8 + (fontSize + 4) * 3);
    }
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

  const handleStartTraining = () => {
    if (socketRef.current && connected) {
      socketRef.current.emit("start_game", {
        grid_width: 29,
        grid_height: 19,
        game_tick: 0.05,
      });
    }
  };

  const handleSaveModel = () => {
    if (socketRef.current && connected) {
      socketRef.current.emit("save_model", {});
      alert("Model saved successfully!");
    }
  };

  return (
    <div className="absolute top-16 left-0 right-0 bottom-0 flex flex-col items-center justify-center bg-gray-950">
      <canvas
        ref={canvasRef}
        style={{
          border: "2px solid #333",
          backgroundColor: "#000",
          maxWidth: "100%",
          maxHeight: "100%",
        }}
      />

      {/* Control buttons when not training */}
      {!isTraining && (
        <div className="absolute flex flex-col items-center justify-center gap-4">
          <div className="text-center mb-4">
            <h2 className="text-3xl font-bold text-white mb-2">Snake AI Training</h2>
            <p className="text-gray-400">
              {connected ? "Ready to start training" : "Connecting to server..."}
            </p>
          </div>
          <button
            onClick={handleStartTraining}
            disabled={!connected}
            className="px-8 py-4 rounded-lg bg-green-500 text-white font-semibold hover:bg-green-600 disabled:bg-gray-600 disabled:cursor-not-allowed transition text-lg"
          >
            {connected ? "Start Training" : "Connecting..."}
          </button>
        </div>
      )}

      {/* Save button when training */}
      {isTraining && (
        <div className="absolute bottom-8 right-8">
          <button
            onClick={handleSaveModel}
            className="px-6 py-3 rounded-lg bg-blue-500 text-white font-semibold hover:bg-blue-600 transition shadow-lg"
          >
            Save Model
          </button>
        </div>
      )}

      {/* Connection status indicator */}
      <div className="absolute top-20 right-4">
        <div
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            connected ? "bg-green-900 text-green-300" : "bg-red-900 text-red-300"
          }`}
        >
          {connected ? "● Connected" : "● Disconnected"}
        </div>
      </div>
    </div>
  );
}