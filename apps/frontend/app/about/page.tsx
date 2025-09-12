"use client";

import Image from "next/image";

export default function AboutPage() {
  return (
    <div className="min-h-screen w-full flex flex-col items-center justify-center bg-background px-2 py-8">
      <div className="rounded-lg shadow-md backdrop-blur-md bg-card w-full max-w-2xl p-4 sm:p-8 flex flex-col gap-6">
        <span className="text-primary text-3xl font-extrabold mb-2">
          about me
        </span>
        <div className="flex flex-col sm:flex-row gap-6 items-center justify-center mb-2">
          <Image
            src="/image.png"
            alt="student image"
            width={300}
            height={300}
            className="rounded-[10px] w-[150px] h-[150px] sm:w-[250px] sm:h-[250px] md:w-[300px] md:h-[300px] object-cover"
          />
          <div className="flex flex-col gap-2 w-full sm:max-w-xs">
            <span className="block text-foreground">
              This is a text block for some stuff about you!
            </span>
            <span className="block text-foreground">more text</span>
          </div>
        </div>
      </div>
    </div>
  );
}
