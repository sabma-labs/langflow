'use client'

import { MouseEvent, useState, useRef, useEffect } from 'react'
import styles from './HomeScreen2.module.scss'
import DecrativeBlock from './DecrativeBlock'
import RotateIcon from '@/components/common/RotateIcon'
import TypingAnimation from '@/components/common/TypingAnimation'
import AnimationHighlights from '@/components/common/AnimationHighlights'
import BasicArrows from '@/components/common/BasicArrows'

const Content = () => {
  const [moveIn, setMoveIn] = useState(false)
  const [contentPosition, setContentPosition] = useState({ x: 0, y: 0 })
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const contentRef = useRef<HTMLDivElement>(null)

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    // console.log(e.clientX - contentPosition.x, e.clientY - contentPosition.y)
    setMousePosition({ x: e.clientX - contentPosition.x, y: e.clientY - contentPosition.y })
  }

  const handleSetContentOffset = () => {
    if (contentRef.current) {
      const { top, left } = contentRef.current.getBoundingClientRect()
      setContentPosition({ x: left, y: top })
    }
  }

  useEffect(() => {
    if (contentRef.current) {
      handleSetContentOffset()
      window.addEventListener('scroll', handleSetContentOffset)
    }

    return () => window.removeEventListener('scroll', handleSetContentOffset)
  }, [])

  return (
    <div className={`container ${styles.content}`}
      onMouseOver={() => setMoveIn(true)}
      onMouseOut={() => setMoveIn(false)}
      onMouseMove={(e: MouseEvent<HTMLDivElement>) => handleMouseMove(e)}
      ref={contentRef}
    >
      <div className={styles.bg}>
        <AnimationHighlights
          mouseY={mousePosition.y}
          mouseX={mousePosition.x}
        />
      </div>

      <div className={styles.contentInner}>
        <div className={styles.decorative_blocks}>
          {
            [0, 1, 2, 3, 4].map(i => (
              <div key={i} className={styles.block}></div>
            ))
          }
        </div>

        <div className={styles.middleInner}>
          <DecrativeBlock
            mouseX={ mousePosition.x }
            mouseY={ mousePosition.y }
            moveIn={ moveIn }
            type='left'
          />
          <div className={styles.content_box}>
            <TypingAnimation>
              <h2>
              Build the Next-Generation Web3 Applications with LEGO-level Experience
              </h2>
            </TypingAnimation>
            {/* <div className={styles.content_box_inner}>

              The first cloud protocol to revolutionize the construction of Web3 applications
            </div> */}
          </div>
          <DecrativeBlock
            mouseX={ mousePosition.x }
            mouseY={ mousePosition.y }
            moveIn={ moveIn }
            type='right'
          />
        </div>

        <div className={ styles.arrows_wrapper }>
          <BasicArrows />
        </div>

        <div className={styles.bottomInner}>
          <div className={ `a-4 ${ styles.bottom_block }` }>
            <pre>{ '//' }</pre>
            <div>{ '<A class="Core Features">href' }</div>
            <div>{ '<P class="Positioning">' }</div>
            <pre>{'}'}</pre>
          </div>
          <div className={styles.bottom_block}></div>
          <div className={styles.bottom_icon}>
            <RotateIcon />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Content