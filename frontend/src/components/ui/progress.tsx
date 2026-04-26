import * as React from 'react'
import { cn } from '@/lib/utils'

interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number
  max?: number
  indicatorClassName?: string
}

const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value, max = 5, indicatorClassName, ...props }, ref) => (
    <div
      ref={ref}
      className={cn('relative h-2 w-full overflow-hidden rounded-full bg-secondary', className)}
      {...props}
    >
      <div
        className={cn('h-full rounded-full transition-all duration-500 ease-out', indicatorClassName || getProgressColor(value, max))}
        style={{ width: `${(value / max) * 100}%` }}
      />
    </div>
  )
)
Progress.displayName = 'Progress'

function getProgressColor(value: number, max: number): string {
  const ratio = value / max
  if (ratio >= 0.8) return 'bg-emerald-500'
  if (ratio >= 0.6) return 'bg-violet-500'
  if (ratio >= 0.4) return 'bg-amber-500'
  return 'bg-red-500'
}

export { Progress }
