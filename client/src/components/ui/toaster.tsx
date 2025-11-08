import { useToast } from "@/hooks/use-toast"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from '@/components/ui';
import { CheckCircle2, XCircle, AlertTriangle, Info } from 'lucide-react';

export function Toaster() {
  const { toasts } = useToast()

  return (
    <ToastProvider>
      {toasts.map(function ({ id, title, description, action, variant, ...props }) {
        return (
          <Toast key={id} {...props}>
            <div className="flex items-center">
              {variant === "success" && <CheckCircle2 className="h-5 w-5 text-green-400 mr-3" />}
              {variant === "destructive" && <XCircle className="h-5 w-5 text-red-400 mr-3" />}
              {variant === "warning" && <AlertTriangle className="h-5 w-5 text-orange-400 mr-3" />}
              {variant === "default" && <Info className="h-5 w-5 text-blue-400 mr-3" />}
              <div className="grid gap-1">
                {title && <ToastTitle>{title}</ToastTitle>}
                {description && (
                  <ToastDescription>{description}</ToastDescription>
                )}
              </div>
            </div>
            {action}
            <ToastClose />
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
