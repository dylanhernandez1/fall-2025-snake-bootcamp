"use client";

import { useEffect, useRef } from "react";
import { io, Socket } from "socket.io-client";

const HEADER_HEIGHT_PX = 64;

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const socketRef = useRef<Socket | undefined>(undefined);

  // TODO: variables for tracking the snake attributes

  useEffect(() => {
    if (socketRef.current === undefined) {
      socketRef.current = io("localhost:8765");

      const onConnect = () => {
        socketRef.current?.emit("start_game", {
          // TODO: data about initial game setup
        });
      };

      const onUpdate = (data: unknown) => {
        // TODO: update the snake and food state based on data from server
      };

      socketRef.current.on("connect", onConnect);
      socketRef.current.on("update", onUpdate);

      return () => {
        socketRef.current?.off("connect", onConnect);
        socketRef.current?.off("update", onUpdate);
      };
    }
  }, []); // socket stuff

  // TODO: function to draw the data to the screen

  useEffect(() => {
    const canvas = canvasRef.current;
    const context = canvas?.getContext("2d");

    if (!context) {
      console.warn("Canvas 2D context is not available");
      return;
    }

    // TODO: clear the canvas before drawing more
    // TODO: draw the info

    const observer = new MutationObserver(() => {
      // TODO: handle redwaring on theme change
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    return () => {
      observer.disconnect();
    };
  }, []); // redraw

  useEffect(() => {
    const handleResize = () => {
      // TODO: maybe manage canvas on resize
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
        // width={/* TODO: canvas width */}
        // height={/* TODO: canvas height */}
        style={{ position: "absolute", border: "none", outline: "none" }}
      />
      <div className="absolute rounded-lg p-8 w-fit flex flex-col items-center shadow-md backdrop-blur-md bg-background-trans">
        <span className="text-primary text-3xl font-extrabold mb-2 text-center">
          CSAI Student
        </span>
      </div>
    </div>
  );
}
