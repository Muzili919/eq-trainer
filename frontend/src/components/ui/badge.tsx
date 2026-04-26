import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground',
        secondary: 'border-transparent bg-secondary text-secondary-foreground',
        outline: 'text-foreground',
        workplace: 'border-blue-200 bg-blue-50 text-blue-700',
        social: 'border-emerald-200 bg-emerald-50 text-emerald-700',
        intimate: 'border-pink-200 bg-pink-50 text-pink-700',
        parent: 'border-amber-200 bg-amber-50 text-amber-700',
        self: 'border-violet-200 bg-violet-50 text-violet-700',
        beginner: 'border-green-200 bg-green-50 text-green-700',
        intermediate: 'border-yellow-200 bg-yellow-50 text-yellow-700',
        challenge: 'border-red-200 bg-red-50 text-red-700',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
