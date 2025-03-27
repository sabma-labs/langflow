'use client'

import { FC, useMemo, useRef, useState, useEffect } from 'react'
import * as pixi from './pixi.js'
import { Stage, Container, Sprite, Text, Graphics, useTick } from '@pixi/react'
import gsap from 'gsap'

type IProps = {
  mouseX: number,
  mouseY: number,
}

const AnimationHighlights: FC<IProps> = ({ mouseX, mouseY }) => {
  const [ size, setSize ] = useState({ width: 0, height: 0 })
  const [ mask, setMask ] = useState<any>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)

  const clearMask = (g: pixi.Graphics) => {
    const r = g.clone()
    let obj = { num: .3, num2: 40 }
    gsap.to(obj, {
      num: 0,
      num2: 1,
      duration: .5,
      delay: 0,
      ease: 'slow',
      onUpdate: () => {
        r.beginFill(0xDE3249, obj.num)
        r.drawCircle(mouseX, mouseY, obj.num2)
        r.endFill()
      },
      onComplete: () => {
        r.clear()
      }
    })
  }

  const drawMask = (g: pixi.Graphics) => {
    g.beginFill(0xDE3249, 1);
    g.drawCircle(mouseX, mouseY, 40);
    g.endFill();

    clearMask(g)
  }

  useEffect(() => {
    const wrapper = wrapperRef.current
    if (wrapper) {
      setSize({ width: wrapper.offsetWidth, height: wrapper.offsetHeight })
    }
  }, [])

  return (
    <div ref={ wrapperRef } style={{ width: '100%', height: '100%', overflow: 'hidden' }}>
      <Stage width={ size.width } height={ size.height } options={{ backgroundAlpha: .5 }}>
        {/* <Sprite
          image="https://pixijs.io/pixi-react/img/bunny.png"
          x={400}
          y={270}
          anchor={{ x: 0.5, y: 0.5 }}
        /> */}

        <Sprite
          image='/imgs/groupPoint.png'
          width={ size.width }
          height={ size.height }
          x={ 0 }
          y={ 0 }
          mask={ mask }
        />

        <Sprite
          image='/imgs/groupPoint.png'
          width={ size.width }
          height={ size.height }
          x={ 0 }
          y={ 0 }
          alpha={ .2 }
        />

        <Graphics
          draw={ drawMask }
          ref={ ref => setMask(ref) }
          alpha={ 1 }
        />

        <Container x={400} y={330}>
          {/* <Text text="Hello World" anchor={{ x: 0.5, y: 0.5 }} filters={[blurFilter]}
            style={
              new TextStyle({
                fontSize: 36,
                fill: 'white'
              })
            }
          /> */}
          {/* <Sprite
            image='/imgs/groupPoint.png'
            width={ size.width }
            height={ size.height }
            x={ 0 }
            y={ 0 }
            mask={ mask }

          />

          <Graphics
            draw={ g => {
              let alpha = .3
              g.beginFill(0xDE3249, alpha);
              g.drawCircle(mouseX, mouseY, 30);
              g.endFill();
            }}
            ref={ ref => setMask(ref) }
          /> */}
        </Container>
      </Stage>
    </div>
  )
}

export default AnimationHighlights