import type { LucideIcon } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface StatusCardProps {
  title: string
  value: string
  icon: LucideIcon
  description?: string
  trend?: string
  variant?: "default" | "success" | "warning" | "danger"
}

export function StatusCard({ title, value, icon: Icon, description, trend, variant = "default" }: StatusCardProps) {
  const variantStyles = {
    default: "bg-card",
    success: "bg-card border-l-4 border-l-chart-4",
    warning: "bg-card border-l-4 border-l-chart-2",
    danger: "bg-card border-l-4 border-l-destructive",
  }

  return (
    <Card className={cn("overflow-hidden", variantStyles[variant])}>
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <div className="mt-2 flex items-baseline gap-2">
              <h3 className="text-2xl font-bold text-foreground">{value}</h3>
              {trend && <span className="text-sm text-muted-foreground">{trend}</span>}
            </div>
            {description && <p className="mt-2 text-xs text-muted-foreground">{description}</p>}
          </div>
          <div
            className={cn(
              "flex h-12 w-12 items-center justify-center rounded-lg",
              variant === "success" && "bg-chart-4/10",
              variant === "warning" && "bg-chart-2/10",
              variant === "danger" && "bg-destructive/10",
              variant === "default" && "bg-primary/10",
            )}
          >
            <Icon
              className={cn(
                "h-6 w-6",
                variant === "success" && "text-chart-4",
                variant === "warning" && "text-chart-2",
                variant === "danger" && "text-destructive",
                variant === "default" && "text-primary",
              )}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
