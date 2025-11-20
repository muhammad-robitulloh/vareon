import { Button } from '@/components/ui';
import { ArrowRight, Sparkles } from "lucide-react";
import { Link } from "wouter";
import { motion } from "framer-motion";

export default function Hero() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <div className="relative min-h-[calc(100vh-4rem)] flex items-center justify-center overflow-hidden">
      {/* Background Effect - Subtle Animated Grid */}
      <div className="absolute inset-0 z-0 opacity-10">
        <div className="absolute inset-0 bg-grid-small-white/[0.2] [mask-image:linear-gradient(to_b,white,transparent)]" />
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-transparent opacity-50" />
      </div>

      <motion.div
        className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 lg:px-8 z-10"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
          <motion.div
            className="mb-6 inline-flex items-center space-x-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-2"
            variants={itemVariants}
          >
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm font-medium text-primary">
              Powered by Arcana AI
            </span>
          </motion.div>

          <motion.h1
            className="mb-6 text-5xl font-bold tracking-tight text-foreground sm:text-6xl md:text-7xl text-glow"
            variants={itemVariants}
          >
            Engineering
            <br />
            <motion.span
              className="bg-gradient-to-r from-primary to-blue-400 bg-clip-text text-transparent"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 1 }}
            >
              Adaptive Intelligence
            </motion.span>
          </motion.h1>

          <motion.p
            className="mb-12 max-w-2xl text-lg text-muted-foreground sm:text-xl"
            variants={itemVariants}
          >
            The VAREON ecosystem integrates cutting-edge AI with manufacturing execution systems.
            From research to production, powered by Arcana's multi-model orchestration.
          </motion.p>

          <motion.div
            className="flex flex-col items-center space-y-4 sm:flex-row sm:space-x-4 sm:space-y-0"
            variants={itemVariants}
          >
            <Link href="/neosyntis-demo">
              <Button size="lg" className="group bg-primary text-primary-foreground hover:bg-primary/90">
                Try NEOSYNTIS Lab
                <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Button>
            </Link>
            <Link href="/arcana-demo">
              <Button size="lg" variant="outline" className="border-primary text-primary hover:bg-primary/10">
                Explore Arcana AI
              </Button>
            </Link>
          </motion.div>

          <motion.div
            className="mt-20 grid gap-6 sm:grid-cols-3"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
          >
            <motion.div className="rounded-xl card-glow bg-card p-6" variants={itemVariants} whileHover={{ scale: 1.05 }}>
              <div className="mb-2 text-3xl font-bold text-primary">150K+</div>
              <div className="text-sm text-muted-foreground">AI Inferences Daily</div>
            </motion.div>
            <motion.div className="rounded-xl card-glow bg-card p-6" variants={itemVariants} whileHover={{ scale: 1.05 }}>
              <div className="mb-2 text-3xl font-bold text-primary">99.9%</div>
              <div className="text-sm text-muted-foreground">System Uptime</div>
            </motion.div>
            <motion.div className="rounded-xl card-glow bg-card p-6" variants={itemVariants} whileHover={{ scale: 1.05 }}>
              <div className="mb-2 text-3xl font-bold text-primary">24/7</div>
              <div className="text-sm text-muted-foreground">Real-time Monitoring</div>
            </motion.div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
