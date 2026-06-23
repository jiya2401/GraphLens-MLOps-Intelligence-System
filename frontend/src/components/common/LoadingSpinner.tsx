import { motion } from 'framer-motion';

export function LoadingSpinner({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-64 gap-4">
      <motion.div
        className="w-10 h-10 rounded-full border-2 border-transparent"
        style={{ borderTopColor: 'var(--accent-primary)', borderRightColor: 'var(--accent-secondary)' }}
        animate={{ rotate: 360 }}
        transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      />
      <span className="text-sm" style={{ color: 'var(--text-muted)' }}>{message}</span>
    </div>
  );
}
