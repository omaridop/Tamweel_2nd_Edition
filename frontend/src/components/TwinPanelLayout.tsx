import React from 'react';
import { motion } from 'framer-motion';

interface TwinPanelLayoutProps {
  leftPanel: React.ReactNode;
  rightPanel?: React.ReactNode;
  headerTitle?: React.ReactNode;
}

export const TwinPanelLayout: React.FC<TwinPanelLayoutProps> = ({ leftPanel, rightPanel, headerTitle }) => {
  return (
    <div className="flex flex-col lg:flex-row gap-6 h-full min-h-[calc(100vh-8rem)]">
      {/* Financial Context (Left Panel / Drawer on Mobile) */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.4 }}
        className={`flex flex-col space-y-6 overflow-y-auto no-scrollbar pb-10 ${rightPanel ? 'w-full lg:w-3/5 xl:w-2/3' : 'w-full'}`}
      >
        {headerTitle && (
          <div className="mb-4">
            {headerTitle}
          </div>
        )}
        {leftPanel}
      </motion.div>

      {/* Chat Conversation (Right Panel) */}
      {rightPanel && (
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
          className="w-full lg:w-2/5 xl:w-1/3 flex flex-col h-[600px] lg:h-[calc(100vh-10rem)] rounded-3xl overflow-hidden glass shadow-glow border border-brand-accent/20 sticky top-6"
        >
          {rightPanel}
        </motion.div>
      )}
    </div>
  );
};
