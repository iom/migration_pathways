import './ResponsiveIllustration.css'

import motto from "./assets/images/motto.svg"
import concept from "./assets/images/concept.svg"
import topIllustrationTopRightCircle from "./assets/images/topIllustration-topRightCircle.svg"
import topIllustrationLeftCircle from "./assets/images/topIllustration-leftCircle.svg"
import rightIllustrationTopRightCircle from "./assets/images/rightIllustration-topRightCircle.svg"

export default function ResponsiveIllustration (props)
{
        if(props.location === "top") return <div className='ResponsiveIllustration-top'>
                <div className='ResponsiveIllustration_top-motto'>
                        <p>Your Journey,</p>
                        <p>Your Future</p>
                        <p>Let's <span>Make It Safe</span>.</p>
                </div>

                <img className='ResponsiveIllustration_top-concept' src={concept} alt="My Rafiki" />

                <img className='ResponsiveIllustration_top-leftCircle' src={topIllustrationLeftCircle} alt="Design" />

                <img className='ResponsiveIllustration_top-topRightCircle' src={topIllustrationTopRightCircle} alt="Design" />
        </div>

        else return <div className='ResponsiveIllustration-right'>
                <div className='ResponsiveIllustration_right-blueRectangle' />

                <div className='ResponsiveIllustration_right-orangeRectangle' />

                <div className='ResponsiveIllustration_right-yellowRectangle' />

                <div className='ResponsiveIllustration_right-contentRectangle'>
                        <img className='ResponsiveIllustration_right-motto' src={motto} alt="Your Journey, Your Future — Let's Make It Safe." />

                        <img className='ResponsiveIllustration_right-concept' src={concept} alt="My Rafiki" />
                </div>

                <img className='ResponsiveIllustration_right-topRightCircle' src={rightIllustrationTopRightCircle} alt="Design" />
        </div>
}
