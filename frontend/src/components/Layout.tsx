import { ReactNode } from 'react'

interface LayoutProps {
  children: ReactNode
}

/** 响应式布局容器 */
export function Layout({ children }: LayoutProps) {
  return (
    <div className="h-screen w-screen overflow-hidden bg-gray-50 text-gray-900">
      {children}
    </div>
  )
}
