import React, { useState, useEffect } from 'react';

interface TypewriterEffectProps {
  text: string;
  delay?: number; // Delay between each character in ms
  onComplete?: () => void; // Callback when typing is complete
  prefix?: string; // Optional prefix like "> "
}

export const TypewriterEffect: React.FC<TypewriterEffectProps> = ({
  text,
  delay = 20,
  onComplete,
  prefix = '',
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prevText => prevText + text[currentIndex]);
        setCurrentIndex(prevIndex => prevIndex + 1);
      }, delay);
      return () => clearTimeout(timeout);
    } else if (onComplete) {
      onComplete();
    }
  }, [text, delay, currentIndex, onComplete]);

  return <>{prefix}{displayedText}</>;
};
