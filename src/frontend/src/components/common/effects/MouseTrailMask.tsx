import { useEffect, useState } from "react"

type Position = { x: number; y: number }

const MouseTrailMask = () => {
  const [trail, setTrail] = useState<Position[]>([])

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const pos = { x: e.clientX, y: e.clientY }

      setTrail((prev) => {
        const updated = [...prev, pos]
        return updated.slice(-15) // 保留最近10个位置点
      })
    }

    window.addEventListener("mousemove", handleMouseMove)
    return () => window.removeEventListener("mousemove", handleMouseMove)
  }, [])

  return (
    <>
      {trail.map((pos, index) => {
        const opacity = 1 - index / trail.length
        const radius = 50 * (index / trail.length) + 10
        return (
          <circle
            key={index}
            cx={pos.x}
            cy={pos.y}
            r={radius}
            fill="black"
            fillOpacity={opacity * 0.6}
          />
        )
      })}
    </>
  )
}

export default MouseTrailMask
