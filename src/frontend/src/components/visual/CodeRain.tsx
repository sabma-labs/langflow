import { useEffect, useState } from "react";

const CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890".split("");

const generateRainLine = (length: number) =>
  Array.from({ length }, () => CHAR_SET[Math.floor(Math.random() * CHAR_SET.length)]);

type CodeRainProps = {
  side?: "left" | "right";
  columnCount?: number;
};

const CodeRain = ({ side = "left", columnCount = 3 }: CodeRainProps) => {
  const [rains, setRains] = useState<string[][]>([]);

  useEffect(() => {
    // 初始化每列 rain
    setRains(Array.from({ length: columnCount }, () => generateRainLine(30)));
  }, [columnCount]);

  useEffect(() => {
    const interval = setInterval(() => {
      setRains((prev) =>
        prev.map((line) => {
          const newLine = [...line];
          newLine.pop();
          newLine.unshift(CHAR_SET[Math.floor(Math.random() * CHAR_SET.length)]);
          return newLine;
        })
      );
    }, 120);

    return () => clearInterval(interval);
  }, []);

  return (
    <div
      className={`absolute top-0 bottom-0 z-10 pointer-events-none flex gap-4 px-2
        ${side === "left" ? "left-0" : "right-0 flex-row-reverse"}`}
    >
      {rains.map((line, colIdx) => (
        <div key={colIdx} className="flex flex-col text-green-400 text-xs font-mono opacity-30 leading-tight">
          {line.map((char, i) => (
            <span key={i} className={i < 2 ? "opacity-90 text-white" : ""}>
              {char}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
};

export default CodeRain;
