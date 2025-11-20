import * as React from "react"
import { motion, HTMLMotionProps } from "framer-motion"

import { cn } from "@/lib/utils"

// Helper to merge types and overwrite conflicting keys
type Merge<T, U> = Omit<T, keyof U> & U;

// Define MotionDivProps that merges React's div attributes and framer-motion's props
type MotionDivProps = Merge<
  React.HTMLAttributes<HTMLDivElement>,
  HTMLMotionProps<"div">
>;


const Card = React.forwardRef<
  HTMLDivElement,
  MotionDivProps
>(({ className, ...props }, ref) => (
  <motion.div
    ref={ref}
    className={cn(
      "shadcn-card rounded-xl card-glow bg-card text-card-foreground",
      className
    )}
    whileHover={{ scale: 1.01 }}
    transition={{ type: "spring", stiffness: 300, damping: 20 }}
    {...props}
  />
));
Card.displayName = "Card"

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight text-foreground", // Ensure text-foreground
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)} // Ensure text-muted-foreground
    {...props}
  />
));
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"
export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
}
