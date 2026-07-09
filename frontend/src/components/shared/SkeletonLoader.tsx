import React from 'react';
import { motion } from 'framer-motion';

interface SkeletonLoaderProps {
  className?: string;
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ className = '' }) => {
  return (
    <motion.div
      initial={{ opacity: 0.4 }}
      animate={{ opacity: 0.8 }}
      transition={{
        repeat: Infinity,
        repeatType: "reverse",
        duration: 1.2,
        ease: "easeInOut"
      }}
      className={`bg-brand-dark rounded-xl border border-brand-accent/20 ${className}`}
    />
  );
};
