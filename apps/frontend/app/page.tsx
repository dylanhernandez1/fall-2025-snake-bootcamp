"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { io, Socket } from "socket.io-client";

const CELL_SIZE = 40;
const HEADER_HEIGHT_PX = 64;
const DEFAULT_GRID_HEIGHT = Math.floor(
  (window.innerHeight - HEADER_HEIGHT_PX) / CELL_SIZE
);
const DEFAULT_GRID_WIDTH = Math.floor((window.innerWidth - 20) / CELL_SIZE);

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const socketRef = useRef<Socket | undefined>(undefined);

  const [gridWidth, setGridWidth] = useState<number>(DEFAULT_GRID_WIDTH);
  const [gridHeight, setGridHeight] = useState<number>(DEFAULT_GRID_HEIGHT);
  const [snake, setSnake] = useState<number[][]>([]);
  const [food, setFood] = useState<number[]>([]);
  const [delay, setDelay] = useState<number>(0.03);
  const changingDelay = useRef(false);

  useEffect(() => {
    setGridHeight(
      Math.floor((window.innerHeight - HEADER_HEIGHT_PX) / CELL_SIZE)
    );
    setGridWidth(Math.floor((window.innerWidth - 4) / CELL_SIZE));
  }, []); // initial grid size

  useEffect(() => {
    if (socketRef.current === undefined) {
      socketRef.current = io("localhost:8765");

      const onConnect = () => {
        socketRef.current?.emit("start_game", {
          grid_width: DEFAULT_GRID_WIDTH,
          grid_height: DEFAULT_GRID_HEIGHT,
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

  const drawRoundedRect = (
    context: CanvasRenderingContext2D,
    x: number,
    y: number,
    color: string,
    size: number
  ) => {
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

  const fillGrid = useCallback(
    (context: CanvasRenderingContext2D) => {
      const gridColor = getComputedStyle(
        document.documentElement
      ).getPropertyValue("--background-alt");

      for (let i = 0; i < gridWidth; i++) {
        for (let j = 0; j < gridHeight; j++) {
          drawRoundedRect(
            context,
            i * CELL_SIZE,
            j * CELL_SIZE,
            gridColor,
            CELL_SIZE * 0.75
          );
        }
      }
    },
    [gridHeight, gridWidth]
  ); // fill grid

  const drawSnakeAndFood = useCallback(
    (context: CanvasRenderingContext2D) => {
      const snakeColor = getComputedStyle(
        document.documentElement
      ).getPropertyValue("--chart-2");
      const foodColor = getComputedStyle(
        document.documentElement
      ).getPropertyValue("--chart-5");
      context.fillStyle = snakeColor;
      snake.forEach(([x, y]) => {
        drawRoundedRect(
          context,
          x * CELL_SIZE,
          y * CELL_SIZE,
          snakeColor,
          CELL_SIZE * 0.85
        );
      });
      context.fillStyle = foodColor;
      drawRoundedRect(
        context,
        food[0] * CELL_SIZE,
        food[1] * CELL_SIZE,
        foodColor,
        CELL_SIZE * 0.85
      );
    },
    [food, snake]
  ); // draw snake and food

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");

    if (!context) {
      console.warn("Canvas 2D context is not available");
      return;
    }

    context.clearRect(0, 0, CELL_SIZE * gridWidth, CELL_SIZE * gridHeight);
    fillGrid(context);
    drawSnakeAndFood(context);

    const observer = new MutationObserver(() => {
      context.clearRect(0, 0, CELL_SIZE * gridWidth, CELL_SIZE * gridHeight);
      fillGrid(context);
      drawSnakeAndFood(context);
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => {
      observer.disconnect();
    };
  }, [food, gridWidth, gridHeight, snake, fillGrid, drawSnakeAndFood]); // redraw

  useEffect(() => {
    const handleResize = () => {
      setGridWidth(Math.floor((window.innerWidth - 4) / CELL_SIZE));
      setGridHeight(
        Math.floor((window.innerHeight - HEADER_HEIGHT_PX) / CELL_SIZE)
      );
    };

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []); // resize

  return (
    <div className="absolute top-16 left-0 right-0 bottom-0 flex flex-col items-center justify-center">
      <canvas
        ref={canvasRef}
        width={CELL_SIZE * (gridWidth ?? 0)}
        height={CELL_SIZE * (gridHeight ?? 0)}
        tabIndex={0}
        autoFocus
        style={{ position: "absolute", border: "none", outline: "none" }}
      />
      <div className="absolute rounded-lg p-8 w-fit flex flex-col items-center shadow-md backdrop-blur-md bg-background-trans">
        <span className="text-primary text-3xl font-extrabold mb-2 text-center">
          CSAI Student
        </span>
        <span className="text-primary text-xl font-bold text-center">
          Cal Poly San Luis Obispo
        </span>
        <span className="text-md text-center text-chart-5 mt-1">
          watch the snake learn in the background!
        </span>
      </div>
    </div>
  );
}
