"use client";

import { useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const CELL_SIZE = 40;

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const socketRef = useRef<Socket | undefined>(undefined);

  const [gridWidth, setGridWidth] = useState(0);
  const [gridHeight, setGridHeight] = useState(0);
  const [snake, setSnake] = useState<number[][]>([]);
  const [food, setFood] = useState<number[]>([]);
  const [delay, setDelay] = useState<number>(0.05);
  const changingDelay = useRef(false);

  useEffect(() => {
    if (socketRef.current === undefined) {
      socketRef.current = io(process.env.NEXT_PUBLIC_SNAKE_URL);

      const onConnect = () => {
        console.log("connected to server");
        socketRef.current?.emit("start_game", {
          grid_width: Math.floor(window.innerWidth / CELL_SIZE),
          grid_height: Math.floor(window.innerHeight / CELL_SIZE),
          starting_tick: delay,
        });
      };

      const onUpdate = (data: {
        grid_width: number;
        grid_height: number;
        game_tick: number;
        snake: number[][];
        food: number[];
        score: number;
      }) => {
        setGridWidth(data.grid_width);
        setGridHeight(data.grid_height);
        if (!changingDelay.current) {
          setDelay(data.game_tick);
        }
        setSnake(data.snake);
        setFood(data.food);
      };

      const onGameOver = () => {
        console.log("game over");
      };

      socketRef.current.on("connect", onConnect);
      socketRef.current.on("update", onUpdate);
      socketRef.current.on("game_over", onGameOver);

      return () => {
        socketRef.current?.off("connect", onConnect);
        socketRef.current?.off("update", onUpdate);
        socketRef.current?.off("game_over", onGameOver);
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // socket stuff

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");

    const roundedRect = (x: number, y: number, color: string, size: number) => {
      if (!context) {
        return;
      }
      const offset = (CELL_SIZE - size) / 2;
      const width = size;
      const height = size;
      context.beginPath();
      context.moveTo(x + offset + size / 4, y + offset);
      context.arcTo(
        x + offset + width,
        y + offset,
        x + offset + width,
        y + offset + height,
        size / 4
      );
      context.arcTo(
        x + offset + width,
        y + offset + height,
        x + offset,
        y + offset + height,
        size / 4
      );
      context.arcTo(
        x + offset,
        y + offset + height,
        x + offset,
        y + offset,
        size / 4
      );
      context.arcTo(
        x + offset,
        y + offset,
        x + offset + width,
        y + offset,
        size / 4
      );
      context.closePath();
      context.fillStyle = color;
      context.fill();
    };

    const fillGrid = () => {
      if (!context) {
        return;
      }
      const isDark =
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches;
      const gridColor = isDark ? "#22272e" : "#FAFAFA";
      for (let i = 0; i < gridWidth; i++) {
        for (let j = 0; j < gridHeight; j++) {
          roundedRect(
            i * CELL_SIZE,
            j * CELL_SIZE,
            gridColor,
            CELL_SIZE * 0.75
          );
        }
      }
    };

    if (!context) {
      console.warn("Canvas 2D context is not available");
      return;
    }

    context.clearRect(0, 0, CELL_SIZE * gridWidth, CELL_SIZE * gridHeight);
    fillGrid();

    context.fillStyle = "blue";
    snake.forEach(([x, y]) => {
      roundedRect(x * CELL_SIZE, y * CELL_SIZE, "blue", CELL_SIZE * 0.85);
    });

    context.fillStyle = "red";
    roundedRect(
      food[0] * CELL_SIZE,
      food[1] * CELL_SIZE,
      "red",
      CELL_SIZE * 0.85
    );
  }, [food, gridWidth, gridHeight, snake]); // canvas

  const canvasWidth = CELL_SIZE * gridWidth;
  const canvasHeight = CELL_SIZE * gridHeight;
  const [offsets, setOffsets] = useState({ top: 0, left: 0 });

  useEffect(() => {
    const handleResize = () => {
      const windowWidth = window.innerWidth;
      const windowHeight = window.innerHeight;
      setOffsets({
        top: Math.max(0, (windowHeight - canvasHeight) / 2),
        left: Math.max(0, (windowWidth - canvasWidth) / 2),
      });
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [canvasWidth, canvasHeight]);

  return (
    <div className="fixed inset-0 flex items-center justify-center">
      <canvas
        ref={canvasRef}
        width={canvasWidth}
        height={canvasHeight}
        style={{
          position: "absolute",
          border: "none",
          outline: "none",
          top: `${offsets.top}px`,
          left: `${offsets.left}px`,
        }}
      />
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-3 rounded-xl w-fit max-w-lg">
        <span className="text-blue-800 dark:text-blue-300 text-4xl font-extrabold drop-shadow-sm text-center">
          snake-nextjs-socketio
        </span>
        <span className="text-red-500 dark:text-red-400 text-base text-center">
          fork this repo to make your own personal website!
        </span>
      </div>
    </div>
  );
}
